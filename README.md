# RoboHand: a wireless, 3D-printed robotic hand (beginner build)

This project is a robotic hand, and later a full arm, whose fingers bend the way real ones
do. **Strings ("tendons") pulled by small motors** do the bending, and you control it
**wirelessly from your phone** (and later by moving your own hand in front of a webcam).

It is designed for someone with a 3D printer and little electronics experience:

- **No soldering.** Every electrical connection is a plug or a screw terminal.
- **Cheap.** The whole five-finger hand on its stand costs about **$35–50** in parts.
- **Straight to the full hand,** with two cheap checks first: one finger's bones for the print
  fit, and one servo wiggled from your phone.
- **End goal:** operate a rolling machine to roll a cigarette (see the roadmap).

## Start here

| What | Where |
|---|---|
| **Build-guide video** (print plates → finished hand, 13 steps, ~3 min) | [`video/robohand_build_guide.mp4`](video/robohand_build_guide.mp4) |
| **Whole arm in 3D** (assembled, coloured; opens in Windows 3D Viewer, Blender or any GLB viewer) | [`cad/assembly/robohand_assembly.glb`](cad/assembly/robohand_assembly.glb) (+ `.stl`) |
| **Print plates**, laid out for a 220 × 220 mm bed (open in PrusaSlicer / Bambu / Orca / Cura) | [`cad/plates/`](cad/plates/): `plate_1_fit_test.3mf` … `plate_5_stand.3mf` |
| **Shopping list with amazon.de links** | [`docs/02b-amazon-de.md`](docs/02b-amazon-de.md) |
| **Design validation** (all checks, what was fixed, pre-build checklist): run `./validate.sh` | [`VALIDATION.md`](VALIDATION.md) |
| Step-by-step build guide (text) | [`docs/05-full-hand.md`](docs/05-full-hand.md) |

## The roadmap

| Step | What you do | Guide |
|---|---|---|
| 0 | Learn the 10 ideas you need (servo, tendon, ESP32, power, ground, connectors) | [01-basics.md](docs/01-basics.md) |
| 1 | Buy the parts for the full hand | [02-shopping-list.md](docs/02-shopping-list.md) |
| 2 | **Fit test:** print the index finger's 3 bones and check the pin holes and channels | [03-print-and-assemble.md](docs/03-print-and-assemble.md) |
| 3 | **Electronics test:** Arduino IDE, wire one servo, move it from your phone | [04-wiring-and-first-test.md](docs/04-wiring-and-first-test.md) |
| 4 | Print and build the **five-finger hand on its table stand**, calibrate, run gestures | [05-full-hand.md](docs/05-full-hand.md) (+ finger assembly in [03](docs/03-print-and-assemble.md)) |
| 5 | **Wrist** (tilt + rotate) and a **movable thumb base** for real pinching | *next design step* |
| 6 | Grip pads + fingertip **pressure sensors** for gentle handling of paper | *later* |
| 7 | **Rolling station:** holder for a rolling machine, tobacco hopper, paper slot, damp sponge; recorded move sequence | *later* |
| 8 | Hand copies your hand through a webcam (MediaPipe → WiFi → ESP32) | *optional* |

## What's in this folder

```
robot-hand/
  docs/                      Step-by-step guides (start with 01-basics.md)
  cad/generate_parts.py      Parametric generator for every printed part (Python)
  cad/render_preview.py      Renders the preview picture + checks parts don't collide
  cad/stl/                   Ready-to-print STL files (already oriented for printing)
  cad/hand.py                Five-finger hand + table stand: printable parts and checks
  cad/stl/hand/              Ready-to-print STLs for the full hand (one file per part)
  cad/plates/                The same parts laid out on 5 print plates (3MF + STL)
  cad/assembly/              Whole arm assembled (GLB coloured, STL)
  cad/export_assembly.py     Regenerates assembly/ and plates/
  video/                     Build-guide video + the script that renders it
  sim/finger_sim.py          Physics simulation (MuJoCo): motion, servo load, grip, strength
  firmware/finger_control/   ESP32 Arduino sketch: WiFi + phone slider + serial commands
```

## Status

- **Shape:** finger-like oval, tapered bones with a domed fingertip, following the style of
  open-source printed hands. They still print flat-backed with no supports.
- **Printable parts:** generated and checked in software. A 3-D test rotates each real
  bone through its whole range to confirm nothing collides. Every part is a closed,
  printable solid, each joint curls about 85° with a 3° stop against bending backwards,
  and the finger, spool and servo don't collide with the base. **They have not been
  test-printed yet**, so expect small fit tweaks after your first print. Print tolerances
  are all at the top of `generate_parts.py`.
- **Simulation:** the finger was checked in the MuJoCo physics engine (see
  [`sim/README.md`](sim/README.md)). That found 4 flaws in the first design: joints snapping,
  the finger falling closed palm-down, not enough string travel, and a pinched string. All 4
  are fixed in the current parts. Result: smooth curl, fully closed at ~165° servo turn,
  ~35 % of the servo's stall force, pins ~4× stronger than needed.
- **Firmware:** written for the ESP32 Arduino core with the ESP32Servo library. **It has
  not been compiled or run on real hardware yet.** Step 3 is where we check it together.
