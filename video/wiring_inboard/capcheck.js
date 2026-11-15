const { chromium } = require('playwright');
(async () => { const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  await p.goto('file:///home/user/robo-to-roll/video/wiring_inboard/wiring.html'); await p.waitForFunction('window.READY === true');
  const r = await p.evaluate(() => window.CAPCHECK()); console.log(JSON.stringify(r));
  const dP = Math.abs(r.longY - r.P), dN = Math.abs(r.shortY - r.N);
  console.log(dP < 0.5 && dN < 0.5 && (r.stripeDY < 0) === (r.N < r.P) ? 'CAP OK: long leg in + rail, short leg + stripe on the - rail side' : 'CAP WRONG'); await b.close(); })();
