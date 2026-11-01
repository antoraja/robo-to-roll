"""Five-finger hand CONCEPT built from the tested finger design.

* Same bones / pins / channels as the one-finger rig (only bone LENGTHS differ per finger).
* Rounded palm with a knuckle fork for every finger; the thumb sits on an angled boss.
* Forearm holds 5 MG90S servos + spools; strings run through the palm and wrist.

This is a layout concept for visualising and planning - the palm/forearm are not yet split
into printable pieces. Run:  python hand_concept.py  (prints a collision + material check,
and with --export writes a JSON of meshes for the 3-D viewer).
"""
from __future__ import annotations

import base64
import json
import math
import os
import sys

import numpy as np
import manifold3d as m

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_parts as gp  # noqa: E402
from generate_parts import (C, H, W, ZP, box, joint_distal_end, slab, body_profile,  # noqa: E402
                            channels, skin, phalanx, TAPER)

gp.SEG = 40
gp.SKIN_SEG = 40

# finger:      bone lengths (mm)         knuckle pin (world x, y, z)   splay (deg about X)
FINGERS = {
    "index":  dict(L=[45, 30, 25], pin=(0.0, 28.0, 0.0), splay=4.0),
    "middle": dict(L=[49, 33, 26], pin=(0.0, 9.5, 4.0), splay=0.0),
    "ring":   dict(L=[46, 31, 25], pin=(0.0, -9.5, 1.0), splay=-3.0),
    "little": dict(L=[37, 25, 22], pin=(0.0, -28.0, -8.0), splay=-8.0),
}
# Thumb: 2 bones, on the index side, pointing up-and-out, curling across the palm
THUMB = dict(L=[40, 30], pin=(16.0, 44.0, -40.0), direction=(0.35, 0.45, 0.82), curl=(0.75, -0.62, 0.0))

PALM_DROP = 13.0      # palm top sits this far below each knuckle pin (finger clears it when curled)
WRIST_Z = -100.0
FOREARM = dict(z0=-112.0, z1=-310.0, x=(-30.0, 26.0), y=(-38.0, 38.0))
SERVO_Z = [-145.0, -179.0, -213.0, -247.0, -281.0]   # 5 servos stacked along the forearm
SERVO_Y = [12.0, -12.0, 12.0, -12.0, 12.0]


def basis(direction, curl):
    """Rotation whose world-Z axis = finger direction and world-X axis = curl (palm) direction."""
    d = np.array(direction, float); d /= np.linalg.norm(d)
    c = np.array(curl, float); c -= d * (c @ d); c /= np.linalg.norm(c)
    y = np.cross(d, c)
    return np.column_stack([c, y, d])            # columns: images of world x, y, z


def finger_basis(splay):
    a = math.radians(splay)
    d = (0.0, math.sin(a), math.cos(a))           # tilt toward +y for positive splay
    return basis(d, (1.0, 0.0, 0.0))


def place(part_local, R, pin):
    """finger-local part (pivot at origin, after -ZP shift) -> world."""
    p = part_local.rotate((0.0, -90.0, 0.0))     # local x -> world z, local -z -> world x
    M = np.eye(4); M[:3, :3] = R; M[:3, 3] = pin
    return p.transform(M[:3, :].tolist())


def knuckle_local():
    """Fork + short column that the finger's first bone pins into (finger-local coords)."""
    col_len = PALM_DROP + 2
    col = slab(body_profile(-C - col_len, -C, chamfer_start=False), -W / 2, W / 2)
    col += joint_distal_end(0.0)
    col -= channels(-C - col_len - 5, 1.0)
    col ^= skin(-C - col_len - 8, 0.0, 1.03, TAPER[0]) + box(-C - col_len - 1, -C - col_len + 3, -W, W, -H, H)
    return col.translate((0, 0, -ZP))


def palm():
    pts = []
    for f in FINGERS.values():
        R = finger_basis(f["splay"])
        top = np.array(f["pin"]) + R @ np.array([0, 0, -PALM_DROP - 4])
        pts.append(top)
    blobs = []
    for p in pts:
        blobs.append(m.Manifold.sphere(1, 32).scale((11, 10, 6)).translate(tuple(p + np.array([1.5, 0, 0]))))
    # lower palm, thumb pad (thenar) and wrist
    blobs.append(m.Manifold.sphere(1, 32).scale((13, 34, 14)).translate((2.0, 0.0, -55.0)))
    blobs.append(m.Manifold.sphere(1, 32).scale((12, 11, 16)).translate((4.0, 30.0, -64.0)))
    blobs.append(m.Manifold.sphere(1, 32).scale((12, 26, 6)).translate((0.0, 0.0, WRIST_Z + 4)))
    p = m.Manifold.batch_hull(blobs)
    for f in FINGERS.values():
        p += place(knuckle_local(), finger_basis(f["splay"]), f["pin"])
    Rt = basis(THUMB["direction"], THUMB["curl"])
    p += place(knuckle_local(), Rt, THUMB["pin"])
    # thumb boss: fill between the thumb knuckle column and the palm
    foot = np.array(THUMB["pin"]) + Rt @ np.array([0, 0, -PALM_DROP - 2])
    p += m.Manifold.batch_hull([m.Manifold.sphere(1, 24).scale((8, 8, 8)).translate(tuple(foot)),
                                m.Manifold.sphere(1, 24).scale((9, 9, 9)).translate((4.0, 30.0, -60.0))])
    return p


def forearm():
    f = FOREARM
    cx, cy = (f["x"][0] + f["x"][1]) / 2, 0.0
    ax, ay = (f["x"][1] - f["x"][0]) / 2, (f["y"][1] - f["y"][0]) / 2
    outer = m.Manifold.batch_hull([
        m.Manifold.sphere(1, 40).scale((ax * 0.92, ay * 0.85, 8)).translate((cx, cy, f["z0"])),
        m.Manifold.sphere(1, 40).scale((ax, ay, 10)).translate((cx, cy, f["z1"] + 10)),
    ])
    inner = m.Manifold.batch_hull([
        m.Manifold.sphere(1, 40).scale((ax * 0.92 - 2.5, ay * 0.85 - 2.5, 6)).translate((cx, cy, f["z0"])),
        m.Manifold.sphere(1, 40).scale((ax - 2.5, ay - 2.5, 8)).translate((cx, cy, f["z1"] + 10)),
    ])
    shell = outer - inner
    shell -= box(-10, 10, -14, 14, f["z0"] - 10, f["z0"] + 6)   # wrist opening for the strings
    return shell


def servo_and_spool(i):
    """MG90S lying with its shaft pointing to +x (palm side), spool on the shaft."""
    z, y = SERVO_Z[i], SERVO_Y[i]
    body = box(-20.0, -4.0, y - 6.1, y + 6.1, z - 11.4, z + 11.4) + box(-9.5, -7.0, y - 6.1, y + 6.1, z - 16.15, z + 16.15)
    spool = gp.spool().translate((0, 0, -4)).rotate((0.0, 90.0, 0.0)).translate((4.0, y, z + 5.5))
    return body, spool, (4.0 + 4.0, y, z + 5.5)    # spool centre


def esp32():
    return box(-22.0, -20.0, -26.0, 26.0, -150.0, -122.0)  # flat board on the back wall (placeholder)


def finger_meshes():
    out = {}
    for name, f in list(FINGERS.items()) + [("thumb", THUMB)]:
        L = f["L"]
        if len(L) == 3:
            bones = [phalanx(L[0]), phalanx(L[1], which="mid"), phalanx(L[2], distal=True)]
        else:
            bones = [phalanx(L[0]), phalanx(L[1], distal=True)]
        out[name] = [b.translate((0, 0, -ZP)) for b in bones]
    return out


def posed_finger(bones, L, curl_deg, R, pin):
    T = np.eye(4); parts = []
    for b, length in zip(bones, L):
        a = math.radians(curl_deg)
        Ry = np.array([[math.cos(a), 0, math.sin(a), 0], [0, 1, 0, 0], [-math.sin(a), 0, math.cos(a), 0], [0, 0, 0, 1]])
        T = T @ Ry
        parts.append(place(b.transform(T[:3, :].tolist()), R, pin))
        S = np.eye(4); S[0, 3] = length; T = T @ S
    return parts


def check():
    pal = palm()
    fm = finger_meshes()
    print("Collision check (finger bones vs palm, and neighbouring fingers):")
    for curl in (0, 45, 85):
        worst_palm, worst_pair = 0.0, 0.0
        posed = {}
        for name, f in FINGERS.items():
            posed[name] = posed_finger(fm[name], f["L"], curl, finger_basis(f["splay"]), f["pin"])
            for i, b in enumerate(posed[name]):
                if i == 0:
                    continue               # first bone touches its own fork by design (pin joint)
                worst_palm = max(worst_palm, (b ^ pal).volume())
            worst_palm = max(worst_palm, (posed[name][0] ^ (pal - place(knuckle_local(), finger_basis(f["splay"]), f["pin"]))).volume())
        names = list(FINGERS)
        for a_, b_ in zip(names, names[1:]):
            for pa in posed[a_]:
                for pb in posed[b_]:
                    worst_pair = max(worst_pair, (pa ^ pb).volume())
        print(f"   all fingers at {curl:2d} deg/joint: finger-palm overlap {worst_palm:6.1f} mm3, finger-finger {worst_pair:6.1f} mm3")
    th = posed_finger(fm["thumb"], THUMB["L"], 0, basis(THUMB["direction"], THUMB["curl"]), THUMB["pin"])
    idx = posed_finger(fm["index"], FINGERS["index"]["L"], 0, finger_basis(FINGERS["index"]["splay"]), FINGERS["index"]["pin"])
    print(f"   thumb (open) vs index (open): {sum((a ^ b).volume() for a in th for b in idx):.1f} mm3")
    vol = pal.volume() + forearm().volume() + sum(b.volume() for v in fm.values() for b in v) + 5 * gp.spool().volume()
    grams = vol / 1000 * 1.24 * 0.45     # ~30 % infill + walls
    print(f"Printed volume ~{vol / 1000:.0f} cm3 -> roughly {grams:.0f} g of PLA (about ${grams / 1000 * 20:.0f} at $20/kg)")


def export(path):
    def enc(p):
        mm = p.to_mesh()
        v = np.asarray(mm.vert_properties)[:, :3].astype(np.float32)
        f = np.asarray(mm.tri_verts).astype(np.uint32)
        return {"v": base64.b64encode(v.tobytes()).decode(), "i": base64.b64encode(f.tobytes()).decode()}
    fm = finger_meshes()
    data = {"palm": enc(palm()), "forearm": enc(forearm()), "esp32": enc(esp32()), "fingers": {}, "servos": []}
    for name, f in list(FINGERS.items()) + [("thumb", THUMB)]:
        R = finger_basis(f["splay"]) if name != "thumb" else basis(THUMB["direction"], THUMB["curl"])
        data["fingers"][name] = dict(L=f["L"], pin=list(f["pin"]), R=R.T.flatten().tolist(),
                                     bones=[enc(b) for b in fm[name]])
    order = ["thumb", "index", "middle", "ring", "little"]
    for i in range(5):
        body, spool, centre = servo_and_spool(i)
        data["servos"].append(dict(finger=order[i], body=enc(body), spool=enc(spool), centre=list(centre)))
    data["params"] = dict(FLEX_Z=gp.FLEX_Z, ZP=ZP, C=C, spoolR=gp.SPOOL_R, wristZ=WRIST_Z)
    with open(path, "w") as fh:
        json.dump(data, fh)
    print("exported", path, os.path.getsize(path) // 1024, "KB")


if __name__ == "__main__":
    check()
    if "--export" in sys.argv:
        export(sys.argv[sys.argv.index("--export") + 1])
