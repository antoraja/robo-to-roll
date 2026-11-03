"""Narration for the close-up video: string + elastic into one finger.  Writes timeline.js + narration.wav."""
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

scene("intro", "This video shows how to put the string and the elastic into one finger, the updated way: no glue and no lock pins. Afterwards you do the same for the other four fingers.",
      "This video shows how to put the string and the elastic into one finger, the updated way. No glue, and no lock pins. Afterwards, you do the same for the other four fingers.")
scene("items", "From your shopping list: item 1, the braided fishing line (0.30 mm), and item 2, the 2 mm rubber cord. Also: a 5 mm piece of printer filament, scissors or side cutters, a ruler, a pen and a lighter.",
      "From your shopping list, you need item one, the braided fishing line, zero point three millimetres. And item two, the two millimetre rubber cord. Also: a five millimetre piece of printer filament, scissors or side cutters, a ruler, a pen, and a lighter.", part="What you need")
scene("sides", "First find the two sides of the finger. The BACK has a small flat lip at each joint. The other side is the PALM side. The finger bends towards the palm side.",
      "First, find the two sides of the finger. The back has a small flat lip at each joint. The other side is the palm side. The finger bends towards the palm side.", part="Know your finger")
scene("channels", "Inside, two long holes run through all the bones: a THIN one on the palm side for the string, and a WIDE one on the back for the elastic.",
      "Inside, two long holes run through all the bones. A thin one on the palm side, for the string. And a wide one on the back, for the elastic.")
scene("tipholes", "At the fingertip you can see both holes. The thin hole sits in a small notch near the palm side. The wide hole is near the back.",
      "At the fingertip, you can see both holes. The thin hole sits in a small notch, near the palm side. The wide hole is near the back.")
scene("cut_line", "Part 1, the string. Cut 60 cm of the braided fishing line.",
      "Part one, the string. Cut 60 centimetres of the braided fishing line.", part="The string")
scene("toggle", "Cut a 5 mm piece of filament: this is the toggle. Lay the line over its middle and tie it around the piece with three tight knots. Melt the short tail with the lighter.",
      "Cut a five millimetre piece of filament. This is the toggle. Lay the line over its middle, and tie it around the piece with three tight knots. Melt the short tail with the lighter.")
scene("why_toggle", "Why: a knot alone slips through the 2 mm hole, because the line is so thin. The 5 mm toggle lies across the hole and can never pull through. No glue needed.",
      "Why? A knot alone slips through the two millimetre hole, because the line is so thin. The five millimetre toggle lies across the hole, and can never pull through. No glue needed.")
scene("thread_in", "Cut the free end of the line at an angle and push it into the THIN hole at the fingertip.",
      "Cut the free end of the line at an angle, and push it into the thin hole at the fingertip.")
scene("thread_through", "Keep pushing. At every joint the line crosses a small gap. Bend the finger a little so the next hole lines up, and guide the line in. If it gets stuck, clear the hole with a piece of filament first.",
      "Keep pushing. At every joint, the line crosses a small gap. Bend the finger a little, so the next hole lines up, and guide the line in. If it gets stuck, clear the hole with a piece of filament first.")
scene("pull", "The line comes out at the other end, under the round tab. Pull until the toggle lies across the notch at the fingertip.",
      "The line comes out at the other end, under the round tab. Pull, until the toggle lies across the notch at the fingertip.")
scene("cut_elastic", "Part 2, the elastic. Cut 25 cm of the 2 mm rubber cord, and tie a fat double knot at one end.",
      "Part two, the elastic. Cut 25 centimetres of the two millimetre rubber cord, and tie a fat double knot at one end.", part="The elastic")
scene("elastic_in", "Push the other end into the WIDE hole at the fingertip, on the back, and through all the bones, until the knot sits against the fingertip.",
      "Push the other end into the wide hole at the fingertip, on the back, and through all the bones, until the knot sits against the fingertip.")
scene("no_pins", "Leave the small cross holes in the middle of the bones EMPTY. Lock pins are not used any more: they cannot grip the 2 mm cord.",
      "Leave the small cross holes in the middle of the bones empty. Lock pins are not used any more. They cannot grip the two millimetre cord.")
scene("hang", "Leave the rest of the elastic hanging out of the bottom of the finger. It is stretched and knotted later, at the palm.",
      "Leave the rest of the elastic hanging out of the bottom of the finger. It is stretched, and knotted, later, at the palm.")
scene("later_palm", "Later, at the palm: make two pen marks 5 cm apart on the hanging elastic, pull until they are 7.5 cm apart with the finger straight, and tie a fat knot against the back of the palm.",
      "Later, at the palm. Make two pen marks, five centimetres apart, on the hanging elastic. Pull until they are 7.5 centimetres apart, with the finger straight, and tie a fat knot against the back of the palm.", part="Later, at the palm")
scene("check", "Check now: the finger bends freely, and pulling the string curls it. It springs back straight once the elastic is knotted at the palm.",
      "Check now. The finger bends freely, and pulling the string curls it. It springs back straight, once the elastic is knotted at the palm.", part="Check")
scene("others", "Do the same for the other fingers. The thumb works exactly the same way, it just has two bones.",
      "Do the same for the other fingers. The thumb works exactly the same way. It just has two bones.")


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
