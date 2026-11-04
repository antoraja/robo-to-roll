"""Narration for the short video: tying the elastic knots on the back of the palm.  Writes timeline.js + narration.wav."""
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

scene("intro", "How to tie the elastic knots on the back of the palm. Each finger's elastic is already threaded through the finger and hangs out of the palm.",
      "This short video shows how to tie the elastic knots on the back of the palm. Each finger's elastic is already threaded through the finger, and hangs out of the palm.")
scene("where", "Look at the BACK of the palm. Each finger's elastic comes out of its own small hole just below the knuckles. The thumb's hole is lower, near the thumb.",
      "Look at the back of the palm. Each finger's elastic comes out of its own small hole, just below the knuckles. The thumb's hole is lower, near the thumb.", part="Find the holes")
scene("straight", "One finger at a time. The finger is pinned to the palm and STRAIGHT. Its elastic hangs out of the hole.",
      "Do one finger at a time. The finger is pinned to the palm, and straight. Its elastic hangs out of the hole.", part="Step by step")
scene("mark", "With a pen, put two dots on the elastic, 5 cm apart. The first dot just below the hole.",
      "With a pen, put two dots on the elastic, five centimetres apart. The first dot, just below the hole.")
scene("stretch", "Keep the finger straight and pull the elastic down until the dots are 7.5 cm apart. The rubber gets a bit thinner: that's normal.",
      "Keep the finger straight, and pull the elastic down, until the dots are seven and a half centimetres apart. The rubber gets a bit thinner. That is normal.")
scene("pinch", "Hold the stretch. Pinch the elastic right at the hole, with your fingers or a clothes peg, so it can't slide back in.",
      "Hold the stretch. Pinch the elastic right at the hole, with your fingers or a clothes peg, so it can't slide back in.")
scene("knot", "Just below the pinch, tie a fat double knot and pull it tight.",
      "Just below the pinch, tie a fat double knot, and pull it tight.")
scene("release", "Let go. The elastic pulls the knot up against the palm. The knot is bigger than the hole, so it can't go back in.",
      "Let go. The elastic pulls the knot up against the palm. The knot is bigger than the hole, so it can't go back in.")
scene("check", "Check: bend the finger and let go. It should spring back straight on its own.",
      "Now check. Bend the finger, and let go. It should spring back straight, on its own.", part="Check and adjust")
scene("adjust", "Finger floppy? Untie and stretch a little more. Servo hums or struggles to close the finger? Stretch a little less. Adjust BEFORE you trim.",
      "If the finger is floppy, untie, and stretch a little more. If the servo hums, or struggles to close the finger, stretch a little less. Do this before you trim.")
scene("trim", "When you're happy, cut off the spare elastic, leaving about 1 cm after the knot.",
      "When you are happy, cut off the spare elastic, leaving about one centimetre after the knot.")
scene("all", "Do the same for the other four fingers, including the thumb. Done: all five elastics are knotted on the back of the palm.",
      "Do the same for the other four fingers, including the thumb. Done. All five elastics are knotted on the back of the palm.", part="All five")


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
