"""Export the whole arm as 3-D files.

  assembly/robohand_assembly.glb   assembled hand on its stand, coloured, one node per part
                                   (opens in Windows 3D Viewer, Blender, online GLB viewers)
  assembly/robohand_assembly.stl   same, single mesh (for slicers / quick viewing)
  plates/plate_N_*.3mf + .stl      print plates for a 220 x 220 mm bed, parts already laid
                                   out and oriented (open the 3MF in PrusaSlicer / Bambu /
                                   Orca / Cura)

Run:  python export_assembly.py
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_parts as gp  # noqa: E402
import hand  # noqa: E402

BED = 256.0          # Bambu Lab P1S build plate (256 x 256 mm)
GAP = 6.0
COLORS = {
    "finger": (232, 116, 42), "palm": (225, 228, 232), "spine": (120, 140, 156), "stand": (70, 84, 96),
    "spool": (42, 157, 143), "servo": (40, 48, 56),
}


def tm(part):
    mesh = part.to_mesh()
    return trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts), process=False)


def print_oriented(part, rot):
    p = part.rotate(rot)
    lo = np.array(p.bounding_box()[:3])
    return tm(p.translate(tuple(-lo)))


def assembly(P, SP, ST, bones, curl=12):
    scene = trimesh.Scene()

    def add(name, mesh, color):
        mat = trimesh.visual.material.PBRMaterial(name=name, baseColorFactor=[c / 255 for c in color] + [1.0],
                                                  metallicFactor=0.0, roughnessFactor=0.7)
        mesh.visual = trimesh.visual.TextureVisuals(material=mat)
        scene.add_geometry(mesh, node_name=name, geom_name=name)

    add("stand", tm(ST), COLORS["stand"])
    add("spine", tm(SP), COLORS["spine"])
    add("palm", tm(P), COLORS["palm"])
    import palm_camera
    add("palm_camera_cover", tm(palm_camera.cover()), (194, 90, 23))
    for n in hand.ORDER:
        body, sp, _, _ = hand.servo_geom(n)
        add(f"servo_{n}", tm(body), COLORS["servo"])
        add(f"spool_{n}", tm(sp), COLORS["spool"])
        names = ["proximal", "middle", "distal"] if len(hand.finger_L(n)) == 3 else ["proximal", "distal"]
        for b, nm in zip(hand.posed(n, curl if n != "thumb" else 8, bones[n]), names):
            add(f"{n}_{nm}", tm(b), COLORS["finger"])
    return scene


def pack(items, bed=BED, gap=GAP):
    """Simple shelf packing. items: list of (name, trimesh). Returns list of plates."""
    plates, cur, x, y, shelf = [], [], gap, gap, 0.0
    for name, m in sorted(items, key=lambda it: -it[1].extents[1]):
        ex, ey = m.extents[0], m.extents[1]
        if ex > ey and ex > bed - 2 * gap:
            pass
        if x + ex > bed - gap:
            x, y, shelf = gap, y + shelf + gap, 0.0
        if y + ey > bed - gap:
            plates.append(cur); cur, x, y, shelf = [], gap, gap, 0.0
        cur.append((name, m.copy().apply_translation((x, y, 0))))
        x += ex + gap
        shelf = max(shelf, ey)
    if cur:
        plates.append(cur)
    return plates


def save_plate(idx, title, items, outdir):
    scene = trimesh.Scene()
    for name, m in items:
        scene.add_geometry(m, node_name=name, geom_name=name)
    base = os.path.join(outdir, f"plate_{idx}_{title}")
    scene.export(base + ".3mf")
    trimesh.util.concatenate([m for _, m in items]).export(base + ".stl")
    lo, hi = scene.bounds
    print(f"   plate {idx} {title:<14} {len(items):2d} parts, footprint {hi[0] - lo[0]:5.0f} x {hi[1] - lo[1]:5.0f} mm, "
          f"height {hi[2]:4.0f} mm")
    return dict(file=os.path.basename(base) + ".3mf", parts=[n for n, _ in items])


def main():
    P, SP, ST = hand.palm(), hand.spine(), hand.stand()
    bones = {n: hand.finger_bones(n) for n in hand.ORDER}
    out_a = os.path.join(HERE, "assembly"); os.makedirs(out_a, exist_ok=True)
    out_p = os.path.join(HERE, "plates"); os.makedirs(out_p, exist_ok=True)

    scene = assembly(P, SP, ST, bones)
    scene.export(os.path.join(out_a, "robohand_assembly.glb"))
    trimesh.util.concatenate(list(scene.dump())).export(os.path.join(out_a, "robohand_assembly.stl"))
    ext = scene.extents
    print(f"Assembly: {len(scene.geometry)} parts, {ext[0]:.0f} x {ext[1]:.0f} x {ext[2]:.0f} mm -> assembly/")

    def bone_items(n):
        names = ["proximal", "middle", "distal"] if len(hand.finger_L(n)) == 3 else ["proximal", "distal"]
        return [(f"{n}_{nm}", print_oriented(b, (180, 0, 0))) for b, nm in zip(bones[n], names)]

    spool = print_oriented(gp.spool_v3(), (180, 0, 0))          # horn-free spool, outer flange on the bed
    plates = []
    plates.append(("fit_test", bone_items("index") + [(f"spool_{i + 1}", spool.copy()) for i in range(5)]))
    other = sum((bone_items(n) for n in ("thumb", "middle", "ring", "little")), [])
    for i, pl in enumerate(pack(other)):
        plates.append((f"fingers{'' if i == 0 else i + 1}", pl))
    plates.append(("palm", [("palm", print_oriented(P, (0, 0, 0)))]))
    # spine: lie flat and turn 45 deg so 224 mm fits a 220 mm bed diagonally
    sp = print_oriented(SP, (0, 90, 0))                     # flat front face on the bed
    if sp.extents[0] > BED - 2 * GAP:                       # only small beds need the diagonal
        sp.apply_transform(trimesh.transformations.rotation_matrix(math.radians(45), (0, 0, 1)))
    sp.apply_translation(-sp.bounds[0] + np.array([(BED - sp.extents[0]) / 2, (BED - sp.extents[1]) / 2, 0.0]))
    plates.append(("spine", [("spine", sp)]))
    plates.append(("stand", [("stand", print_oriented(ST, (0, 0, 0)))]))
    # plate 6: the five fingertips (with the cap socket) and their string caps (+2 spares)
    tips = []
    for n in hand.ORDER:
        Ld = hand.finger_L(n)[-1]
        tips.append((f"{n}_distal", print_oriented(bones[n][-1], (180, 0, 0))))
        tips.append((f"{n}_tip_cap", print_oriented(gp.tip_cap(Ld), (0, -90, 0))))
    for k in range(2):
        tips.append((f"spare_tip_cap_{k + 1}", print_oriented(gp.tip_cap(25), (0, -90, 0))))
    plates.append(("tips_and_caps", [it for pl in pack(tips) for it in pl]))

    # horn-free spools: fit test first (plate 8), then the 5 spools (plate 9)
    plates.append(("spline_fit_test", [("spline_fit_test_1to4_dots", print_oriented(gp.spline_fit_test(), (0, 0, 0)))]))
    plates.append(("spools", [it for pl in pack([(f"spool_{i + 1}", print_oriented(gp.spool_v3(), (180, 0, 0))) for i in range(5)]) for it in pl]))
    print(f"Print plates ({BED:.0f} x {BED:.0f} mm bed) -> plates/")
    manifest = []
    for i, (title, items) in enumerate(plates, 1):
        if title == "fit_test":
            items = [it for pl in pack(items) for it in pl]
        num = {"spline_fit_test": 8, "spools": 9}.get(title, i)   # 7 = palm camera (palm_camera.py)
        manifest.append(dict(plate=num, title=title, **save_plate(num, title, items, out_p)))
    with open(os.path.join(out_p, "plates.json"), "w") as fh:
        json.dump(manifest, fh, indent=1)


if __name__ == "__main__":
    main()
