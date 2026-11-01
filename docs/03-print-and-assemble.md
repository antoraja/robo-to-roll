# 03 · Print and assemble the one-finger rig

## Parts to print (`cad/stl/`)

| File | Qty | Size (mm) | Notes |
|---|---|---|---|
| `finger_proximal.stl` | 1 | 55 × 16 × 16 | Lower finger bone |
| `finger_middle.stl` | 1 | 40 × 16 × 16 | Middle bone |
| `finger_distal.stl` | 1 | 30 × 16 × 16 | Fingertip |
| `servo_spool.stl` | 1 (print 2, they're tiny) | Ø26 × 8 | Glued onto the servo horn and winds the tendon |
| `finger_base.stl` | 1 | 59 × 58 × 66 | Stand: holds the finger upright and the servo underneath |

All files are **already rotated for printing**. Don't rotate them in the slicer.
The finger bones lie **on their back** (the flat top of the finger is on the bed). That way
there are no overhangs, and the pin holes come out round.

## Slicer settings

| Setting | Value | Why |
|---|---|---|
| Material | PLA (easy) or PETG (tougher) | |
| Layer height | 0.2 mm (0.16 mm for the finger if you want smoother joints) | |
| Walls / perimeters | **4** | Strength around the pin holes |
| Infill | 30 % | |
| Supports | **Off** for the finger bones and spool. Base: off; turn on *"supports touching build plate only"* only if the 37 mm roof bridge sags on your printer | |
| Brim | Optional for the base | |

## Before assembly: test the fit

1. Push a piece of 1.75 mm filament through each **pin hole**.
   - In the **tongue** (centre tab) it should **turn freely**.
   - In the **prongs** (side forks) it should be **snug**.
   - Too tight: twist a 2 mm drill bit through by hand. Too loose: a drop of super glue on
     the prong side only (never on the tongue).
2. Push a piece of filament or a needle through each **tendon channel** to clear any
   strings of plastic: the 1 palm-side channel and the 2 back-side channels.

> If many holes are too tight or too loose, change `PIN_HOLE_PRONG`, `PIN_HOLE_TONGUE` or
> `CHANNEL_D` at the top of `cad/generate_parts.py`, run `python generate_parts.py`, and
> re-print. That's the whole point of a parametric design.

## Assemble the finger

1. Slide the **tongue** of `finger_middle` between the **prongs** of `finger_proximal`.
   The side with the flat lip (the "ear") is the **back** of the finger. Both parts must
   have their backs facing the same way.
2. Push a ~17 mm piece of filament through the holes as the pin. Briefly heat each end with
   the lighter and press it flat with something metal so it forms a little "rivet" head.
3. Repeat for `finger_distal` → `finger_middle`.
4. Repeat for `finger_proximal` → the knuckle on top of `finger_base`. Line the channels up:
   the **single centre (palm-side) channel** of the finger must sit above the **single centre
   hole** in the knuckle, and the two back channels above the two back holes.
5. Check: the finger should **flop forward freely** and **stop when straight**. It should
   not bend backwards.

## Mount the servo (do this after step 3 of the wiring guide, once the servo is at 0°)

1. Push the servo through the rectangular window in the base's side wall **from inside the
   open bay**. The body sticks out the back of the wall, the output shaft points into the
   bay, and the shaft goes at the end of the window **nearer the back pillar**.
   The tabs rest on the wall. Fix them with the 2 screws that came with the servo.
2. Press the **single-arm or cross horn** onto the shaft and fix it with the small centre screw.
3. **Glue the spool** onto the horn with super glue. The flat side goes against the horn,
   centred on the shaft. Let it cure for 5 minutes.

## Thread the tendon (flexor)

1. Cut ~40 cm of braided line.
2. Tie a fat knot (double overhand) at one end. Thread the line **from the fingertip down**
   through the **palm-side channel** (the single channel near the palm, centre). Pull until the
   knot sits in the small recess at the fingertip, then add a drop of super glue on the knot.
3. Continue through the hole in the base roof into the bay. Pass the line through one of the
   spool's small holes via the slot in the rim, and tie it.
4. With the servo at its **open** angle and the finger **straight**, the line should be just
   barely tight, with no slack. Adjust by re-tying or by winding it once around the spool.

## Thread the elastic (extensor / return)

1. Thread the elastic cord **up** one back channel of the base and finger to the fingertip,
   lay it in the small groove on the tip face, and thread it **down** the other back channel.
2. Under the base roof, pull both ends so the finger is held straight with **light** tension,
   and tie them together with a knot bigger than the hole.
3. Too much tension and the servo strains. Too little and the finger won't open fully. You
   want the finger to spring back straight, nothing more.

## How it should behave

- Servo turns toward `closedAngle` → line winds onto the spool → finger curls (up to ~85°
  per joint).
- Servo turns back to `openAngle` → line unwinds → elastic pulls the finger straight.

If the finger curls in the wrong order (the tip first, or the base only), that's normal for
tendon fingers and depends on friction. We can tune it later by changing the elastic
tension or the channel heights in the CAD script.
