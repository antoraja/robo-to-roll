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

## Part 2: wiring & programming (`electronics/robohand_wiring_programming.mp4`, ~7.7 min, voice + subtitles)

For the exact parts on the order list (MG90S, ESP32 USB-C/CH340 30-pin, 400-hole breadboard,
5 V 3 A supply, DC socket adapter, 1000 µF capacitor, Elegoo 20 cm jumpers):
the parts → Arduino IDE, CH340 driver, ESP32 support, ESP32Servo, upload → wiring step by step →
first test from the phone → all five servos → calibration → troubleshooting.

```bash
sudo apt-get install espeak-ng mbrola-us2   # offline voice
cd electronics
python script.py                 # narration text -> narration.wav + timeline.js
node render.js --part 0/3 & node render.js --part 1/3 & node render.js --part 2/3 & wait
node render.js --encode          # frames + narration -> MP4
```
