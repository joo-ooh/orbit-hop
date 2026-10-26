// Captures raw App Store screenshots (iPhone 6.9", 1320x2868) into store/screenshots/raw/.
// Uses the test build with invincibility so random taps can climb; operator UI is hidden in the shots.
// Afterwards www/ is rebuilt as the store build.
import { execFileSync } from 'node:child_process';
import { createServer } from 'node:http';
import { readFile, mkdir } from 'node:fs/promises';
import { dirname, join, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const out = join(root, 'store/screenshots/raw');
await mkdir(out, { recursive: true });
execFileSync('node', [join(root, 'scripts/build.mjs'), '--dev'], { stdio: 'inherit' });

const TYPES = { '.html': 'text/html; charset=utf-8', '.ttf': 'font/ttf' };
const server = createServer(async (req, res) => {
  const path = join(root, 'www', decodeURIComponent(new URL(req.url, 'http://x').pathname).replace(/^\/$/, '/index.html'));
  let body;
  try { body = await readFile(path); } catch { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'content-type': TYPES[extname(path)] || 'application/octet-stream' });
  res.end(body);
}).listen(0);
const url = `http://127.0.0.1:${server.address().port}/`;

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
const sleep = ms => new Promise(r => setTimeout(r, ms));
const HIDE_OPERATOR = '#adminBadge, #cheatNote, #debug { display: none !important; }';

async function newPage(storage) {
  const ctx = await browser.newContext({ viewport: { width: 440, height: 956 }, deviceScaleFactor: 3, hasTouch: true, isMobile: true });
  await ctx.addInitScript(s => { for (const [k, v] of Object.entries(s)) localStorage.setItem(k, JSON.stringify(v)); }, storage);
  const page = await ctx.newPage();
  await page.goto(url);
  await page.addStyleTag({ content: HIDE_OPERATOR });
  await page.evaluate(() => document.fonts.ready);
  await sleep(1200);
  return page;
}
const shot = (page, name) => page.screenshot({ path: join(out, name) }).then(() => console.log('saved', name));
const scoreOf = page => page.$eval('#score', el => Number(el.textContent));

// 1. main menu, with a few trails unlocked
let page = await newPage({ oh_best: 37, oh_trail: 1, oh_admin: {} });
await shot(page, '1-menu.png');

// 2 and 3. gameplay right after a landing: once early in the climb, once higher up
async function climbShot(target, name) {
  const page = await newPage({ oh_best: 37, oh_trail: 1, oh_admin: { god: true } });
  await page.click('#play');
  await sleep(600);
  for (let i = 0; i < 600; i++) {
    const before = await scoreOf(page);
    await page.mouse.click(220, 500);
    await sleep(450);
    const after = await scoreOf(page);
    if (after > before && after >= target) { await sleep(120); await shot(page, name); return; }
    if (after === before) await sleep(1100 + Math.random() * 900); // let the respawn text fade and the angle change
    else await sleep(300 + Math.random() * 600);
  }
  console.warn(`could not reach score ${target} for ${name}`);
}
await climbShot(6, '2-play.png');
await climbShot(15, '3-climb.png');

// 4. how to play
page = await newPage({ oh_best: 37, oh_trail: 1, oh_admin: {} });
await page.click('#howBtn');
await sleep(400);
await shot(page, '4-howto.png');

await browser.close();
server.close();
execFileSync('node', [join(root, 'scripts/build.mjs')], { stdio: 'inherit' });
