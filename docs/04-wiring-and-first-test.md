# 04 · Wiring and first wireless test (one servo)

Goal of this step: **move one servo from your phone.** You don't need the finger attached
yet. Doing the electronics on their own first means that if something doesn't work, we
know it's the electronics and not the mechanics.

## A. Install the software (one time, about 15 minutes)

1. Install **Arduino IDE 2** from arduino.cc/en/software.
2. Add ESP32 support:
   - *File → Preferences → Additional boards manager URLs*, paste:
     `https://espressif.github.io/arduino-esp32/package_esp32_index.json`
   - *Tools → Board → Boards Manager*, search **esp32** by *Espressif Systems*, then click **Install**.
3. Add the servo library: *Tools → Manage Libraries*, search **ESP32Servo**, then click **Install**.
4. Plug the ESP32 into your laptop with the **data** USB cable.
   - Under *Tools → Port* a new port should appear (`COM3`… on Windows, `/dev/cu.usbserial…`
     or `/dev/cu.SLAB…` on Mac).
   - **No new port?** Look at the small chip next to the USB socket on the board:
     - It says **CP2102** → install the "CP210x USB to UART driver" from Silicon Labs.
     - It says **CH340** → install the "CH340 driver" from WCH.
     - Still nothing → try another cable (it's probably charge-only).

## B. Wire one servo (power OFF, meaning USB unplugged)

For the **first test with one servo, no finger load**, the servo can take power from the
ESP32's VIN/5V pin:

```
      ESP32 DevKit                         MG90S servo plug
   +--------------+
   |          VIN |----- red jumper ------- RED    (middle wire)
   |          GND |----- black jumper ----- BROWN
   |       GPIO13 |----- yellow jumper ---- ORANGE
   +-----[USB]----+
           |
        laptop
```

- Use **female–male** jumpers: the female socket goes on the ESP32 pin, the male pin goes into the servo plug.
- The pin labels are printed on the board. **VIN** may be labelled `5V` or `VIN`. GPIO13 is
  labelled `D13` or `13` or `G13`.
- Double-check: **never** use the `3V3` pin for the servo.

### Better wiring (when the finger is attached, and always for 2+ servos)

```
  phone charger -> [USB-C screw breakout]  + ----> breadboard + rail ----> servo RED
                                           - ----> breadboard - rail ----> servo BROWN
                                                        |
                                    ESP32 GND ----------+          (shared ground!)
                                    ESP32 GPIO13 -----------------> servo ORANGE
  (optional) 1000 uF capacitor across the + and - rails: long leg (+) to +, striped side (-) to -
```

The ESP32 itself stays powered by the laptop's USB (or a second USB charger).

## C. Upload the code

1. Open `firmware/finger_control/finger_control.ino` in Arduino IDE.
2. *Tools → Board → esp32 → **ESP32 Dev Module***, and *Tools → Port →* your port.
3. Click **Upload** (→ arrow).
   - If it gets stuck at `Connecting.....`, **hold the BOOT button** on the ESP32 until the
     upload starts.
4. Open *Tools → Serial Monitor* and set it to **115200 baud**. You should see:
   ```
   RoboHand starting
   WiFi network: RoboHand   open http://192.168.4.1
   ```
   The servo moves to its start ("open") angle.

## D. Control it from your phone

1. On your phone, join the WiFi network **RoboHand**, password **robohand123**.
   (The phone may warn "no internet". Choose to stay connected.)
2. Open a browser and go to **http://192.168.4.1**
3. Move the **Index** slider. The servo should follow. 🎉

**This is your first wireless robot control.**

## E. Calibrate (after the finger and tendon are mounted, see guide 03)

In the Serial Monitor, type raw angles for finger 0 and watch the finger:

```
a 0 90       <- move servo 0 to 90 degrees
a 0 30
a 0 150
```

1. Find the angle where the finger is **just straight** with the line barely tight, e.g. 25.
2. Find the angle where the finger is **fully curled** but the servo isn't straining or
   buzzing, e.g. 150.
3. Put those numbers in the code and upload again:
   ```cpp
   FingerConfig FINGERS[] = {
     {"Index", 13, 25, 150},
   };
   ```
   (If the finger closes when the angle goes *down*, just swap them, e.g. `150, 25`. The
   code works either way.)

Now 0 % on the slider means fully open and 100 % means fully closed.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Servo doesn't move at all | Signal on the wrong pin / no common ground | Check orange is on GPIO13, and GND is shared |
| Servo jitters / twitches | Weak power or loose jumper | Use the separate 5 V supply + capacitor, re-seat the jumpers |
| ESP32 reboots when the servo moves (Serial Monitor shows "RoboHand starting" again) | Servo drawing too much from USB | Switch to the separate 5 V supply |
| Phone can't find "RoboHand" | Code not running / out of range | Check the Serial Monitor output, move closer, press EN (reset) |
| Page won't open | Phone using mobile data instead | Turn mobile data off, or answer "stay connected" |
| Servo buzzes loudly at the end of travel | Pushing past the finger's limit | Move `closedAngle` a few degrees back |

## Next step

When one finger opens and closes from your phone, tell me. Then we will:
1. Design the **palm** that holds 5 fingers + 5 servos (the same finger CAD, scaled per finger).
2. Add 4 lines to `FINGERS[]` (pins 14, 27, 26, 25).
3. Move to the 3 A external supply.
