"""Narration for the short video: fitting the spools on the servos and tying the strings.  Writes timeline.js + narration.wav."""
import json
import os
import subprocess
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE, SPEED, RATE = "mb-us2", 135, 16000
GAP_BEFORE, GAP_AFTER, MIN_SCENE = 0.6, 1.4, 4.5

S = []
def scene(id, text, say=None, part=None):
    S.append(dict(id=id, text=text, say=say or text, part=part))

scene("intro", "Fitting the spools (the round wheels) on the servos, then tying the strings. You need: the servo horns and small screws from the servo bags, super glue, a small Phillips screwdriver.",
      "This video shows how to fit the spools, the round wheels, on the servos, and then tie the strings. You need the servo horns and small screws from the servo bags, super glue, and a small Phillips screwdriver.")
scene("power", "First power on, with the firmware uploaded. Every servo turns to its OPEN position and holds it. Don't turn the shafts by hand.",
      "First, power on, with the firmware uploaded. Every servo turns to its open position, and holds it. Don't turn the shafts by hand.", part="Spools (power ON)")
scene("horn", "Press a single-arm horn straight onto the toothed shaft, as far as it goes. Which way the arm points doesn't matter.",
      "Press a single arm horn straight onto the toothed shaft, as far as it goes. Which way the arm points does not matter.")
scene("screw", "Fix it with the small centre screw (the shortest one in the bag). Firm, not forced.",
      "Fix it with the small centre screw, the shortest one in the bag. Firm, but not forced.")
scene("glue", "A few drops of super glue on the horn's flat face. Keep glue off the shaft and the screw.",
      "Put a few drops of super glue on the horn's flat face. Keep the glue off the shaft and the screw.")
scene("spool", "Press the spool flat onto the horn, centred on the shaft: through its centre hole you should see the screw. Hold it for 30 seconds.",
      "Press the spool flat onto the horn, centred on the shaft. Through its centre hole, you should see the screw. Hold it for thirty seconds.")
scene("all", "Same for all five servos. Let the glue cure for 5 minutes, then UNPLUG the power.",
      "Do the same for all five servos. Let the glue cure for five minutes, then unplug the power.")
scene("direction", "Strings: power on again. Move this finger's slider to 30 % and back, and watch which way its spool turns.",
      "Now the strings. Power on again. Move this finger's slider to thirty percent and back, and watch which way its spool turns.", part="Strings")
scene("wrap", "The string comes straight down from under the palm. Wrap it ONCE around the spool, in that same direction.",
      "The string comes straight down from under the palm. Wrap it once around the spool, in that same direction.")
scene("tie", "With the finger straight, pull the string just tight, pass it through the slot in the rim into the small hole, and tie it. Trim the end.",
      "With the finger straight, pull the string just tight, pass it through the slot in the rim, into the small hole, and tie it. Trim the end.")
scene("test", "Test: move the slider. The spool winds the string on, and the finger curls. Back to 0 %, the elastic opens it again.",
      "Test it. Move the slider. The spool winds the string on, and the finger curls. Back to zero percent, and the elastic opens it again.", part="Test")
scene("others", "Do the same for the other four strings: each runs straight down to its own spool. Middle, index, thumb, ring, little, from the top.",
      "Do the same for the other four strings. Each one runs straight down to its own spool. Middle, index, thumb, ring, and little, from the top.")


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
