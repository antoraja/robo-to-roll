"""Camera in the palm: an ESP32-CAM in a small cover that slides onto a rail on the inside of the palm.

  rail   is part of the palm (hand.cam_rail): low down, centred, where curled fingers never reach
  cover  printed separately (plate 7, standing upright, no supports): slides DOWN onto the rail until its closed top rests on the
         rail's top; one 1.75 mm filament pin under the rail's bottom end stops it lifting off.
         The ESP32-CAM stands upright (antenna end up), lens looking out of the palm.
         Board held from behind by 2 mm rubber cord (no glue, no screws).
         The two power jumpers (5 V, GND) sit beside the rail and leave through the bottom.

Run:  python palm_camera.py      (checks + stl/camera/palm_camera_cover.stl + plates/plate_7_palm_camera.3mf)
"""
from __future__ import annotations

import os
import sys

import manifold3d as m
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_parts as gp  # noqa: E402
import hand as H  # noqa: E402
from hand import box  # noqa: E402

SEG = 48
CL = 0.25                                   # dovetail clearance per side
RZ0, RZ1 = H.CAM_RAIL_Z
RX0, RX1 = H.CAM_RAIL_X
Z_TOP, Z_BOT = RZ1 + 2.0, -116.0            # cover top = 2 mm above the rail top (closed slot end)
BACK = RX0 + 0.2                            # cover's back face (just clear of the rail pedestal)
BLOCK_X, BLOCK_HW = 36.0, 10.7              # back block that carries the slot
OUT_HW = 16.0                               # cover half-width (y)
WALL, FRONT = 2.0, 2.4
BOARD_W, BOARD_L = 27.6, 41.0               # ESP32-CAM 27 x 40.5 mm + clearance
PCB_BACK = 46.5                             # x of the board's back face (pins + 2 jumper plugs fit behind it)
PCB_T = 1.6
CAM_FACE = 9.0                              # board front -> inside of the front wall (camera + lens)
X_FRONT = PCB_BACK + PCB_T + CAM_FACE + FRONT
Z_MID = (Z_TOP + Z_BOT) / 2
LENS_UP, LENS_WIN = 4.0, (14.0, 24.0)       # lens window, centred 4 mm above the board centre
LOCK_Z = RZ0 - 1.5                          # lock pin just under the rail's bottom end
CORD_HOLE = 2.6


def rod_y(d, x, z, y0, y1):
    return m.Manifold.cylinder(y1 - y0, d / 2, d / 2, SEG).rotate((-90.0, 0.0, 0.0)).translate((x, y0, z))


def rail_hw(x):
    return H.CAM_RAIL_HW[0] + (x - RX0) * (H.CAM_RAIL_HW[1] - H.CAM_RAIL_HW[0]) / (RX1 - RX0)


def slot():
    xa, xb = BACK - 0.5, RX1 + CL
    return m.Manifold.batch_hull([box(xa, xa + 0.01, -rail_hw(xa) - CL, rail_hw(xa) + CL, Z_BOT - 1, RZ1),
                                  box(xb - 0.01, xb, -rail_hw(RX1) - CL, rail_hw(RX1) + CL, Z_BOT - 1, RZ1)])


def cover():
    pts = [m.Manifold.cylinder(X_FRONT - BACK, 5.0, 5.0, SEG).rotate((0.0, 90.0, 0.0)).translate((BACK, yy, zz))
           for yy in (-OUT_HW + 5, OUT_HW - 5) for zz in (Z_BOT + 5, Z_TOP - 5)]
    c = m.Manifold.batch_hull(pts)
    # hollow: everything in front of the back block, plus the two side pockets beside it (jumper plugs)
    inner = box(BLOCK_X, X_FRONT - FRONT, -OUT_HW + WALL, OUT_HW - WALL, Z_BOT + WALL, Z_TOP - WALL)
    inner += box(BACK - 1, BLOCK_X + 0.01, -OUT_HW + WALL, -BLOCK_HW, Z_BOT + WALL, Z_TOP - WALL)
    inner += box(BACK - 1, BLOCK_X + 0.01, BLOCK_HW, OUT_HW - WALL, Z_BOT + WALL, Z_TOP - WALL)
    c -= inner
    c -= slot()
    # board stops at the four corners (board pressed onto them by the cords)
    for sy in (-1, 1):
        for sz in (-1, 1):
            cy, cz = sy * BOARD_W / 2, Z_MID + sz * BOARD_L / 2
            post = box(PCB_BACK + PCB_T, X_FRONT - FRONT + 0.01, cy - 2.5, cy + 2.5, cz - 2.5, cz + 2.5)
            if sz > 0:                       # 45 deg gusset under the upper stops: prints standing, no support
                reach = X_FRONT - FRONT - (PCB_BACK + PCB_T)
                post = m.Manifold.batch_hull([post, box(X_FRONT - FRONT - 0.01, X_FRONT - FRONT + 0.01,
                                                        cy - 2.5, cy + 2.5, cz - 2.5 - reach, cz + 2.5)])
            notch = box(PCB_BACK - 1.5, PCB_BACK + PCB_T + 0.01,
                        min(cy, cy - sy * 5), max(cy, cy - sy * 5), min(cz, cz - sz * 5), max(cz, cz - sz * 5))
            side = box(PCB_BACK - 1, PCB_BACK + PCB_T + 0.01, cy - 2.5, cy + 2.5, cz - 2.5, cz + 2.5) - notch
            c += post + side
    # lens window, chamfered outward
    lw, lh = LENS_WIN
    zc = Z_MID + LENS_UP

    def stadium(x0, x1, w, h):
        r = w / 2
        return m.Manifold.batch_hull([m.Manifold.cylinder(x1 - x0, r, r, SEG).rotate((0.0, 90.0, 0.0))
                                      .translate((x0, 0, zc + dz)) for dz in (-(h / 2 - r), h / 2 - r)])
    c -= m.Manifold.batch_hull([stadium(X_FRONT - FRONT - 0.5, X_FRONT - FRONT + 0.01, lw, lh),
                                stadium(X_FRONT - 0.01, X_FRONT + 0.5, lw + 3, lh + 3)])
    # rubber cords across the back of the board: near the top end, above the pin rows, and at the bottom edge
    for z in (Z_MID + BOARD_L / 2 - 4, Z_MID - BOARD_L / 2 + 23, Z_MID - BOARD_L / 2 + 1.2):
        c -= rod_y(CORD_HOLE, PCB_BACK - CORD_HOLE / 2 - 0.3, z, -OUT_HW - 1, OUT_HW + 1)
    # wire exits in the bottom, beside the back block
    for sy in (-1, 1):
        y0, y1 = sorted((sy * (BLOCK_HW + 0.3), sy * (OUT_HW - WALL - 0.3)))
        c -= box(BACK + 1, PCB_BACK, y0, y1, Z_BOT - 1, Z_BOT + WALL + 0.01)
    # lock pin under the rail
    c -= rod_y(H.PIN_D, (RX0 + RX1) / 2, LOCK_Z, -BLOCK_HW - 1, BLOCK_HW + 1)
    return c


def checks():
    print("Palm camera: checks")
    P, C = H.palm(), cover()
    bad = []

    def ok(cond, msg):
        print(("   OK    " if cond else "   FAIL  ") + msg)
        if not cond:
            bad.append(msg)
    ok((C ^ P).volume() < 0.05, f"cover slides on the rail without touching the palm: {(C ^ P).volume():.2f} mm3")
    rail = H.cam_rail() ^ box(RX0 - 0.01, RX1 + 0.01, -20, 20, RZ0, RZ1)
    ok((C ^ rail).volume() < 0.05, f"dovetail clearance: {(C ^ rail).volume():.2f} mm3 touching")
    ok((C.translate((0, 0, -0.5)) ^ rail).volume() > 0.5, "closed top of the slot rests on the rail top (cannot slide further down)")
    pin = rod_y(1.7, (RX0 + RX1) / 2, LOCK_Z, -BLOCK_HW - 0.5, BLOCK_HW + 0.5)
    ok((pin ^ C).volume() < 0.05 and (pin ^ P).volume() < 0.05,
       f"lock pin ({2 * BLOCK_HW + 1:.0f} mm) passes the cover under the rail end: {(pin ^ C).volume() + (pin ^ P).volume():.2f} mm3")
    up = pin.translate((0, 0, 1.5))
    ok((up ^ P).volume() > 0.3, "the lock pin stops the cover lifting off (it hits the rail end)")
    stuff = [H.spine(), H.stand()]
    for n in H.ORDER:
        body, sp, _, _ = H.servo_geom(n)
        t, w, _ = H.string_path(n)
        stuff += [body, sp, H.rod(t, w, 0.8)]
    v = sum((C ^ s).volume() for s in stuff)
    ok(v < 0.05, f"cover vs spine, stand, servos, spools, strings: {v:.2f} mm3")
    worst = 0.0
    for a in range(0, 91, 5):
        for n in H.ORDER:
            for b in H.posed(n, a):
                worst = max(worst, (C ^ b).volume())
    ok(worst < 0.05, f"fingers and thumb at every angle 0-90 deg never touch the cover ({worst:.2f} mm3)")
    board = box(PCB_BACK, PCB_BACK + PCB_T, -13.5, 13.5, Z_MID - 20.25, Z_MID + 20.25)
    ok((C ^ board).volume() < 0.05, "ESP32-CAM board (27 x 40.5) sits on its corner stops")
    plugs = box(PCB_BACK - 16.5, PCB_BACK - 2.5, 10.9, 13.5, Z_MID - 20, Z_MID - 2)
    ok((C ^ plugs).volume() < 0.05 and (C ^ plugs.mirror((0, 1, 0))).volume() < 0.05,
       "jumper plugs on the pin rows have room behind the board (16.5 mm)")
    print(f"   cover {X_FRONT - BACK:.0f} mm deep x {2 * OUT_HW:.0f} wide x {Z_TOP - Z_BOT:.0f} tall, "
          f"sticks out {X_FRONT - 29.0:.0f} mm from the palm; lens {Z_MID + LENS_UP - H.PLATE_Z:.0f} mm above the stand plate")
    print(f"   one solid piece: {len(C.decompose()) == 1}")
    assert not bad, bad
    return P, C


def main():
    _, C = checks()
    from export_assembly import print_oriented, save_plate
    out = os.path.join(HERE, "stl", "camera"); os.makedirs(out, exist_ok=True)
    mesh = print_oriented(C, (0, 0, 0))             # stands on its bottom, exactly as it sits on the palm
    mesh.export(os.path.join(out, "palm_camera_cover.stl"))
    print(f"   palm_camera_cover.stl {mesh.extents[0]:.0f} x {mesh.extents[1]:.0f} x {mesh.extents[2]:.0f} mm")
    save_plate(7, "palm_camera", [("palm_camera_cover", mesh.apply_translation((100, 100, 0)))], os.path.join(HERE, "plates"))


if __name__ == "__main__":
    main()
