// Renders the launcher icon (android/app/icon.png, 192x192 = 48dp at xxxhdpi) with a headless browser.
// Run from the repo root:  node android/tools/make_icon.js   (needs Playwright)
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');

const html = `<canvas id="c" width="192" height="192"></canvas><script>
const g = document.getElementById('c').getContext('2d'), S = 192;
// night sky fading to blood-red fog at the horizon
let sky = g.createLinearGradient(0, 0, 0, S);
sky.addColorStop(0, '#05070d'); sky.addColorStop(.62, '#151a26'); sky.addColorStop(1, '#3a0b0b');
g.fillStyle = sky; g.fillRect(0, 0, S, S);
// full moon with a soft halo
let halo = g.createRadialGradient(124, 58, 10, 124, 58, 70);
halo.addColorStop(0, 'rgba(255,236,200,.55)'); halo.addColorStop(1, 'rgba(255,236,200,0)');
g.fillStyle = halo; g.fillRect(0, 0, S, S);
g.fillStyle = '#f3e7c9'; g.beginPath(); g.arc(124, 58, 26, 0, 7); g.fill();
g.fillStyle = 'rgba(160,140,110,.35)';
for (const [x, y, r] of [[116, 52, 6], [132, 66, 4], [128, 48, 3]]) { g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); }
// dead treeline
g.fillStyle = '#07080c';
for (let x = -4; x < S; x += 9) { const h = 18 + ((x * 37) % 23); g.fillRect(x, 150 - h, 3, h); g.fillRect(x - 4, 150 - h * .7, 11, 2); }
g.fillRect(0, 148, S, 44);
// a rotting hand clawing up out of the ground
g.save(); g.translate(70, 186); g.rotate(-.12);
g.fillStyle = '#6d7a5e'; g.strokeStyle = '#1a1f14'; g.lineWidth = 3;
const fingers = [[-20, -96, -.32, 30], [-6, -108, -.08, 34], [8, -104, .12, 32], [21, -92, .34, 27]];
for (const [x, y, a, len] of fingers) {
  g.save(); g.translate(x, y); g.rotate(a);
  g.beginPath(); g.moveTo(-5, 0); g.lineTo(-4, -len * .55); g.lineTo(-7, -len); g.lineTo(-1, -len - 6); g.lineTo(3, -len * .5); g.lineTo(5, 0); g.closePath(); g.fill(); g.stroke();
  g.restore();
}
g.beginPath(); g.moveTo(-27, -88); g.quadraticCurveTo(-40, -70, -32, -60); g.lineTo(-24, -70); g.closePath(); g.fill(); g.stroke();   // thumb
g.beginPath(); g.moveTo(-26, -96); g.lineTo(28, -94); g.lineTo(22, -40); g.lineTo(-16, -40); g.closePath(); g.fill(); g.stroke();       // palm
g.fillRect(-14, -42, 32, 50); g.strokeRect(-14, -42, 32, 50);                                                                           // wrist
g.fillStyle = '#4a0606'; g.beginPath(); g.ellipse(2, -66, 9, 6, .4, 0, 7); g.fill();                                                    // wound
g.restore();
// churned earth over the wrist
g.fillStyle = '#120d0a'; g.beginPath(); g.ellipse(70, 168, 46, 12, 0, 0, 7); g.fill();
// title mark
g.font = 'bold 30px Georgia, serif'; g.textAlign = 'right'; g.fillStyle = '#c21414';
g.shadowColor = 'rgba(255,0,0,.6)'; g.shadowBlur = 10; g.fillText('DED', 182, 182);
</script>`;

(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROMIUM || undefined });
  const p = await b.newPage({ viewport: { width: 192, height: 192 } });
  await p.setContent(`<body style="margin:0;background:#000">${html}</body>`);
  await p.locator('#c').screenshot({ path: path.join(__dirname, '..', 'app', 'icon.png') });
  await b.close();
  console.log('wrote android/app/icon.png');
})();
