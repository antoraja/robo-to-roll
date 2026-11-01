# 03 · Print and assemble the one-finger rig

## Parts to print (`cad/stl/`)

| File | Qty | Size (mm) | Notes |
|---|---|---|---|
| `finger_proximal.stl` | 1 | 55 × 16 × 16 | Lower finger bone |
| `finger_middle.stl` | 1 | 40 × 16 × 16 | Middle bone |
| `finger_distal.stl` | 1 | 30 × 16 × 16 | Fingertip |
| `servo_spool.stl` | 1 (print 2, they're small) | Ø32 × 8 | Glued onto the servo horn and winds the tendon |
| `finger_base.stl` | 1 | 62 × 58 × 72 | Stand: holds the finger upright and the servo underneath |

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
| Brim | **Yes for `finger_distal`** (it stands on a small flat strip), optional for the base | |

## How the finger is shaped (and why)

The bones follow the usual approach of open-source printed hands such as InMoov,
Flexy-Hand and e-NABLE:

- **Oval, tapered segments.** Each bone is a smooth oval that gets slightly thinner toward the tip,
  instead of a box. The fingertip is a rounded dome.
- **A flat strip along the back.** That's the side that lies on the print bed. Printed hands keep
  one flat face so they print **without supports**, which saves filament and cleanup time.
- **Mechanics hidden inside.** The pin joints, string and elastic channels are exactly the ones
  checked in the simulation. Only the outer shape changed.
- **Cost:** no extra parts. The rounded bones use **~13 % less plastic** than the box version.

### Cheap ways to make it look and grip more like a hand (optional, later)

| Trick | Cost | Effect |
|---|---|---|
| A blob of **hot glue** on the fingertip pad, pressed flat | ~$0 | Rubbery grip pad |
| A strip of old **bicycle inner tube** glued on the palm side | ~$0 | Grip + skin look |
| Sand with 240-grit, then spray paint (skin tone or matte grey) | $3–5 | Hides layer lines |
| Pull the finger of a **nitrile glove** over it (InMoov-style "skin") | ~$0.10 | Looks like a real hand, grips well. Check the servo still closes it fully |
| Print a fingertip cap in **TPU** (flexible filament) | only if you own TPU | Best grip |

## Before assembly: test the fit

1. Push a piece of 1.75 mm filament through each **pin hole**.
   - In the **tongue** (centre tab) it should **turn freely**.
   - In the **prongs** (side forks) it should be **snug**.
   - Too tight: twist a 2 mm drill bit through by hand. Too loose: a drop of super glue on
     the prong side only (never on the tongue).
2. Push a piece of filament or a needle through both **channels** in every bone to clear any
   strings of plastic: the thin palm-side one (string) and the wider back one (elastic).
   Also clear the small **cross hole** in the middle of each bone. That's the lock-pin hole for
   the elastic. The string must slide freely, because the simulation shows friction is the
   biggest load on the servo.

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
   the **palm-side channel** of the finger must sit above the **palm-side hole** in the knuckle,
   and the back channel above the back hole.
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

## Thread and lock the elastic (return spring)

The elastic runs along the **back** of the finger and over a rounded groove at each knuckle.
It's pinched in every bone by a **lock pin**, so each joint gets its own spring. The
simulation showed this is what makes the joints bend smoothly instead of snapping
(see `sim/README.md`).

1. Cut ~25 cm of **2 mm** round elastic cord. Thread it **down** from the fingertip through the
   back channel of all three bones and the base, until ~5 cm comes out under the base roof.
2. Push a ~17 mm filament **lock pin** through the cross hole of the **fingertip** bone. It
   pinches the cord. Melt the pin ends like the joint pins.
3. With a pen, make two marks on the cord **50 mm apart** just below the base. Pull the cord
   from underneath until the marks are **75 mm apart** (≈50 % stretch, the tension the
   simulation was checked with).
4. Holding that stretch, push lock pins into the **middle** bone, the **lower** bone and the
   **base** cross hole. Trim the spare cord.
5. Test: the finger should **spring back straight firmly**, even with the base held upside
   down. If it's floppy, re-do step 3 with more stretch. If the servo struggles later, use a
   little less.

## How it should behave

- Servo turns toward `closedAngle` → line winds onto the spool → finger curls (up to ~85°
  per joint).
- Servo turns back to `openAngle` → line unwinds → elastic pulls the finger straight.

Expected motion (from the simulation): the **base joint bends first, then the middle, then
the tip**, smoothly, and the finger is fully closed at about **165°** of servo turn. If yours
snaps, sticks or curls tip-first, tell me what you see and I'll re-tune the design.
