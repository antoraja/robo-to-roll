# Design lessons: flaws found so far, and the rule for the next design

Every problem found in simulation, in the checks, or while building the real prototype is
listed here with its cause, the fix that was applied, and a **rule** so the next design
(wrist, thumb base, rolling station, hand v2) doesn't repeat it.

Status: ✅ fixed in the current files · 🔧 worked around in the build (no reprint) · 📝 fix planned for v2

## Found while building the prototype

| # | Flaw | Cause | Fix / workaround | Rule for the next design |
|---|---|---|---|---|
| B1 | **Elastic lock pins don't grip** the 2 mm cord | Lock hole offset only lets the pin reach 0.57 mm into the 2.6 mm channel, leaving 2.03 mm of room for a 2.0 mm cord, so nothing gets squeezed | 🔧 Elastic knotted at the fingertip and the palm, no lock pins. Simulated: same curl, load and hold-open margins | **Check every clamp numerically:** remaining gap must be **≤ 70 %** of the cord diameter. Add this to the automated checks. Better still, avoid friction clamps where a knot or hook works |
| B2 | **String knot pulls through** the fingertip, even with 4 knots | 0.3 mm braided PE is thin and slippery, and knots stay smaller than the 2 mm hole | 🔧 5 mm filament **toggle** tied to the string. 📝 v2: fingertip socket and flush **tip cap** (plate 6 design) | **Never rely on a knot in braided line against a hole.** Anchor every string around a solid bar (cap, toggle, spool post) |
| B3 | **Knot pocket at the fingertip is almost all open** | Pocket box sat where the tip dome curves away, leaving < 1 mm inside the plastic | 🔧 Toggle sits in the notch. 📝 v2: deeper socket inside the tip | **Check that every pocket or socket is enclosed by material** (measure its volume inside the part, not only the box) |
| B4 | **Thumb lower bone broke** while threading the string | Thin walls around the channels plus force while threading | 🔧 Reprinted with 6 walls / 50 % infill | **Minimum wall 1.2 mm** around every channel/hole. Thread-friendly paths (no sharp steps). Print load-bearing small parts with 6 walls |
| B5 | **Bones got mixed up** between fingers | Bones of different fingers look almost identical (differ by 1–4 mm) | 🔧 Measured with a ruler, annotated photos, pen labels | **Emboss a label** on every part (T1, I2, M3 …) and make lengths differ visibly, or key the joints so only the right bones fit |
| B6 | **Pin lengths were wrong** for the stand and palm (all said 17 mm) | Instructions simplified one length for every pin | ✅ Guide 05: 17 / 26 / 45 mm | **Generate the pin list from the CAD** (hole lengths), never write it by hand |
| B7 | **Coin pockets looked like magnet pockets** | Unlabelled features | — | **Label or explain every non-obvious feature** in the guide and the 3D view |
| B8 | **Videos lag behind design changes** (lock pins, knot + glue, 17 mm pins) | Videos were rendered before later fixes | Text guides updated, videos re-rendered on request | **Re-render the videos as part of every design change** (`video/*/render.js`), or mark outdated steps on screen |
| B9 | **All 10 palm holes blocked** (string and elastic don't go through) | The palm's outer shape was joined to the knuckle forks *after* their holes were cut, so it filled ~6 mm of every hole back in. The checks only looked at the channel walls lower down, never at whether the path is open end to end | ✅ Holes re-cut through each knuckle fork after joining, plus a rounded chamber at each corner. New check slides a ball through every path end to end. 🔧 Printed palm: reprint plate 3 (or drill the plugs) | **Cut holes last**, after every solid is added. **Check every channel end to end with a probe** (open-path test), not only its walls |
| B10 | **Elastic jams in the palm** (string goes through fine) | Each elastic hole runs 14 mm straight down the knuckle, then turns a **sharp 53° corner** (almost no radius) into a 10 mm sloping hole. A pushed 2 mm rubber cord in a 2.6 mm hole hits the wall at the corner. Printed holes also come out ~0.2–0.3 mm small, and rubber grips. The checks only slid an ideal 1.8 mm ball along the centre line, which passes a corner the real cord can't. See [img/elastic_corner.png](img/elastic_corner.png) | ✅ Same palm, only the elastic tunnels changed: 3.4 mm hole, smooth 12 mm-radius curve (6× the cord), funnel at the top, knot still tied on the back. New check runs a 2.3 mm cord along the real path, plus the wall and the knot stop. See [img/elastic_tunnel_fix.png](img/elastic_tunnel_fix.png). Reprint plate 3 | **A cord or string path needs a bend radius ≥ 5× its diameter, or no closed corner at all.** Holes for rubber cord: ≥ 1.0 mm larger than the cord. Checks must model the real item (diameter after print shrink, stiffness), not just an ideal ball. Prefer open slots and knots you can see over hidden tunnels |

## Found in simulation and checks (before printing)

| # | Flaw | Fix | Rule for the next design |
|---|---|---|---|
| S1 | Joints **snapped closed one by one** (single elastic loop, leverage shrinking with bend) | ✅ Elastic runs over a **rounded groove at each knuckle** (constant leverage) | Any return spring must have **constant or increasing** leverage with angle. Check dτ/dθ > 0 in simulation |
| S2 | Finger **fell closed palm-down** (1 mm elastic too weak) | ✅ 2 mm cord stretched 50 % | Simulate **all orientations** (finger up, palm up, palm down) with real part masses |
| S3 | **Not enough string travel** (10 mm spool: 31 mm < 37.5 mm needed) | ✅ 13 mm spool (41 mm in 180°) | Spool travel ≥ **1.1 ×** the simulated string travel, inside the servo's real range (~170°) |
| S4 | **String pinched** between bones at full bend | ✅ Relief groove at each joint face | Check the string path **at every joint angle**, not only straight |
| S5 | **Thumb rubbed the palm** at full bend | ✅ Clearance groove along the thumb's sweep | Collision-check with the **real motion order** (base joint first), not only equal angles |
| S6 | **Thumb over-pulled** (2 joints need ~110°, default was for 3 joints) | ✅ Firmware default 10 → 115° | Derive servo limits **per finger** from the simulation |
| S7 | **Power spike** at switch-on (5 servos start together) | ✅ Servos start 250 ms apart | Stagger servo start-up. Size the supply for **all servos moving at once** |
| S8 | **Servo straining at the end stop** | ✅ Calibrate closedAngle a few degrees before the stop | Calibration procedure must stop **before** mechanical limits |
| S9 | **Top servo lead too short** for the breadboard (20 cm leads) | ✅ 20 cm jumpers bridge it | Check every cable length with the **actual purchased part's** spec |
| S10 | **ESP32 wiring with loose female jumpers** | ✅ ESP32 plugged into the breadboard, male-male only | Prefer plug-in boards over flying wires. Fewer connector types |
| S11 | **Spine could be mounted back to front** | ✅ FRONT dot on the spine | **Asymmetric parts need a visible orientation mark** (or a shape that only fits one way) |
| S12 | **Spine needed a 56 mm support bridge** (ribs both sides) | ✅ Ribs on the back only, flat face on the bed | Run the **overhang analysis on every part in print orientation**, before export |
| S13 | **Stand had an overhanging rounded bottom edge** | ✅ Straight walls, corners rounded in plan only | Same: no rounding on bed-side edges |
| S14 | **Palm needed extra support** at the wrist corners | ✅ Vertical wrist corners | Same |

## Checklist for the next design (wrist, thumb base, rolling station, v2)

- [ ] Every clamp / pinch: remaining gap ≤ 70 % of the clamped item (B1)
- [ ] Every string anchored around a solid bar, never a knot against a hole (B2)
- [ ] Every pocket/socket enclosed by material (B3); walls ≥ 1.2 mm around holes (B4)
- [ ] Holes cut after all solids are joined; every channel probed open end to end (B9)
- [ ] Cord/string paths: bend radius ≥ 5× diameter, rubber-cord holes ≥ cord + 1 mm, no hidden sharp corners (B10)
- [ ] Parts labelled and impossible to mix up or mount backwards (B5, S11)
- [ ] Pin and screw lists generated from the CAD (B6)
- [ ] Springs: leverage constant or increasing with angle; all orientations simulated (S1, S2)
- [ ] String travel ≥ 1.1 × needed; string path checked at all angles (S3, S4)
- [ ] Collision check with the real motion order (S5)
- [ ] Servo limits per joint from simulation; staggered start-up; supply sized for all moving (S6–S8)
- [ ] Cable lengths from the purchased parts (S9)
- [ ] Overhang analysis in print orientation; no rounded bed-side edges (S12–S14)
- [ ] Guides **and videos** updated in the same change (B8)
