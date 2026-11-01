// Render the build-guide video:  node render.js [--frames a:b] [--still t1,t2,...]
// Needs: npm install (three), python export_scene.py (scene.json), ffmpeg.
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const { chromium } = require('playwright');

(async () => {
  const here = __dirname;
  fs.writeFileSync(path.join(here, 'scene.js'), 'window.SCENE=' + fs.readFileSync(path.join(here, 'scene.json'), 'utf8') + ';');
  const args = process.argv.slice(2);
  const stillArg = args.indexOf('--still');
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto('file://' + path.join(here, 'tutorial.html'));
  await page.waitForFunction('window.READY === true', null, { timeout: 120000 });
  if (errors.length) { console.error('page errors:', errors); }
  const { FPS, DURATION } = await page.evaluate(() => ({ FPS: window.FPS, DURATION: window.DURATION }));

  if (stillArg >= 0) {
    const times = args[stillArg + 1].split(',').map(Number);
    for (const t of times) {
      await page.evaluate(tt => window.renderAt(tt), t);
      await page.screenshot({ path: path.join(here, `still_${String(t).replace('.', '_')}.png`) });
    }
    console.log('stills done', errors.length ? errors : '');
    await browser.close();
    return;
  }

  const outDir = path.join(here, 'frames');
  fs.mkdirSync(outDir, { recursive: true });
  const total = Math.round(FPS * DURATION);
  const t0 = Date.now();
  // --part k/n renders every n-th frame starting at k (run several in parallel); existing frames are skipped
  const partArg = args.indexOf('--part');
  const [k, n] = partArg >= 0 ? args[partArg + 1].split('/').map(Number) : [0, 1];
  for (let f = k; f < total; f += n) {
    const file = path.join(outDir, `f${String(f).padStart(5, '0')}.jpg`);
    if (fs.existsSync(file) && fs.statSync(file).size > 0) continue;
    await page.evaluate(tt => window.renderAt(tt), f / FPS);
    await page.screenshot({ path: file, type: 'jpeg', quality: 90 });
    if (f % 200 < n) console.log(`frame ${f}/${total}  ${((Date.now() - t0) / 1000).toFixed(0)} s`);
  }
  await browser.close();
  if (partArg >= 0) { console.log('part done', k, n); return; }
  const out = path.join(here, 'robohand_build_guide.mp4');
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(outDir, 'f%05d.jpg'),
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '24', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]);
  console.log('wrote', out, (fs.statSync(out).size / 1e6).toFixed(1), 'MB', errors.length ? errors : '');
})();
