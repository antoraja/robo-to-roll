"""Narration for the short video: fitting a finger onto the palm with the new pin slots.  Writes timeline.js + narration.wav."""
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

scene("intro", "How to fit a finger onto the palm with the new pin slots. No side access needed: the pin goes in from above.",
      "This short video shows how to fit a finger onto the palm, using the new pin slots. No side access is needed. The pin goes in from above.")
scene("slots", "Each knuckle on the palm has two prongs. Each prong has a slot, open at the top, that ends in a round seat.",
      "Each knuckle on the palm has two prongs. Each prong has a slot, open at the top, that ends in a round seat.", part="The slots")
scene("pin", "Step 1: push a 17 mm piece of filament through the finger's own tab, so the same length sticks out on both sides.",
      "Step one. Push a seventeen millimetre piece of filament through the finger's own tab, so the same length sticks out on both sides.", part="Step by step")
scene("above", "Step 2: hold the finger straight, just above its knuckle and a little towards the back of the hand, so the pin ends line up with the slots.",
      "Step two. Hold the finger straight, just above its knuckle, and a little towards the back of the hand, so the pin ends line up with the slots.")
scene("lower", "Lower the finger: both pin ends slide down the slots.",
      "Lower the finger. Both pin ends slide down the slots.")
scene("nudge", "Step 3: at the bottom, nudge the finger towards the palm side. The pin drops into its seat. The elastic's pull keeps it there.",
      "Step three. At the bottom, nudge the finger towards the palm side. The pin drops into its seat. The elastic's pull keeps it there.")
scene("melt", "Step 4: lightly melt both pin ends with the lighter (small mushroom heads) so the pin can't slide out sideways. Keep the melted plastic off the palm.",
      "Step four. Lightly melt both pin ends with the lighter, to make small mushroom heads, so the pin can't slide out sideways. Keep the melted plastic off the palm.")
scene("check", "Check: the finger swings freely from straight to fully bent.",
      "Now check. The finger swings freely, from straight to fully bent.", part="Check")
scene("all", "Do the same for the other fingers and the thumb. The string and elastic can already be threaded: the pin passes between them.",
      "Do the same for the other fingers and the thumb. The string and elastic can already be threaded. The pin passes between them.", part="All five")


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
