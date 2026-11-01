# 05 · The five-finger hand on a table stand

Start this **after** the one-finger rig works (guides 03 and 04). Everything here reuses
the same finger bones, string, elastic, spool and firmware.

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

## Parts to print (`cad/stl/hand/`)

| File | Qty | Size (mm) | How to print |
|---|---|---|---|
| `stand.stl` | 1 | 160 × 140 × 33 | flat as exported, **15 % infill** |
| `spine.stl` | 1 | 224 × 62 × 14 | flat as exported. **Place it diagonally** on a 220 mm bed |
| `palm.stl` | 1 | 58 × 89 × 109 | standing on its flat wrist as exported, **15 % infill**, supports *touching build plate* for the thumb boss |
| `servo_spool_x5.stl` | 5 | Ø32 × 8 | flat |
| `thumb_*`, `index_*`, `middle_*`, `ring_*`, `little_*` | 1 each (14 bones) | | flat on their backs, no supports, brim on the small tips |

Use the same settings as guide 03 (4 walls, 0.2 mm layers). Total is about **330 g of PLA**.
The index finger is identical to the one-finger rig, so you can **reuse it**.

## Extra parts to buy (beyond the one-finger kit)

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

1. **Stand:** press 4 coins into the corner pockets (a drop of glue holds them). Put 4 dots
   of hot glue on the underside as non-slip feet.
2. **Servos onto the spine:** push each servo through its window. Tabs go on the side where
   its spool will be, and the **shaft goes at the top** of the window. Fix with the servo's screws.
   Set each servo to its *open* angle (run the firmware once), then fit the horn and **glue the spool**.
3. **Spine into the stand:** slide it into the slot and push 2 filament pins through the
   socket and spine.
4. **Fingers onto the palm:** pin each finger to its knuckle fork (as in guide 03). The
   thumb goes on the angled boss.
5. **Elastic:** for each finger, thread the 2 mm elastic **down** from the tip through the
   back channel. It comes out on the **back of the palm**. Lock the tip bone, stretch 50 % as in
   guide 03, push the lock pins into the bones, then **tie a fat knot** where it leaves the palm.
6. **Strings:** for each finger, thread the braided line from the fingertip down the palm-side
   channel. It comes out of the **underside of the wrist**.
7. **Palm onto the spine:** feed all 5 strings down past the spine, push the palm onto the
   spine's top tab, and pin it with 2 filament pins.
8. Run each string straight down to **its** spool (table above). It leaves the spool on the
   **outer** side. Wrap it once and tie it through the anchor hole with the finger straight and
   the line just tight.

## Wiring five servos

```
5V 3A supply (+) ── breadboard + rail ── all 5 servo RED wires
5V 3A supply (−) ── breadboard − rail ── all 5 servo BROWN wires ── ESP32 GND   (shared ground!)
ESP32 pins 25, 13, 14, 27, 26 ─────────── servo ORANGE wires (thumb, index, middle, ring, little)
1000 µF capacitor across the + and − rails
ESP32 powered from your laptop USB (or a second USB charger)
```

**Never** power 5 servos from the ESP32's VIN pin.

## Firmware

In `firmware/finger_control/finger_control.ino`, delete the one-finger `FINGERS` block and
uncomment the five-finger block. Keep the order. Upload, then:

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
