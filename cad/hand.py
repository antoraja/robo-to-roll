"""Five-finger RoboHand on a table stand - printable parts + checks.

Structure (all printed, held together with 1.75 mm filament pins - no screws needed):
  stand   flat base plate: socket for the spine, coin pockets for weight, breadboard tray,
          zip-tie slots for the ESP32
  spine   flat plate (prints flat) carrying the 5 MG90S servos, alternating front / back so
          every string runs straight up to the wrist without touching another spool
  palm    one piece, prints standing on its wrist: knuckle forks for 4 fingers + thumb,
          internal string channels from the wrist to every finger
  fingers the tested finger bones, with human-like lengths per finger (thumb: 2 bones)

Run:   python hand.py            -> collision / stability / routing checks + STLs in stl/hand/
       python hand.py --export X -> also writes a mesh JSON for the 3-D viewer
"""
from __future__ import annotations

import base64
import json
import math
import os
import sys

import numpy as np
import manifold3d as m

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_parts as gp  # noqa: E402
from generate_parts import (C, H, W, ZP, box, joint_distal_end, slab, body_profile,  # noqa: E402
                            channels, skin, phalanx, relief, rod_y, TAPER)

gp.SEG = 40
gp.SKIN_SEG = 40

# ------------------------------------------------------------------ layout
# finger:      bone lengths (mm)         knuckle pin (world x, y, z)   splay (deg)
FINGERS = {
    "index":  dict(L=[45, 30, 25], pin=(0.0, 28.0, 0.0), splay=4.0),
    "middle": dict(L=[49, 33, 26], pin=(0.0, 9.5, 4.0), splay=0.0),
    "ring":   dict(L=[46, 31, 25], pin=(0.0, -9.5, 1.0), splay=-3.0),
    "little": dict(L=[37, 25, 22], pin=(0.0, -28.0, -8.0), splay=-8.0),
}
THUMB = dict(L=[40, 30], pin=(16.0, 44.0, -40.0), direction=(0.35, 0.45, 0.82), curl=(0.75, -0.62, 0.0))
ORDER = ["thumb", "index", "middle", "ring", "little"]

PALM_DROP = 13.0          # palm top sits this far below each knuckle pin
WRIST_Z = -100.0          # flat underside of the palm
SPINE_T = 5.0             # spine plate thickness (x)
SPINE_HW = 31.0           # spine half-width (y)
SPINE_TOP = WRIST_Z + 14  # tab that goes up into the palm
SOCKET_TOP = -285.0
SPINE_BOT = -310.0
PLATE_Z = -313.0          # top of the stand's base plate (= table + 5)
PLATE_T = 5.0

# servos: side +1 = spool in front of the spine (palm side), -1 = behind
# every string leaves its spool at "ty" and runs straight up to the wrist
SERVOS = {
    "middle": dict(side=+1, z=-132.0, y=0.0, ty=13.0),
    "index":  dict(side=-1, z=-164.0, y=12.0, ty=25.0),
    "thumb":  dict(side=+1, z=-196.0, y=14.0, ty=27.0),
    "ring":   dict(side=-1, z=-228.0, y=-12.0, ty=-25.0),
    "little": dict(side=+1, z=-260.0, y=-14.0, ty=-27.0),
}
# MG90S
S_BODY_BELOW_TAB = 15.9
S_TAB_T = 2.5
S_CASE_ABOVE_TAB = 4.3
S_LEN, S_WID = 22.8, 12.2
S_TAB_SPAN, S_HOLE_SPACING = 32.3, 27.8
S_SHAFT_FROM_END = 5.9
HORN_GAP = 9.5            # tab top -> spool base (shaft + horn)

STRING_D = 2.4            # palm string channel
PIN_D = 1.9               # filament pin holes


# ----------------------------------------------------------------- helpers
def basis(direction, curl):
    d = np.array(direction, float); d /= np.linalg.norm(d)
    c = np.array(curl, float); c -= d * (c @ d); c /= np.linalg.norm(c)
    return np.column_stack([c, np.cross(d, c), d])


def finger_basis(name):
    if name == "thumb":
        return basis(THUMB["direction"], THUMB["curl"])
    a = math.radians(FINGERS[name]["splay"])
    return basis((0.0, math.sin(a), math.cos(a)), (1.0, 0.0, 0.0))


def finger_pin(name):
    return np.array(THUMB["pin"] if name == "thumb" else FINGERS[name]["pin"], float)


def finger_L(name):
    return THUMB["L"] if name == "thumb" else FINGERS[name]["L"]


def local_to_world_pt(p_local, name):
    """finger-local point (pivot at origin, i.e. after the -ZP shift) -> world."""
    x, y, z = p_local
    v = np.array([-z, y, x])
    return finger_basis(name) @ v + finger_pin(name)


def place(part_local, name):
    p = part_local.rotate((0.0, -90.0, 0.0))
    M = np.eye(4); M[:3, :3] = finger_basis(name); M[:3, 3] = finger_pin(name)
    return p.transform(M[:3, :].tolist())


def rod(p0, p1, d, seg=24):
    """Cylinder between two world points."""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    v = p1 - p0
    L = float(np.linalg.norm(v))
    z = v / L
    a = np.array([1.0, 0, 0]) if abs(z[0]) < 0.9 else np.array([0, 1.0, 0])
    x = np.cross(a, z); x /= np.linalg.norm(x)
    y = np.cross(z, x)
    M = np.eye(4); M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, y, z, p0
    return m.Manifold.cylinder(L, d / 2, d / 2, seg).transform(M[:3, :].tolist())


def blob(c, s, seg=32):
    return m.Manifold.sphere(1, seg).scale(tuple(s)).translate(tuple(c))


# ----------------------------------------------------------------- servos
def spool_x(side):
    tab_top = side * (SPINE_T / 2 + S_TAB_T)
    return tab_top + side * HORN_GAP          # spool base (glued to horn)


def spool_core_x(side):
    return spool_x(side) + side * (gp.SPOOL_FLANGE_T + gp.SPOOL_CORE_W / 2)


def servo_geom(name):
    s = SERVOS[name]; side, y, z = s["side"], s["y"], s["z"]
    face = side * SPINE_T / 2
    # body: shaft end at the top, body hangs downward
    z_top, z_bot = z + S_SHAFT_FROM_END, z + S_SHAFT_FROM_END - S_LEN
    x_back = face - side * S_BODY_BELOW_TAB
    x_front = face + side * (S_TAB_T + S_CASE_ABOVE_TAB)
    body = box(min(x_back, x_front), max(x_back, x_front), y - S_WID / 2, y + S_WID / 2, z_bot, z_top)
    zc = (z_top + z_bot) / 2
    tabs = box(min(face, face + side * S_TAB_T), max(face, face + side * S_TAB_T), y - S_WID / 2, y + S_WID / 2,
               zc - S_TAB_SPAN / 2, zc + S_TAB_SPAN / 2)
    sp = gp.spool().rotate((0.0, 90.0 * side, 0.0)).translate((spool_x(side), y, z))
    holes = [(y, zc - S_HOLE_SPACING / 2), (y, zc + S_HOLE_SPACING / 2)]
    cut = (y, z_bot - 0.2, z_top + 0.2)
    return body + tabs, sp, holes, cut


def string_path(name):
    """World points of the flexor string from the spool to the knuckle column bottom."""
    s = SERVOS[name]
    xs = spool_core_x(s["side"])
    tangent = (xs, s["ty"], s["z"])
    wrist = (xs, s["ty"], WRIST_Z - 0.5)
    col_len = PALM_DROP + 2
    knuckle = local_to_world_pt((-C - col_len, 0.0, gp.FLEX_Z - ZP), name)
    return [np.array(tangent), np.array(wrist), knuckle]


# ------------------------------------------------------------------ parts
def knuckle_local():
    col_len = PALM_DROP + 2
    col = slab(body_profile(-C - col_len, -C, chamfer_start=False), -W / 2, W / 2)
    col += joint_distal_end(0.0)
    col -= channels(-C - col_len - 5, 1.0)
    col -= relief(-C, -1)
    col ^= skin(-C - col_len - 8, 0.0, 1.03, TAPER[0]) + box(-C - col_len - 1, -C - col_len + 3, -W, W, -H, H)
    return col.translate((0, 0, -ZP))


def palm():
    blobs = []
    for name, f in FINGERS.items():
        top = finger_pin(name) + finger_basis(name) @ np.array([0, 0, -PALM_DROP - 4])
        blobs.append(blob(top + np.array([1.5, 0, 0]), (11, 10, 6)))
    blobs.append(blob((2.0, 0.0, -55.0), (13, 34, 14)))
    blobs.append(blob((4.0, 30.0, -64.0), (12, 11, 16)))
    # wrist block: wide enough to take all five strings coming up from the spools
    for sx in (-23.0, 23.0):
        for sy in (-31.0, 31.0):
            blobs.append(blob((sx, sy, WRIST_Z + 6), (6, 6, 6), 20))
    p = m.Manifold.batch_hull(blobs)
    p ^= box(-60, 60, -60, 60, WRIST_Z, 200)                       # flat bottom (prints on it)
    for name in ORDER:
        p += place(knuckle_local(), name)
    Rt = finger_basis("thumb")
    foot = finger_pin("thumb") + Rt @ np.array([0, 0, -PALM_DROP - 2])
    p += m.Manifold.batch_hull([blob(foot, (8, 8, 8), 24), blob((4.0, 30.0, -60.0), (9, 9, 9), 24)])
    # string channels (straight, smooth) and elastic anchor channels (exit on the back)
    for name in ORDER:
        _, w, k = string_path(name)
        p -= rod(w - np.array([0, 0, 2]), k + (k - w) / np.linalg.norm(k - w) * 3, STRING_D)
        col_len = PALM_DROP + 2
        e0 = local_to_world_pt((-C - col_len + 1, 0.0, gp.EXT_Z - ZP), name)
        back = -finger_basis(name)[:, 0]                   # opposite to the curl direction
        down = -finger_basis(name)[:, 2]
        e1 = e0 + (back * 0.8 + down * 0.6) * 40
        p -= rod(e0, e1, gp.EXT_D)
    # spine socket + pin holes
    p -= box(-SPINE_T / 2 - 0.2, SPINE_T / 2 + 0.2, -15.2, 15.2, WRIST_Z - 1, SPINE_TOP + 0.3)
    for y in (-5.0, 5.0):
        p -= rod((-40, y, WRIST_Z + 7), (40, y, WRIST_Z + 7), PIN_D)
    return p


def spine():
    s = box(-SPINE_T / 2, SPINE_T / 2, -SPINE_HW, SPINE_HW, SPINE_BOT, WRIST_Z)
    s += box(-SPINE_T / 2, SPINE_T / 2, -15.0, 15.0, WRIST_Z - 0.1, SPINE_TOP)     # palm tab
    for sy in (-SPINE_HW, SPINE_HW - 3):                                           # edge ribs
        s += box(-7.0, 7.0, sy, sy + 3, SPINE_BOT, WRIST_Z)
    for name in ORDER:
        _, _, holes, (y, z0, z1) = servo_geom(name)
        s -= box(-10, 10, y - S_WID / 2 - 0.2, y + S_WID / 2 + 0.2, z0, z1)
        for (hy, hz) in holes:
            s -= rod((-10, hy, hz), (10, hy, hz), 1.8)
    for y in (-5.0, 5.0):                                                          # palm pins
        s -= rod((-10, y, WRIST_Z + 7), (10, y, WRIST_Z + 7), PIN_D)
    for y in (-20.0, 20.0):                                                        # stand pins
        s -= rod((-10, y, SPINE_BOT + 11), (10, y, SPINE_BOT + 11), PIN_D)
    return s


def stand():
    hx, hy, r = 80.0, 70.0, 10.0
    corners = [blob((sx * (hx - r), sy * (hy - r), PLATE_Z - PLATE_T / 2), (r, r, PLATE_T / 2), 32)
               for sx in (-1, 1) for sy in (-1, 1)]
    plate = m.Manifold.batch_hull(corners) ^ box(-hx, hx, -hy, hy, PLATE_Z - PLATE_T, PLATE_Z)
    sock = box(-12.0, 12.0, -38.0, 38.0, PLATE_Z - 0.1, SOCKET_TOP)
    sock += m.Manifold.batch_hull([box(-12, 12, -38, 38, PLATE_Z - 0.1, PLATE_Z + 0.1),
                                   box(-26, 26, -46, 46, PLATE_Z - 0.1, PLATE_Z + 0.1),
                                   box(-12, 12, -38, 38, PLATE_Z + 12, PLATE_Z + 12.1)])   # gusset flare
    st = plate + sock
    st -= box(-SPINE_T / 2 - 0.2, SPINE_T / 2 + 0.2, -SPINE_HW - 0.2, SPINE_HW + 0.2, SPINE_BOT, SOCKET_TOP + 1)
    st -= box(-7.2, 7.2, -SPINE_HW - 0.2, -SPINE_HW + 3.2, SPINE_BOT, SOCKET_TOP + 1)
    st -= box(-7.2, 7.2, SPINE_HW - 3.2, SPINE_HW + 0.2, SPINE_BOT, SOCKET_TOP + 1)
    for y in (-20.0, 20.0):
        st -= rod((-30, y, SPINE_BOT + 11), (30, y, SPINE_BOT + 11), PIN_D)
    # coin pockets (weight) at the corners: 26 mm coins / washers, 3.5 mm deep
    for sx in (-1, 1):
        for sy in (-1, 1):
            st -= m.Manifold.cylinder(4, 13.5, 13.5, 48).translate((sx * 62, sy * 50, PLATE_Z - 3.5))
    # breadboard tray (400-point, 84 x 56 mm) behind the arm
    st -= box(-78.0, -22.0, -42.5, 42.5, PLATE_Z - 1.5, PLATE_Z + 1)
    # ESP32 zip-tie slots in front of the arm
    for x in (32.0, 64.0):
        for y in (-22.0, 22.0):
            st -= box(x - 2, x + 2, y - 1.5, y + 1.5, PLATE_Z - PLATE_T - 1, PLATE_Z + 1)
    return st


def finger_bones(name):
    L = finger_L(name)
    if len(L) == 3:
        return [phalanx(L[0]), phalanx(L[1], which="mid"), phalanx(L[2], distal=True)]
    return [phalanx(L[0]), phalanx(L[1], distal=True)]


def posed(name, curl_deg, bones=None):
    bones = bones or finger_bones(name)
    T = np.eye(4); out = []
    for b, length in zip(bones, finger_L(name)):
        a = math.radians(curl_deg)
        Ry = np.array([[math.cos(a), 0, math.sin(a), 0], [0, 1, 0, 0], [-math.sin(a), 0, math.cos(a), 0], [0, 0, 0, 1]])
        T = T @ Ry
        out.append(place(b.translate((0, 0, -ZP)).transform(T[:3, :].tolist()), name))
        S = np.eye(4); S[0, 3] = length; T = T @ S
    return out


# ------------------------------------------------------------------ checks
def checks(P, SP, ST, bones):
    print("1) Collisions")
    servos = {n: servo_geom(n) for n in ORDER}
    worst = 0.0
    for n in ORDER:
        body, sp, _, _ = servos[n]
        worst = max(worst, (body ^ ST).volume(), (sp ^ ST).volume(), (sp ^ SP).volume(), (sp ^ P).volume(), (body ^ P).volume())
        for n2 in ORDER:
            if n2 != n:
                worst = max(worst, (sp ^ servos[n2][0]).volume(), (sp ^ servos[n2][1]).volume(), (body ^ servos[n2][0]).volume())
    print(f"   servos / spools vs each other, spine, palm, stand: worst overlap {worst:.2f} mm3")
    tubes = {n: rod(string_path(n)[0], string_path(n)[1], 0.6) for n in ORDER}
    hit = max((tubes[n] ^ (servos[n2][1] + servos[n2][0])).volume() for n in ORDER for n2 in ORDER if n2 != n)
    hit_spine = max((tubes[n] ^ SP).volume() for n in ORDER)
    print(f"   strings (spool -> wrist) touching another servo/spool: {hit:.2f} mm3, touching spine: {hit_spine:.2f} mm3")
    for curl in (0, 45, 85):
        palm_hit, pair = 0.0, 0.0
        ps = {n: posed(n, curl if n != "thumb" else 0, bones[n]) for n in ORDER}
        for n in ORDER:
            for i, b in enumerate(ps[n]):
                tgt = P - place(knuckle_local(), n) if i == 0 else P
                palm_hit = max(palm_hit, (b ^ tgt).volume())
        for a, b in zip(ORDER[1:], ORDER[2:]):
            pair = max(pair, max((x ^ y).volume() for x in ps[a] for y in ps[b]))
        print(f"   fingers at {curl:2d} deg/joint: finger-palm {palm_hit:.1f} mm3, finger-finger {pair:.1f} mm3")
    for c in (45, 85):
        th = posed("thumb", c, bones["thumb"])
        print(f"   thumb at {c} deg vs palm: {sum(((b ^ (P - place(knuckle_local(), 'thumb'))) if i == 0 else (b ^ P)).volume() for i, b in enumerate(th)):.1f} mm3")

    print("2) String routing through the palm")
    for n in ORDER:
        t, w, k = string_path(n)
        p0 = w + (k - w) / np.linalg.norm(k - w) * 2
        p1 = k - (k - w) / np.linalg.norm(k - w) * 2
        wall = rod(p0, p1, STRING_D + 2.4) - rod(p0, p1, STRING_D + 0.2)    # 1.2 mm wall around the channel
        outside = (wall - P).volume() / wall.volume() * 100
        d_in = (k - w) / np.linalg.norm(k - w)
        axis = finger_basis(n)[:, 2]
        bend_wrist = math.degrees(math.acos(np.clip(d_in @ np.array([0, 0, 1.0]), -1, 1)))
        bend_knuckle = math.degrees(math.acos(np.clip(d_in @ axis, -1, 1)))
        extra = math.exp(0.25 * math.radians(bend_wrist + bend_knuckle))
        print(f"   {n:<7} channel wall (1.2 mm) missing: {outside:4.1f} %  bends {bend_wrist:4.1f}° at wrist + "
              f"{bend_knuckle:4.1f}° at knuckle -> friction x{extra:.2f}")

    print("3) Stability on the table (PLA ~45 % effective density, servos 13.4 g)")
    rho = 1.24e-3 * 0.45
    items = [(P, rho), (SP, rho), (ST, rho)]
    for n in ORDER:
        for b in posed(n, 85 if n != "thumb" else 60, bones[n]):
            items.append((b, rho))
    mass, mom = 0.0, np.zeros(3)
    for part, r in items:
        v = part.volume(); c = centroid(part)
        mass += v * r; mom += v * r * c
    for n in ORDER:
        body, sp, _, _ = servo_geom(n)
        mass += 13.4; mom += 13.4 * centroid(body)
    com = mom / mass
    h = com[2] - (PLATE_Z - PLATE_T)
    edges = {"front": 80 - com[0], "back": 80 + com[0], "side": 70 - abs(com[1])}
    tip = {k: math.degrees(math.atan2(v, h)) for k, v in edges.items()}
    print(f"   total ~{mass:.0f} g, centre of mass {h:.0f} mm above the table, {com[0]:+.0f} mm forward")
    print("   tips over only if tilted: " + ", ".join(f"{k} {v:.0f}°" for k, v in tip.items()))
    top = 430.0
    push = mass * min(edges.values()) / top
    coins = 4 * 7.5                                     # four 26 mm coins / washers (~7.5 g each)
    push_c = (mass * min(edges.values()) + coins * 62) / top
    print(f"   sideways push at the fingertips needed to tip it: ~{push:.0f} g-force; with 4 coins in the pockets ~{push_c:.0f} g-force")


def seg_dist(p1, q1, p2, q2):
    """Shortest distance between two 3-D segments."""
    d1, d2, r = q1 - p1, q2 - p2, p1 - p2
    a, e, f = d1 @ d1, d2 @ d2, d2 @ r
    c, b = d1 @ r, d1 @ d2
    den = a * e - b * b
    s = np.clip((b * f - c * e) / den, 0, 1) if den > 1e-9 else 0.0
    t = np.clip((b * s + f) / e, 0, 1)
    s = np.clip((b * t - c) / a, 0, 1)
    return float(np.linalg.norm((p1 + d1 * s) - (p2 + d2 * t)))


SERVO_LEAD = 200.0        # MG90S lead length (mm): the ordered 6-pack has 20 cm leads


def extra_checks(P):
    """Things a builder would trip over: channels crossing, elastic exits, pins, cable reach."""
    print("5) Assembly details")
    col_len = PALM_DROP + 2
    strings, elastics = {}, {}
    for n in ORDER:
        _, w, k = string_path(n)
        strings[n] = (w, k)
        e0 = local_to_world_pt((-C - col_len + 1, 0.0, gp.EXT_Z - ZP), n)
        back, down = -finger_basis(n)[:, 0], -finger_basis(n)[:, 2]
        elastics[n] = (e0, e0 + (back * 0.8 + down * 0.6) * 40)
    worst = (99.0, "")
    names = list(ORDER)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            d = seg_dist(*strings[a], *strings[b]) - STRING_D
            worst = min(worst, (d, f"string {a} / string {b}"))
        for b in names:
            d = seg_dist(*strings[a], *elastics[b]) - (STRING_D + gp.EXT_D) / 2
            worst = min(worst, (d, f"string {a} / elastic {b}"))
            if a < b:
                d2 = seg_dist(*elastics[a], *elastics[b]) - gp.EXT_D
                worst = min(worst, (d2, f"elastic {a} / elastic {b}"))
    print(f"   closest pair of channels in the palm: {worst[1]} with {worst[0]:.1f} mm of plastic between them")
    pins = [(np.array([-40.0, y, WRIST_Z + 7]), np.array([40.0, y, WRIST_Z + 7])) for y in (-5.0, 5.0)]
    near_pin = min(seg_dist(*p, *strings[n]) - (PIN_D + STRING_D) / 2 for p in pins for n in ORDER)
    print(f"   palm pin holes vs string channels: {near_pin:.1f} mm apart")
    exits = []
    for n in ORDER:
        e0, e1 = elastics[n]
        probe = m.Manifold.sphere(1.5, 16).translate(tuple(e1))
        exits.append((probe ^ P).volume() < 0.5)
    print(f"   elastic channels reach the outside of the palm (to tie the knot): {sum(exits)}/5")
    slot = box(-SPINE_T / 2 - 0.2, SPINE_T / 2 + 0.2, -15.2, 15.2, WRIST_Z - 1, SPINE_TOP + 0.3)
    hit = sum((rod(*elastics[n], gp.EXT_D) ^ slot).volume() + (rod(*strings[n], STRING_D) ^ slot).volume() for n in ORDER)
    print(f"   channels cutting into the spine slot: {hit:.1f} mm3")
    print("   servo lead reach (MG90S lead 20 cm) to the breadboard behind the arm:")
    bb = np.array([-50.0, 0.0, PLATE_Z + 9])
    for n in ORDER:
        body, _, _, _ = servo_geom(n)
        lo, hi = body.bounding_box()[:3], body.bounding_box()[3:]
        exit_pt = np.array([(lo[0] + hi[0]) / 2, SERVOS[n]["y"], lo[2]])   # lead leaves the bottom end of the case
        route = abs(exit_pt[2] - (PLATE_Z + 2)) + abs(exit_pt[0] - bb[0]) + abs(exit_pt[1] - bb[1]) + 30  # +30 slack
        ok = "OK" if route <= SERVO_LEAD - 20 else "short - bridged by the 20 cm male-male jumpers to the breadboard"
        print(f"      {n:<7} needs ~{route:3.0f} mm  {ok}")


def centroid(part):
    mesh = part.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]; f = np.asarray(mesh.tri_verts)
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    vol = np.einsum("ij,ij->i", a, np.cross(b, c)) / 6
    return ((a + b + c) / 4 * vol[:, None]).sum(0) / vol.sum()


def save(part, name, rot=(0, 0, 0)):
    import trimesh
    p = part.rotate(rot)
    lo = np.array(p.bounding_box()[:3]); p = p.translate(tuple(-lo))
    mesh = p.to_mesh()
    t = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts))
    assert t.is_watertight, name
    out = os.path.join(HERE, "stl", "hand"); os.makedirs(out, exist_ok=True)
    t.export(os.path.join(out, name))
    e = t.extents
    print(f"   {name:<26} {e[0]:6.1f} x {e[1]:6.1f} x {e[2]:6.1f} mm  {t.volume / 1000 * 1.24 * 0.45:5.0f} g")


def write_stls(P, SP, ST, bones):
    print("4) Printable parts (stl/hand/), PLA estimate")
    save(P, "palm.stl")                              # stands on its flat wrist
    save(SP, "spine.stl", (0, 90, 0))                # lies flat
    save(ST, "stand.stl")
    save(gp.spool(), "servo_spool_x5.stl")
    for n in ORDER:
        names = ["proximal", "middle", "distal"] if len(finger_L(n)) == 3 else ["proximal", "distal"]
        for b, part in zip(bones[n], names):
            save(b, f"{n}_{part}.stl", (180, 0, 0))   # on its flat back


def export(path, P, SP, ST, bones):
    def enc(p):
        mm = p.to_mesh()
        v = np.asarray(mm.vert_properties)[:, :3].astype(np.float32)
        f = np.asarray(mm.tri_verts).astype(np.uint32)
        return {"v": base64.b64encode(v.tobytes()).decode(), "i": base64.b64encode(f.tobytes()).decode()}
    data = {"palm": enc(P), "spine": enc(SP), "stand": enc(ST), "fingers": {}, "servos": [],
            "params": dict(FLEX_Z=gp.FLEX_Z, ZP=ZP, C=C, spoolR=gp.SPOOL_R, colLen=PALM_DROP + 2)}
    for n in ORDER:
        data["fingers"][n] = dict(L=finger_L(n), pin=finger_pin(n).tolist(), R=finger_basis(n).T.flatten().tolist(),
                                  bones=[enc(b.translate((0, 0, -ZP))) for b in bones[n]])
        body, sp, _, _ = servo_geom(n)
        s = SERVOS[n]
        t, w, _ = string_path(n)
        data["servos"].append(dict(finger=n, body=enc(body), spool=enc(sp), side=s["side"],
                                   centre=[spool_core_x(s["side"]), s["y"], s["z"]],
                                   path=[t.tolist(), w.tolist()]))
    with open(path, "w") as fh:
        json.dump(data, fh)
    print("exported", path, os.path.getsize(path) // 1024, "KB")


if __name__ == "__main__":
    P, SP, ST = palm(), spine(), stand()
    bones = {n: finger_bones(n) for n in ORDER}
    checks(P, SP, ST, bones)
    extra_checks(P)
    if "--checks-only" in sys.argv:
        sys.exit(0)
    write_stls(P, SP, ST, bones)
    if "--export" in sys.argv:
        export(sys.argv[sys.argv.index("--export") + 1], P, SP, ST, bones)
