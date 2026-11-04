"""Whole-model audit: how the parts fit TOGETHER (complements hand.py / generate_parts.py checks).

Every pin path, socket, slot and channel is probed with a solid slightly smaller than the real
item (pin, tab, string, cord). Any plastic in the way is reported as a failure, which catches
'filled-in' holes like the prototype-1 palm plugs. Also: one solid piece per part, supports needed
per part in its print orientation, and that the new palm only REMOVES plastic from the old one.

Run:  python audit.py            (exit code 1 if anything fails)
"""
from __future__ import annotations

import math
import os
import subprocess
import sys
import tempfile

import manifold3d as m
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import palm_camera as PC  # noqa: E402
import generate_parts as gp  # noqa: E402
import hand as H  # noqa: E402

FAIL = []


def ok(cond, msg):
    print(("   OK    " if cond else "   FAIL  ") + msg)
    if not cond:
        FAIL.append(msg)


def blocked(part, probe):
    return (part ^ probe).volume()


def seg_probe(points, d):
    """Chain of rods + balls through world points (a bendy string / cord)."""
    out = None
    for a, b in zip(points[:-1], points[1:]):
        r = H.rod(a, b, d, 16) + m.Manifold.sphere(d / 2, 16).translate(tuple(b))
        out = r if out is None else out + r
    return out


def man(mesh):
    return m.Manifold(m.Mesh(vert_properties=np.asarray(mesh.vertices, np.float32),
                             tri_verts=np.asarray(mesh.faces, np.uint32)))


def overhang(part, rot, name, expect_support):
    """Downward faces steeper than ~48 deg (print orientation), grouped into connected patches.
    A patch is harmless if it is a small hole/channel (narrower than 3.5 mm) or a flat bridge
    (nearly horizontal, narrower than 30 mm: the P1S bridges that cleanly), or the rounded
    edge in the first 2 mm above the bed (the brim takes it). What's left would need support."""
    import networkx as nx
    p = part.rotate(rot)
    p = p.translate((0, 0, -p.bounding_box()[2]))
    mm = p.to_mesh()
    t = trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts), process=True)
    n, c, a = t.face_normals, t.triangles_center, t.area_faces
    down = np.where((n[:, 2] < -0.74) & (c[:, 2] > 0.3))[0]      # steeper than ~48 deg from vertical (45 deg prints fine)
    g = nx.Graph(); g.add_nodes_from(down)
    dset = set(down.tolist())
    for f1, f2 in t.face_adjacency:
        if f1 in dset and f2 in dset:
            g.add_edge(f1, f2)
    bad = 0.0
    for comp in nx.connected_components(g):
        idx = np.fromiter(comp, int)
        pts = t.vertices[t.faces[idx].reshape(-1)]
        ext = np.sort(pts[:, :2].max(0) - pts[:, :2].min(0))
        flat = np.all(n[idx, 2] < -0.97)
        if ext[0] <= 3.5 or (flat and ext[0] <= 30.0) or pts[:, 2].max() <= 2.0:
            continue
        bad += a[idx].sum()
    bed = a[(n[:, 2] < -0.99) & (c[:, 2] <= 0.3)].sum()
    print(f"         {name:<16} bed contact {bed:7.0f} mm2, overhang needing support {bad:6.0f} mm2"
          + ("  (palm: tree support from the build plate, as in the guide)" if expect_support else ""))
    return bad, bed


def main():
    print("Building every part ...")
    P, SP, ST = H.palm(), H.spine(), H.stand()
    bones = {n: H.finger_bones(n) for n in H.ORDER}
    CV = PC.cover()

    # ------------------------------------------------------------------ 1 palm
    print("\n1) Palm")
    old = subprocess.run(["git", "show", "4d8aa27:cad/stl/hand/palm.stl"], capture_output=True, cwd=HERE).stdout
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as fh:
        fh.write(old)
    old_m = man(trimesh.load(fh.name))
    new_stl = man(trimesh.load(os.path.join(HERE, "stl", "hand", "palm.stl")))
    off = np.array(P.bounding_box()[:3]) - np.array(new_stl.bounding_box()[:3])
    old_m = old_m.translate(tuple(off))
    rail_zone = H.box(21.9, 40, -12, 12, H.WRIST_Z - 1, H.CAM_RAIL_Z[1] + 0.5)
    old_tunnels = None                     # the old elastic tunnels (column + sloping exit): now solid, as intended
    for n in H.ORDER:
        B_ = H.finger_basis(n)
        e0_ = H.local_to_world_pt((-gp.C - H.PALM_DROP - 2 + 1, 0.0, gp.EXT_Z - gp.ZP), n)
        top_ = H.local_to_world_pt((-gp.C + 1, 0.0, gp.EXT_Z - gp.ZP), n)
        tun = H.rod(e0_, e0_ + (-B_[:, 0] * .8 - B_[:, 2] * .6) * 40, gp.EXT_D + 0.6) + H.rod(top_, e0_, gp.EXT_D + 0.6) \
            + m.Manifold.sphere(gp.EXT_D / 2 + 0.8, 16).translate(tuple(e0_))
        old_tunnels = tun if old_tunnels is None else old_tunnels + tun
    added = ((P - old_m) - rail_zone - old_tunnels).volume()
    removed = (old_m - P).volume()
    forks = None
    for n in H.ORDER:
        f_ = H.place(gp.box(-gp.R - 0.5, gp.R + 0.5, -gp.W / 2 - 0.5, gp.W / 2 + 0.5, gp.ZP - gp.R - 0.5, gp.H / 2 + 0.5).translate((0, 0, -gp.ZP)), n)
        forks = f_ if forks is None else forks + f_
    fork_change = ((P ^ forks) - (old_m ^ forks)).volume() + ((old_m ^ forks) - (P ^ forks)).volume()
    ok(added < 0.5, f"new palm adds plastic only for the camera rail and where the old elastic tunnels were (elsewhere {added:.2f} mm3)")
    ok(fork_change < 1.0 + sum((H.ELASTIC[n]["cut"] ^ forks).volume() for n in H.ORDER),
       f"knuckle forks (where the printed fingers pin on) unchanged except the elastic funnel ({fork_change:.1f} mm3)")
    ok(removed > 50, f"new palm removes {removed:.0f} mm3 (plugs in the string holes, wider smooth elastic tunnels)")
    stl_diff = (new_stl.translate(tuple(off)) ^ P).volume() / P.volume()
    ok(abs(stl_diff - 1) < 0.01, f"palm.stl on disk = the current model ({stl_diff * 100:.1f} %)")
    col_len = H.PALM_DROP + 2
    for n in H.ORDER:
        # pin through the knuckle fork (1.75 mm filament, 17 mm long)
        pin = H.place(gp.rod_y(1.7, 0, gp.ZP, -8.5, 8.5).translate((0, 0, -gp.ZP)), n)
        b1 = blocked(P, pin)
        # slot between the prongs: room for the finger's tongue (6 mm in a 6.6 mm slot)
        slot = H.place(gp.box(-gp.R, gp.R, -gp.TONGUE_HALF, gp.TONGUE_HALF, gp.ZP - gp.R, gp.ZP + gp.R)
                       .translate((0, 0, -gp.ZP)) - gp.rod_y(gp.PIN_HOLE_TONGUE + 4, 0, 0, -9, 9), n)
        b2 = blocked(P, slot ^ H.place(m.Manifold.cylinder(1, 1, 1).scale((1, 1, 1)).translate((0, 0, 0)), n)) if False else 0.0
        # use the real proximal bone instead: at -3 / 0 / 45 / 85 deg it must not touch the palm
        b2 = max((P ^ H.posed(n, a)[0]).volume() for a in (0, 45, 85))
        # string: knuckle-fork top -> column -> palm channel -> wrist (ball 1.2 mm)
        _, w, k = H.string_path(n)
        top_s = H.local_to_world_pt((-gp.C + 0.5, 0.0, gp.FLEX_Z - gp.ZP), n)
        b3 = blocked(P, seg_probe([top_s, k, w - np.array([0, 0, 3])], 1.2))
        # elastic: the REAL cord (2.3 mm = 2 mm + print shrink) along the smooth tunnel to the exit
        E_ = H.ELASTIC[n]
        b4 = blocked(P, seg_probe(E_["path"] + [E_["exit"] + E_["dir"] * 2], 2.3))
        ok(max(b1, b2, b3, b4) < 0.3, f"{n:<6} fork pin path {b1:.2f}, finger 0-85 deg {b2:.2f}, "
           f"string path {b3:.2f}, elastic path {b4:.2f} mm3 of plastic in the way")
    tab = gp.box(-H.SPINE_T / 2, H.SPINE_T / 2, -15.0, 15.0, H.WRIST_Z - 0.5, H.SPINE_TOP)
    ok(blocked(P, tab) < 0.1, f"spine tab (5 x 30 mm) slides into the palm socket: {blocked(P, tab):.2f} mm3 in the way")
    for y in (-5.0, 5.0):
        pin = H.rod((-22.5, y, H.WRIST_Z + 7), (22.5, y, H.WRIST_Z + 7), 1.7)
        ok(blocked(P, pin) + blocked(SP, pin) < 0.1,
           f"palm->spine pin y={y:+.0f} (45 mm) passes palm + spine: {blocked(P, pin) + blocked(SP, pin):.2f} mm3")

    # ------------------------------------------------------------------ 2 spine / stand / servos
    print("\n2) Spine, stand, servos")
    ok((SP ^ ST).volume() < 0.1, f"spine sits in the stand socket without touching: {(SP ^ ST).volume():.2f} mm3")
    ok((SP ^ P).volume() < 0.1, f"spine tab vs palm: {(SP ^ P).volume():.2f} mm3")
    for y in (-20.0, 20.0):
        pin = H.rod((-13, y, H.SPINE_BOT + 11), (13, y, H.SPINE_BOT + 11), 1.7)
        b = blocked(ST, pin) + blocked(SP, pin)
        ok(b < 0.1, f"stand->spine pin y={y:+.0f} (26 mm) passes stand + spine: {b:.2f} mm3")
    for n in H.ORDER:
        body, sp, holes, _ = H.servo_geom(n)
        bt = (body ^ SP).volume()
        sh = sum(blocked(SP, H.rod((-4, hy, hz), (4, hy, hz), 1.5)) for hy, hz in holes)
        ok(bt < 0.1 and sh < 0.1, f"{n:<6} servo fits its window ({bt:.2f}) and both screw holes are open ({sh:.2f})")

    # ------------------------------------------------------------------ 3 fingers (already printed: report only)
    print("\n3) Finger bones (already printed - checked so you know they are right)")
    for n in H.ORDER:
        L = H.finger_L(n)
        res = []
        for i, (b, length) in enumerate(zip(bones[n], L)):
            last = i == len(L) - 1
            x1 = length - (8.5 if last else 0.5)
            s = blocked(b, gp.rod_x(1.2, 0, gp.FLEX_Z, 0.5, x1))
            e = blocked(b, gp.rod_x(1.8, 0, gp.EXT_Z, 0.5 if i else 0.5, x1 + (8.0 if last else 0)))
            pin = blocked(b, gp.rod_y(1.7, 0, gp.ZP, -2.9, 2.9))
            if not last:
                pin += blocked(b, gp.rod_y(1.7, length, gp.ZP, -8.5, 8.5) - gp.box(length - 6, length + 6, -3.3, 3.3, -9, 9))
            res.append(max(s, e, pin))
        ok(max(res) < 0.3, f"{n:<6} every bone: string + elastic holes open, pin holes open "
           f"(worst {max(res):.2f} mm3)")

    # ------------------------------------------------------------------ 4 palm camera
    print("\n4) Palm camera cover (new)")
    ok((CV ^ P).volume() < 0.05, f"cover slides onto the palm rail without touching: {(CV ^ P).volume():.2f} mm3")
    worst = max((CV ^ b).volume() for a in range(0, 91, 10) for n in H.ORDER for b in H.posed(n, a))
    ok(worst < 0.05, f"fingers + thumb 0-90 deg never touch the camera cover ({worst:.2f} mm3)")
    pin = gp.rod_y(1.7, (H.CAM_RAIL_X[0] + H.CAM_RAIL_X[1]) / 2, PC.LOCK_Z, -11.2, 11.2)
    ok(blocked(CV, pin) + blocked(P, pin) < 0.05, "camera lock pin (22 mm) path is open")
    stuffc = [SP, ST] + [H.servo_geom(n)[1] for n in H.ORDER] + [H.servo_geom(n)[0] for n in H.ORDER]
    v = sum((CV ^ s_).volume() for s_ in stuffc)
    ok(v < 0.05, f"camera cover vs spine, stand, servos, spools: {v:.2f} mm3")

    # ------------------------------------------------------------------ 5 every part: one piece + supports
    print("\n5) Every printed part: one solid piece, supports needed in its print orientation")
    parts = [("palm", P, (0, 0, 0), True), ("spine", SP, (0, 90, 0), False), ("stand", ST, (0, 0, 0), False),
             ("spool", gp.spool(), (0, 0, 0), False), ("camera_cover", CV, (0, 0, 0), False)]
    for n in H.ORDER:
        for i, b in enumerate(bones[n]):
            parts.append((f"{n}_{i + 1}", b, (180, 0, 0), False))
    for name, part, rot, sup in parts:
        pieces = len(part.decompose())
        area, bed = overhang(part, rot, name, sup)
        ok(pieces == 1, f"{name:<16} is {pieces} solid piece(s)")
        if not sup:
            ok(area < 25 and bed > 40, f"{name:<16} prints without supports")

    print()
    if FAIL:
        print(f"AUDIT FAILED: {len(FAIL)} problem(s)")
        for f in FAIL:
            print("  -", f)
        sys.exit(1)
    print("AUDIT PASSED: every check above is OK")


if __name__ == "__main__":
    main()
