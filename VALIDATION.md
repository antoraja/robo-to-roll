# Design validation: before you build the prototype

Re-run everything with one command (about 10 minutes):

```bash
./validate.sh
```

It checks, in order: the printable finger parts and joint range → the full hand
(collisions, string routing, stability, assembly details) → physics for every finger
(MuJoCo) → the firmware (compiled and behaviour-tested on the PC). The latest full run
**passed every stage**.

## Results

| Area | Check | Result |
|---|---|---|
| **Joints** | Real 3-D bones rotated −3…85° | ✅ Only contact is the intended −3° stop |
| **Collisions** | Fingers 0 / 45 / 85° vs palm and each other; servos, spools, strings vs spine, palm, stand | ✅ None |
| | Thumb vs palm | ✅ Up to ~80° (1.9 mm³ touch at 85°: firmware default stops the thumb before that) |
| **Palm channels** | String channels fully enclosed | ✅ Walls 96–99 % intact (thin spots only at the ends) |
| | Channels crossing each other | ✅ Closest pair still has 8.9 mm of plastic between them |
| | Pin holes / spine slot vs channels | ✅ 5.5 mm clear / no contact |
| | Elastic channels come out on the back of the palm | ✅ 5 / 5 |
| | Every string and elastic path open end to end (ball slid from knuckle fork to palm exit) | ✅ 10 / 10 (added after the first printed palm had all 10 blocked) |
| **Physics** | All 5 fingers close fully (85° every joint) | ✅ |
| | Servo load incl. palm friction (μ = 0.25) | ✅ 27 % (thumb) to 44 % (little) of MG90S stall |
| | Worse friction (μ = 0.35) | ⚠️ ~55–65 % of stall: works, servos run warmer |
| | Fingers stay open against gravity in every orientation | ✅ Margin 3.9–8.5 mN·m |
| | String travel vs servo range | ✅ Fingers 165° (of 180°), thumb 110° |
| | Grip on a 24 mm bar | ✅ ~5–6 N squeeze per finger |
| **Strength** | Filament pin at full servo stall | ✅ 4.3× safety |
| | Printed tongue bearing | ✅ 12.6× safety |
| **Stability** | Tip-over angle on the table | ✅ 22° (side) – 27° (back). ~60 g sideways push at the fingertips tips it: clamp or weigh it down for rough tests |
| **Firmware** | Compiles with `-Wall -Wextra -Werror` (against stand-in ESP32 headers) | ✅ |
| | 32 behaviour tests: sliders, gestures, bad input, clamping, serial commands | ✅ |

## How the parts fit together (`cad/audit.py`, added after the palm-plug mistake)

Every pin, socket, slot and channel is probed with a solid slightly smaller than the real
item. Any plastic in the way fails the check.

| Check | Result |
|---|---|
| New palm vs the old palm file | ✅ only removes the 10 plugs and adds the camera rail. Knuckle forks identical, so the printed fingers fit as before |
| 5 knuckle forks: finger + pin lowered in along the slot, pin can't lift out, finger swing 0–85°, string path, elastic path | ✅ all open, 0 mm³ in the way |
| Spine tab into the palm, 2 palm pins (45 mm), 2 stand pins (26 mm) | ✅ open through both parts |
| 5 servos in their spine windows, 10 screw holes | ✅ |
| 14 finger bones: string + elastic holes and pin holes | ✅ all open (already printed: confirms they are right) |
| Camera cover: slides on the rail, lock pin, never touched by fingers/thumb at 0–90° | ✅ |
| Every printed part is one solid piece | ✅ |
| Supports: only the palm needs them (tree, from the build plate); everything else prints without | ✅ |

## Printability (Bambu Lab P1S, PLA): see docs/03b-bambu-p1s.md

| Part | Orientation | Supports |
|---|---|---|
| 14 bones, 5 spools | flat back / flat | none (brim on bones) |
| Spine | flat front face down, ribs up | none: was a 56 mm bridge before the ribs moved to the back only |
| Stand | base down | none: straight walls now (was a rounded bottom edge) |
| Palm | on its flat wrist | tree supports from the build plate only (~480 mm² under the knuckles) |

All 5 plates fit the 256 × 256 mm bed. About 290 g of PLA, ~13 h of printing.

## Problems this validation found, and fixed

| Problem | Fix |
|---|---|
| **Servo leads are short.** The ordered MG90S have 20 cm leads, and the top (middle-finger) servo needs ~20.5 cm to reach the breadboard; jumpers must bridge the gap | Use **20 cm** male-male jumpers between each servo plug and the breadboard (tape the joints). The ESP32 plugs straight into the breadboard, so no male-female jumpers are needed |
| **Finger pins couldn't be inserted** (found during the build, flaw B11): forks 1.1–1.6 mm apart, sideways holes printed small | Slot open at the top of each prong, pin seats at the pivot; finger + pin lowered along the slot in the check, can't lift straight out |
| **Elastic jammed at a sharp corner in the palm** (found during the build, flaw B10): 2.6 mm hole with a 53° corner | Same palm, only the elastic tunnels changed: 3.4 mm, smooth 12 mm-radius curve, funnel. Checked with a real 2.3 mm cord along the path, wall all round, knot can't enter |
| **All 10 palm holes blocked** (found during the build): the palm shape was joined to the knuckle forks after their holes were cut, filling ~6 mm of each hole | Holes now cut after joining, with a rounded chamber at each corner; new end-to-end open-path check. Reprint plate 3. See [docs/img/palm_channel_fix.png](docs/img/palm_channel_fix.png) |
| **Elastic lock pins don't grip** (found during the build): the pin only reaches 0.57 mm into the 2.6 mm channel, leaving 2.03 mm for a 2.0 mm cord | Lock pins dropped: the elastic is knotted at the fingertip and at the palm. Simulated: same smooth curl, same 38 % servo load, same hold-open margins |
| **Thumb rubbed the palm** when its base joint bent fully (8.7 mm³ contact) | Clearance groove cut into the palm along the thumb's path: 0 mm³ at every angle |
| **Thumb over-pulled.** The thumb has 2 joints, so it needs only ~110° of servo. The old default would have pushed it against its stop | Firmware default for the thumb is now 10° → 115° |
| **Power spike at switch-on.** All 5 servos jumping at once can pull > 3 A and reset the ESP32 | Firmware now starts the servos one by one (250 ms apart) |
| **Servos straining at the end stop** if calibrated too far | Calibration note: set `closedAngle` a few degrees **before** the finger stops |

## What software cannot guarantee (check these on the real parts)

No simulation makes a design 100 % certain. These are the things only the prototype can
prove. They're also why the fit test comes first.

1. **Hole sizes on your printer.** This is the most likely issue. Fit test = plate 1. Tell me tight/loose and I'll regenerate all parts.
2. **String friction** in printed channels (assumed μ 0.15–0.35). Clean every channel with filament before threading.
3. **Elastic stiffness.** It varies by brand. Set it by feel: firm spring-back, but the servo must not strain.
4. **Servo quality.** Cheap MG90S clones vary in torque and travel (some only reach ~170°, which is fine since we need 165°).
5. **Long-term wear** of filament pins and PLA creep under constant elastic tension. PETG lasts longer if you have it.
6. **Real ESP32 build.** The firmware was compiled against stand-in headers, not the real ESP32 core. The first real upload (guide 04) confirms it.

## Pre-build checklist

- [ ] Plate 1 printed. Pins turn freely in the tongue, snug in the forks. Channels clean.
- [ ] One servo moves from the phone (guide 04) **before** anything is glued.
- [ ] Every servo set to its open angle **before** fitting the horn and gluing the spool.
- [ ] Servo cables labelled (thumb / index / middle / ring / little).
- [ ] Servo plugs joined to male-male jumpers and taped (middle and index leads are the tightest).
- [ ] 1000 µF capacitor across the breadboard rails, **long leg to +**.
- [ ] ESP32 GND connected to the breadboard − rail (shared ground). Hole next to VIN left empty.
- [ ] Servos powered from the 5 V 3 A supply, **never** from the ESP32's VIN pin.
- [ ] Each finger calibrated (`a <finger> <angle>`); `closedAngle` a few degrees before the end stop.
- [ ] Stand weighed down (coins) or clamped before testing fast gestures.
