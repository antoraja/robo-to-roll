# Build-guide video

`robohand_build_guide.mp4` (1280 × 720, ~3 min) walks from the five print plates to the
finished hand in 13 steps, with on-screen captions (no voice-over), and ends with the
hand running through its gestures.

It's rendered from the real CAD parts, so it updates whenever the design changes:

```bash
python export_scene.py   # parts, plate positions and final positions -> scene.json
npm install              # three.js
node render.js           # renders frames with headless Chromium, encodes the MP4 with ffmpeg
node render.js --still 31,120   # quick preview frames (seconds)
```
