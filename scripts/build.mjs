// Builds the app's web bundle (www/) from src/game.html.
//   node scripts/build.mjs        store build: operator mode removed
//   node scripts/build.mjs --dev  test build: operator mode kept (for TestFlight testing)
//   node scripts/build.mjs --pages  store build as index.html at the repo root, served by GitHub Pages
import { readFileSync, writeFileSync, mkdirSync, copyFileSync, rmSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const dev = process.argv.includes('--dev');
const pages = process.argv.includes('--pages');
const SITE = 'https://joo-ooh.github.io/orbit-hop/';
// the app bundle carries its own copy of the fonts; the Pages site uses the ones already in the repo
const fontBase = pages ? 'resources/fonts/' : 'fonts/';
const src = readFileSync(join(root, 'src/game.html'), 'utf8');

// src/game.html is a page fragment (it is also published as a web preview), so split it into head and body here
const split = src.indexOf('<div id="stage">');
if (split < 0) throw new Error('src/game.html: <div id="stage"> not found');
let head = src.slice(0, split);
const body = src.slice(split);

// the app runs offline, so swap Google Fonts for the bundled files
head = head
  .replace(/<link rel="preconnect"[^>]*>\n?/g, '')
  .replace(/<link rel="stylesheet" href="https:\/\/fonts\.googleapis\.com[^>]*>\n?/g, '')
  .replace(/<meta name="claude:[^>]*>\n?/g, '');
if (/fonts\.googleapis\.com/.test(head)) throw new Error('Google Fonts link still present');

const fontFaces = `<style>
@font-face { font-family: "Black Han Sans"; src: url("${fontBase}BlackHanSans-Regular.ttf") format("truetype"); font-weight: 400; font-display: block; }
@font-face { font-family: "Gothic A1"; src: url("${fontBase}GothicA1-Regular.ttf") format("truetype"); font-weight: 400; font-display: block; }
@font-face { font-family: "Gothic A1"; src: url("${fontBase}GothicA1-Bold.ttf") format("truetype"); font-weight: 700; font-display: block; }
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; -webkit-text-size-adjust: 100%; }
[hidden] { display: none !important; }
</style>`;

const html = `<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<meta name="theme-color" content="#170f2e">
${pages ? `<meta name="description" content="탭 한 번으로 행성 사이를 점프하는 우주 게임. 가장자리를 스치면 PERFECT!">
<meta property="og:type" content="website">
<meta property="og:title" content="궤도점프">
<meta property="og:description" content="탭 한 번으로 행성 사이를 점프! 몇 점까지 갈 수 있을까요?">
<meta property="og:url" content="${SITE}">
<meta property="og:image" content="${SITE}store/play/feature-graphic-1024x500.png">
<link rel="icon" type="image/png" href="store/play/play-icon-512.png">
<link rel="apple-touch-icon" href="store/play/play-icon-512.png">
` : ''}<meta name="format-detection" content="telephone=no">
<script>window.OH_CONFIG = { operator: ${dev && !pages} };</script>
${fontFaces}
${head.trim()}
</head>
<body>
${body.trim()}
</body>
</html>
`;

if (pages) {
  writeFileSync(join(root, 'index.html'), html);
  console.log('index.html built for GitHub Pages (store build, operator mode OFF)');
  process.exit(0);
}

const out = join(root, 'www');
rmSync(out, { recursive: true, force: true });
mkdirSync(join(out, 'fonts'), { recursive: true });
writeFileSync(join(out, 'index.html'), html);
for (const f of ['BlackHanSans-Regular.ttf', 'GothicA1-Regular.ttf', 'GothicA1-Bold.ttf']) {
  copyFileSync(join(root, 'resources/fonts', f), join(out, 'fonts', f));
}
console.log(`www/ built (${dev ? 'test build, operator mode ON' : 'store build, operator mode OFF'})`);
