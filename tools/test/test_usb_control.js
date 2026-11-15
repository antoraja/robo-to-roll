// Drives tools/usb_control.html with a fake ESP32 serial port and checks what it sends.  node tools/test/test_usb_control.js
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
(async () => {
  const fails = []; const ok = (c, m) => { console.log((c ? 'ok:   ' : 'FAIL: ') + m); if (!c) fails.push(m); };
  // finger table must match the firmware
  const ino = fs.readFileSync(path.join(__dirname, '../../firmware/finger_control/finger_control.ino'), 'utf8');
  const fw = [...ino.matchAll(/\{"(\w+)",\s*(\d+),\s*(\d+),\s*(\d+)\}/g)].map(m => [m[1], +m[2], +m[3], +m[4]]);
  const html = fs.readFileSync(path.join(__dirname, '../usb_control.html'), 'utf8');
  const page_ = [...html.matchAll(/\{ name: '(\w+)',\s*pin: (\d+), open: (\d+), closed: (\d+) \}/g)].map(m => [m[1], +m[2], +m[3], +m[4]]);
  ok(JSON.stringify(fw) === JSON.stringify(page_), 'page finger order, pins and default angles = firmware FINGERS[] ' + JSON.stringify(page_));

  const b = await chromium.launch(); const p = await b.newPage();
  await p.addInitScript(() => {
    window.SENT = [];
    const dec = new TextDecoder(); let push;
    const readable = new ReadableStream({ start(c) { push = c; } });
    const writable = new WritableStream({ write(chunk) { const s = dec.decode(chunk); window.SENT.push(s);
      push.enqueue(new TextEncoder().encode('OK -> ' + s.trim() + '\r\n')); } });
    const port = { open: async (o) => { window.BAUD = o.baudRate; }, close: async () => { window.CLOSED = true; }, readable, writable };
    Object.defineProperty(navigator, 'serial', { value: { requestPort: async () => port } });
  });
  const errors = []; p.on('pageerror', e => errors.push(String(e)));
  await p.goto('file://' + path.join(__dirname, '../usb_control.html')); await p.waitForFunction('window.ROBOHAND_READY');
  await p.evaluate(() => localStorage.clear()); await p.reload(); await p.waitForFunction('window.ROBOHAND_READY');
  await p.click('#connect'); await p.waitForTimeout(100);
  ok(await p.evaluate(() => window.BAUD) === 115200, 'opens the port at 115200 baud');
  ok((await p.textContent('#status')) === 'connected', 'status shows connected');
  const idx = p.locator('#cal .cal').nth(1);                      // Index = finger 1
  await idx.locator('[data-d="5"]').click(); await idx.locator('[data-d="5"]').click(); await idx.locator('[data-d="-1"]').click();
  await p.waitForTimeout(50);
  let sent = await p.evaluate(() => window.SENT.slice());
  ok(JSON.stringify(sent) === JSON.stringify(['a 1 15\n', 'a 1 20\n', 'a 1 19\n']), 'step buttons send "a 1 <angle>\\n" for the index: ' + JSON.stringify(sent));
  await idx.locator('[data-set="open"]').click();
  await idx.locator('input').fill('137'); await idx.locator('input').dispatchEvent('change'); await p.waitForTimeout(200);
  await idx.locator('[data-set="closed"]').click();
  const code = await p.textContent('#code');
  ok(code.includes('{"Index",  13,  19, 137},'), 'generated firmware line for the index: open 19, closed 137');
  ok(code.includes('{"Thumb",  25,  10, 115},') && code.includes('{"Little", 26,  10, 150},'), 'other fingers keep the firmware defaults');
  ok(/FingerConfig FINGERS\[\] = \{[\s\S]*\};/.test(code), 'code block is a complete FINGERS[] array');
  // the generated block must compile in the firmware: splice it in and compare parsed values
  const spliced = ino.replace(/FingerConfig FINGERS\[\] = \{[\s\S]*?\n\};/, code);
  const parsed = [...spliced.matchAll(/\{"(\w+)",\s*(\d+),\s*(\d+),\s*(\d+)\}/g)].map(m => m[1] + m[2] + ':' + m[3] + '-' + m[4]);
  ok(parsed.join(' ') === 'Thumb25:10-115 Index13:19-137 Middle14:10-150 Ring27:10-150 Little26:10-150', 'pasted into the .ino it gives ' + parsed.join(' '));
  fs.writeFileSync('/tmp/robohand_spliced.ino', spliced);
  ok(await p.evaluate(() => JSON.parse(localStorage.getItem('robohand-calibration-v1'))[1].closed) === 137, 'saved angles kept in the browser');
  // % pane
  await p.click('#tab-pct'); await p.evaluate(() => window.SENT.length = 0);
  const mid = p.locator('#pct input').nth(2);
  await mid.fill('40'); await mid.dispatchEvent('change'); await p.waitForTimeout(200);
  sent = await p.evaluate(() => window.SENT.slice());
  ok(sent[sent.length - 1] === 'f 2 40\n', 'middle slider sends "f 2 40": ' + JSON.stringify(sent));
  await p.click('#openall'); await p.waitForTimeout(50);
  sent = await p.evaluate(() => window.SENT.slice());
  ok(sent[sent.length - 1] === 'open\n', '"Open all" sends "open"');
  ok(!(await p.locator('text=Close all').count()), 'no "Close all" button (not safe before calibration)');
  const logText = await p.textContent('#log');
  ok(logText.includes('OK -> a 1 19') && logText.includes('OK -> f 2 40'), 'replies from the ESP32 appear in the message box');
  // throttle: fast drag sends few commands, last one = final value
  await p.evaluate(() => window.SENT.length = 0);
  await p.evaluate(() => { const s = document.querySelectorAll('#pct input')[0]; for (let v = 1; v <= 60; v++) { s.value = v; s.dispatchEvent(new Event('input')); } });
  await p.waitForTimeout(300);
  sent = await p.evaluate(() => window.SENT.slice());
  ok(sent.length <= 3 && sent[sent.length - 1] === 'f 0 60\n', `dragging the thumb 1->60 quickly sends ${sent.length} commands, ending at 60`);
  // gestures must equal the firmware's GESTURES[]
  const fwG = [...ino.matchAll(/\{"([\w ]+)",\s*\{([\d, ]+)\}\}/g)].map(m => m[1] + ':' + m[2].replace(/\s/g, ''));
  const pgG = [...html.matchAll(/\{ name: '([\w ]+)',\s*pct: \[([\d, ]+)\] \}/g)].map(m => m[1] + ':' + m[2].replace(/\s/g, ''));
  ok(fwG.length === 7 && JSON.stringify(fwG) === JSON.stringify(pgG), 'page gestures = firmware GESTURES[] ' + pgG.join(' '));
  await p.evaluate(() => window.SENT.length = 0);
  await p.click('#gestures button:has-text("Peace")'); await p.waitForTimeout(100);
  sent = await p.evaluate(() => window.SENT.slice());
  ok(JSON.stringify(sent) === JSON.stringify(['f 0 70\n', 'f 1 0\n', 'f 2 0\n', 'f 3 100\n', 'f 4 100\n']), 'Peace sends f 0 70, f 1 0, f 2 0, f 3 100, f 4 100');
  ok(await p.locator('#pct input').nth(3).inputValue() === '100', 'finger sliders follow the gesture');
  await p.evaluate(() => window.SENT.length = 0);
  await p.check('#grp-checks input[data-i="1"]'); await p.check('#grp-checks input[data-i="2"]');
  await p.locator('#grp').fill('40'); await p.locator('#grp').dispatchEvent('change'); await p.waitForTimeout(250);
  sent = await p.evaluate(() => window.SENT.slice());
  const last = {}; sent.forEach(c => { const m = c.match(/^f (\d) (\d+)/); if (m) last[m[1]] = +m[2]; });
  ok(JSON.stringify(last) === JSON.stringify({ 1: 40, 2: 40 }), 'Move together (index + middle ticked) moves only those two to 40 %: ' + JSON.stringify(sent));
  await p.click('#disconnect'); await p.waitForTimeout(100);
  ok(await p.evaluate(() => window.CLOSED) === true && (await p.textContent('#status')) === 'not connected', 'Disconnect closes the port (frees it for Arduino)');
  // no Web Serial (Firefox/Safari): clear message, connect disabled
  const p2 = await b.newPage(); await p2.addInitScript(() => Object.defineProperty(navigator, 'serial', { value: undefined }));
  await p2.goto('file://' + path.join(__dirname, '../usb_control.html'));
  ok(await p2.locator('#connect').isDisabled() && await p2.locator('#nosupport').isVisible(), 'other browsers: "use Chrome or Edge" message, Connect disabled');
  ok(!errors.length, 'no page errors ' + JSON.stringify(errors));
  ok(await p.evaluate(() => window.isSecureContext), 'opened from a file, the page is a secure context (Web Serial allowed)');
  await b.close();
  console.log(fails.length ? `\nUSB CONTROL TEST FAILED (${fails.length})` : '\nUSB CONTROL TEST PASSED'); process.exit(fails.length ? 1 : 0);
})();
