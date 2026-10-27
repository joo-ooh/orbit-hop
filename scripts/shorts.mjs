// Renders a vertical Shorts/Reels/TikTok clip (1080x1920, 30fps) of autoplay gameplay.
//   node scripts/shorts.mjs --dry            try seeds quickly (no frames) and print how each run goes
//   node scripts/shorts.mjs --seed 7         render frames + sound log for one seed into store/video/work/
// Then: python3 scripts/make_shorts_audio.py && the ffmpeg step it prints (or `npm run shorts`).
//
// The page runs on a virtual clock (performance.now, requestAnimationFrame, setTimeout), so every
// frame is captured at an exact time no matter how slow the screenshot is, and runs are repeatable.
import { execFileSync } from 'node:child_process';
import { createServer } from 'node:http';
import { readFile, mkdir, rm, writeFile } from 'node:fs/promises';
import { dirname, join, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const dry = args.includes('--dry');
const seedArg = args.includes('--seed') ? Number(args[args.indexOf('--seed') + 1]) : 1;
const STOP_AT = 13; // autoplay misses on purpose from this planet on
const FPS = 30;
const work = join(root, 'store/video/work');

// timeline (seconds). Captions sit in the upper-middle: Shorts covers the bottom and right edges with its own UI.
const CAPTIONS = [
  { from: 0.2, to: 2.8, text: '탭 한 번이면<br><em>날아가요</em>' },
  { from: 3.2, to: 7.6, text: '가장자리를 스치면<br><em>PERFECT</em>' },
  { from: 8.2, to: 13.2, text: '올라갈수록<br><em>더 빨라져요</em>' },
];
const OVER_CAPTION = '당신은<br><em>몇 점까지?</em>';
const OVER_HOLD = 2.6, END_CARD = 2.6, MAX_SECONDS = 40;

execFileSync('node', [join(root, 'scripts/build.mjs'), '--dev'], { stdio: 'inherit' });
const iconB64 = (await readFile(join(root, 'resources/icon.png'))).toString('base64');

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

function pageInit({ seed, storage }) {
  // seeded Math.random (mulberry32) so a seed always produces the same level and run
  let s = seed >>> 0;
  Math.random = () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  // virtual clock
  let now = 0, rafs = [], timers = [], timerId = 0;
  performance.now = () => now;
  window.requestAnimationFrame = cb => { rafs.push(cb); return rafs.length; };
  window.setTimeout = (cb, ms = 0) => { const id = ++timerId; timers.push({ id, at: now + ms, cb }); return id; };
  window.clearTimeout = id => { timers = timers.filter(t => t.id !== id); };
  window.__step = ms => {
    now += ms;
    const due = timers.filter(t => t.at <= now); timers = timers.filter(t => t.at > now);
    due.forEach(t => t.cb());
    const list = rafs; rafs = []; list.forEach(cb => cb(now));
  };
  window.__ohToneLog = [];
  for (const [k, v] of Object.entries(storage)) localStorage.setItem(k, JSON.stringify(v));
}

const STYLE = `
#adminBadge, #cheatNote, #debug { display: none !important; }
/* game over card in the video: score and stats only, so the caption fits above it */
#over [data-trails], #over [data-trail-hint], #over .btns, #over #reason, #over #unlock { display: none !important; }
#cap.over { top: 15%; }
#cap { position: fixed; left: 0; right: 0; top: 24%; text-align: center; pointer-events: none; z-index: 50;
  font: 400 46px/1.15 "Black Han Sans", sans-serif; color: #f6eefc; letter-spacing: 0.01em;
  text-shadow: 0 4px 0 rgba(23,15,46,0.55), 0 0 28px rgba(23,15,46,0.9); transition: none; }
#cap em { font-style: normal; color: #ffb36b; }
#end { position: fixed; inset: 0; z-index: 60; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 18px;
  background: radial-gradient(ellipse at 50% 40%, #3a1d4f, #170f2e 70%); }
#end img { width: 150px; height: 150px; border-radius: 34px; box-shadow: 0 18px 50px rgba(255,111,145,0.35); }
#end h1 { margin: 6px 0 0; font: 400 58px/1 "Black Han Sans", sans-serif; color: #f6eefc; }
#end p { margin: 0; font: 700 19px "Gothic A1", sans-serif; color: #ffb36b; letter-spacing: 0.06em; }
#end small { font: 400 15px "Gothic A1", sans-serif; color: #b7a6d6; }
`;

async function runOnce(seed, capture) {
  const ctx = await browser.newContext({ viewport: { width: 360, height: 640 }, deviceScaleFactor: 3 });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.addInitScript(pageInit, {
    seed,
    storage: { oh_best: 41, oh_trail: 1, oh_admin: { autoplay: true, autoplayStopAt: STOP_AT, unlockAll: true } },
  });
  await page.goto(url);
  await page.addStyleTag({ content: STYLE });
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => { const d = document.createElement('div'); d.id = 'cap'; document.body.appendChild(d); });
  await page.evaluate(() => { for (let i = 0; i < 6; i++) window.__step(1000 / 60); });
  await page.click('#play');

  const frames = [];
  let overAt = null, frame = 0, lastCap = null;
  const total = () => (overAt === null ? MAX_SECONDS : overAt + OVER_HOLD + END_CARD);
  while (frame / FPS < total()) {
    const t = frame / FPS;
    // two 60 Hz game steps per 30 fps video frame
    const st = await page.evaluate(() => {
      window.__step(1000 / 60); window.__step(1000 / 60);
      return { over: !document.getElementById('over').hidden, score: Number(document.getElementById('score').textContent) };
    });
    if (st.over && overAt === null) overAt = t;
    let cap = CAPTIONS.find(c => t >= c.from && t < c.to)?.text || '';
    if (overAt !== null && t >= overAt + 0.3) cap = OVER_CAPTION;
    const showEnd = overAt !== null && t >= overAt + OVER_HOLD;
    if (showEnd) cap = '';
    if (cap !== lastCap) {
      await page.evaluate(([h, over]) => { const c = document.getElementById('cap'); c.innerHTML = h; c.classList.toggle('over', over); }, [cap, cap === OVER_CAPTION]);
      lastCap = cap;
    }
    if (showEnd && !(await page.$('#end'))) {
      await page.evaluate(src => {
        const d = document.createElement('div'); d.id = 'end';
        d.innerHTML = `<img src="data:image/png;base64,${src}" alt=""><h1>궤도점프</h1><p>탭 한 번으로 우주를 건너요</p><small>App Store 출시 예정</small>`;
        document.body.appendChild(d);
      }, iconB64);
    }
    if (capture) {
      const name = `f${String(frame).padStart(5, '0')}.jpg`;
      await page.screenshot({ path: join(work, 'frames', name), type: 'jpeg', quality: 93 });
    }
    frames.push(st.score);
    frame++;
  }
  const result = await page.evaluate(() => ({
    tones: window.__ohToneLog,
    perfects: Number(document.getElementById('perfOut').textContent),
    final: Number(document.getElementById('final').textContent),
  }));
  await ctx.close();
  return { seed, seconds: +(frame / FPS).toFixed(1), overAt: overAt && +overAt.toFixed(1), errors, ...result, frames: frame };
}

if (dry) {
  for (let seed = 1; seed <= 8; seed++) {
    const r = await runOnce(seed, false);
    console.log(`seed ${seed}: game over at ${r.overAt}s, final score ${r.final}, PERFECT ${r.perfects}, length ${r.seconds}s${r.errors.length ? ', errors: ' + r.errors.join(' | ') : ''}`);
  }
} else {
  await rm(work, { recursive: true, force: true });
  await mkdir(join(work, 'frames'), { recursive: true });
  const r = await runOnce(seedArg, true);
  await writeFile(join(work, 'run.json'), JSON.stringify({ fps: FPS, seed: r.seed, seconds: r.seconds, overAt: r.overAt, endCardAt: r.overAt + OVER_HOLD, tones: r.tones }, null, 1));
  console.log(`seed ${r.seed}: ${r.frames} frames (${r.seconds}s), score ${r.final}, PERFECT ${r.perfects}, ${r.tones.length} sounds${r.errors.length ? ', errors: ' + r.errors.join(' | ') : ''}`);
}

await browser.close();
server.close();
execFileSync('node', [join(root, 'scripts/build.mjs')], { stdio: 'inherit' });
