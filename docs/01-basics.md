# 01 · The basics: everything you need to know (and nothing you don't)

Read this once before buying anything. It takes about 15 minutes.

## 1. How the finger moves: tendons, like a real hand

Your own fingers have no motors in them. Muscles in your forearm pull **tendons** (strings)
that run along the palm side of each finger. Our robot finger works the same way:

```
   fingertip  <- line is tied here
      |
  [distal]      Pulling the line (palm side) makes every joint bend -> finger CLOSES
      o  pin
  [middle]      An elastic cord on the back side pulls it straight again -> finger OPENS
      o  pin
  [proximal]
      o  pin
  [ base ]
      |
   (spool on the servo)  <- servo turns, winds up the line
```

- **Flexor tendon:** braided fishing line, tied at the fingertip and wound on the servo spool.
- **Extensor (return):** a loop of elastic cord along the back. No second motor needed.
- **Pins:** each joint turns on a short piece of 1.75 mm 3D-printer filament. You already own these!

## 2. The servo motor: the muscle

A **servo** is a small motor with a gearbox and a controller built in. You tell it an
**angle (0°–180°)** and it moves there and holds that position. You don't need to know
anything about motor drivers.

| Servo | Use | Torque | Price (approx.) |
|---|---|---|---|
| SG90 (blue, plastic gears) | quick tests only, gears strip under load | ~1.8 kg·cm | $1–2 |
| **MG90S (metal gears)** | **fingers (recommended)** | ~2.2 kg·cm | $2–4 |
| MG996R (big, metal gears) | wrist / elbow later | ~10 kg·cm | $4–7 |

Every hobby servo has **3 wires** ending in one 3-hole plug:

| Wire colour | Meaning | Goes to |
|---|---|---|
| **Brown** (or black) | GND (minus, 0 V) | GND |
| **Red** (middle) | + power, 5 V | 5 V |
| **Orange** (or yellow / white) | **signal**, which says "go to this angle" | an ESP32 pin (GPIO 13) |

> The red wire is always in the middle, so plugging the connector in backwards usually
> doesn't damage anything. It just won't move. Still, check the colours.

## 3. The ESP32: the brain with WiFi built in

The **ESP32 DevKit** is a $4–7 board about the size of a stick of gum. It has:

- **WiFi and Bluetooth** built in. This is how we get "wireless" without any extra parts.
- **Pins (GPIO)** along both edges. Each one can send a servo signal.
- A **USB port** for uploading code from your laptop and for power while testing.

You program it with the free **Arduino IDE**. I write the code, and you click "Upload".

Our code makes the ESP32 create **its own WiFi network** called `RoboHand`. Your phone joins
it, you open a web page, and you get a slider for each finger. No router or internet needed,
and no app to install.

## 4. Power: the #1 beginner trap

- The ESP32 runs on **3.3 V** internally and gets power from USB.
- Servos need **5 V** and draw a lot of current **in bursts**: up to ~0.7 A each when
  they start moving or pull hard.
- If too many servos draw from the ESP32's USB power, the voltage drops, the **ESP32
  reboots**, and the WiFi disconnects.

**Rule of thumb:**

| Setup | Power the servo from |
|---|---|
| **1 servo, testing on the desk** | The ESP32's **VIN / 5V pin** (passes USB 5 V through). Fine for step 3. |
| **Finger under load / 2+ servos** | A **separate 5 V supply**: a phone charger (2–3 A) + USB-C screw-terminal adapter |
| **5 fingers** | A 5 V supply rated **3 A or more** |

## 5. Ground: the one connection everyone forgets

All the parts must share the same **GND (ground, 0 V)**. When you use a separate 5 V supply,
**connect its GND to the ESP32's GND** as well as to the servo's brown wire. Without that
shared ground, the servo doesn't understand the signal and jitters or does nothing.

```
  5V supply (+) ----------------------------- servo RED
  5V supply (-) ----+------------------------ servo BROWN
                    |
  ESP32 GND --------+          ESP32 GPIO13 -- servo ORANGE
```

## 6. The connectors you'll use (all plug-in, no soldering)

| Name | Looks like | Used for |
|---|---|---|
| **Dupont / jumper wire** | Thin wire with a pin or socket at each end | Every connection in this project |
| ↳ male–male (M-M) | pin ↔ pin | breadboard ↔ servo plug |
| ↳ male–female (M-F) | pin ↔ socket | ESP32 pin ↔ breadboard |
| ↳ female–female (F-F) | socket ↔ socket | ESP32 pin ↔ servo wires directly |
| **Servo plug** | 3-hole black plug, 2.54 mm spacing | Male jumper pins push straight in |
| **Breadboard** | White board full of holes, with connected rows | Joining several wires without soldering (the long +/− rails along the edge carry 5 V and GND) |
| **Screw terminal** | Little box with screws that clamp a wire | Power adapter outputs |
| **USB-C screw-terminal breakout** | Tiny board: USB-C socket → + and − screws | Turns any phone charger into a 5 V servo supply |
| **USB cable** | Micro-USB or USB-C, whichever your ESP32 has | **Must be a data cable!** Many cheap cables are charge-only and the laptop won't see the board |

## 7. Software you'll install (step 3)

1. **Arduino IDE 2** (free, Windows/Mac/Linux)
2. **ESP32 board support** (added from inside the IDE)
3. **ESP32Servo** library (added from inside the IDE)
4. Possibly a **USB driver** (CP210x or CH340, depending on the chip printed near the ESP32's USB port)

## 8. Calibration: why the numbers in the code will change

Every printed finger and every servo is slightly different. The code has two numbers per
finger, `openAngle` and `closedAngle`. In step 4 you'll find the right values by typing angles
in the Serial Monitor and watching the finger. This takes about 5 minutes.

## 9. Safety

- Unplug power before you change any wiring.
- Don't let a servo push against a hard stop for long. It heats up and can burn out
  ("stall"). If one buzzes loudly while not moving, ease the angle back a bit.
- Avoid LiPo batteries until you're comfortable. Use USB chargers / 5 V adapters (or AA
  NiMH packs).
- Cut fishing line with scissors and keep it away from your eyes when it's under tension.

## 10. Glossary

- **GPIO:** a numbered pin on the ESP32 that the code can control.
- **PWM:** the pulse signal on the orange wire. Its pulse length encodes the angle. The library handles it.
- **VIN / 5V pin:** an ESP32 pin carrying the 5 V from USB.
- **3V3 pin:** 3.3 V output. **Never** power servos from it.
- **Stall:** a motor pushing but unable to move. It draws its maximum current and heats up.
- **Access Point (AP):** a device that creates its own WiFi network, which our ESP32 does.
