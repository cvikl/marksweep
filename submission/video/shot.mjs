// Headless capture of Marksweep screens. Uses the puppeteer-core already on this machine.
// node shot.mjs '<json shots>'  -> remotion/public/<name>.png + rects-<name>.json (data-shot rects)
import puppeteer from '/home/timotej/Avtonet-WebApp/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js';
import fs from 'fs'; import { fileURLToPath } from 'url';
const CHROME = '/home/timotej/.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome';
const OUT = fileURLToPath(new URL('./remotion/public/', import.meta.url));
const base = process.env.BASE || 'http://127.0.0.1:8766';
const shots = JSON.parse(process.argv[2] || '[]');
const browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ['--no-sandbox', '--hide-scrollbars', '--force-device-scale-factor=1'] });
const page = await browser.newPage();
await page.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: 'light' }]);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
for (const s of shots) {
  await page.setViewport({ width: 1920, height: s.height ?? 1080, deviceScaleFactor: 1 });
  await page.goto(base + s.path, { waitUntil: 'networkidle0', timeout: 60000 });
  await sleep(s.wait ?? 1500);
  for (const step of s.steps ?? []) {
    if (step.click) { const el = await page.$(step.click); if (el) await el.click(); else console.error('no element', step.click); }
    if (step.eval) await page.evaluate(step.eval);
    if (step.type) { await page.type(step.type[0], step.type[1], { delay: 20 }); }
    await sleep(step.wait ?? 800);
  }
  await page.screenshot({ path: OUT + s.name + '.png', fullPage: s.full ?? true });
  const rects = await page.evaluate(() => {
    const out = {};
    for (const el of document.querySelectorAll('[data-shot]')) {
      const r = el.getBoundingClientRect(); if (r.width < 4 || r.height < 4) continue;
      out[el.getAttribute('data-shot')] = [Math.round(r.x + scrollX), Math.round(r.y + scrollY), Math.round(r.width), Math.round(r.height)];
    }
    out.__page = [document.documentElement.scrollWidth, document.documentElement.scrollHeight];
    return out;
  });
  fs.writeFileSync(OUT + 'rects-' + s.name + '.json', JSON.stringify(rects, null, 1));
  console.log('shot', s.name, rects.__page, Object.keys(rects).length - 1, 'rects');
}
await browser.close();
