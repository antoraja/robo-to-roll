"""Narration for the full assembly video (printed plates -> working hand).

Each scene: id (what the page draws), text (subtitle), say (spoken; spelled out where needed).
Writes timeline.js + narration.wav.   Needs: espeak-ng, mbrola-us2.
"""
import json
import os
import subprocess
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE, SPEED, RATE = "mb-us2", 140, 16000
GAP_BEFORE, GAP_AFTER, MIN_SCENE = 0.6, 1.2, 4.5

S = []
def scene(id, text, say=None, part=None):
    S.append(dict(id=id, text=text, say=say or text, part=part))

# ---------------------------------------------------------------- getting ready
scene("intro", "This video shows the complete build, from the five printed plates to a working hand. Pause after each step and copy it.",
      part="Getting ready")
scene("tools", "You need the printed plates, 1.75 mm filament for the pins, side cutters, a lighter, super glue, a small Phillips screwdriver, scissors, a ruler, a pen, tape and four 2-euro coins.",
      "You need the printed plates, 1.75 millimetre filament for the pins, side cutters, a lighter, super glue, a small Phillips screwdriver, scissors, a ruler, a pen, tape, and four two euro coins.")
scene("plates", "Here are the five plates. Plate 1: index finger and five spools. Plate 2: the other fingers. Plate 3: palm. Plate 4: servo spine. Plate 5: stand.",
      "Here are the five plates. Plate one: the index finger and five spools. Plate two: the other fingers. Plate three: the palm. Plate four: the servo spine. Plate five: the stand.")
scene("remove", "Let each plate cool down, then flex the bed or use a scraper to take the parts off. Peel off the brim and trim any thin plastic strings with the side cutters.",
      "Let each plate cool down, then flex the bed, or use a scraper, to take the parts off. Peel off the brim, and trim any thin plastic strings with the side cutters.")
scene("sort", "Sort the bones by finger and lay them out in order: lower bone, middle bone, tip. The thumb has only two bones.",
      "Sort the bones by finger, and lay them out in order. Lower bone, middle bone, and tip. The thumb has only two bones.")
scene("pins", "Make the pins: cut 1.75 mm filament into pieces 17 mm long. You need about 35: 14 for the joints, 14 to lock the elastic, 4 for the spine and palm, plus a few spares.",
      "Make the pins. Cut 1.75 millimetre filament into pieces 17 millimetres long. You need about 35. 14 for the joints, 14 to lock the elastic, 4 for the spine and the palm, plus a few spares.")
scene("clean", "Push a piece of filament through every pin hole and every channel to clear them. In the centre tab the pin must turn freely; in the side forks it should be snug.",
      "Push a piece of filament through every pin hole, and every channel, to clear them. In the centre tab, the pin must turn freely. In the side forks, it should be snug.")

# ---------------------------------------------------------------- fingers
scene("joint1", "Build the index finger first. Slide the centre tab of the middle bone between the two forks of the lower bone. The flat lip goes on the back of the finger.",
      "Build the index finger first. Slide the centre tab of the middle bone, between the two forks of the lower bone. The flat lip goes on the back of the finger.", part="Fingers")
scene("pin1", "Push a pin through. Heat each end for a moment with the lighter and press it flat with something metal, so it can't slide out.",
      "Push a pin through. Heat each end for a moment with the lighter, and press it flat with something metal, so it can't slide out.")
scene("joint2", "Join the fingertip the same way, with another pin.",
      "Join the fingertip the same way, with another pin.")
scene("bendcheck", "Check: the finger bends forward freely and stops when it is straight. It must not bend backwards.",
      "Check. The finger bends forward freely, and stops when it is straight. It must not bend backwards.")
scene("string", "The string: cut 60 cm of braided line and tie a fat double knot at one end. Thread it from the fingertip down the thin palm-side channel until the knot sits in the tip. Add a drop of super glue on the knot.",
      "The string. Cut 60 centimetres of braided line, and tie a fat double knot at one end. Thread it from the fingertip down the thin channel on the palm side, until the knot sits in the tip. Add a drop of super glue on the knot.")
scene("elastic1", "The elastic: cut 25 cm of 2 mm cord. Thread it from the tip down the wide channel on the back. Push a pin through the cross hole of the tip bone to lock it.",
      "The elastic. Cut 25 centimetres of 2 millimetre cord. Thread it from the tip down the wide channel on the back. Push a pin through the cross hole of the tip bone, to lock it.")
scene("elastic2", "Mark two lines 50 mm apart on the cord below the finger. Pull until they are 75 mm apart and, holding it, push pins into the cross holes of the middle and lower bone. Leave the rest hanging.",
      "Mark two lines, 50 millimetres apart, on the cord below the finger. Pull until they are 75 millimetres apart. And while holding it, push pins into the cross holes of the middle and lower bone. Leave the rest hanging.")
scene("others", "Build the thumb, middle, ring and little finger exactly the same way. The thumb has two bones, so it needs one joint pin and two lock pins.",
      "Build the thumb, middle, ring, and little finger exactly the same way. The thumb has two bones, so it needs one joint pin, and two lock pins.")

# ---------------------------------------------------------------- stand + spine + servos
scene("stand", "Take the stand. Press a 2-euro coin into each corner pocket with a drop of glue. Four dots of hot glue underneath make non-slip feet.",
      "Take the stand. Press a two euro coin into each corner pocket, with a drop of glue. Four dots of hot glue underneath make non slip feet.", part="Stand, spine and servos")
scene("frontdot", "Look at the spine. The small round dot below the top marks the FRONT, the palm side. Three servos mount on the front, two on the back.",
      "Look at the spine. The small round dot, just below the top, marks the front, the palm side. Three servos mount on the front, and two on the back.")
scene("servos", "Push each servo through its window from the spool side, so the tabs rest on the spine and the shaft is at the top of the window. Fix it with its two screws.",
      "Push each servo through its window from the spool side, so the tabs rest on the spine, and the shaft is at the top of the window. Fix it with its two screws.")
scene("servo_order", "From the top: 1 middle, front. 2 index, back. 3 thumb, front. 4 ring, back. 5 little, front. Label every servo cable with tape.",
      "From the top. One: middle finger, front. Two: index, back. Three: thumb, front. Four: ring, back. Five: little finger, front. Label every servo cable with tape.")
scene("spine_stand", "Slide the spine into the stand's slot, front dot facing away from the breadboard tray, and lock it with two pins.",
      "Slide the spine into the stand's slot, with the front dot facing away from the breadboard tray, and lock it with two pins.")

# ---------------------------------------------------------------- electronics + spools
scene("elec", "Now do the wiring exactly as in the wiring video: breadboard into the tray behind the spine, ESP32 into the breadboard, then all five servos.",
      "Now do the wiring exactly as shown in the wiring video. The breadboard goes into the tray behind the spine, the E S P 32 into the breadboard, and then all five servos.", part="Electronics and spools")
scene("open_angles", "Upload the firmware and switch everything on. Every servo turns to its open angle. Keep the power on for the next step.",
      "Upload the firmware, and switch everything on. Every servo turns to its open angle. Keep the power on for the next step.")
scene("spools", "Press a single-arm horn onto each shaft and fix it with the small centre screw. Glue a spool flat onto each horn, centred on the shaft. Let the glue cure for five minutes.",
      "Press a single arm horn onto each shaft, and fix it with the small centre screw. Glue a spool flat onto each horn, centred on the shaft. Let the glue cure for five minutes.")
scene("power_off", "Now unplug the power. Always unplug before working on the hand.",
      "Now unplug the power. Always unplug before working on the hand.")

# ---------------------------------------------------------------- hand
scene("palm_fingers", "Take the palm. Pin each finger to its knuckle fork, just like the finger joints. The thumb goes on the angled boss on the side.",
      "Take the palm. Pin each finger to its knuckle fork, just like the finger joints. The thumb goes on the angled boss on the side.", part="Palm and strings")
scene("knots", "Each elastic comes out on the back of the palm. Pull it until the finger is straight and firm, and tie a fat knot against the palm.",
      "Each elastic comes out on the back of the palm. Pull it until the finger is straight and firm, and tie a fat knot against the palm.")
scene("bundle", "The five strings come out under the wrist. Bundle their ends with a piece of tape so they don't tangle.",
      "The five strings come out under the wrist. Bundle their ends with a piece of tape, so they don't tangle.")
scene("palm_spine", "Feed the strings down beside the spine, push the palm onto the spine's top tab, and lock it with two pins.",
      "Feed the strings down beside the spine, push the palm onto the spine's top tab, and lock it with two pins.")
scene("strings", "Each string runs straight down to its own spool, in the same order as the servos: middle, index, thumb, ring, little.",
      "Each string runs straight down to its own spool, in the same order as the servos. Middle, index, thumb, ring, and little.")
scene("tie", "Power on. For each finger move its slider to 30 % and back, and watch which way the spool turns. Wrap the string once in that direction, pull it just tight with the finger straight, and tie it through the anchor hole.",
      "Power on. For each finger, move its slider to 30 percent and back, and watch which way the spool turns. Wrap the string once around the spool in that direction, pull it just tight with the finger straight, and tie it through the anchor hole.")

# ---------------------------------------------------------------- test
scene("test", "Now move each slider slowly. The finger should curl smoothly, the base joint first, then the middle, then the tip.",
      "Now move each slider slowly. The finger should curl smoothly. The base joint first, then the middle, then the tip.", part="Test and calibrate")
scene("calibrate", "Calibrate each finger in the Serial Monitor: a, finger number, angle. Find straight, and fully bent a few degrees before it presses hard. Put the numbers in FINGERS and upload again. Stop the thumb before it touches the palm.",
      "Calibrate each finger in the Serial Monitor. Type a, the finger number, and an angle. Find straight, and fully bent, a few degrees before it presses hard. Put the numbers into the FINGERS list, and upload again. Stop the thumb before it touches the palm.")
scene("tune", "Tuning: a finger that doesn't open fully needs more elastic stretch. A servo that hums or struggles needs less. A string that slips needs retying tighter on the spool.",
      "Tuning. A finger that doesn't open fully needs more elastic stretch. A servo that hums or struggles needs less. And a string that slips needs retying, tighter, on the spool.")
scene("final", "And that's it: your RoboHand is complete. Try the gesture buttons: fist, point, peace, thumbs up, pinch and rock on.",
      "And that's it. Your RoboHand is complete. Try the gesture buttons. Fist, point, peace, thumbs up, pinch, and rock on.", part="Done")
scene("outro", "Have fun with it. Next steps: a wrist, a movable thumb base, and then the rolling station.",
      "Have fun with it. The next steps are a wrist, a movable thumb base, and then the rolling station.")
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
