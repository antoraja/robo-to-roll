# 02 · Shopping list (cost-effective)

Prices are rough single-unit figures from AliExpress / Amazon / local electronics shops in
2025–26. AliExpress is cheapest but slowest (1–3 weeks), so **order first, then print while
you wait**. Search terms are given so you can find the item anywhere.

## The full hand (what to buy now)

| # | Item | Search for | Qty | ≈ Price |
|---|---|---|---|---|
| 1 | ESP32 dev board, 30-pin, ESP-WROOM-32 | `ESP32 DevKit V1 ESP-WROOM-32 30 pin` (USB-C version if offered) | 1 | $4–7 |
| 2 | Metal-gear micro servo | `MG90S servo` (a **6-pack**: 5 for the fingers + 1 spare) | 6 | $12–18 (pack) |
| 3 | Jumper wires, all three kinds | `dupont jumper wire 40pcs male-male male-female female-female` | 1 set | $2–4 |
| 4 | Breadboard | `breadboard 400 points` or `830 points` | 1 | $1–3 |
| 5 | Braided fishing line (the tendon) | `PE braided fishing line 0.3mm 20lb` (any 0.2–0.4 mm braided line; **not** nylon mono, which stretches) | 1 spool | $2–4 |
| 6 | Elastic cord (the return spring) | `round elastic cord 2mm` (stretchy rubber-core cord; the simulation showed 1 mm is too weak) | 1 roll | $1–3 |
| 7 | USB data cable matching your ESP32 | micro-USB or USB-C (you probably have one; check it's a **data** cable) | 1 | $0–2 |
| 8 | 5 V **3 A** power supply for the servos | `5V 3A power adapter` + `DC barrel jack to screw terminal`, **or** a 3 A USB-C charger + `USB-C female to screw terminal breakout` | 1 | $5–8 |
| 9 | Capacitor | `electrolytic capacitor 1000uF 16V` (across the servo power rails, stops ESP32 resets) | 1 | $1 (pack) |

**Total: about $30–45**, plus ~330 g of filament you already have. The 400-point
breadboard fits the tray on the stand.

## Recommended (cheap, saves headaches)

| Item | Why | ≈ Price |
|---|---|---|
| Cheap multimeter (`DT830`) | Check voltages and find bad wires | $5–8 |

## Tools

- Small Phillips screwdriver (for the servo screws)
- Scissors / side cutters
- Super glue (CA glue). It fixes the spool to the servo horn and seals knots.
- Lighter (melts the end of the filament pins so they don't slide out)
- *Optional:* 2 mm drill bit to clean out printed holes if they come out tight

## You already have

- 3D printer + **PLA or PETG** filament (about 330 g for the hand and stand)
- 1.75 mm filament = the joint pins

- 4 coins or big washers (~26 mm) for the weight pockets in the stand

## Later, for the rolling stage (don't buy yet)

| Item | Qty | ≈ Price |
|---|---|---|
| Manual cigarette rolling machine (70 mm), or a tube injector | 1 | $3–20 |
| 2 more servos for the wrist + 1 for the thumb base (MG90S, or MG996R for the wrist) | 3 | $6–20 |
| `FSR402` thin pressure sensors for the fingertips | 2–3 | $2 each |

> **Why no extra servo driver board?** The ESP32 can drive up to ~16 servos straight from its
> own pins, so 5 fingers plus 3 wrist/thumb servos need no extra board.
