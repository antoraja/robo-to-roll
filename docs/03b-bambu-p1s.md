# 03b · Printing on a Bambu Lab P1S (PLA)

The plates in `cad/plates/` are laid out for the P1S's **256 × 256 mm** bed. Every part is
already turned so it prints with **as little support as possible**. Only the palm needs
supports, and only from the build plate.

## What was checked before these plates were made

| Part | Print orientation | Overhang that needs support | Supports |
|---|---|---|---|
| Finger bones (14) | Flat back on the bed | none (arcs ≤ 55°, small bridges) | **off** |
| Spools (5) | Flat | none (45° cone under the top rim) | **off** |
| Spine | Flat front face on the bed, ribs up | none: the ribs are now on the back only, so there's no 56 mm bridge any more | **off** |
| Stand | Base plate down | none: corners rounded only in plan, so the walls are straight | **off** |
| Palm | Standing on its flat wrist | ~480 mm² under the knuckles and thumb pad | **tree, build plate only** |

## Bambu Studio: global setup (once)

1. **Printer:** Bambu Lab P1S, 0.4 mm nozzle. **Plate:** Textured PEI (no glue needed for PLA).
2. **Filament:** Bambu PLA Basic (or *Generic PLA*).
3. **Process:** `0.20mm Standard @BBL X1C` (it's the P1S default as well).
4. Open the plate file: **File → Import → `plate_N_….3mf`**. If it asks *"Load as a single object
   with multiple parts?"*, choose **No**, so the parts stay separate objects. Don't rotate anything.

## Settings per plate

Change only what's listed; everything else stays at the profile default.

| Setting (Process tab) | 1 · fit test | 2 · fingers | 3 · palm | 4 · spine | 5 · stand |
|---|---|---|---|---|---|
| Strength → **Wall loops** | 4 | 4 | 3 | 4 | 3 |
| Strength → **Top / bottom shell layers** | 5 / 4 | 5 / 4 | 4 / 3 | 5 / 4 | 4 / 3 |
| Strength → **Sparse infill density** | 25 % | 25 % | **10 %** | 30 % | **15 %** |
| Strength → **Sparse infill pattern** | Gyroid | Gyroid | Gyroid | Gyroid | Gyroid |
| Support → **Enable support** | off | off | **on** | off | off |
| Support → **Type** | | | **tree(auto)** | | |
| Support → **On build plate only** | | | **✔** | | |
| Support → **Threshold angle** | | | 30° | | |
| Others → **Brim type** | Outer brim only, 3 mm | Outer brim only, 3 mm | Auto | No brim | No brim |

Why these values:
- **4 walls on bones and spine:** the pin holes and servo screw holes sit in solid walls. That's where the strength is needed.
- **10 % infill on the palm:** it's big and lightly loaded. The 10 string/elastic holes, pin holes and spine socket each get their own 3 walls, so the strength is there. Saves ~15 g and some time versus 15 %. The palm's shape can't get much smaller: the 10 channels fan through almost all of it.
- **15 % infill on the stand, and keep it heavy:** the stand's weight is what stops the hand tipping over, so don't lighten it.
- **Support on build plate only:** stops supports from growing inside the string channels.
- **Brim on the bones:** the fingertips stand on a small flat strip, and a 3 mm outer brim keeps them stuck down. Peel it off afterwards.

Leave **X-Y hole compensation at 0**. The hole sizes in the design already include the
clearances. If the fit test shows tight or loose pins, tell me and I'll change the design rather than the slicer.

## Print order and rough times

| Plate | Contents | Approx. PLA | Approx. time (P1S) |
|---|---|---|---|
| 1 · fit test | index finger (3 bones) + 5 spools | ~25 g | ~1 h |
| 2 · fingers | thumb, middle, ring, little (11 bones) | ~45 g | ~2.5 h |
| 3 · palm | palm (+ tree supports) | ~110 g | ~5–6 h |
| 4 · spine | servo spine | ~40 g | ~1.5 h |
| 5 · stand | stand | ~70 g | ~2.5 h |
| 6 · tips and caps | the 5 fingertips (with the cap socket) + 5 tip caps + 2 spare caps | ~12 g | ~1 h |
| 8 · horn fit tests | 2 small discs (2 dots = double-arm horn, 1 dot = single-arm horn), **no supports** | ~3 g | ~15 min |
| 9 · spools, double-arm horn | 5 spools (horn pocket down), **no supports**, 4 walls, 30 % infill | ~25 g | ~1 h |
| 10 · spools, single-arm horn | same, for the single-arm horn. Print **9 or 10**, whichever horn fits better | ~25 g | ~1 h |
| 7 · palm camera | camera cover (standing upright, **no supports**, 3 walls, 20 % infill) | ~6 g | ~40 min |
| **Total** | | **~295 g** | **~13.5 h** |

Bambu Studio shows the exact grams and time after you click **Slice plate**. Use those numbers.

**Print plate 1 first** and do the fit test (guide 03) before printing the others.

## After printing
- Let the plate cool for a minute and flex the PEI sheet. The parts pop off.
- Palm: break the tree supports away with pliers (they come off in big pieces).
- Clean every pin hole and channel with a piece of filament before assembly.
