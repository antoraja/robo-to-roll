# 02 · Shopping list (cost-effective)

Prices are rough single-unit figures from AliExpress / Amazon / local electronics shops in
2025–26. AliExpress is cheapest but slowest (1–3 weeks), so **order first, then print while
you wait**. Search terms are given so you can find the item anywhere.

## Phase 1: one finger (what to buy now)

| # | Item | Search for | Qty | ≈ Price |
|---|---|---|---|---|
| 1 | ESP32 dev board, 30-pin, ESP-WROOM-32 | `ESP32 DevKit V1 ESP-WROOM-32 30 pin` (USB-C version if offered) | 1 | $4–7 |
| 2 | Metal-gear micro servo | `MG90S servo` (buy a **6-pack**: 1 now, 5 for the hand later, and they're cheaper in packs) | 6 | $12–18 (pack) |
| 3 | Jumper wires, all three kinds | `dupont jumper wire 40pcs male-male male-female female-female` | 1 set | $2–4 |
| 4 | Breadboard | `breadboard 400 points` or `830 points` | 1 | $1–3 |
| 5 | Braided fishing line (the tendon) | `PE braided fishing line 0.3mm 20lb` (any 0.2–0.4 mm braided line; **not** nylon mono, which stretches) | 1 spool | $2–4 |
| 6 | Elastic cord (the return spring) | `round elastic cord 2mm` (stretchy rubber-core cord; the simulation showed 1 mm is too weak) | 1 roll | $1–3 |
| 7 | USB data cable matching your ESP32 | micro-USB or USB-C (you probably have one; check it's a **data** cable) | 1 | $0–2 |

**Phase 1 total: about $15–25**, plus filament you already have.

## Recommended (cheap, saves headaches)

| Item | Why | ≈ Price |
|---|---|---|
| `USB-C female to screw terminal breakout` (2–5 pack) | Turns any phone charger into a clean 5 V servo supply, no soldering | $1–3 |
| Phone charger, **5 V ≥ 2 A** | Separate servo power (you probably own one) | $0 |
| `electrolytic capacitor 1000uF 16V` | Placed across the servo 5 V/GND rails, it smooths current spikes so the ESP32 doesn't reboot | $1 (pack) |
| Cheap multimeter (`DT830`) | Check voltages and find bad wires | $5–8 |

## Tools

- Small Phillips screwdriver (for the servo screws)
- Scissors / side cutters
- Super glue (CA glue). It fixes the spool to the servo horn and seals knots.
- Lighter (melts the end of the filament pins so they don't slide out)
- *Optional:* 2 mm drill bit to clean out printed holes if they come out tight

## You already have

- 3D printer + **PLA or PETG** filament (about 60 g for the whole one-finger rig)
- 1.75 mm filament = the joint pins

## Phase 2: the full hand (buy later, not now)

| Item | Qty | ≈ Price |
|---|---|---|
| 4 more MG90S (already in the 6-pack) | — | — |
| 5 V supply ≥ 3 A (e.g. `5V 3A power adapter` + `DC barrel jack to screw terminal`, or a 3 A USB-C charger) | 1 | $5–8 |
| *Optional:* `PCA9685 16 channel servo driver` (only if we run out of ESP32 pins for the arm) | 1 | $3–5 |
| MG996R servos for wrist/elbow (phase 3) | 2–3 | $4–7 each |

> **Why no PCA9685 now?** The ESP32 can drive up to ~16 servos straight from its own pins,
> so five fingers need no extra board. We only add one if the arm needs more channels.
