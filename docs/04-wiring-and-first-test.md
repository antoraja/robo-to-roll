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

## B. Wire it up (power OFF: USB and power supply unplugged)

Your ESP32 (30 pins) plugs **straight into the 400-hole breadboard**, so every connection is a
plain **male-male** jumper. The wiring video (`video/electronics/robohand_wiring_programming.mp4`)
shows each step in 3D.

```
 breadboard, top edge:     ── − rail (blue line) ──────────────────────────────
                           ── + rail (red line)  ──────────────────────────────
 row a (free holes):        VIN  GND  D13  D12  D14  D27  D26  D25 ...
 row b (ESP32 pins):       [ESP32 pushed in across the middle groove, USB end at column 1]
 row i (ESP32 pins):       [other pin row]
```

1. **ESP32:** push it into the breadboard across the middle groove, USB socket at the edge
   (column 1). Its two pin rows sit in rows **b** and **i**, so row **a** has one free hole next
   to each pin.
2. **Power adapter:** red jumper in the adapter's **+** screw terminal, black jumper in **−**.
   Tighten the screws. Red jumper into the **+ rail (red line)**, black into the **− rail (blue line)**.
3. **Capacitor 1000 µF:** long leg into the + rail, striped side (short leg) into the − rail.
4. **Shared ground:** black jumper from the free hole next to **GND** (row a) into the − rail.
5. **Servo (index):** push 3 male-male jumpers into its plug (brown, red, orange) and tape the joint.
   Brown into the − rail, red into the + rail, **orange into the free hole next to D13** (row a).
6. **Leave the hole next to VIN empty.** Servos get power only from the 5 V 3 A supply.

The pin labels are printed on the board (`D13`, `GND`, ...). Always read them: some boards use a
different order.

## C. Upload the code

1. Open `firmware/finger_control/finger_control.ino` in Arduino IDE. It's set up for the
   full hand. For this first test only the servo on **pin 13 (index)** is connected; the others
   simply aren't plugged in yet.
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

In the Serial Monitor, type raw angles for one finger and watch it. Finger numbers are
0 thumb, 1 index, 2 middle, 3 ring, 4 little:

```
a 1 90       <- move the index servo to 90 degrees
a 1 30
a 1 150
```

1. Find the angle where the finger is **just straight** with the line barely tight, e.g. 25.
2. Find the angle where the finger is **fully curled** but the servo isn't straining or
   buzzing, e.g. 150.
3. Put those numbers in the code and upload again:
   ```cpp
     {"Index",  13, 25, 150},
   ```
   (If the finger closes when the angle goes *down*, just swap them, e.g. `150, 25`. The
   code works either way.)

Now 0 % on the slider means fully open and 100 % means fully closed.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Servo doesn't move at all | Signal in the wrong hole / no common ground | Orange must be in row a, next to D13. GND jumper to the − rail |
| Servo jitters / twitches | Weak power or loose jumper | Use the separate 5 V supply + capacitor, re-seat the jumpers |
| ESP32 reboots when the servo moves (Serial Monitor shows "RoboHand starting" again) | Servo drawing too much from USB | Switch to the separate 5 V supply |
| Phone can't find "RoboHand" | Code not running / out of range | Check the Serial Monitor output, move closer, press EN (reset) |
| Page won't open | Phone using mobile data instead | Turn mobile data off, or answer "stay connected" |
| Servo buzzes loudly at the end of travel | Pushing past the finger's limit | Move `closedAngle` a few degrees back |

## Next step

When the servo moves from your phone, the electronics work. Go to
[guide 05](05-full-hand.md) to build the full hand. The firmware is already set up for 5
fingers, and the servo you just tested on pin 13 is the **index** finger.
