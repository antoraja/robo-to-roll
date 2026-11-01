"""Physics check of the one-finger rig (MuJoCo + quasi-static friction model).

Two designs are compared:
  v1 "loop"      - one elastic loop runs over all three joints (first design)
  v2 "per_joint" - the elastic is locked into every bone with a filament lock pin,
                   so each joint has its OWN elastic segment (current design)

What is modelled
  * Bone lengths, pin height, string-channel positions, joint limits and the 5 mm
    round tongue the string wraps over: taken from cad/generate_parts.py.
  * Bone masses from the printed volumes (PLA, ~30 % infill).
  * Flexor string = MuJoCo spatial tendon wrapping the tongues.
  * Elastic = spring tendons (rubber cord, linear).
  * Servo = position actuator on the string, limited to the MG90S stall force
    on the 10 mm spool.
  * String friction in the channels: capstan equation, T_out = T_in * e^(-mu*angle),
    applied joint by joint in the quasi-static check (the physics engine itself has
    frictionless tendons).
  * Gravity in three orientations: finger up, palm up (gravity opens the finger),
    palm down (gravity closes the finger).

Run:  pip install mujoco numpy matplotlib manifold3d trimesh
      python finger_sim.py
"""
from __future__ import annotations

import math
import os
import sys

import mujoco
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cad"))
import generate_parts as gp  # noqa: E402

OUT = os.path.join(HERE, "results")
mm = 1e-3
G = 9.81

# ---------------------------------------------------------------- inputs
L = [gp.L_PROX * mm, gp.L_MID * mm, gp.L_DIST * mm]
C = gp.C * mm
FLEX_X = -(gp.FLEX_Z - gp.ZP) * mm     # string runs this far in front of the pins (palm side)
EXT_X = -(gp.EXT_Z - gp.ZP) * mm       # elastic runs this far behind the pins (negative = back)
EXT_X_V1 = -(4.5 - gp.ZP) * mm         # first design had the elastic 3.5 mm behind the pins
WRAP_R = gp.R * mm
JOINT_MAX, JOINT_MIN = 85.0, -3.0
LOCK_X = [l / 2 for l in L]            # lock-pin position in each bone (v2), from that bone's pin
BASE_LOCK = 0.015                      # lock pin in the base column, 15 mm below the knuckle pin
EXIT = C + 0.8 * mm                    # string leaves each bone on the 45-degree chamfer, ~0.8 mm past the face

PLA_DENSITY = 1240 * 0.6
VOLUMES_CM3 = [8.8, 5.3, 3.4]           # printed volumes from generate_parts.py (finger-shaped bones)

SERVO_STALL_NM = 0.216                 # MG90S, 4.8 V
SPOOL_R = gp.SPOOL_R * mm
SERVO_MAX_DEG = 180.0
F_STALL = SERVO_STALL_NM / SPOOL_R
F_COMFORT = 0.5 * F_STALL

MU = 0.25                              # braided PE line on printed PLA (0.15 - 0.35 tested)

# Elastic cord: tension = EA * strain. Rubber E ~1.5 MPa.
def cord_EA(d_mm):
    return 1.5e6 * math.pi * (d_mm * mm) ** 2 / 4

V1 = dict(mode="loop", cord=1.0, pre=0.5, ext_x=EXT_X_V1)        # first design
V2 = dict(mode="per_joint", cord=2.0, pre=[1.3, 1.3, 1.3], ext_x=EXT_X)   # N per strand, same for every joint

# v3: one elastic strand in the middle of the back, wrapping over a rounded groove in each
# knuckle (constant leverage), locked in every bone
KNUCKLE_R = (gp.EXT_Z - gp.ZP) * mm      # cord centre runs on this radius around the pin
V3 = dict(mode="knuckle", cord=2.0, pre=[2.4, 2.4, 2.4], ext_x=EXT_X)   # CURRENT design: 2 mm cord stretched ~50%

GRAVITY = {"finger up": (0, 0, -G), "palm up": (-G, 0, 0), "palm down": (G, 0, 0)}


# ---------------------------------------------------------------- model
def build(design, gravity=(0, 0, -G), obstacle=None):
    ext_x = design["ext_x"]
    EA = cord_EA(design["cord"])
    masses = [v * 1e-6 * PLA_DENSITY for v in VOLUMES_CM3]
    W, H = gp.W * mm / 2, gp.H * mm / 2

    def bone(i, last=False):
        z0, z1 = C, (L[i] if last else L[i] - C)
        return f"""
        <joint name="j{i}" type="hinge" axis="0 1 0" range="{JOINT_MIN} {JOINT_MAX}" limited="true"
               damping="0.003" armature="1e-6"/>
        <geom type="box" size="{H} {W} {(z1 - z0) / 2}" pos="0 0 {(z0 + z1) / 2}" mass="{masses[i]}"/>
        <site name="f{i}a" pos="{FLEX_X} 0 {EXIT}"/><site name="f{i}b" pos="{FLEX_X} 0 {L[i] if last else L[i] - EXIT}"/>
        <site name="e{i}a" pos="{ext_x} 0 {z0}"/><site name="e{i}b" pos="{ext_x} 0 {z1}"/>
        <site name="lock{i}" pos="{ext_x} 0 {LOCK_X[i]}"/>
        <geom name="knuckle{i}" type="cylinder" size="{KNUCKLE_R} 0.003" euler="90 0 0" contype="0" conaffinity="0"/>
        <site name="kside{i}" pos="{ext_x - 0.003} 0 0"/>
        {'<site name="tip" pos="0 0 %f"/>' % L[i] if last else ''}"""

    obstacle_xml = ""
    if obstacle:
        ox, oz, r = obstacle
        obstacle_xml = (f'<body pos="{ox} 0 {oz}"><geom name="obj" type="cylinder" size="{r} 0.03" '
                        f'euler="90 0 0" friction="0.6"/></body>')

    if design["mode"] == "loop":
        k = 2 * (2 * EA / 0.240)            # 240 mm loop, two strands acting
        tendons = (f'<spatial name="el" stiffness="{k}" springlength="SL0"><site site="eb0"/><site site="eb"/>'
                   + "".join(f'<site site="e{i}a"/><site site="e{i}b"/>' for i in range(len(L))) + "</spatial>")
        springs = [("el", k, 2 * design["pre"])]
    elif design["mode"] == "knuckle":
        tendons, springs = "", []
        for j in range(len(L)):
            a = "lockb" if j == 0 else f"lock{j - 1}"
            seg_len = (BASE_LOCK + LOCK_X[0]) if j == 0 else (L[j - 1] - LOCK_X[j - 1] + LOCK_X[j])
            k = EA / seg_len                       # one strand
            tendons += (f'<spatial name="el{j}" stiffness="{k}" springlength="SL{j}"><site site="{a}"/>'
                        f'<geom geom="knuckle{j}" sidesite="kside{j}"/><site site="lock{j}"/></spatial>')
            springs.append((f"el{j}", k, design["pre"][j]))
    else:
        segs = [None] * len(L)
        tendons, springs = "", []
        for j, _ in enumerate(segs):
            pts = ["lockb", "eb", "e0a", "lock0"] if j == 0 else [f"lock{j - 1}", f"e{j - 1}b", f"e{j}a", f"lock{j}"]
            seg_len = (BASE_LOCK + LOCK_X[0]) if j == 0 else (L[j - 1] - LOCK_X[j - 1] + LOCK_X[j])
            k = 2 * EA / seg_len               # two strands (both back channels)
            tendons += (f'<spatial name="el{j}" stiffness="{k}" springlength="SL{j}">'
                        + "".join(f'<site site="{p}"/>' for p in pts) + "</spatial>")
            springs.append((f"el{j}", k, 2 * design["pre"][j]))

    nb = len(L)
    chain = ""
    for i in range(nb - 1, -1, -1):
        pos = "" if i == 0 else f' pos="0 0 {L[i - 1]}"'
        chain = f'<body name="b{i}"{pos}>{bone(i, i == nb - 1)}{chain}</body>'
    flex_sites = "".join(f'<site site="f{i}a"/><site site="f{i}b"/>' for i in range(nb))
    xml = f"""
<mujoco>
  <option timestep="0.0005" gravity="{gravity[0]} {gravity[1]} {gravity[2]}" integrator="implicitfast"/>
  <worldbody>
    <site name="spool" pos="{FLEX_X} 0 -0.040"/><site name="fbase" pos="{FLEX_X} 0 {-EXIT}"/>
    <site name="eb0" pos="{ext_x} 0 -0.040"/><site name="lockb" pos="{ext_x} 0 {-BASE_LOCK}"/>
    <site name="eb" pos="{ext_x} 0 {-C}"/>
    {obstacle_xml}
    {chain}
  </worldbody>
  <tendon>
    <spatial name="flexor"><site site="spool"/><site site="fbase"/>
      {flex_sites}</spatial>
    {tendons}
  </tendon>
  <actuator>
    <position name="servo" tendon="flexor" kp="4000" kv="20" forcelimited="true" forcerange="{-F_STALL} 0"/>
  </actuator>
</mujoco>"""
    # set spring rest lengths so each elastic has its pretension when the finger is straight
    probe = mujoco.MjModel.from_xml_string(_fill(xml, {n: 0.0 for n, _, _ in springs}))
    d = mujoco.MjData(probe)
    mujoco.mj_forward(probe, d)
    rest = {n: d.ten_length[probe.tendon(n).id] - pre / k for n, k, pre in springs}
    return mujoco.MjModel.from_xml_string(_fill(xml, rest))


def _fill(xml, rest):
    for i, (n, v) in enumerate(rest.items()):
        key = "SL0" if n == "el" else f"SL{n[-1]}"
        xml = xml.replace(f'springlength="{key}"', f'springlength="{v}"')
    return xml


# ---------------------------------------------------------------- tests
def free_sweep(design, gravity=(0, 0, -G), n=37):
    """Turn the servo 0..180 deg slowly; record how the joints actually move (frictionless)."""
    m = build(design, gravity)
    d = mujoco.MjData(m)
    mujoco.mj_forward(m, d)
    L0 = d.ten_length[m.tendon("flexor").id]
    rows = []
    for deg in np.linspace(0, SERVO_MAX_DEG, n):
        d.ctrl[0] = L0 + 0.5 * mm - math.radians(deg) * SPOOL_R   # calibrated "open" = string just slack
        for _ in range(6000):
            mujoco.mj_step(m, d)
        rows.append(dict(servo=deg, q=np.degrees(d.qpos[:len(L)]).copy(), tension=-d.actuator_force[0],
                         tip=d.site("tip").xpos.copy() / mm))
    return rows


def static_requirement(design, gravity, mu=MU, curl_deg=None):
    """Servo string tension needed to HOLD the finger at a given curl, with channel friction.

    For each pose (all joints at the same angle) MuJoCo gives the torque each joint needs
    (elastic + gravity) and the string's lever arm at each joint. Friction reduces the
    tension the further the string travels from the servo (capstan), so the servo must
    supply enough for the worst joint."""
    m = build(design, gravity)
    d = mujoco.MjData(m)
    fid = m.tendon("flexor").id
    out = []
    for th in (curl_deg if curl_deg is not None else np.linspace(0, 85, 18)):
        d.qpos[:len(L)] = math.radians(th)
        d.qvel[:] = 0
        mujoco.mj_forward(m, d)
        tau = d.qfrc_bias[:len(L)] - d.qfrc_passive[:len(L)]        # torque the string must provide at each joint
        arm = np.zeros(3)                                   # string lever arm = -dLength/dAngle
        base_q = d.qpos[:len(L)].copy()
        for j in range(len(L)):
            for sgn in (1, -1):
                d.qpos[:len(L)] = base_q
                d.qpos[j] += sgn * 1e-4
                mujoco.mj_kinematics(m, d)
                mujoco.mj_tendon(m, d)
                arm[j] -= sgn * d.ten_length[fid] / 2e-4
        d.qpos[:len(L)] = base_q
        mujoco.mj_forward(m, d)
        need = []
        wrap = 0.0
        for j in range(len(L)):
            wrap += math.radians(th)                      # string turns by the joint angle at each joint
            t_joint = max(tau[j], 0) / max(arm[j], 1e-6)  # tension needed AT that joint
            need.append(t_joint * math.exp(mu * wrap))    # ...so this much at the servo
        out.append(dict(curl=th, servo_tension=max(need), per_joint=need, arm_mm=arm / mm,
                        tau_mNm=tau * 1e3, pull_mm=None))
    # string travel for each pose (from geometry)
    d.qpos[:len(L)] = 0
    mujoco.mj_forward(m, d)
    l0 = d.ten_length[fid]
    for r in out:
        d.qpos[:len(L)] = math.radians(r["curl"])
        mujoco.mj_forward(m, d)
        r["pull_mm"] = (l0 - d.ten_length[fid]) / mm
    return out


def holds_open(design, gravity):
    """With the servo relaxed, does the elastic keep the finger straight against gravity?"""
    m = build(design, gravity)
    d = mujoco.MjData(m)
    d.qpos[:len(L)] = 0
    mujoco.mj_forward(m, d)
    margin = (d.qfrc_passive[:len(L)] - d.qfrc_bias[:len(L)])       # >0: elastic beats gravity at that joint
    # joint torque sign: positive = flexion. The elastic pushes negative (opening); gravity in
    # "palm down" pushes positive. Margin = opening torque - closing torque.
    return -margin * 1e3                                    # mN*m per joint (positive = stays open)


def grip_test(design):
    m = build(design, obstacle=(0.040, 0.045, 0.012))
    d = mujoco.MjData(m)
    mujoco.mj_forward(m, d)
    L0 = d.ten_length[m.tendon("flexor").id]
    obj = m.geom("obj").id
    res = []
    for deg in (60, 90, 120, 150, 180):
        d.ctrl[0] = L0 - math.radians(deg) * SPOOL_R
        for _ in range(8000):
            mujoco.mj_step(m, d)
        f6, force = np.zeros(6), 0.0
        for i in range(d.ncon):
            c = d.contact[i]
            if obj in (c.geom1, c.geom2):
                mujoco.mj_contactForce(m, d, i, f6)
                force += abs(f6[0])
        wrap = math.radians(max(np.degrees(d.qpos[:len(L)]).sum(), 0))
        res.append(dict(servo=deg, squeeze=force * math.exp(-MU * wrap), squeeze_frictionless=force,
                        q=np.degrees(d.qpos[:len(L)]).copy()))
    return res


def structural(t):
    pin_area = math.pi * (1.75e-3) ** 2 / 4
    load = 2 * t
    return dict(load=load, shear=load / (2 * pin_area) / 1e6, bearing=load / (1.75e-3 * 6e-3) / 1e6)


# ---------------------------------------------------------------- report
def spread(q):
    return float(np.max(q) - np.min(q))


def report():
    os.makedirs(OUT, exist_ok=True)
    print(f"Servo: MG90S {SERVO_STALL_NM} N*m on a {SPOOL_R / mm:.0f} mm spool -> {F_STALL:.1f} N stall, "
          f"{F_COMFORT:.1f} N comfortable (50%)\n")
    summary = {}
    sweeps = {}
    for name, design in (("v1 single loop", V1), ("v2 per-joint", V2), ("v3 knuckle", V3)):
        print(f"=== {name} ===")
        rows = free_sweep(design)
        sweeps[name] = rows
        print("  A) servo sweep, finger upright (how the joints actually move):")
        for r in rows[::6]:
            q = r["q"]
            print(f"     servo {r['servo']:5.0f}°  joints {q[0]:5.1f} {q[1]:5.1f} {q[2]:5.1f}°")
        worst_spread = max(spread(r["q"]) for r in rows[1:-1])
        print(f"     -> largest difference between joints during the sweep: {worst_spread:.0f}°")
        print("  B) holding still with the servo relaxed (elastic vs gravity), margin per joint, mN*m:")
        for g, vec in GRAVITY.items():
            mg = holds_open(design, vec)
            ok = "stays open" if mg.min() > 0 else "FALLS CLOSED"
            print(f"     {g:<10} {mg[0]:6.1f} {mg[1]:6.1f} {mg[2]:6.1f}   {ok}")
        print(f"  C) servo string tension needed to curl fully (friction mu={MU}):")
        worst = 0
        for g, vec in GRAVITY.items():
            req = static_requirement(design, vec)
            peak = max(r["servo_tension"] for r in req)
            worst = max(worst, peak)
            print(f"     {g:<10} peak {peak:5.2f} N = {peak / F_STALL * 100:3.0f}% of stall; "
                  f"string travel {req[-1]['pull_mm']:.1f} mm = {math.degrees(req[-1]['pull_mm'] * mm / SPOOL_R):.0f}° of servo")
        summary[name] = dict(spread=worst_spread, peak=worst)
        print()

    print("=== v3 sensitivity: string friction mu 0.15 / 0.25 / 0.35 (worst orientation) ===")
    for mu in (0.15, 0.25, 0.35):
        peak = max(max(r["servo_tension"] for r in static_requirement(V3, v, mu)) for v in GRAVITY.values())
        print(f"   mu={mu:.2f}: peak {peak:5.2f} N = {peak / F_STALL * 100:3.0f}% of stall")
    print()

    print("=== v3 grip: closing on a fixed 24 mm bar in front of the finger ===")
    for g in grip_test(V3):
        print(f"   servo {g['servo']:3.0f}°: squeeze ~{g['squeeze']:.1f} N with friction "
              f"({g['squeeze_frictionless']:.1f} N frictionless), joints {g['q'].round(0)}")
    s = structural(F_STALL)
    print(f"\n=== strength at full stall ({F_STALL:.1f} N on the string) ===\n"
          f"   joint load {s['load']:.0f} N; 1.75 mm filament pin shear {s['shear']:.1f} MPa vs PLA ~30 "
          f"(x{30 / s['shear']:.1f}); tongue bearing {s['bearing']:.1f} MPa vs ~40 (x{40 / s['bearing']:.1f})")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.3))
    for k, (name, rows) in enumerate((n, sweeps[n]) for n in ("v1 single loop", "v3 knuckle")):
        deg = [r["servo"] for r in rows]
        for j, (lab, c) in enumerate((("base joint", "C0"), ("middle", "C1"), ("tip", "C2"))):
            ax[k].plot(deg, [r["q"][j] for r in rows], c=c, label=lab)
        ax[k].set(title=f"{name}: joint angles", xlabel="servo turn (deg)", ylabel="joint angle (deg)", ylim=(-10, 95))
        ax[k].grid(alpha=.3); ax[k].legend()
    for g, vec in GRAVITY.items():
        req = static_requirement(V3, vec)
        ax[2].plot([r["curl"] for r in req], [r["servo_tension"] for r in req], label=f"v3, {g}")
    ax[2].axhline(F_STALL, c="red", label="servo stall"); ax[2].axhline(F_COMFORT, c="orange", ls=":", label="50% stall")
    ax[2].set(title="v3: servo load to hold a curl", xlabel="curl per joint (deg)", ylabel="string tension at servo (N)")
    ax[2].grid(alpha=.3); ax[2].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "finger_sim.png"), dpi=90)
    print("\nPlot: sim/results/finger_sim.png")
    return summary


def other_fingers():
    """Re-run the key checks for every finger length of the full hand (thumb = 2 joints)."""
    global L, LOCK_X, VOLUMES_CM3
    saved = (L, LOCK_X, VOLUMES_CM3)
    print("\n=== every finger of the full hand (v3 design, palm friction x1.2 included) ===")
    hand = {"thumb": [40, 30], "index": [45, 30, 25], "middle": [49, 33, 26], "ring": [46, 31, 25], "little": [37, 25, 22]}
    base = [8.8, 5.3, 3.4]
    worst = 0.0
    for name, lens in hand.items():
        L = [x * mm for x in lens]
        LOCK_X = [l / 2 for l in L]
        VOLUMES_CM3 = ([base[0] * lens[0] / 45, base[2] * lens[1] / 25] if len(lens) == 2
                       else [v * l / b for v, l, b in zip(base, lens, [45, 30, 25])])
        q = free_sweep(V3, n=13)[-1]["q"]
        peak = max(max(r["servo_tension"] for r in static_requirement(V3, g)) for g in GRAVITY.values()) * 1.2
        hold = min(holds_open(V3, g).min() for g in GRAVITY.values())
        travel = static_requirement(V3, GRAVITY["finger up"])[-1]["pull_mm"]
        worst = max(worst, peak / F_STALL)
        ok = q.min() > 80 and hold > 0 and peak < F_COMFORT
        print(f"   {name:<7} closes to {np.round(q).astype(int)} deg; string {travel:4.1f} mm = "
              f"{math.degrees(travel * mm / SPOOL_R):3.0f} deg servo; servo load {peak / F_STALL * 100:3.0f} % of stall; "
              f"holds open (margin {hold:4.1f} mN*m)  {'PASS' if ok else 'CHECK'}")
    L, LOCK_X, VOLUMES_CM3 = saved
    return worst


if __name__ == "__main__":
    report()
    other_fingers()
