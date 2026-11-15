"""Does the wide ESP32 fit the 400-hole breadboard with free holes for the wires?

Plan: only the ESP32's VIN-side pin row goes into the breadboard, in row j; the other pin row hangs in the
air past the breadboard's edge. Rows f, g, h of each pin's column are then free for wires.

Sizes:
  breadboard   measured from the user's photo: 2.54 mm pitch, rows a-e / f-j with a 3-pitch groove,
               power rails 2.7 and 3.7 pitches outside row a/j, edge ~5.2 pitches outside row j, 8.5 mm tall
  ESP32        30-pin USB-C CH340C board, 51.5 x 28.3 mm. Its pin-row spacing is NOT measured, so the test is
               run for all three spacings these boards come in: 0.9, 1.0 and 1.1 inch
  jumper       male Dupont housing 2.6 x 2.6 mm (+0.3 allowance), from the breadboard surface up 14 mm
Pin order (from the user's photo, USB end = pin 1): VIN GND D13 D12 D14 D27 D26 D25 ...

Run:  python wiring_fit.py
"""
from __future__ import annotations

import os
import sys

import manifold3d as m

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hand as H  # noqa: E402
from hand import box  # noqa: E402

P = 2.54
ROW = {r: (4 - i) * P + 1.5 * P for i, r in enumerate("abcde")}           # a = +13.97 ... e = +3.81
ROW.update({r: -(i * P + 1.5 * P) for i, r in enumerate("fghij")})       # f = -3.81 ... j = -13.97
BB_HW, BB_HL, BB_H = 27.25, 41.25, 8.5                                    # half width (across rows), half length, height
col_y = lambda c: (c - 15.5) * P                                          # column 1 .. 30 along the length
PINS = ["VIN", "GND", "D13", "D12", "D14", "D27", "D26", "D25", "D33", "D32", "D35", "D34", "VN", "VP", "EN"]
USED = {"GND": "- rail jumper", "D13": "index", "D14": "middle", "D27": "ring", "D26": "little", "D25": "thumb"}
PCB_W, PCB_L, PCB_T, SPACER, PIN_BELOW, TOP_PARTS = 28.3, 51.5, 1.6, 2.5, 6.0, 3.5
JUMP = 2.6 + 0.3


def esp(spacing, u_vin, x0, z_top, flip=1):
    """ESP32 as solids in breadboard coordinates (u across the rows, y along the columns, z up).
    u_vin: where the VIN-side pin row sits; the other row is at u_vin - flip * spacing."""
    u_out = u_vin - flip * spacing
    lo, hi = sorted((u_vin + flip * (PCB_W - spacing) / 2, u_out - flip * (PCB_W - spacing) / 2))
    y0 = col_y(1) - (PCB_L - 14 * P) / 2
    pcb = box(lo, hi, y0, y0 + PCB_L, z_top + SPACER, z_top + SPACER + PCB_T + TOP_PARTS)
    rows = []
    for u in (u_vin, u_out):
        spacer = box(u - 1.25, u + 1.25, col_y(1) - 1.27, col_y(15) + 1.27, z_top, z_top + SPACER)
        pins = [box(u - .32, u + .32, col_y(k) - .32, col_y(k) + .32, z_top - PIN_BELOW, z_top) for k in range(1, 16)]
        rows.append((u, spacer, pins))
    return pcb, rows, u_out, y0


def jumper(row, col, z_top):
    u = ROW[row]
    return box(u - JUMP / 2, u + JUMP / 2, col_y(col) - JUMP / 2, col_y(col) + JUMP / 2, z_top + 0.01, z_top + 14)


def main():
    bad = []

    def ok(cond, msg):
        print(("   OK    " if cond else "   FAIL  ") + msg)
        if not cond:
            bad.append(msg)

    print("ESP32 on the 400-hole breadboard: VIN-side row in row j, other row hanging past the edge")
    for name, sp in (("0.9 in", 22.86), ("1.0 in", 25.4), ("1.1 in", 27.94)):
        print(f" pin rows {name} apart ({sp} mm):")
        pcb, rows, u_out, _ = esp(sp, ROW["j"], 0, BB_H)
        ok(u_out + 0.32 < -BB_HW - 2.0, f"other pin row hangs {-BB_HW - u_out:.1f} mm past the breadboard edge (in the air, on no hole)")
        ok(abs(rows[0][0] - ROW["j"]) < 1e-6, "VIN-side pins: all 15 go into row j, columns 1-15")
        for pin, what in USED.items():
            c = PINS.index(pin) + 1
            free = [r for r in "fgh" if (jumper(r, c, BB_H) ^ (pcb + rows[0][1] + rows[1][1])).volume() < 1e-6]
            ok(free == list("fgh"), f"{pin:<4} column {c}: rows f, g, h free for a jumper ({what})")
        blocked = (jumper("i", 3, BB_H) ^ (pcb + rows[0][1])).volume() > 0
        print(f"   (control) row i, right next to the pins, {'is blocked by the board edge' if blocked else 'is free'}")
    ok(len(set(PINS.index(p) for p in USED)) == len(USED) and "D12" not in USED and "VIN" not in USED,
       "every wire has its own column; VIN (column 1) and D12 (column 4) stay empty")
    # control: pushed in across the groove (both rows in the breadboard) a 1.0 in board leaves no usable free row
    pcb, rows, _, _ = esp(25.4, ROW["a"], 0, BB_H, flip=1)
    usable = [r for r in "abcdefghij" if (jumper(r, 3, BB_H) ^ (pcb + rows[0][1] + rows[1][1])).volume() < 1e-6
              and abs(ROW[r] - ROW["a"]) > 0.1 and abs(ROW[r] - (ROW["a"] - 25.4)) > 0.1]
    ok(not usable, f"(control) both rows in the breadboard (rows a + i): free holes next to D13 = {usable or 'none'} -> why it failed before")

    # ---- in the stand's pocket: breadboard long sides at x = -78 (outer) and x = -22 (spine side)
    print(" in the stand pocket:")
    st = H.stand()
    z_bb = H.PLATE_Z - 1.5
    for outward, label in ((True, "ESP32 side facing OUT, away from the spine"), (False, "(control) ESP32 side facing the spine")):
        pcb, rows, u_out, _ = esp(25.4, ROW["j"], 0, BB_H)
        solids = pcb + rows[0][1] + rows[1][1]
        for p in rows[0][2] + rows[1][2]:
            solids += p
        # breadboard coords -> stand: u -> x (row j on the outer side if outward), z -> plate
        sgn = 1 if outward else -1
        placed = solids.scale((sgn, 1, 1)).translate((-50.0, 0.0, z_bb))
        hit = (placed ^ st).volume()
        if outward:
            ok(hit < 1e-3, f"{label}: ESP32 touches nothing on the stand ({hit:.2f} mm3)")
            x_out = -50.0 + u_out
            ok(x_out < -80.0, f"hanging pin row ends up past the plate edge (x = {x_out:.1f}, plate edge -80): pins in the air")
        else:
            ok(hit > 1, f"{label}: would hit the spine socket ({hit:.0f} mm3), so don't")
    assert not bad, bad
    print("wiring fit: all checks passed")


if __name__ == "__main__":
    main()
