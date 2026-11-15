const { chromium } = require('playwright'); const path = require('path');
(async () => { const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  await p.goto('file://' + path.join(__dirname, 'wiring.html')); await p.waitForFunction('window.READY === true');
  const t = await p.evaluate(() => { const s = window.TIMELINE.scenes.find(x => x.id === 'w_esp_check'); return s.t0 + s.dur - 0.3; });
  for (const v of ['top', 'side']) { await p.evaluate(([tt, vv]) => window.renderView(tt, vv), [t, v]); await p.screenshot({ path: path.join(__dirname, `view_${v}.png`) }); }
  await b.close(); console.log('ok'); })();
