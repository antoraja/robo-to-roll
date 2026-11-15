"""Narration for the electronics & programming video.

Each scene has: id (which picture the page draws), text (subtitle) and say (spoken; spelled
out where the voice would stumble). This script speaks every line with espeak-ng + MBROLA,
measures it, and writes timeline.js (scene timings) + narration.wav (the full audio track).

    sudo apt-get install espeak-ng mbrola-us2
    python script.py
"""
import json
import os
import subprocess
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE, SPEED, RATE = "mb-us2", 140, 16000
GAP_BEFORE, GAP_AFTER, MIN_SCENE = 0.6, 1.1, 4.0

S = []
def scene(id, text, say=None, part=None):
    S.append(dict(id=id, text=text, say=say or text, part=part))


scene("intro", "Wiring the RoboHand with your ESP32. Your board is wide and covers every breadboard hole, so it lies next to the breadboard and connects with female-to-male jumpers.",
      "Wiring the RoboHand, with your E S P 32. Your board is wide, and covers every breadboard hole. So it lies next to the breadboard, and connects with female to male jumpers.", part="Before you start")
scene("safety", "Before you start: the 5 volt supply is unplugged from the wall, the USB cable is unplugged, and all five finger strings are slack.",
      "Before you start. The five volt supply is unplugged from the wall. The U S B cable is unplugged. And all five finger strings are slack.")
scene("fm_jumper", "Two kinds of jumper are used. Female-to-male: the socket end pushes onto an ESP32 pin. Male-to-male: for the servo plugs and the power. The colour doesn't matter.",
      "Two kinds of jumper are used. Female to male. The socket end pushes onto an E S P 32 pin. And male to male, for the servo plugs, and the power. The colour of a jumper doesn't matter.")
scene("esp_pins", "Look at the ESP32 from the top. Start at the USB end, on the side marked VIN. Pin 1 is VIN: leave it empty. Pin 2 is GND. Pin 3 is D13. Pin 4 is D12: never use it.",
      "Look at the E S P 32 from the top. Start at the U S B end, on the side marked V I N. Pin one is V I N. Leave it empty. Pin two is ground. Pin three is D 13. Pin four is D 12. Never use it.", part="The ESP32")
scene("esp_flip", "Turn the board over and lay it on its back next to the breadboard, pins pointing up. The labels are now underneath, so count the pins from the USB end.",
      "Turn the board over, and lay it on its back, next to the breadboard, with the pins pointing up. The labels are now underneath, so count the pins from the U S B end.")
scene("w_gnd_f", "Step 1. Push the socket of a female-to-male jumper onto pin 2, GND, all the way down.",
      "Step one. Push the socket of a female to male jumper onto pin two, ground, all the way down.", part="Wiring, power off")
scene("w_d13_f", "Step 2. A second female-to-male jumper goes onto pin 3, D13. That is the index finger's signal.",
      "Step two. A second female to male jumper goes onto pin three, D 13. That is the index finger's signal.")
scene("w_adapter", "Step 3. Take the socket adapter. Two red male-to-male jumpers into its plus terminal, two black ones into minus. Tighten the screws and tug each jumper.",
      "Step three. Take the socket adapter. Two red male to male jumpers go into its plus terminal, and two black ones into minus. Tighten the screws, and tug each jumper.")
scene("w_rails", "Step 4. The red jumpers go into the red plus rail of the breadboard, the black jumpers into the blue minus rail.",
      "Step four. The red jumpers go into the red plus rail of the breadboard. The black jumpers go into the blue minus rail.")
scene("w_cap", "Step 5. The capacitor goes across the rails: long leg into plus, the striped side into minus.",
      "Step five. The capacitor goes across the rails. Long leg into plus. The striped side into minus.")
scene("w_gnd", "Step 6. The free end of the GND jumper goes into the minus rail. Now the ESP32 and the servos share the same ground.",
      "Step six. The free end of the ground jumper goes into the minus rail. Now the E S P 32 and the servos share the same ground.")
scene("breadboard_rows", "In the middle of the breadboard, the five holes of one column, rows a to e, are connected. We use column 5 to join two wires.",
      "In the middle of the breadboard, the five holes of one column, rows a to e, are connected inside. We use column five to join two wires.")
scene("w_d13", "Step 7. The free end of the D13 jumper goes into column 5, row a.",
      "Step seven. The free end of the D 13 jumper goes into column five, row a.")
scene("w_servo", "Step 8, the index servo. Push three male-to-male jumpers into its plug: brown, red, orange. Wrap a little tape around the joint.",
      "Step eight, the index servo. Push three male to male jumpers into its plug. Brown, red, and orange. Wrap a little tape around the joint.")
scene("w_servo2", "Brown goes into the minus rail, red into the plus rail.",
      "Brown goes into the minus rail. Red goes into the plus rail.")
scene("w_signal", "Orange goes into column 5, row b: the same column as the D13 jumper, so they are connected.",
      "Orange goes into column five, row b. That's the same column as the D 13 jumper, so the two are connected.")
scene("w_check", "Check: red to plus, brown to minus, capacitor stripe on minus, GND to the minus rail, D13 and orange in column 5. VIN and D12 empty.",
      "Check. Red to plus. Brown to minus. The capacitor stripe on minus. Ground to the minus rail. D 13 and orange, both in column five. V I N and D 12 empty.")
scene("photo", "Now take a photo from above and send it to Claude before you plug in any power.",
      "Now take a photo from above, and send it to Claude, before you plug in any power.")
scene("power_on", "After the OK: first plug the 5 volt supply into the wall, then plug the USB cable into the ESP32. The servo turns to its open position.",
      "After the OK. First, plug the five volt supply into the wall. Then plug the U S B cable into the E S P 32. The servo turns to its open position.", part="First move")
scene("phone", "On your phone, join the WiFi RoboHand, password robohand123, stay connected, and open 192.168.4.1.",
      "On your phone, join the WiFi called RoboHand, password robohand 1 2 3. Stay connected, and open 1 9 2 dot 1 6 8 dot 4 dot 1.")
scene("phone2", "Move the Index slider slowly. The servo follows. Your electronics work.",
      "Move the Index slider slowly. The servo follows. Your electronics work.")
scene("all", "Later, the other four servos the same way. Thumb: pin 8, D25, column 8. Middle: pin 5, D14, column 11. Ring: pin 6, D27, column 14. Little: pin 7, D26, column 17.",
      "Later, the other four servos, the same way. Thumb. Pin eight, D 25, column eight. Middle. Pin five, D 14, column eleven. Ring. Pin six, D 27, column fourteen. Little. Pin seven, D 26, column seventeen.", part="All five servos")
scene("all2", "Each pin gets one female-to-male jumper into row a of its column, and that servo's orange wire goes into row b of the same column. Brown and red always go to the rails.",
      "Each pin gets one female to male jumper, into row a of its column. And that servo's orange wire goes into row b, of the same column. Brown and red always go to the rails.")
scene("outro", "Power off before changing any wire. Then tie the strings to the spools with the servos at their open position.",
      "Always power off before you change any wire. Then tie the strings to the spools, with the servos at their open position.")

def speak(text, path):
    subprocess.run(["espeak-ng", "-v", VOICE, "-s", str(SPEED), "-a", "110", "-w", path, text], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with wave.open(path) as w:
        assert w.getframerate() == RATE, w.getframerate()
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)


def main():
    tmp = os.path.join(HERE, "_tts"); os.makedirs(tmp, exist_ok=True)
    t, audio, timeline = 0.0, [], []
    for i, s in enumerate(S):
        pcm = speak(s["say"], os.path.join(tmp, f"{i:02d}.wav"))
        dur_voice = len(pcm) / RATE
        dur = max(MIN_SCENE, GAP_BEFORE + dur_voice + GAP_AFTER)
        timeline.append(dict(id=s["id"], text=s["text"], part=s["part"], t0=round(t, 3), dur=round(dur, 3),
                             voice=[round(t + GAP_BEFORE, 3), round(t + GAP_BEFORE + dur_voice, 3)]))
        seg = np.zeros(int(round(dur * RATE)), np.int16)
        start = int(GAP_BEFORE * RATE)
        seg[start:start + len(pcm)] = pcm[: len(seg) - start]
        audio.append(seg)
        t += dur
    full = np.concatenate(audio)
    with wave.open(os.path.join(HERE, "narration.wav"), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(full.tobytes())
    with open(os.path.join(HERE, "timeline.js"), "w") as fh:
        fh.write("window.TIMELINE=" + json.dumps(dict(scenes=timeline, total=round(t, 3))) + ";")
    print(f"{len(S)} scenes, {t:.0f} s ({t / 60:.1f} min)")


if __name__ == "__main__":
    main()
