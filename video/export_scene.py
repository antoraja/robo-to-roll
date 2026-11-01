"""Export everything the build-guide video needs: every printed part, where it sits on its
print plate, and where it goes in the finished hand.  ->  video/scene.json"""
from __future__ import annotations

import base64
import json
import math
import os
import sys

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cad"))
import generate_parts as gp  # noqa: E402
import hand  # noqa: E402
import export_assembly as ea  # noqa: E402

TF = trimesh.transformations


def enc(mesh):
    v = np.asarray(mesh.vertices, np.float32)
    f = np.asarray(mesh.faces, np.uint32)
    return {"v": base64.b64encode(v.tobytes()).decode(), "i": base64.b64encode(f.tobytes()).decode()}


def T(v):
    return TF.translation_matrix(v)


def rot(rx, ry, rz):
    """Same order as manifold3d .rotate((x, y, z)): X first, then Y, then Z."""
    return (TF.rotation_matrix(math.radians(rz), (0, 0, 1)) @ TF.rotation_matrix(math.radians(ry), (0, 1, 0))
            @ TF.rotation_matrix(math.radians(rx), (1, 0, 0)))


def print_matrix(mesh, R):
    """matrix that turns `mesh` into its print orientation (rotated, min corner at origin)."""
    m = mesh.copy(); m.apply_transform(R)
    return T(-m.bounds[0]) @ R


def main():
    P, SP, ST = hand.palm(), hand.spine(), hand.stand()
    bones = {n: hand.finger_bones(n) for n in hand.ORDER}
    out = {"parts": {}, "fingers": {}, "servos": {}, "plates": []}

    # --- plates: same packing as export_assembly.py
    def bone_items(n):
        names = ["proximal", "middle", "distal"] if len(hand.finger_L(n)) == 3 else ["proximal", "distal"]
        items = []
        for b, nm in zip(bones[n], names):
            local = ea.tm(b.translate((0, 0, -gp.ZP)))          # chain-local geometry (pivot at origin)
            M = print_matrix(local, rot(180, 0, 0) @ T((0, 0, gp.ZP)))
            pm = local.copy(); pm.apply_transform(M)
            items.append((f"{n}_{nm}", pm, local, M))
        return items

    spool_local = ea.tm(gp.spool())
    plate_defs = []
    fit = bone_items("index") + [(f"spool_{i}", spool_local.copy(), spool_local, np.eye(4)) for i in range(5)]
    plate_defs.append(("Plate 1 · fit test: index finger + 5 spools", fit))
    other = sum((bone_items(n) for n in ("thumb", "middle", "ring", "little")), [])
    plate_defs.append(("Plate 2 · thumb, middle, ring, little", other))
    palm_m = ea.tm(P)
    plate_defs.append(("Plate 3 · palm", [("palm", palm_m.copy(), palm_m, print_matrix(palm_m, np.eye(4)))]))
    sp_m = ea.tm(SP)
    M = print_matrix(sp_m, rot(0, 90, 0))
    tmp = sp_m.copy(); tmp.apply_transform(M)
    Rz = TF.rotation_matrix(math.radians(45), (0, 0, 1)) if tmp.extents[0] > ea.BED - 2 * ea.GAP else np.eye(4)
    tmp.apply_transform(Rz)
    shift = -tmp.bounds[0] + np.array([(ea.BED - tmp.extents[0]) / 2, (ea.BED - tmp.extents[1]) / 2, 0])
    plate_defs.append(("Plate 4 · servo spine", [("spine", None, sp_m, T(shift) @ Rz @ M)]))
    st_m = ea.tm(ST)
    plate_defs.append(("Plate 5 · stand", [("stand", st_m.copy(), st_m, print_matrix(st_m, np.eye(4)))]))

    for k, (title, items) in enumerate(plate_defs):
        placed = {}
        pack_in = [(n, pm) for (n, pm, _, _) in items if pm is not None]
        if len(pack_in) > 1:
            for pl in ea.pack(pack_in):
                for n, pm in pl:
                    placed[n] = T(pm.bounds[0] * np.array([1, 1, 0]))   # packed offset (pm started at origin)
        plate = {"title": title, "parts": []}
        for (n, pm, geom, M) in items:
            off = placed.get(n, np.eye(4))
            plate["parts"].append(n)
            out["parts"].setdefault(n, {})["plate"] = {"k": k, "M": (off @ M).T.flatten().tolist()}
        out["plates"].append(plate)

    # --- geometry
    out["geom"] = {"palm": enc(palm_m), "spine": enc(sp_m), "stand": enc(st_m), "spool": enc(spool_local)}
    for n in hand.ORDER:
        names = ["proximal", "middle", "distal"] if len(hand.finger_L(n)) == 3 else ["proximal", "distal"]
        out["geom"].update({f"{n}_{nm}": enc(ea.tm(b.translate((0, 0, -gp.ZP)))) for b, nm in zip(bones[n], names)})
        out["fingers"][n] = dict(L=hand.finger_L(n), pin=hand.finger_pin(n).tolist(),
                                 B=hand.finger_basis(n).T.flatten().tolist(), bones=[f"{n}_{nm}" for nm in names])
        body, sp, _, _ = hand.servo_geom(n)
        s = hand.SERVOS[n]
        side = s["side"]
        Msp = T((hand.spool_x(side), s["y"], s["z"])) @ rot(0, 90 * side, 0)
        t, w, _ = hand.string_path(n)
        out["geom"][f"servo_{n}"] = enc(ea.tm(body))
        bb = ea.tm(body).bounds
        out["servos"][n] = dict(side=side, y=s["y"], z=s["z"], spoolM=Msp.T.flatten().tolist(),
                                centre=[hand.spool_core_x(side), s["y"], s["z"]], path=[t.tolist(), w.tolist()],
                                bottom=[float((bb[0][0] + bb[1][0]) / 2), s["y"], float(bb[0][2])])
    out["params"] = dict(ZP=gp.ZP, C=gp.C, FLEX_Z=gp.FLEX_Z, EXT_Z=gp.EXT_Z, colLen=hand.PALM_DROP + 2,
                         PLATE_Z=hand.PLATE_Z, PLATE_T=hand.PLATE_T, spoolR=gp.SPOOL_R, BED=ea.BED,
                         WRIST_Z=hand.WRIST_Z, SPINE_BOT=hand.SPINE_BOT)
    with open(os.path.join(HERE, "scene.json"), "w") as fh:
        json.dump(out, fh)
    print("scene.json", os.path.getsize(os.path.join(HERE, "scene.json")) // 1024, "KB;",
          len(out["parts"]), "parts on", len(out["plates"]), "plates")


if __name__ == "__main__":
    main()
