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

# ---------------------------------------------------------------- part A: the parts
scene("intro", "In this video we wire up and program the RoboHand, step by step. You don't need any electronics experience. Just pause the video after each step and copy it.",
      part="Your parts")
scene("servo", "This is an MG90S servo. It is a small motor that turns to the angle you tell it. It has three wires: brown is ground (minus), red is plus 5 volts, orange is the signal.",
      "This is an M G 90 S servo. It is a small motor that turns to the angle you tell it. It has three wires. Brown is ground, or minus. Red is plus five volts. Orange is the signal.")
scene("esp32", "This is the ESP32 board, the brain of the hand. It has WiFi built in. The USB-C socket is for programming and power. We use the pins labelled 13, 14, 25, 26, 27 and GND.",
      "This is the E S P 32 board, the brain of the hand. It has WiFi built in. The U S B C socket is for programming and for power. We use the pins labelled 13, 14, 25, 26, 27, and G N D.")
scene("esp32_buttons", "Next to the USB socket are two small buttons: EN restarts the board, BOOT is only needed if an upload gets stuck.",
      "Next to the U S B socket are two small buttons. E N restarts the board. BOOT is only needed if an upload gets stuck.")
scene("breadboard", "This is the 400-hole breadboard. Inside, holes are connected in lines. The long rails along the edge, red plus and blue minus, are connected all the way along.",
      "This is the 400 hole breadboard. Inside, the holes are connected in lines. The long rails along the edge, red plus, and blue minus, are connected all the way along.")
scene("breadboard_rows", "In the middle, each short column of five holes is connected. Anything plugged into the same column is joined together.",
      "In the middle, each short column of five holes is connected. Anything you plug into the same column is joined together.")
scene("jumpers", "Jumper wires come in three kinds. A male end has a pin, a female end has a hole. We only need male-to-male. The others are spares.",
      "Jumper wires come in three kinds. A male end has a pin. A female end has a hole. We only need male to male. The others are spares.")
scene("power", "The power supply gives 5 volts and 3 amps for the servos. Its plug goes into the black socket adapter, which has two screw terminals marked plus and minus.",
      "The power supply gives five volts, and three amps, for the servos. Its plug goes into the black socket adapter, which has two screw terminals, marked plus, and minus.")
scene("capacitor", "The capacitor smooths out power spikes. It has a direction: the side with the stripe is minus, and the longer leg is plus.",
      "The capacitor smooths out power spikes. It has a direction. The side with the stripe is minus, and the longer leg is plus.")

# ---------------------------------------------------------------- part B: software
scene("sw_ide", "Now the software. On your laptop, download and install Arduino IDE 2 from arduino.cc/en/software.",
      "Now the software. On your laptop, download and install Arduino I D E 2, from arduino dot c c, slash e n, slash software.", part="Software on your laptop")
scene("sw_driver", "Your ESP32 board talks to the laptop through a chip called CH340. On Windows or Mac, search for 'CH340 driver', download it from the maker WCH, and install it.",
      "Your E S P 32 board talks to the laptop through a chip called C H 3 4 0. On Windows or Mac, search for C H 3 4 0 driver, download it from the maker, W C H, and install it.")
scene("sw_url", "In Arduino IDE open File > Preferences. Paste the ESP32 address shown on screen into 'Additional boards manager URLs', and click OK.",
      "In Arduino I D E, open File, then Preferences. Paste the E S P 32 address shown on screen into the field, Additional boards manager U R Ls, and click OK.")
scene("sw_core", "Open Tools > Board > Boards Manager. Search for esp32 and install 'esp32 by Espressif Systems'. This takes a few minutes.",
      "Open Tools, Board, Boards Manager. Search for E S P 32, and install E S P 32 by Espressif Systems. This takes a few minutes.")
scene("sw_lib", "Open Tools > Manage Libraries. Search for ESP32Servo and click Install.",
      "Open Tools, Manage Libraries. Search for E S P 32 Servo, and click Install.")
scene("sw_open", "Download the project from GitHub (Code > Download ZIP) and unzip it. In Arduino IDE open firmware/finger_control/finger_control.ino.",
      "Download the project from GitHub. Click Code, then Download ZIP, and unzip it. In Arduino I D E, open the folder firmware, finger control, and the file finger control dot I N O.")
scene("sw_board", "Plug the ESP32 into your laptop with your USB-C cable. In Tools > Board choose 'ESP32 Dev Module'. In Tools > Port choose the new port that appeared.",
      "Plug the E S P 32 into your laptop with your U S B C cable. In Tools, Board, choose E S P 32 Dev Module. In Tools, Port, choose the new port that appeared.")
scene("sw_upload", "Click the Upload arrow. If it stops at 'Connecting...', hold the BOOT button on the board until the upload starts. 'Done uploading' means the board is programmed.",
      "Click the Upload arrow. If it stops at Connecting, hold the BOOT button on the board until the upload starts. Done uploading means the board is programmed.")
scene("sw_serial", "Open Tools > Serial Monitor and set it to 115200 baud. You should see 'RoboHand starting' and the WiFi name. Then unplug the USB cable.",
      "Open Tools, Serial Monitor, and set it to 1 1 5 2 0 0 baud. You should see RoboHand starting, and the WiFi name. Then unplug the U S B cable.")

# ---------------------------------------------------------------- part C: wiring + first servo
scene("safety", "Wiring rule number one: always unplug the power supply and the USB cable before you change any wire. Never power the servos from the ESP32's pins.",
      "Wiring rule number one. Always unplug the power supply, and the U S B cable, before you change any wire. Never power the servos from the E S P 32's pins.", part="Wiring")
scene("w_esp32", "Step 1. Push the ESP32 into the breadboard, across the middle groove, with its USB socket at the edge. Press gently and evenly until the pins are fully in.",
      "Step one. Push the E S P 32 into the breadboard, across the middle groove, with its U S B socket at the edge. Press gently and evenly, until the pins are fully in.")
scene("w_adapter", "Step 2. Take the socket adapter. Push the pin of a red male-to-male jumper into the plus (+) terminal and tighten the screw. Do the same with a black jumper on the minus (−) terminal.",
      "Step two. Take the socket adapter. Push the pin of a red male to male jumper into the plus terminal, and tighten the screw. Do the same with a black jumper, on the minus terminal.")
scene("w_rails", "Step 3. Plug the red jumper into the red plus rail of the breadboard, and the black jumper into the blue minus rail.",
      "Step three. Plug the red jumper into the red plus rail of the breadboard, and the black jumper into the blue minus rail.")
scene("w_cap", "Step 4. Put the capacitor across the rails: long leg into the plus rail, striped side (short leg) into the minus rail.",
      "Step four. Put the capacitor across the rails. Long leg into the plus rail. Striped side, the short leg, into the minus rail.")
scene("w_gnd", "Step 5, the shared ground. Find the ESP32 pin labelled GND. One black jumper goes from the free hole next to it into the minus rail.",
      "Step five, the shared ground. Find the E S P 32 pin labelled G N D. One black jumper goes from the free hole next to it, into the minus rail.")
scene("w_servo", "Step 6, the first servo (index finger). Push three male-to-male jumpers into its plug: brown, red, orange. Wrap a little tape around the joint.",
      "Step six, the first servo, for the index finger. Push three male to male jumpers into its plug. Brown, red, and orange. Wrap a little tape around the joint.")
scene("w_servo2", "Brown goes into the minus rail, red into the plus rail.",
      "Brown goes into the minus rail. Red goes into the plus rail.")
scene("w_signal", "Orange goes into the free hole right next to ESP32 pin D13 (same column). That is the signal. Always read the label printed next to the pin.",
      "Orange goes into the free hole right next to E S P 32 pin D 13, in the same column. That is the signal. Always read the label printed next to the pin.")
scene("w_check", "Check once more: red to plus, brown to minus, orange next to D13, ESP32 GND to the minus rail, capacitor stripe on minus. Nothing in the hole next to VIN.",
      "Check once more. Red to plus. Brown to minus. Orange next to D 13. E S P 32 ground to the minus rail. The capacitor stripe on minus. And nothing in the hole next to V I N.")
scene("power_on", "Now plug the USB-C cable into the ESP32 and the power supply into the socket adapter. The servo turns to its start position.",
      "Now plug the U S B C cable into the E S P 32, and the power supply into the socket adapter. The servo turns to its start position.")
scene("phone", "On your phone, join the WiFi 'RoboHand', password robohand123. If it warns about no internet, stay connected. Open the browser at 192.168.4.1.",
      "On your phone, join the WiFi called RoboHand. The password is robohand 1 2 3. If the phone warns about no internet, stay connected. Then open the browser, and go to 1 9 2 dot 1 6 8 dot 4 dot 1.")
scene("phone2", "Move the Index slider. The servo follows. Your electronics work!",
      "Move the Index slider. The servo follows. Your electronics work!")

# ---------------------------------------------------------------- part D: all servos + calibration
scene("all", "Now the other four servos, exactly the same way: brown to minus, red to plus, orange next to its pin. Thumb D25, middle D14, ring D27, little D26. Label every servo cable with tape.",
      "Now the other four servos, exactly the same way. Brown to minus, red to plus, and orange next to its pin. Thumb, D 25. Middle, D 14. Ring, D 27. And little, D 26. Label every servo cable with tape.", part="All five servos")
scene("spools", "Power everything once: every servo moves to its open position. Only now press a horn onto each shaft and glue the spool onto the horn.",
      "Power everything once. Every servo moves to its open position. Only now, press a horn onto each shaft, and glue the spool onto the horn.")
scene("calib", "Calibration, after the hand is built. In the Serial Monitor type: a, space, finger number, space, angle, then Enter. 'a 1 90' moves the index servo to 90 degrees.",
      "Calibration, after the hand is built. In the Serial Monitor, type a, space, the finger number, space, an angle, and press Enter. For example, a 1 90 moves the index servo to 90 degrees.")
scene("calib_numbers", "Finger numbers: 0 thumb, 1 index, 2 middle, 3 ring, 4 little.",
      "Finger numbers. Zero, thumb. One, index. Two, middle. Three, ring. Four, little.")
scene("calib2", "For each finger find the angle where it is just straight, and the angle where it is fully bent, stopping a few degrees before it presses hard. Put both numbers in the FINGERS list and upload again.",
      "For each finger, find the angle where it is just straight, and the angle where it is fully bent, stopping a few degrees before it presses hard. Put both numbers into the FINGERS list, and upload again.")
scene("trouble", "If the ESP32 restarts when servos move: check the power supply and the capacitor. A servo doesn't move: check its orange wire and the shared ground. Phone can't find RoboHand: press EN.",
      "If the E S P 32 restarts when the servos move, check the power supply and the capacitor. If a servo doesn't move, check its orange wire and the shared ground. If the phone can't find RoboHand, press the E N button.", part="Troubleshooting")
scene("outro", "That's it. Your RoboHand is wired, programmed and calibrated. Have fun!",
      "That's it. Your RoboHand is wired, programmed, and calibrated. Have fun!")


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
