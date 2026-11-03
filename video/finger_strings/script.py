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

scene("intro", "This video shows how to put the string and the elastic into one finger. Afterwards you do exactly the same for the other four fingers.",
      "This video shows how to put the string, and the elastic, into one finger. Afterwards, you do exactly the same for the other four fingers.")
scene("items", "From your shopping list you need item 1, the braided fishing line (0.30 mm), and item 2, the 2 mm rubber cord. Also: super glue, scissors, a ruler, a pen and three 1.7 cm filament pins.",
      "From your shopping list, you need item one, the braided fishing line, zero point three millimetres. And item two, the two millimetre rubber cord. Also: super glue, scissors, a ruler, a pen, and three filament pins, 1.7 centimetres long.", part="What you need")
scene("sides", "First find the two sides of the finger. The BACK has a small flat lip at each joint. The other side is the PALM side. The finger bends towards the palm side.",
      "First, find the two sides of the finger. The back has a small flat lip at each joint. The other side is the palm side. The finger bends towards the palm side.", part="Know your finger")
scene("channels", "Inside, two long holes run through all the bones: a THIN one on the palm side for the string, and a WIDE one on the back for the elastic.",
      "Inside, two long holes run through all the bones. A thin one on the palm side, for the string. And a wide one on the back, for the elastic.")
scene("tipholes", "Look at the end of the fingertip: you can see both holes. The thin hole near the palm side has a small pocket around it. That pocket holds the knot.",
      "Look at the end of the fingertip. You can see both holes. The thin hole, near the palm side, has a small pocket around it. That pocket holds the knot.")

scene("cut_line", "Part 1, the string. Cut 60 cm of the braided fishing line.",
      "Part one, the string. Cut 60 centimetres of the braided fishing line.", part="The string")
scene("knot", "Tie a knot at one end: make a loop, pass the end through it, and pull tight. Then tie a second knot right on top of the first. This double knot is fatter than the hole, so it can't slip through.",
      "Tie a knot at one end. Make a loop, pass the end through it, and pull tight. Then tie a second knot, right on top of the first one. This double knot is fatter than the hole, so it can't slip through.")
scene("stiffen", "Tip: braided line is floppy. Put a drop of super glue on the last 2 cm of the OTHER end and let it dry. Cut it at an angle. Now it is stiff like a needle.",
      "A tip. Braided line is floppy. Put a drop of super glue on the last two centimetres of the other end, and let it dry. Cut it at an angle. Now it is stiff, like a needle.")
scene("thread_in", "Push the stiff end into the THIN hole at the fingertip.",
      "Push the stiff end into the thin hole at the fingertip.")
scene("thread_through", "Keep pushing. At every joint the line crosses a small gap. Bend the finger a little so the next hole lines up, and guide the line in. If it gets stuck, clear the hole with a piece of filament first.",
      "Keep pushing. At every joint, the line crosses a small gap. Bend the finger a little, so the next hole lines up, and guide the line in. If it gets stuck, clear the hole with a piece of filament first.")
scene("pull", "The line comes out at the other end of the finger, under the round tab. Pull it until the knot sits tight in the pocket at the fingertip.",
      "The line comes out at the other end of the finger, under the round tab. Pull it, until the knot sits tight in the pocket at the fingertip.")
scene("glue", "Put ONE small drop of super glue on the knot and let it dry for a minute. Keep glue away from the joints.",
      "Put one small drop of super glue on the knot, and let it dry for a minute. Keep glue away from the joints.")

scene("cut_elastic", "Part 2, the elastic. Cut 25 cm of the 2 mm rubber cord. Cut the end at an angle; a little tape wrapped around the end makes it easier to push.",
      "Part two, the elastic. Cut 25 centimetres of the two millimetre rubber cord. Cut the end at an angle. A little tape wrapped around the end makes it easier to push.", part="The elastic")
scene("elastic_in", "Push the elastic into the WIDE hole at the fingertip, on the back side, and through all the bones until it comes out at the other end.",
      "Push the elastic into the wide hole at the fingertip, on the back side, and through all the bones, until it comes out at the other end.")
scene("lock_tip", "Lock it in the tip: push a 1.7 cm filament pin through the small cross hole in the side of the tip bone. The pin pinches the elastic.",
      "Lock it in the tip. Push a 1.7 centimetre filament pin through the small cross hole, in the side of the tip bone. The pin pinches the elastic.")
scene("marks", "Below the finger, make two pen marks on the elastic, 5 cm apart.",
      "Below the finger, make two pen marks on the elastic, five centimetres apart.")
scene("stretch", "Pull the elastic until the two marks are 7.5 cm apart, and hold it there.",
      "Pull the elastic, until the two marks are 7.5 centimetres apart, and hold it there.")
scene("lock_rest", "While holding it, push pins through the cross holes of the middle bone and the lower bone. Then let go.",
      "While holding it, push pins through the cross holes of the middle bone, and the lower bone. Then let go.")

scene("check", "Check: bend the finger and let go. It springs back straight. Pull the string: the finger curls.",
      "Check. Bend the finger, and let go. It springs back straight. Pull the string. The finger curls.", part="Check")
scene("ends", "Leave the loose ends of the string and the elastic hanging. They are connected later at the palm and the servo spools.",
      "Leave the loose ends of the string and the elastic hanging. They are connected later, at the palm, and at the servo spools.")
scene("others", "Now do the same for the other fingers. The thumb has only two bones, so it needs two lock pins instead of three.",
      "Now do the same for the other fingers. The thumb has only two bones, so it needs two lock pins, instead of three.")
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
