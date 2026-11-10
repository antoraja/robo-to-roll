"""Generate printable STL parts for the one-finger test rig.

Run:   pip install manifold3d trimesh numpy
       python generate_parts.py          # writes ./stl/*.stl and checks joint range

Coordinate conventions (finger "local" frame, used for the phalanges):
  x = along the finger (base -> tip)
  y = across the finger (width)
  z = up (back of the finger = +z, palm side = -z). The finger curls toward -z.
Every joint is a pin along y. A phalanx has a TONGUE (centre tab) at its
proximal end and a CLEVIS (two side prongs) at its distal end; the next
phalanx's tongue slides between the previous one's prongs.

All sizes in millimetres. Edit the PARAMETERS block and re-run to resize.
"""
from __future__ import annotations

import math
import os

import manifold3d as m
import numpy as np
import trimesh

# ----------------------------------------------------------------- PARAMETERS
W = 16.0           # finger width (y)
H = 16.0           # finger height (z), body spans z = -8 .. +8
ZP = 1.0           # pin height (z) - slightly above centre
R = 5.0            # radius of tongue / prong around the pin
C = 5.5            # distance from pin to the body faces (joint gap = 2*C)
TONGUE_HALF = 3.0  # tongue spans y = -3 .. +3
SLOT_HALF = 3.3    # gap between prongs y = -3.3 .. +3.3 (0.3 mm clearance)
CHAMFER = 3.0      # 45 deg chamfer on palm-side body corners at each joint

PIN_HOLE_PRONG = 1.9   # snug hole in the prongs for 1.75 mm filament pin
PIN_HOLE_TONGUE = 2.3  # free-turning hole in the tongue

FLEX_Z = -5.8          # flexor (closing) tendon channel, palm side, centred
EXT_Z = 5.8            # elastic channel, back side, centred: cord runs 4.8 mm behind the pin
KNUCKLE_GROOVE_R = 3.8 # rounded groove in each tongue the elastic wraps over (cord centre at 4.8 mm)
CHANNEL_D = 2.0        # flexor (string) channel diameter
EXT_D = 2.6            # elastic channel diameter (2 mm round elastic cord)
LOCK_D = 1.9           # lock-pin hole (1.75 mm filament) that pinches the elastic in each bone
LOCK_DZ = -1.6         # lock hole sits this far below the elastic channel so the pin pinches the cord
RELIEF_W = 2.4         # groove at each joint face so the string isn't pinched when the joint closes
RELIEF_LEN = 3.5

L_PROX, L_MID, L_DIST = 45.0, 30.0, 25.0   # joint-to-joint lengths (distal: joint-to-tip)

# Spool for the servo horn
SPOOL_R = 13.0         # string winding radius -> ~41 mm of pull over 180 deg (sim needs ~38 mm)
SPOOL_FLANGE_R = 16.0
SPOOL_CORE_W = 5.0
SPOOL_FLANGE_T = 1.5

# SG90 / MG90S micro servo (typical, clones vary +/-0.5 mm)
SERVO_L, SERVO_W = 22.8, 12.2      # body footprint
SERVO_TAB_HOLE_SPACING = 27.8      # distance between the two mounting-tab holes
SERVO_TAB_SPAN = 32.3              # overall length including the mounting tabs
SERVO_SHAFT_FROM_END = 5.9         # output shaft centre measured from the near short end
SERVO_CLEAR = 0.4                  # clearance added to the body cut-out

SEG = 64  # circle resolution

# Finger "skin": every bone is trimmed to a smooth, tapered oval shape (like printed
# prosthetic / InMoov-style fingers) instead of a box. The back keeps a flat strip so the
# bones still print flat on their back with no supports.
SKIN_AX = 10.0                 # length of the rounded knuckle around each pin
SKIN_AY = W / 2 + 0.6          # oval half-width  (corners get rounded off)
SKIN_AZ = H / 2 + 1.6          # oval half-height (back stays flat where the oval exceeds H/2)
TAPER = [1.00, 0.97, 0.94, 0.91]   # oval scale at: knuckle, joint 1, joint 2, fingertip
TIP_LEN = 6.0                  # fingertip dome length
TIP_AY, TIP_AZ, TIP_Z = 6.4, 7.5, 0.5  # fingertip dome half-width / half-height / centre (top = flat back)
SKIN_SEG = 48
# ----------------------------------------------------------------------------

CS = m.CrossSection


def rect(x0, x1, z0, z1):
    return CS.square((x1 - x0, z1 - z0)).translate((x0, z0))


def circ(r, cx, cz):
    return CS.circle(r, SEG).translate((cx, cz))


def poly(pts):
    return CS([pts])


def slab(profile: m.CrossSection, y0: float, y1: float) -> m.Manifold:
    """Extrude an (x, z) side profile across y in [y0, y1]."""
    solid = m.Manifold.extrude(profile, y1 - y0)       # profile in XY, height along +Z
    solid = solid.rotate((90.0, 0.0, 0.0))              # XY -> XZ, extrusion -> -Y
    return solid.translate((0.0, y1, 0.0))


def rod_x(d, y, z, x0, x1):
    """Cylinder along x."""
    cyl = m.Manifold.cylinder(x1 - x0, d / 2, d / 2, SEG)   # along +Z
    return cyl.rotate((0.0, 90.0, 0.0)).translate((x0, y, z))


def rod_y(d, x, z, y0=-30.0, y1=30.0):
    cyl = m.Manifold.cylinder(y1 - y0, d / 2, d / 2, SEG)
    return cyl.rotate((-90.0, 0.0, 0.0)).translate((x, y0, z))


def box(x0, x1, y0, y1, z0, z1):
    return m.Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


# ---------------------------------------------------------- 2-D side profiles
def body_profile(x0, x1, chamfer_start=True, chamfer_end=True):
    """Body block between x0 and x1 with palm-side chamfers at the joint ends."""
    pts = []
    zb, zt = -H / 2, H / 2
    pts.append((x0 + (CHAMFER if chamfer_start else 0), zb))
    pts.append((x1 - (CHAMFER if chamfer_end else 0), zb))
    if chamfer_end:
        pts.append((x1, zb + CHAMFER))
    pts.append((x1, zt))
    pts.append((x0, zt))
    if chamfer_start:
        pts.append((x0, zb + CHAMFER))
    return poly(pts)


def tongue_profile():
    """Centre tab at a proximal joint (pin at x=0)."""
    return (circ(R, 0, ZP)
            + rect(-R, C + 0.01, ZP, H / 2)      # top half extends back (flat for printing)
            + rect(0, C + 0.01, ZP - R, H / 2))


def ear_profile():
    """Full-width lip on top of the tongue side: hyper-extension stop."""
    return rect(0.3, C + 0.01, ZP + R + 0.3, H / 2)


def prong_profile():
    """Side prong at a distal joint (pin at x=0)."""
    return circ(R, 0, ZP) + rect(-C - 0.01, 0, ZP, H / 2)


# ------------------------------------------------------------------ 3-D parts
def joint_proximal_end(x_pin=0.0):
    """Tongue + ear for the joint at x_pin (this part is the DISTAL side of that joint)."""
    t = slab(tongue_profile(), -TONGUE_HALF, TONGUE_HALF)
    e = slab(ear_profile(), -W / 2, W / 2)
    hole = rod_y(PIN_HOLE_TONGUE, 0, ZP)
    return (t + e - hole - knuckle_groove()).translate((x_pin, 0, 0))


def joint_distal_end(x_pin):
    """Clevis prongs for the joint at x_pin (this part is the PROXIMAL side)."""
    p = slab(prong_profile(), -W / 2, -SLOT_HALF) + slab(prong_profile(), SLOT_HALF, W / 2)
    hole = rod_y(PIN_HOLE_PRONG, 0, ZP)
    return (p - hole).translate((x_pin, 0, 0))


def channels(x0, x1):
    c = rod_x(CHANNEL_D, 0, FLEX_Z, x0, x1)
    c += rod_x(EXT_D, 0, EXT_Z, x0, x1)
    return c


def knuckle_groove():
    """Groove over the back of a tongue: the elastic wraps round it, so its leverage stays
    constant at every joint angle (stops the joints snapping closed one by one)."""
    keep = m.Manifold.cylinder(2 * W, KNUCKLE_GROOVE_R, KNUCKLE_GROOVE_R, SEG).rotate((-90.0, 0.0, 0.0)) \
        .translate((0, -W, ZP))
    region = box(-R - 2, C + 0.5, -EXT_D / 2, EXT_D / 2, ZP, H / 2 + 1)
    return region - keep


def lock_hole(x):
    """Cross hole for a filament lock pin that pinches both elastic strands at this bone."""
    return rod_y(LOCK_D, x, EXT_Z + LOCK_DZ, -W, W)


def relief(x_face, direction):
    """Open the palm side of the string channel near a joint face (direction +1: body is at +x)."""
    xa = x_face - 0.2 * direction
    xb = x_face + RELIEF_LEN * direction
    return box(min(xa, xb), max(xa, xb), -RELIEF_W / 2, RELIEF_W / 2, -H / 2 - 1, FLEX_Z)


def _oval(x, scale, ay=SKIN_AY, az=SKIN_AZ, ax=SKIN_AX, z=0.0):
    return m.Manifold.sphere(1.0, SKIN_SEG).scale((ax, ay * scale, az * scale)).translate((x, 0.0, z))


def skin(x0, x1, s0, s1, tip=False):
    """Smooth tapered envelope from the pin at x0 to the pin (or fingertip) at x1."""
    a = _oval(x0, s0)
    if tip:
        b = _oval(x1 - TIP_LEN, 1.0, ay=TIP_AY, az=TIP_AZ, ax=TIP_LEN, z=TIP_Z)
    else:
        b = _oval(x1, s1)
    return m.Manifold.batch_hull([a, b])


BONE_TAPER = {"prox": (TAPER[0], TAPER[1]), "mid": (TAPER[1], TAPER[2]), "dist": (TAPER[2], TAPER[3])}


def phalanx(length, distal=False, which=None):
    which = which or ("dist" if distal else "prox")
    s0, s1 = BONE_TAPER[which]
    if distal:
        prof = body_profile(C, length, chamfer_end=False)
        part = slab(prof, -W / 2, W / 2) + joint_proximal_end(0)
        # round the fingertip a little: cut the top-front edge
        tip_cut = slab(poly([(length - 4, H / 2 + 1), (length + 1, H / 2 - 5), (length + 1, H / 2 + 1)]), -W, W)
        part -= tip_cut
        part -= channels(-10, length + 5)
        part -= lock_hole(length / 2)
        part -= relief(C, +1)
        part ^= skin(0.0, length, s0, s1, tip=True)
        # socket for the tip cap that anchors the string (see tip_cap())
        part -= cap_socket(length)
        return part
    prof = body_profile(C, length - C)
    part = slab(prof, -W / 2, W / 2) + joint_proximal_end(0) + joint_distal_end(length)
    part -= channels(-10, length + 10)
    part -= lock_hole(length / 2)
    part -= relief(C, +1) + relief(length - C, -1)
    return part ^ skin(0.0, length, s0, s1)


# Tip cap: a flush plug in the fingertip that anchors the string (replaces knot + glue).
# The string loops through two small holes in the cap; string tension pulls the cap into its socket.
CAP_DEPTH = 7.0          # how far the socket reaches into the fingertip from its end
CAP_HW, CAP_HH = 3.0, 1.8  # socket half-width (y) / half-height (z) around the string channel
CAP_CLEAR = 0.15         # clearance per side between cap and socket
CAP_HOLE = 1.2           # the two holes for the 0.3 mm braided line
CAP_HOLE_Y = 1.3         # holes at y = +/-1.3 (1.4 mm bar between them)


def cap_socket(length):
    return box(length - CAP_DEPTH, length + 2, -CAP_HW, CAP_HW, FLEX_Z - CAP_HH, FLEX_Z + CAP_HH)


def tip_cap(length):
    """Cap for the distal bone of a given length, in the bone's own coordinates (flush with the skin)."""
    s0, s1 = BONE_TAPER["dist"]
    c = box(length - CAP_DEPTH + CAP_CLEAR, length + 2, -CAP_HW + CAP_CLEAR, CAP_HW - CAP_CLEAR,
            FLEX_Z - CAP_HH + CAP_CLEAR, FLEX_Z + CAP_HH - CAP_CLEAR)
    c ^= skin(0.0, length, s0, s1, tip=True)
    for y in (-CAP_HOLE_Y, CAP_HOLE_Y):
        c -= rod_x(CAP_HOLE, y, FLEX_Z, length - CAP_DEPTH - 1, length + 3)
    return c


def spool():
    core = m.Manifold.cylinder(SPOOL_CORE_W, SPOOL_R, SPOOL_R, SEG).translate((0, 0, SPOOL_FLANGE_T))
    f1 = m.Manifold.cylinder(SPOOL_FLANGE_T, SPOOL_FLANGE_R, SPOOL_FLANGE_R, SEG)
    f2 = f1.translate((0, 0, SPOOL_FLANGE_T + SPOOL_CORE_W))
    # 45-degree cone under the top flange so it prints without a flat overhang
    lip = SPOOL_FLANGE_R - SPOOL_R
    cone = m.Manifold.cylinder(lip, SPOOL_R, SPOOL_FLANGE_R, SEG).translate(
        (0, 0, SPOOL_FLANGE_T + SPOOL_CORE_W - lip))
    s = core + f1 + f2 + cone
    total = 2 * SPOOL_FLANGE_T + SPOOL_CORE_W
    s -= m.Manifold.cylinder(total + 2, 2.0, 2.0, SEG).translate((0, 0, -1))  # screwdriver access to horn screw
    # two tendon anchor holes through the core, near the rim, opposite each other
    for ang in (0, 180):
        a = math.radians(ang)
        s -= m.Manifold.cylinder(total + 2, 0.75, 0.75, 24).translate(
            (math.cos(a) * (SPOOL_R - 2), math.sin(a) * (SPOOL_R - 2), -1))
    # radial slot so the line can pass from the rim to the anchor hole
    s -= box(SPOOL_R - 2.5, SPOOL_R + 1, -0.6, 0.6, SPOOL_FLANGE_T, SPOOL_FLANGE_T + SPOOL_CORE_W)
    return s


# ---- glue-free spool (v2): the servo horn sits in a pocket on the spool's back and is LASHED in with
# the braided line through two pairs of slots. Spool + horn go onto the shaft together, fixed by the
# horn's own centre screw through the spool's centre hole. Horn measured from the builder's photo with a
# ruler (37.8 px/mm): straight double arm, 31.3 mm long, 5.6 -> 3.4 mm wide, hub 7.2 mm.
HORN_LONG = 26.0          # arm tip to tip AFTER trimming (as bought 31.3 mm: cut ~2.7 mm off each end, flaw B12)
HORN_LONG_W = (5.6, 3.9)  # arm width next to the hub / at the cut ends (measured)
HORN_SHORT = 0.0          # no short arms on this horn (0 = none)
HORN_SHORT_W = (5.0, 4.4)
HORN_T = 1.8              # thickness of the flat arms
HORN_HUB_D = 7.2          # round hub (measured)
HORN_FIT = 0.45           # clearance per side in the pocket (0.3 was too tight once printed)
MOUTH_EXTRA, MOUTH_H = 0.4, 0.4   # wider mouth for the first 0.4 mm: the first layer squashes out (elephant's foot)
SPOOL_BASE_T = 2.9        # base disc under the spool: pocket (HORN_T + 0.5) + 0.6 mm floor
SCREW_HOLE_D = 5.5        # centre hole: the horn screw head + screwdriver pass through
BASE_R = 13.5             # base disc radius: the next servo's body is 15.1 mm from the shaft (flaw B12)
LASH_R = (6.0, 12.0)      # radial range of the lashing slots (over the horn arm's holes)
LASH_W = 1.6
LASH_SIDE = 5.0           # second slot of each pair, beside the arm


POCKET_D = HORN_T + 0.5   # pocket depth: the whole horn arm sits inside, even if it is up to 2.3 mm thick
SPOOL_FLOOR = SPOOL_BASE_T - POCKET_D   # 0.6 mm of plastic between the horn and the old spool body


def horn_pocket(fit=HORN_FIT, arms=2, open_ends=True, mouth=True):
    """Horn-shaped recess from the disc's underside (z = -POCKET_D) up to z = 0 (the horn's outer face).
    arms=2: straight double arm, arms=1: single arm (towards +y). open_ends: the arm slots run out through
    the rim, so the exact trimmed length doesn't matter. mouth: first 0.4 mm a bit wider (elephant's foot)."""
    def profile(f):
        def arm(length, w_hub, w_tip, along_y):
            ends = []
            for s_ in (-1, 1):
                c = (0.0, s_ * (length / 2 - w_tip / 2)) if along_y else (s_ * (length / 2 - w_tip / 2), 0.0)
                ends.append(CS.circle(w_tip / 2 + f, SEG).translate(c))
            hub = CS.circle(w_hub / 2 + f, SEG)
            out = CS.batch_hull([ends[1], hub])
            return out + CS.batch_hull([ends[0], hub]) if arms == 2 else out
        L = 2 * (SPOOL_FLANGE_R + 2) if open_ends else HORN_LONG
        w_tip = HORN_LONG_W[1] - (HORN_LONG_W[0] - HORN_LONG_W[1]) * (L - HORN_LONG) / HORN_LONG if open_ends else HORN_LONG_W[1]
        prof = arm(L, HORN_LONG_W[0], max(w_tip, HORN_LONG_W[1]), True) + CS.circle(HORN_HUB_D / 2 + f, SEG)
        if HORN_SHORT > 0:
            prof += arm(HORN_SHORT, *HORN_SHORT_W, False)
        return prof
    pk = m.Manifold.extrude(profile(fit), POCKET_D + 0.01).translate((0, 0, -POCKET_D - 0.01))
    if mouth and fit > 0:
        pk += m.Manifold.extrude(profile(fit + MOUTH_EXTRA), MOUTH_H + 0.01).translate((0, 0, -POCKET_D - 0.01))
    return pk


def _through(solid, z0, z1):
    solid -= m.Manifold.cylinder(z1 - z0 + 2, SCREW_HOLE_D / 2, SCREW_HOLE_D / 2, SEG).translate((0, 0, z0 - 1))
    return solid


def spool_v2(arms=2):
    """Glue-free spool. z = 0 is the horn's outer face (where the old spool was glued). Base disc with the
    horn pocket from z = -POCKET_D to SPOOL_FLOOR, then the old spool body unchanged on top."""
    base = m.Manifold.cylinder(SPOOL_BASE_T, BASE_R, BASE_R, SEG).translate((0, 0, -POCKET_D))
    rise = SPOOL_FLANGE_R - BASE_R                     # 45 deg slope from the small disc out to the spool's rim
    base += m.Manifold.cylinder(rise, BASE_R, SPOOL_FLANGE_R, SEG).translate((0, 0, SPOOL_FLOOR - rise))
    s = base + spool().translate((0, 0, SPOOL_FLOOR))
    top = SPOOL_FLOOR + 2 * SPOOL_FLANGE_T + SPOOL_CORE_W
    s -= horn_pocket(arms=arms)
    s = _through(s, -POCKET_D, top)
    for k in range(arms):                  # marking on top: 2 dots = double-arm horn, 1 dot = single-arm horn
        s -= m.Manifold.cylinder(0.6, 1.0, 1.0, 24).translate((-8.0, (k - (arms - 1) / 2) * 3.2, top - 0.5))
    for sy in ((-1, 1) if arms == 2 else (1,)):   # lashing slots: one over the arm's holes, one beside the arm
        for x in (0.0, LASH_SIDE):
            y0, y1 = sorted((sy * LASH_R[0], sy * LASH_R[1]))
            slot = CS.batch_hull([CS.circle(LASH_W / 2, 24).translate((x, y0)), CS.circle(LASH_W / 2, 24).translate((x, y1))])
            s -= m.Manifold.extrude(slot, top + POCKET_D + 2).translate((0, 0, -POCKET_D - 1))
    return s


def horn_fit_test(arms=2):
    """8-minute test piece: only the base disc with the horn pocket and the centre hole.
    Marked on top with 2 dots (double-arm horn) or 1 dot (single-arm horn)."""
    t = m.Manifold.cylinder(SPOOL_BASE_T, BASE_R, BASE_R, SEG).translate((0, 0, -POCKET_D))
    t -= horn_pocket(arms=arms)
    t = _through(t, -POCKET_D, SPOOL_FLOOR)
    for k in range(arms):
        t -= m.Manifold.cylinder(0.5, 1.0, 1.0, 24).translate((-8.5, (k - (arms - 1) / 2) * 3.2, SPOOL_FLOOR - 0.4))
    return t


def horn_model(arms=2):
    """The horn itself (for checks and pictures): the pocket shape without clearance, HORN_T thick."""
    # outer (flat) face against the pocket floor at z = 0, arm thickness below it
    return horn_pocket(fit=0.0, arms=arms, open_ends=False, mouth=False) ^ m.Manifold.cylinder(HORN_T, 40, 40, SEG).translate((0, 0, -HORN_T))


# ---- spool v3: NO HORN. Presses straight onto the servo's 21-tooth spline (OD ~4.8 mm, community
# measurements; clones vary, 4.6 mm often fits best) and is held by the horn's centre screw (threaded
# shaft). Untrimmed horns would hit the next servo (B12), so they are not used at all.
# z = 0 is the top of the servo shaft.
SPLINE_D = 4.8            # socket for the spline: the 4-dot test hub (4.8 mm) fitted best on the real servo
SPLINE_DEPTH = 2.8        # how far the spline goes into the spool
V3_BODY_Z = 2.0           # spool body starts 2 mm above the shaft top: flanges clear the next servo even
                          # if the real shaft sits 2 mm lower than assumed
V3_FLOOR = 0.9            # plastic under the screw head
V3_RECESS = (6.0, 1.0)    # recess under the base around the shaft (gear boss on the servo case)
V3_SCREW_D, V3_HEAD_D = 2.3, 6.5   # head hole 6.5: the screw head + screwdriver go 9 mm down to the floor
V3_HEAD_MOUTH = (0.5, 0.6)         # first 0.6 mm of that hole 0.5 wider (printed on the bed: first-layer squash)
SCREW = dict(head_d=4.5, head_h=1.6, shank_d=2.0, shank_l=4.0)   # MG90S horn screw, generous assumption
SPLINE_TEST_SIZES = (4.35, 4.5, 4.65, 4.8)


def spool_v3(spline_d=SPLINE_D):
    """Spool that goes straight on the servo shaft. Printed upside down (outer flange on the bed): both
    flanges have 45 deg inner slopes, so the string groove is a V with its bottom at r = 13.5 mm."""
    body_h = 2 * SPOOL_FLANGE_T + SPOOL_CORE_W
    z0 = V3_BODY_Z
    f1 = m.Manifold.cylinder(SPOOL_FLANGE_T, SPOOL_FLANGE_R, SPOOL_FLANGE_R, SEG).translate((0, 0, z0))
    f2 = f1.translate((0, 0, SPOOL_FLANGE_T + SPOOL_CORE_W))
    core = m.Manifold.cylinder(SPOOL_CORE_W, SPOOL_R, SPOOL_R, SEG).translate((0, 0, z0 + SPOOL_FLANGE_T))
    lip = SPOOL_FLANGE_R - SPOOL_R
    c1 = m.Manifold.cylinder(lip, SPOOL_FLANGE_R, SPOOL_R, SEG).translate((0, 0, z0 + SPOOL_FLANGE_T))      # slope above f1
    c2 = m.Manifold.cylinder(lip, SPOOL_R, SPOOL_FLANGE_R, SEG).translate((0, 0, z0 + body_h - SPOOL_FLANGE_T - lip))
    base = m.Manifold.cylinder(z0 + SPLINE_DEPTH, BASE_R, BASE_R, SEG).translate((0, 0, -SPLINE_DEPTH))
    s = f1 + f2 + core + c1 + c2 + base
    top = z0 + body_h
    s -= m.Manifold.cylinder(V3_RECESS[1], V3_RECESS[0], V3_RECESS[0], SEG).translate((0, 0, -SPLINE_DEPTH - 0.01))
    s -= m.Manifold.cylinder(SPLINE_DEPTH + 0.01, spline_d / 2, spline_d / 2, 48).translate((0, 0, -SPLINE_DEPTH - 0.02))
    s -= m.Manifold.cylinder(V3_FLOOR + 0.2, V3_SCREW_D / 2, V3_SCREW_D / 2, 24).translate((0, 0, -0.1))
    s -= m.Manifold.cylinder(top - V3_FLOOR + 1, V3_HEAD_D / 2, V3_HEAD_D / 2, 32).translate((0, 0, V3_FLOOR))
    s -= m.Manifold.cylinder(V3_HEAD_MOUTH[1] + 1, (V3_HEAD_D + V3_HEAD_MOUTH[0]) / 2, (V3_HEAD_D + V3_HEAD_MOUTH[0]) / 2, 32).translate((0, 0, top - V3_HEAD_MOUTH[1]))
    for ang in (0, 180):                       # string anchor holes + rim slot, as before
        a = math.radians(ang)
        s -= m.Manifold.cylinder(top + SPLINE_DEPTH + 2, 0.75, 0.75, 24).translate(
            (math.cos(a) * (SPOOL_R - 2), math.sin(a) * (SPOOL_R - 2), -SPLINE_DEPTH - 1))
    s -= box(SPOOL_R - 2.5, SPOOL_FLANGE_R + 1, -0.6, 0.6, z0 + SPOOL_FLANGE_T, z0 + SPOOL_FLANGE_T + SPOOL_CORE_W)
    return s


def spline_fit_test():
    """Four small hubs with the spline socket in 4.35 / 4.5 / 4.65 / 4.8 mm, marked with 1-4 dots."""
    parts = []
    for k, d in enumerate(SPLINE_TEST_SIZES):
        h = m.Manifold.cylinder(SPLINE_DEPTH + V3_FLOOR + 1.0, 5.5, 5.5, SEG).translate((0, 0, -SPLINE_DEPTH))
        h -= m.Manifold.cylinder(SPLINE_DEPTH + 0.01, d / 2, d / 2, 48).translate((0, 0, -SPLINE_DEPTH - 0.02))
        h -= m.Manifold.cylinder(V3_FLOOR + 2, V3_SCREW_D / 2, V3_SCREW_D / 2, 24).translate((0, 0, -0.1))
        top = V3_FLOOR + 1.0
        for j in range(k + 1):
            a = math.radians(90 * j)
            h -= m.Manifold.cylinder(0.5, 0.7, 0.7, 16).translate((3.6 * math.cos(a), 3.6 * math.sin(a), top - 0.4))
        parts.append(h.translate((14.0 * k, 0, 0)))
    return m.Manifold.batch_boolean(parts, m.OpType.Add)


# ----------------------------------------------------------------- the base
# The base holds the finger standing UP. World frame for the base:
#   X forward (direction the finger curls), Y sideways, Z up.
# local->world for the knuckle: world X = -local z, world Y = local y, world Z = local x.
def local_to_world(part):
    return part.rotate((0.0, -90.0, 0.0))


def base():
    # knuckle column, built in finger-local coords (pin at x = 0)
    col_len = 15.0
    col = slab(body_profile(-C - col_len, -C, chamfer_start=False), -W / 2, W / 2)
    col += joint_distal_end(0.0)
    col -= channels(-C - col_len - 5, 1.0)
    col -= lock_hole(-15.0)                 # elastic lock pin in the base, 15 mm below the knuckle pin
    col -= relief(-C, -1)
    col ^= skin(-C - col_len - 8, 0.0, 1.03, TAPER[0]) + box(-C - col_len - 1, -C - col_len + 3, -W, W, -H, H)
    col_w = local_to_world(col)

    z_ceiling = -C - col_len            # bottom face of the column (world Z)
    flex_x = -FLEX_Z                     # world X of the flexor line
    spool_cx = flex_x - SPOOL_R          # line drops tangent to the spool's front
    roof_t = 4.0
    spool_cz = z_ceiling - roof_t - 5.0 - SPOOL_FLANGE_R   # 5 mm gap under the roof for knots
    wall_face = -16.0                    # servo tabs rest on this face (y), body goes to -y
    wall_t = 3.0
    z_bot = spool_cz - SPOOL_FLANGE_R - 5.0
    plate_t = 4.0

    # servo body long axis along X; shaft SERVO_SHAFT_FROM_END from the front end
    s_x0 = spool_cx - SERVO_SHAFT_FROM_END - SERVO_CLEAR / 2
    s_x1 = s_x0 + SERVO_L + SERVO_CLEAR
    s_cx = (s_x0 + s_x1) / 2
    wall_x0 = min(s_cx - SERVO_TAB_HOLE_SPACING / 2 - 5, spool_cx - SPOOL_FLANGE_R - 7)
    wall_x1 = s_cx + SERVO_TAB_SPAN / 2 + 5.5

    # roof that ties the column to the servo wall
    roof = box(min(wall_x0, -H / 2), max(wall_x1, H / 2), wall_face - wall_t, W / 2, z_ceiling - roof_t, z_ceiling + 0.01)
    wall = box(wall_x0, wall_x1, wall_face - wall_t, wall_face, z_bot, z_ceiling)
    back = box(wall_x0, wall_x0 + 4, wall_face - wall_t, W / 2, z_bot, z_ceiling)   # rear pillar
    front = box(wall_x1 - 4, wall_x1, wall_face - wall_t, W / 2, z_bot, z_ceiling)  # front pillar (roof becomes a bridge)
    plate = box(wall_x0 - 6, wall_x1 + 6, wall_face - 26, W / 2 + 8, z_bot, z_bot + plate_t)
    b = col_w + roof + wall + back + front + plate

    # servo body cut-out through the wall
    b -= box(s_x0, s_x1, wall_face - wall_t - 1, wall_face + 1,
             spool_cz - (SERVO_W + SERVO_CLEAR) / 2, spool_cz + (SERVO_W + SERVO_CLEAR) / 2)
    # pilot holes for the servo's self-tapping screws
    for hx in (s_cx - SERVO_TAB_HOLE_SPACING / 2, s_cx + SERVO_TAB_HOLE_SPACING / 2):
        b -= rod_y(1.8, hx, spool_cz, wall_face - wall_t - 1, wall_face + 1)
    # channels continue through the roof, and a bigger clearance hole for the flexor
    for (cx, cy, dd) in ((flex_x, 0.0, CHANNEL_D), (-EXT_Z, 0.0, EXT_D)):
        b -= m.Manifold.cylinder(30, dd / 2, dd / 2, SEG).translate((cx, cy, z_ceiling - 20))
    # 4 mounting holes in the plate (screw or zip-tie it to a board)
    px0, px1 = wall_x0 - 2, wall_x1 + 2
    py0, py1 = wall_face - 22, W / 2 + 4
    for hx in (px0, px1):
        for hy in (py0, py1):
            b -= m.Manifold.cylinder(10, 1.7, 1.7, 32).translate((hx, hy, z_bot - 1))
    info = dict(spool_center_xz=(spool_cx, spool_cz), z_bottom=z_bot, wall_face=wall_face, wall_x=(wall_x0, wall_x1))
    return b, info


# ------------------------------------------------------------- joint checks
def joint_range():
    """2-D check of how far one phalanx (B) can bend relative to the previous (A)."""
    a_body = body_profile(-40, -C)
    b_body = body_profile(C, 40)
    layers = {
        "centre": (a_body, b_body + tongue_profile() + ear_profile()),
        "side": (a_body + prong_profile(), b_body + ear_profile()),
    }

    def collides(deg):
        for a, b in layers.values():
            rb = b.translate((0, -ZP)).rotate(deg).translate((0, ZP))
            if (a ^ rb).area() > 0.05:
                return True
        return False

    assert not collides(0), "parts overlap when straight"
    flex = next(d for d in range(0, 181) if collides(-d)) - 1    # curling toward palm (-z)
    hyper = next(d for d in range(0, 181) if collides(d)) - 1
    return flex, hyper


def joint_check_3d():
    """Rotate each real (skinned) bone about its pin and measure any overlap with the previous one."""
    pairs = [(phalanx(L_PROX), phalanx(L_MID, which="mid"), L_PROX),
             (phalanx(L_MID, which="mid"), phalanx(L_DIST, distal=True), L_MID)]
    worst = 0.0
    for a, b, la in pairs:
        for deg in (-3, 0, 20, 40, 60, 80, 85):
            rb = b.translate((0, 0, -ZP)).rotate((0.0, float(deg), 0.0)).translate((la, 0, ZP))
            worst = max(worst, (a ^ rb).volume())
    return f"max overlap {worst:.2f} mm3 over -3..85 deg"


def save(part, name, flip_top_down=False, rot=None):
    if rot is not None:
        part = part.rotate(rot)
    if flip_top_down:
        part = part.rotate((180.0, 0.0, 0.0))
    lo = np.array(part.bounding_box()[:3])
    part = part.translate(tuple(-lo))
    mesh = part.to_mesh()
    tm = trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3], faces=np.asarray(mesh.tri_verts))
    assert tm.is_watertight, f"{name} is not watertight"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl", name)
    tm.export(out)
    ext = tm.extents
    print(f"  {name:<22} {ext[0]:6.1f} x {ext[1]:6.1f} x {ext[2]:6.1f} mm   {tm.volume / 1000:5.1f} cm3")


def main():
    flex, hyper = joint_range()
    print(f"Joint range: {flex} deg curl, {hyper} deg hyper-extension (stop)")
    assert flex >= 70, "joint can't curl far enough - check parameters"
    print("Writing STLs:")
    # phalanges print lying on their BACK (top face on the bed) - no supports needed
    save(phalanx(L_PROX), "finger_proximal.stl", flip_top_down=True)
    save(phalanx(L_MID, which="mid"), "finger_middle.stl", flip_top_down=True)
    save(phalanx(L_DIST, distal=True), "finger_distal.stl", flip_top_down=True)
    print("3-D joint check (real parts, rotated):", joint_check_3d())
    save(spool(), "servo_spool.stl")
    save(tip_cap(L_DIST), "tip_cap_index.stl", rot=(0, -90, 0))
    b, info = base()
    save(b, "finger_base.stl")
    print("Base info:", {k: tuple(round(v, 1) for v in val) if isinstance(val, tuple) else round(val, 1)
                         for k, val in info.items()})


if __name__ == "__main__":
    main()
