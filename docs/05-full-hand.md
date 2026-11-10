# 05 · The five-finger hand on a table stand

Start this after the **fit test** (guide 03: index finger bones) and the **electronics
test** (guide 04: one servo moved from your phone). Assemble each finger as in guide 03.

The full hand stands upright on its own printed stand, so you can test it on a table.
**3D view:** run `cad/hand.py --export` and open the RoboHand Five-Finger Hand viewer
(link in the project chat).

```
        fingers (tested bones, 4 lengths) + 2-joint thumb
                        |
                      PALM  (one print, internal string channels)
                        |  <- 2 filament pins
                      SPINE (flat plate, 5 servos: 3 in front, 2 behind)
                        |  <- 2 filament pins
                      STAND (base plate: coin pockets, breadboard tray, ESP32 slots)
```

## What was checked in software (`python cad/hand.py`)

| Check | Result |
|---|---|
| Fingers fully curled vs palm and each other | no contact |
| Thumb vs palm | clear up to ~80°. Calibrate the thumb to stop there |
| Servos / spools / strings vs each other, spine, stand | no contact. Every string has a straight path to the wrist |
| String channels in the palm | fully enclosed. The extra bends add at most 20 % friction |
| Physics, longest (middle) and shortest (little) fingers | both close fully. Servo needs ≤ 44 % of stall including palm friction |
| Stability | ~380 g, centre of mass 17 cm up. It only tips past **22°**. A push of ~60 g at the fingertips tips it sideways, so add coins or clamp it for rough testing |

## Parts to print

**Easiest:** open the 5 ready-made plates in `cad/plates/` in your slicer. Every part is
already oriented and laid out for a 256 × 256 mm bed (Bambu P1S, settings in [03b](03b-bambu-p1s.md)):

| Plate | Contents | Notes |
|---|---|---|
| `plate_1_fit_test.3mf` | index finger (3 bones) + 5 spools | print first = fit test |
| `plate_2_fingers.3mf` | thumb, middle, ring, little (11 bones) | brim on |
| `plate_3_palm.3mf` | palm | 15 % infill, supports touching build plate |
| `plate_4_spine.3mf` | servo spine (diagonal) | |
| `plate_5_stand.3mf` | stand | 15 % infill |

Single parts are also in `cad/stl/hand/`:

| File | Qty | Size (mm) | How to print |
|---|---|---|---|
| `stand.stl` | 1 | 160 × 140 × 33 | flat as exported, **15 % infill** |
| `spine.stl` | 1 | 224 × 62 × 12 | flat front face on the bed, ribs up, no supports |
| `palm.stl` | 1 | 58 × 89 × 109 | standing on its flat wrist as exported, **15 % infill**, supports *touching build plate* for the thumb boss |
| `servo_spool_x5.stl` | 5 | Ø32 × 8 | flat |
| `thumb_*`, `index_*`, `middle_*`, `ring_*`, `little_*` | 1 each (14 bones) | | flat on their backs, no supports, brim on the small tips |

Use the same settings as guide 03 (4 walls, 0.2 mm layers). Total is about **330 g of PLA**.
The fit-test index bones **are** the hand's index finger, so you can reuse them.

## Parts to buy (all in guide 02)

| Item | ≈ Price |
|---|---|
| 4 more MG90S (already in the 6-pack) | — |
| 5 V **3 A** power supply + USB-C/DC screw-terminal adapter | $5–8 |
| 400-point breadboard (fits the tray on the stand) | $1–2 |
| 4 coins or big washers (~26 mm) for the stand pockets | $0 |

No screws are needed. Every joint uses 1.75 mm filament pins.

## Which servo moves which finger

The servos sit on the spine top to bottom. "Front" means the palm side.

| Finger | Servo position | ESP32 pin |
|---|---|---|
| Middle | top, front | 14 |
| Index | 2nd, back | 13 |
| Thumb | 3rd, front | 25 |
| Ring | 4th, back | 27 |
| Little | bottom, front | 26 |

Label each servo cable with tape as you mount it.

## Assembly order

The narrated video `video/assembly/robohand_full_assembly.mp4` shows every step below.

**Pins:** cut them from your own 1.75 mm printer filament (from the PLA spool; not a shopping-list item):

| Pins for | Qty | Length |
|---|---|---|
| Finger joints (bone to bone, finger to palm) | 14 | 17 mm |
| Spine → stand (through the socket) | 2 | 26 mm |
| Palm → spine (through the bottom of the palm) | 2 | 45 mm |

Plus a few spares. Melt both ends flat with a lighter after pushing each pin in.

1. **Fingers** (guide 03): joint pins with melted ends, string anchored at the tip, elastic knotted
   at the fingertip and threaded down the back (no lock pins).
2. **Stand:** 4 coins into the corner pockets (drop of glue), 4 hot-glue dots underneath as feet.
3. **Spine:** the small round **dot** below the top marks the **FRONT** (palm side).
   Push each servo through its window from the spool side: tabs on the spine, **shaft at the
   top** of the window, 2 screws each. Front: 1st (middle), 3rd (thumb), 5th (little).
   Back: 2nd (index), 4th (ring). Label each servo cable.
4. **Spine into the stand**, front dot facing away from the breadboard tray, 2 pins.
5. **Electronics** (guide 04): breadboard in the tray, ESP32 into the breadboard, all 5 servos.
   Upload the firmware and switch on: every servo goes to its open angle.
6. **Spools:** with the power on, press a single-arm horn onto each shaft (centre screw) and
   glue a spool flat onto it. Let it cure 5 minutes. **Unplug the power.**
   Video: [robohand_spool_setup.mp4](../video/spool_setup/robohand_spool_setup.mp4) (also shows step 10).
7. **Fingers onto the palm** (pins go in from above, see [the picture](img/finger_pin_slot.png) and
   [the video](../video/finger_pin/robohand_finger_pin_slots.mp4)):
   push a **17 mm filament pin through the finger's own tab** first (equal ends out both sides). Hold the
   finger straight just above its knuckle, a little towards the back of the hand, and lower it: both pin
   ends slide down the slots in the prongs. At the bottom, nudge the finger towards the palm side: the pin
   drops into its seat. Lightly melt both pin ends. Same for the thumb on the angled boss.
8. **Elastic knots:** each elastic comes out on the back of the palm. Mark two dots 5 cm apart,
   pull until they're 7.5 cm apart (finger straight and firm), then tie a fat knot against the palm.
   Picture guide: [elastic_knot_at_palm.png](../video/palm_knot/elastic_knot_at_palm.png) · video: [robohand_palm_elastic_knots.mp4](../video/palm_knot/robohand_palm_elastic_knots.mp4).
9. **Palm onto the spine:** bundle the 5 strings (they come out under the wrist) with tape,
   feed them down beside the spine, push the palm onto the spine's top tab, 2 pins.
10. **Strings to the spools:** each string runs straight down to its own spool (table above).
    **Power on.** Move that finger's slider to 30 % and back, and watch which way the spool
    turns. **Wrap the string once around the spool in that direction**, pull it just tight with
    the finger straight, and tie it through the anchor hole.

11. **Camera (optional):** slide the camera cover onto the rail on the inside of the palm, see
    [guide 06](06-palm-camera.md).

## Wiring five servos

Same method as guide 04 (ESP32 pushed into the breadboard, male-male jumpers only):

```
5V 3A supply (+) ── + rail (red line)  ── all 5 servo RED wires
5V 3A supply (−) ── − rail (blue line) ── all 5 servo BROWN wires ── jumper from the hole next to ESP32 GND
servo ORANGE wires ── row a, in the free hole next to:  D25 thumb · D13 index · D14 middle · D27 ring · D26 little
1000 µF capacitor across the + and − rails (stripe on −)
hole next to VIN: leave EMPTY
ESP32 powered from your laptop USB (or a USB charger)
```

**Never** power 5 servos from the ESP32's VIN pin.

## Firmware

`firmware/finger_control/finger_control.ino` is already set up for all 5 fingers. Keep the
order of the `FINGERS` list. Upload, then:

- The phone page shows **5 sliders** plus **gesture buttons**: Fist, Point, Peace, Thumbs up, Pinch and Rock on.
- **Calibrate each finger** with `a <n> <angle>` in the Serial Monitor (n = 0 thumb … 4 little),
  then put the numbers into the array. **Stop the thumb at about 80° of bend**, where it would
  start touching the palm.

## If something's off

| Symptom | Fix |
|---|---|
| A finger doesn't close fully | Its string slipped on the spool, or the elastic is too tight. Re-tie, or stretch the elastic less |
| ESP32 resets during "Fist" | All 5 servos start at once and draw too much current. Use the 3 A supply + capacitor. You can also lower `SPEED_DEG_PER_STEP` |
| Hand wobbles | Push the pins fully in, add coins, or clamp the stand's edge to the table |
| Two strings rub inside the palm | Tell me which fingers. I'll re-route the channels |
