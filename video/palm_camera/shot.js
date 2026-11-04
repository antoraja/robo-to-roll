const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(String(e)));
  await p.goto('file://' + path.join(__dirname, 'cam.html'));
  await p.waitForFunction('window.READY === true', null, { timeout: 120000 });
  await p.screenshot({ path: path.join(__dirname, 'palm_camera.png'), fullPage: true });
  console.log('ok', errs); await b.close();
})();
