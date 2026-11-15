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


scene("intro", "Your ESP32 is wide. It still goes into the breadboard if only one pin row goes in. The other row hangs in the air past the edge. Then three holes next to every pin are free for the wires.",
      "Your E S P 32 is wide. It still goes into the breadboard, if only one of its pin rows goes in. The other row hangs in the air, past the edge. Then three holes next to every pin are free for the wires.", part="Before you start")
scene("safety", "Before you start: the 5 volt supply is unplugged from the wall, the USB cable is unplugged, and all five finger strings are slack.",
      "Before you start. The five volt supply is unplugged from the wall. The U S B cable is unplugged. And all five finger strings are slack.")
scene("esp_pins", "Look at the ESP32 from the top. The pin row marked VIN is the one that goes in. From the USB end: pin 1 VIN, empty. Pin 2 GND. Pin 3 D13. Pin 4 D12, never used.",
      "Look at the E S P 32 from the top. The pin row marked V I N is the one that goes in. From the U S B end. Pin one, V I N, stays empty. Pin two, ground. Pin three, D 13. Pin four, D 12, is never used.", part="The ESP32")
scene("bb_rows", "On the breadboard, the five holes f, g, h, i and j of one column are connected inside. Rows a to e on the other side of the groove are a separate set.",
      "On the breadboard, the five holes f, g, h, i, and j, of one column, are connected inside. Rows a to e, on the other side of the groove, are a separate set.")
scene("w_esp_in", "Step 1. USB end over column 1. Put the VIN-side pins into row j, columns 1 to 15. The rest of the board hangs over the edge. Check every pin is over its hole, then press evenly until the black strip sits flat.",
      "Step one. U S B end over column one. Put the V I N side pins into row j, columns one to fifteen. The rest of the board hangs out over the edge. Check that every pin is over its hole, then press evenly, until the black strip sits flat.", part="Wiring, power off")
scene("w_esp_check", "The other pin row hangs in the air past the edge and touches nothing. The rails under the board are not used. Now rows f, g and h are free next to every pin.",
      "The other pin row hangs in the air past the edge, and touches nothing. The rails under the board are not used. Now rows f, g, and h are free, next to every pin.")
scene("w_adapter", "Step 2. Take the socket adapter. Two red male-to-male jumpers into its plus terminal, two black ones into minus. Tighten the screws and tug each jumper.",
      "Step two. Take the socket adapter. Two red male to male jumpers go into its plus terminal, and two black ones into minus. Tighten the screws, and tug each jumper.")
scene("w_rails", "Step 3. Use the rails on the other long side, next to row a. Red jumpers into the rail with the red line, black into the rail with the blue line. Follow the colours: on your board, blue is the one nearer row a.",
      "Step three. Use the rails on the other long side, next to row a. Red jumpers go into the rail with the red line. Black jumpers into the rail with the blue line. Follow the colours. On your board, blue is the one nearer row a.")
scene("w_cap", "Step 4. The capacitor goes across these two rails: long leg into the red plus rail, the striped side into the blue minus rail.",
      "Step four. The capacitor goes across these two rails. Long leg into the red plus rail. The striped side into the blue minus rail.")
scene("w_gnd", "Step 5, shared ground. A black jumper from row f of column 2, that is GND, into the blue minus rail.",
      "Step five, the shared ground. A black jumper from row f of column two, that is ground, into the blue minus rail.")
scene("w_servo", "Step 6, the index servo. Push three male-to-male jumpers into its plug: brown, red, orange. Wrap a little tape around the joint.",
      "Step six, the index servo. Push three male to male jumpers into its plug. Brown, red, and orange. Wrap a little tape around the joint.")
scene("w_servo2", "Brown goes into the blue minus rail, red into the red plus rail.",
      "Brown goes into the blue minus rail. Red goes into the red plus rail.")
scene("w_signal", "Orange goes into row f of column 3. Column 3 is pin D13, the index finger.",
      "Orange goes into row f of column three. Column three is pin D 13, the index finger.")
scene("s_middle", "Step 7, the middle finger servo, pin D14. Same three jumpers in its plug. Brown to minus, red to plus, orange into row f, column 5. Label each servo cable with tape.",
      "Step seven, the middle finger servo, pin D 14. The same three jumpers in its plug. Brown to minus, red to plus, and orange into row f, column five. Label each servo cable with tape.", part="The other four servos")
scene("s_ring", "Step 8, the ring finger servo, pin D27. Brown to minus, red to plus, orange into row f, column 6.",
      "Step eight, the ring finger servo, pin D 27. Brown to minus, red to plus, and orange into row f, column six.")
scene("s_little", "Step 9, the little finger servo, pin D26. Brown to minus, red to plus, orange into row f, column 7.",
      "Step nine, the little finger servo, pin D 26. Brown to minus, red to plus, and orange into row f, column seven.")
scene("s_thumb", "Step 10, the thumb servo, pin D25. Brown to minus, red to plus, orange into row f, column 8.",
      "Step ten, the thumb servo, pin D 25. Brown to minus, red to plus, and orange into row f, column eight.")
scene("w_check", "Check everything: 2 red and 2 black supply jumpers, capacitor stripe on minus, GND column 2 to minus, five browns on minus, five reds on plus, oranges in columns 3, 5, 6, 7 and 8. Columns 1 and 4 empty.",
      "Check everything. Two red and two black supply jumpers. The capacitor stripe on minus. Ground, column two, to minus. Five browns on minus. Five reds on plus. Oranges in columns three, five, six, seven, and eight. Columns one and four stay empty.", part="Check")
scene("stand", "In the stand, put the breadboard in its pocket with the ESP32 side facing outwards, away from the spine. The hanging part sticks out over the edge of the stand.",
      "In the stand, put the breadboard in its pocket with the E S P 32 side facing outwards, away from the spine. The hanging part sticks out over the edge of the stand.")
scene("photo", "Now take a photo from above and send it to Claude before you plug in any power.",
      "Now take a photo from above, and send it to Claude, before you plug in any power.")
scene("power_on", "After the OK: first plug the 5 volt supply into the wall, then the USB cable into the ESP32. The servos turn to their open position, one after another.",
      "After the OK. First, plug the five volt supply into the wall. Then plug the U S B cable into the E S P 32. The servos turn to their open position, one after another.", part="Test all five")
scene("phone", "On your phone, join the WiFi RoboHand, password robohand123, stay connected, and open 192.168.4.1.",
      "On your phone, join the WiFi called RoboHand, password robohand 1 2 3. Stay connected, and open 1 9 2 dot 1 6 8 dot 4 dot 1.")
scene("t_thumb", "Test one finger at a time. Move the Thumb slider slowly up and back to 0. Only the thumb servo may turn.",
      "Test one finger at a time. Move the Thumb slider slowly up, and back to zero. Only the thumb servo may turn.")
scene("t_index", "Index slider: only the index servo turns.", "Index slider. Only the index servo turns.")
scene("t_middle", "Middle slider: only the middle servo turns.", "Middle slider. Only the middle servo turns.")
scene("t_ring", "Ring slider: only the ring servo turns.", "Ring slider. Only the ring servo turns.")
scene("t_little", "Little slider: only the little servo turns.", "Little slider. Only the little servo turns.")
scene("t_wrong", "If the wrong servo turns, its orange wire is in the wrong column. If one doesn't move, check its orange wire. Always unplug USB and the supply before moving a wire.",
      "If the wrong servo turns, its orange wire is in the wrong column. If one doesn't move at all, check its orange wire. Always unplug the U S B and the supply before you move a wire.")
scene("outro", "Always power off before changing a wire. Then tie the strings to the spools with the servos at their open position.",
      "Always power off before you change a wire. Then tie the strings to the spools, with the servos at their open position.")

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
