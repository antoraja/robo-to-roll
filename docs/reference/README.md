# Reference: the correct build (prototype 1, November 2026)

Photos of the real, working build and the pictures of the **current** design. Use this folder
to check what "right" looks like before changing or rebuilding anything. Outdated pictures and
videos are listed at the bottom so they don't get mixed up.

## Photos of the real build

| File | What it shows |
|---|---|
| [`photos/2026-11-05_assembled_hand_front.jpg`](photos/2026-11-05_assembled_hand_front.jpg) | Complete hand on its stand, seen from the palm side: all 4 fingers curled, thumb out, camera rail on the lower palm, servo windows in the spine, coin pockets in the base |
| [`photos/2026-11-05_assembled_hand_side.jpg`](photos/2026-11-05_assembled_hand_side.jpg) | Same, from the side: palm on the spine, strings hanging out under the wrist (servos not fitted yet) |
| [`photos/2026-11-05_assembled_hand_thumb_out.jpg`](photos/2026-11-05_assembled_hand_thumb_out.jpg) | Front view, thumb on its angled boss |
| [`photos/2026-11-05_assembled_hand.mp4`](photos/2026-11-05_assembled_hand.mp4) | Short walk-around video of the assembled hand |
| [`photos/2026-11-02_fingers_correct_layout.jpg`](photos/2026-11-02_fingers_correct_layout.jpg) | All 14 finger bones pinned into the 5 fingers in the **correct** order, next to a ruler (the four 3-bone fingers, then the 2-bone thumb at the bottom) |

The photos were re-saved without their phone data (no location or camera info).

## Current design pictures

| File | What it shows |
|---|---|
| [`design/finger_pin_slot.png`](design/finger_pin_slot.png) | How a finger goes onto the palm: pin through the finger's tab, lower it down the prong slots, nudge it into the seat, melt the pin ends |
| [`design/elastic_tunnel_fix.png`](design/elastic_tunnel_fix.png) | The elastic hole in the palm: smooth 12 mm curve, 3.4 mm wide, with a funnel at the top. The old sharp corner is shown for comparison |
| [`design/elastic_knot_at_palm.png`](design/elastic_knot_at_palm.png) | Tying the elastic on the back of the palm: mark 5 cm, stretch to 7.5 cm, knot, adjust, then trim |
| [`design/spool_v3_design.png`](design/spool_v3_design.png) | Spool without horn: presses onto the servo shaft, held by the original centre screw (plates 8 + 9) |
| [`design/spool_v3_views.png`](design/spool_v3_views.png) | The same spool in 3D: two rims, groove, slot, tie holes, and the string wrapped once and knotted |
| [`design/spool_tie_steps.png`](design/spool_tie_steps.png) | Tying the finger string to the spool after the first power-on: find the turning direction, groove, wrap once, slot → tie hole, 5 mm filament toggle, check |
| [`design/palm_camera.png`](design/palm_camera.png) | The ESP32-CAM cover on the rail on the inside of the palm, clear of the fingers even in a full fist |

## Current videos

| Video | Topic |
|---|---|
| [`video/finger_pin/robohand_finger_pin_slots.mp4`](../../video/finger_pin/robohand_finger_pin_slots.mp4) | Fitting a finger onto the palm with the pin slots |
| [`video/palm_knot/robohand_palm_elastic_knots.mp4`](../../video/palm_knot/robohand_palm_elastic_knots.mp4) | Tying the elastic knots on the back of the palm |
| [`video/finger_strings/robohand_finger_string_elastic.mp4`](../../video/finger_strings/robohand_finger_string_elastic.mp4) | String (with the 5 mm filament toggle) and elastic into one finger, without glue or lock pins |
| [`video/assembly/robohand_servo_mounting.mp4`](../../video/assembly/robohand_servo_mounting.mp4) | Mounting the 5 servos on the spine: front dot, which servo goes where, 2 screws each (40 s, cut from the full assembly video; this part is still correct) |
| [`video/spool_setup/robohand_spool_setup.mp4`](../../video/spool_setup/robohand_spool_setup.mp4) | Tying the strings to the spools (direction, wrap once, slot + hole + knot, test) is still correct. **Its spool-fitting part shows the old glued spool with a horn:** follow [`design/spool_v3_design.png`](design/spool_v3_design.png) instead |
| [`video/electronics/robohand_wiring_programming.mp4`](../../video/electronics/robohand_wiring_programming.mp4) | Wiring the servos and the ESP32, first upload. **Two corrections** (guide 04 is up to date): plug the **5 V supply first, then USB**, and use **two jumpers** each for + and −. Its spool step (horn + glue) is outdated: spools now go straight on the shaft |

## Outdated: don't build from these

| Item | Why it's outdated |
|---|---|
| `video/assembly/robohand_full_assembly.mp4`, `video/robohand_build_guide.mp4` | Made before the build fixes: they show lock pins, glue at the fingertip and pins pushed in from the side. Use guide 05 and the videos above |
| `docs/img/finger_preview.png` | First single-finger prototype on a test base |
| `docs/img/elastic_corner.png`, `docs/img/palm_channel_fix.png` | Pictures of flaws B9 and B10 (kept in [DESIGN_LESSONS.md](../DESIGN_LESSONS.md)) |

## Print files for this build

| Plate | File |
|---|---|
| Palm (latest: pin slots, smooth elastic tunnels, camera rail) | [`cad/plates/plate_3_palm.3mf`](../../cad/plates/plate_3_palm.3mf) |
| Camera cover | [`cad/plates/plate_7_palm_camera.3mf`](../../cad/plates/plate_7_palm_camera.3mf) |
| Fingers, spine, stand, spools | plates 1, 2, 4, 5 in [`cad/plates/`](../../cad/plates/) (unchanged) |
