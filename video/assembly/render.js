// Render the full assembly video:  node render.js [--part k/n] [--still t1,t2] [--encode]
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const { chromium } = require('playwright');
(async () => {
  const here = __dirname, args = process.argv.slice(2);
  const outDir = path.join(here, 'frames');
  const out = path.join(here, 'robohand_full_assembly.mp4');
  if (args.includes('--encode')) {
    const fps = Number(fs.readFileSync(path.join(outDir, 'fps.txt'), 'utf8'));
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(fps), '-i', path.join(outDir, 'f%05d.jpg'), '-i', path.join(here, 'narration.wav'),
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '23', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-shortest', '-movflags', '+faststart', out]);
    console.log('wrote', out, (fs.statSync(out).size / 1e6).toFixed(1), 'MB'); return;
  }
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  const errors = []; page.on('pageerror', e => errors.push(String(e))); page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto('file://' + path.join(here, 'assembly.html'));
  await page.waitForFunction('window.READY === true', null, { timeout: 120000 }).catch(() => {});
  if (errors.length) console.error('page errors:', errors);
  const { FPS, DURATION } = await page.evaluate(() => ({ FPS: window.FPS, DURATION: window.DURATION }));
  const si = args.indexOf('--still');
  if (si >= 0) {
    for (const t of args[si + 1].split(',').map(Number)) { await page.evaluate(tt => window.renderAt(tt), t); await page.screenshot({ path: path.join(here, `still_${t}.png`) }); }
    console.log('stills done', errors); await browser.close(); return;
  }
  fs.mkdirSync(outDir, { recursive: true }); fs.writeFileSync(path.join(outDir, 'fps.txt'), String(FPS));
  const pi = args.indexOf('--part'); const [k, n] = pi >= 0 ? args[pi + 1].split('/').map(Number) : [0, 1];
  const total = Math.ceil(FPS * DURATION);
  for (let f = k; f < total; f += n) {
    const file = path.join(outDir, `f${String(f).padStart(5, '0')}.jpg`);
    if (fs.existsSync(file) && fs.statSync(file).size > 0) continue;
    await page.evaluate(tt => window.renderAt(tt), f / FPS);
    await page.screenshot({ path: file, type: 'jpeg', quality: 90 });
    if (f % 300 < n) console.log(`frame ${f}/${total}`);
  }
  await browser.close(); console.log('part done', k, n, errors);
})();
