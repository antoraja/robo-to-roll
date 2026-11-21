# Prototype 1: what we built, what went wrong, and how we work next time

1–21 November 2026. A five-finger, tendon-driven hand on a stand, printed on a Bambu P1S in PLA, moved by five
MG90S servos and an ESP32. Every finger now moves under control from a laptop. This page collects everything we
learned, so prototype 2 (and the rolling-machine station after it) doesn't repeat it.

The full flaw list with causes and fixes is in [DESIGN_LESSONS.md](DESIGN_LESSONS.md) (B = found on the build,
S = found in simulation, E = electronics). This page is the summary and the way of working.

## What prototype 1 is

| Part | State |
|---|---|
| Fingers (4 × 3 bones) and thumb (2 bones) | Printed, pinned with 1.75 mm filament, string anchored with a 5 mm filament toggle |
| Palm | Third print: holes re-cut after joining (B9), smooth 3.4 mm elastic tunnels (B10), pin slots for the fingers (B11), camera rail |
| Spine + stand | Printed. Servos remounted on the correct sides (B15). Breadboard pocket in the stand |
| Spools | v3, no horn: press onto the spline, original centre screw, 29 mm rims (B12–B14) |
| Elastics | 2 mm cord, 50 % pre-stretch (5 → 7.5 cm), knotted on the back of the palm |
| Electronics | ESP32 (VIN-side row in breadboard row j), 5 V 3 A supply, 1000 µF capacitor, 5 servos wired and tested one by one |
| Control | USB page `tools/usb_control.html` (calibration, % sliders, move together, gestures). Phone/WiFi page works in firmware but **this ESP32's radio is too weak** (E4) |

## Open items (carry into the next session)

| Item | Status / next step |
|---|---|
| **Replacement ESP32** (E4) | Order the same type: 30-pin, USB-C, CH340, labels VIN · GND · D13 · D12 · D14 · D27 · D26 · D25 on one side ([amazon.de search](https://www.amazon.de/s?k=ESP32+30+Pin+USB-C+CH340)). Swap it into row j, upload `finger_control.ino`, done |
| **Thumb only bends its first hinge** at 180° (E7) | Not solved yet. Next: pen-mark test (does the string move ~40 mm from 0° to 180°?), check slack at 0°, spool slipping on the shaft, wrap direction, and that the servo is a 180° type, not a 360° continuous one |
| **Calibration of all five fingers** | Open/closed angles to be saved on the USB page, then pasted into `FINGERS[]` and uploaded |
| **Movement smoothness** | Judge after calibration with the % sliders. If still jerky: `SPEED_DEG_PER_STEP` 2.0 → 1.0 |
| **Plugs lying flat** on the breadboard (E6) | Push every plug upright, tape the servo cables to the table, stick the breadboard down once everything works |
| v2 markings (B5, B15) | Emboss part labels and the finger letter next to each servo window |

## The biggest lessons, by area

### 1. Mechanical design
- **Check the path, not only the final position.** Holes, pins, screws, cords, fingers: every one failed at least
  once because the checks looked at the finished assembly, never at how a part *gets there* (B9, B10, B11, B13).
- **Model the real bought part.** The servo horn (B12), the screw head (B13), the ESP32 width (E2), the servo
  neighbour distance (B14) were all assumed instead of measured. A ruler photo or a fit-test print settled each one.
- **Printed holes come out small,** especially near the bed and in upright walls: bought part + 0.5 mm, rubber cord
  + 1 mm, sideways holes in upright prints replaced by slots open upwards.
- **Cut holes last.** Joining a solid after cutting a hole silently fills it back in (B9).
- **Cords need gentle bends:** radius ≥ 5× the cord, no hidden corners (B10).
- **Knots don't hold in braided line against a hole:** use a toggle or a post (B2).
- **Design to be safe if an assumption is wrong** (B14), and **make wrong assembly impossible or at least visible on
  the part** (B15, S11).

### 2. Printing
- A small **fit-test print first** for anything that mates with a bought part (spline test, 4 hubs: the 4-dot one fit).
- Overhang check in print orientation for every part before export; no rounding on bed-side edges (S12–S14).
- Load-bearing small parts with 6 walls (B4).

### 3. Electronics (new this round)
| # | What happened | Rule |
|---|---|---|
| E1 | Firmware default angle would drive fingers into their stops; video showed the wrong power-on order | Re-derive every number when a part changes. **Power: 5 V supply first, then USB. Off: USB first** |
| E2 | Guide assumed a narrow ESP32; the real one covered every breadboard hole | Check board width on the real part. Fix: only the VIN-side row goes in (row j), the other row hangs past the edge |
| E3 | **Supply wires reversed at the DC adapter** (red on ⊖, black on ⊕), caught from a photo before power-on | Read the ⊕ / ⊖ marks on the adapter itself, never assume left/right. Photo check of polarity before the first power-on is mandatory |
| E4 | **RoboHand WiFi invisible.** The firmware reported "WiFi started OK"; Espressif's own WiFiScan example found the router next to the board rarely or not at all | A cheap board can have a weak radio. Test the radio with the **official example** first, before blaming code or phone. Keep a spare board |
| E5 | Video/guide columns didn't match the user's breadboard (ESP32 mounted mirrored, column 30 at the USB end) | Wiring pictures are drawn for **the real board as it sits** (`docs/wiring_steps/`): one finger per picture, bold = new wires |
| E6 | Plugs lying flat with bent pins: intermittent contact (index moved once, then stopped) | Every plug stands straight in its hole; strain-relieve the cables |
| E7 | Thumb: full 0–180° only bends the first hinge | Open (see above). Rule already known: **tie each string with the servo at its open angle (low end), finger straight, string just tight** |
| — | Jumper colours didn't match servo colours (black jumper on servo red) | Mark + jumpers with red tape; check by servo wire colour, not jumper colour |

### 4. Firmware and tools
- Serial commands (`a`, `f`, `open`, `wifi`, `scan`) made it possible to test without WiFi.
- A **USB control page** (Web Serial, Chrome/Edge) replaced typing: sliders, calibration with Save OPEN/CLOSED that
  writes the `FINGERS[]` code, move-together, gestures. Tested against a fake ESP32 in `tools/test/`.
- Commands must be typed exactly, lowercase; unknown input prints the help.

### 5. How we worked (process)
- **Validation must separate verified from assumed.** Early checks tested the model against itself with ideal
  sizes and passed while the real print failed. Every check now has a **control case that must fail**.
- **Photo before power, every time.** Two serious faults (reversed supply E3, possible VIN short) were caught
  only because nothing was powered until a clear top-down photo was checked.
- **Blurred or angled photos aren't enough to approve wiring;** ask again rather than guess.
- **One finger at a time:** wire, test, then the next. Mistakes stay small and obvious.
- **Diagnose with the simplest independent test** (Serial Monitor instead of the phone, the official WiFiScan
  instead of our scan command) before changing anything.
- **Guides, pictures and videos are updated in the same change as the design** (B8); outdated videos are listed
  in `docs/reference/README.md`.

## Checklist before the first power-on (any future build)
- [ ] Supply: red to ⊕, black to ⊖, read on the adapter body
- [ ] Rails: + row along the red line, − row along the blue line
- [ ] Capacitor: stripe (short leg) on −
- [ ] ESP32 VIN pin empty; D12 empty; GND jumper to the − rail
- [ ] Each servo: red on +, brown on −, signal in its own pin's column (follow the label)
- [ ] All plugs upright, fully in
- [ ] Strings slack
- [ ] Clear top-down photo checked
- [ ] Power on: supply, then USB. Off: USB, then supply

## Checklist for prototype 2
Everything in [DESIGN_LESSONS.md → Checklist](DESIGN_LESSONS.md#checklist-for-the-next-design-wrist-thumb-base-rolling-station-v2), plus:
- [ ] Measure every bought part (servo, horn, screw, board, cable) and record it before designing around it
- [ ] Fit-test prints for every mating feature
- [ ] Emboss labels: bone names, finger letter at each servo window, FRONT
- [ ] A cable-management feature on the stand (strain relief for 5 servo leads)
- [ ] Spare ESP32 in stock; test its radio with WiFiScan on arrival
- [ ] Calibrated angles recorded in the repo after every rebuild
