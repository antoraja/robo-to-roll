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
        # small recess for the flexor knot
        part -= box(length - 2.0, length + 1, -2.0, 2.0, FLEX_Z - 1.5, FLEX_Z + 1.5)
        return part
    prof = body_profile(C, length - C)
    part = slab(prof, -W / 2, W / 2) + joint_proximal_end(0) + joint_distal_end(length)
    part -= channels(-10, length + 10)
    part -= lock_hole(length / 2)
    part -= relief(C, +1) + relief(length - C, -1)
    return part ^ skin(0.0, length, s0, s1)


def spool():
    core = m.Manifold.cylinder(SPOOL_CORE_W, SPOOL_R, SPOOL_R, SEG).translate((0, 0, SPOOL_FLANGE_T))
    f1 = m.Manifold.cylinder(SPOOL_FLANGE_T, SPOOL_FLANGE_R, SPOOL_FLANGE_R, SEG)
    f2 = f1.translate((0, 0, SPOOL_FLANGE_T + SPOOL_CORE_W))
    s = core + f1 + f2
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


def save(part, name, flip_top_down=False):
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
    b, info = base()
    save(b, "finger_base.stl")
    print("Base info:", {k: tuple(round(v, 1) for v in val) if isinstance(val, tuple) else round(val, 1)
                         for k, val in info.items()})


if __name__ == "__main__":
    main()
