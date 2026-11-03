#!/usr/bin/env node
// Recorded voice lines for zombies.html.
//
//   node tools/voice.js script                    writes voice/SCRIPT.md (every line to record, with its file name)
//   node tools/voice.js split <take> <section>    cuts one long take of a section into a file per line
//   node tools/voice.js index                     writes voice/voice.json from the files in voice/ (the game reads it)
//   node tools/voice.js lines                     prints every recordable line as JSON (for matching unnamed takes)
//
// A long take is the section's lines read top to bottom with about two seconds of silence between them.
// File names come from the game's own key function, so a line keeps its file when lines are added or reordered.
// split and the cleanup need ffmpeg.
'use strict';
const fs = require('fs'), path = require('path'), { execFileSync, spawnSync } = require('child_process');
const ROOT = path.dirname(__dirname), DIR = path.join(ROOT, 'voice');
const html = fs.readFileSync(path.join(ROOT, 'zombies.html'), 'utf8');

function grab(name) {   // a top-level `const NAME = {...};` table from the game
  const a = html.indexOf(`const ${name} = {`), b = html.indexOf('\n};', a);
  if (a < 0 || b < 0) throw new Error(`${name} not found in zombies.html`);
  return eval('(' + html.slice(a + name.length + 9, b + 2) + ')');
}
const QUOTES = grab('QUOTE_LINES'), RADIO = grab('RADIO_TALK');
const keySrc = html.match(/\n\s*key: (\(ev, line\) => .+),\n/);
if (!keySrc) throw new Error('VoicePack.key not found in zombies.html');
const key = eval(keySrc[1]);

// sections in the order to record them: what you hear most first
const SECTIONS = [
  ['Kills and fighting', 'Heard all game long.', ['kill', 'head', 'multi', 'melee', 'crawler', 'crowd', 'sparkKill']],
  ['Rounds', 'Every round starts and ends with one of these.', ['round', 'roundEnd', 'roundBig']],
  ['Getting hurt', '', ['hurt', 'lowHp', 'breakIn', 'death', 'revive']],
  ['Ammo', '', ['lastMag', 'noAmmo', 'ammo', 'overheat']],
  ['Starting a match', 'One plays when a match begins, plus one for the map.', ['start', 'start_route9', 'start_depot', 'start_pier', 'start_mine', 'start_farm']],
  ['Buying guns and the mystery box', '', ['buy_rifle', 'buy_smg', 'buy_shotgun', 'boxSpin', 'boxBig', 'boxMeh', 'box_ray', 'box_arc', 'forge']],
  ['Perks', '', ['perk_iron', 'perk_quick', 'perk_dbl', 'perk_wind', 'perk_fleet', 'perk_holster', 'perk_steady', 'perk_spark', 'perk_blast']],
  ['Power-ups', '', ['pu_ammo', 'pu_insta', 'pu_dbl', 'pu_nuke', 'pu_carp']],
  ['Doors, power, building and the bus', '', ['power', 'repair', 'door_lot', 'door_road', 'door_parlor', 'door_barn', 'build_shield', 'build_turret', 'build_trap', 'build_gale', 'bus']],
];
const WHEN = {
  kill: 'killing a zombie', head: 'a headshot kill', multi: 'several kills at once', melee: 'a knife kill', crawler: 'a zombie loses its legs', crowd: 'a crowd is close',
  sparkKill: 'Spark Cider zaps zombies', round: 'a round starts', roundEnd: 'a round is cleared', roundBig: 'every fifth round', hurt: 'taking a hit',
  lowHp: 'almost dead', breakIn: 'a zombie tears a board off', death: 'going down', revive: 'getting back up', lastMag: 'on the last magazine',
  noAmmo: 'out of ammo', ammo: 'buying ammo', overheat: 'the Gale Cannon overheats', start: 'any map', start_route9: 'Route 9', start_depot: 'the depot',
  start_pier: 'the pier', start_mine: 'the mine', start_farm: 'Ashgrove Farmhouse', buy_rifle: 'buying a rifle', buy_smg: 'buying an SMG', buy_shotgun: 'buying a shotgun',
  boxSpin: 'spinning the box', boxBig: 'a great gun from the box', boxMeh: 'a so-so gun from the box', box_ray: 'the ray gun from the box', box_arc: 'the arc gun from the box',
  forge: 'upgrading a gun', perk_iron: 'Ironhide Ale', perk_quick: 'Quickhand Cola', perk_dbl: 'Double Barrel Brew', perk_wind: 'Second Wind Soda', perk_fleet: 'Fleetfoot Fizz',
  perk_holster: 'Third Holster Tonic', perk_steady: 'Steady Hand Stout', perk_spark: 'Spark Cider', perk_blast: 'Blastproof Bitters', pu_ammo: 'Max Ammo',
  pu_insta: 'Insta-Kill', pu_dbl: 'Double Points', pu_nuke: 'the nuke', pu_carp: 'Carpenter', power: 'turning the power on', repair: 'rebuilding a board',
  door_lot: 'opening the lot', door_road: 'opening the road', door_parlor: 'opening the parlor', door_barn: 'opening the barn', build_shield: 'building the shield',
  build_turret: 'building the turret', build_trap: 'building the trap', build_gale: 'building the Gale Cannon', bus: 'the bus',
};
const OTHER = [   // lines spoken by someone else (the radios and the clock's whisper)
  ...Object.entries(RADIO).map(([k, [who, text]]) => ({ file: 'radio--' + k, who, text })),
  { file: 'whisper', who: 'The whisper (after the farmhouse clock strikes midnight)', text: 'The marsh remembers you. Take this, and stay alive.' },
];

// every recordable line, in section order: {section, ev, text, file}
function lines() {
  const out = [], seen = new Set(), listed = new Set();
  SECTIONS.forEach(([title, , evs], si) => evs.forEach(ev => {
    listed.add(ev);
    if (!QUOTES[ev]) throw new Error(`no quote list called ${ev}`);
    for (const text of QUOTES[ev]) {
      if (text.includes('{')) continue;   // names a gun or a round number: the computer voice says those
      const file = key(ev, text);
      if (seen.has(file)) throw new Error(`two ${ev} lines share the file name ${file}: change the first words of one`);
      seen.add(file); out.push({ section: si + 1, title, ev, text, file });
    }
  }));
  const missing = Object.keys(QUOTES).filter(ev => !listed.has(ev));
  if (missing.length) throw new Error('add these situations to a section in tools/voice.js: ' + missing.join(', '));
  OTHER.forEach(o => out.push({ section: SECTIONS.length + 1, title: 'Other voices (optional)', ev: null, text: o.text, file: o.file, who: o.who }));
  return out;
}

function script() {
  const all = lines(), md = [];
  const recorded = new Set((fs.existsSync(DIR) ? fs.readdirSync(DIR) : []).filter(f => /\.(mp3|m4a|ogg|wav)$/i.test(f)).map(f => f.replace(/\.\w+$/, '')));
  md.push('# Dead End Depot voice script', '',
    `${all.length} lines in ${SECTIONS.length + 1} sections, ${all.filter(l => recorded.has(l.file)).length} recorded so far (marked ✅). The game plays your recording whenever one exists and uses the computer voice for the rest, so you can record a few lines at a time.`,
    'Your own lines are welcome too: send them and say when each should play.',
    'Start with section 1: you hear those lines all game long.', '',
    '## How to record', '',
    '- Find a quiet room with soft things around (a closet full of clothes is great). Turn off fans and the TV.',
    '- Hold the phone about a hand\'s width (20 cm) from your mouth, slightly to the side so your breath doesn\'t hit the mic.',
    '- Act it. You\'re tired, scared and a little bit funny. Short lines can be quick; shouts can be loud, the game evens out the volume.',
    '- Any recorder app works (Voice Recorder, Voice Memos). Any common format is fine: m4a, mp3, wav, ogg.', '',
    '### Two ways to send them', '',
    '1. **One recording per section (easiest).** Read the section top to bottom. Leave about **2 seconds of silence** between lines. If you flub a line, stop, wait 2 seconds and read **just that line** again before going on, then tell me which ones you redid. Name the file after the section, like `section-1.m4a`. I\'ll cut it up, clean it and name every piece.',
    '2. **One file per line.** Name each file exactly as listed (the `.mp3` can be `.m4a` or `.wav` instead).', '',
    'You can skip lines. Lines that mention a gun\'s name or a round number aren\'t here: the computer voice still reads those.', '');
  let cur = 0, n = 0;
  for (const l of all) {
    if (l.section !== cur) {
      cur = l.section; n = 0;
      const sec = SECTIONS[cur - 1];
      md.push('', `## Section ${cur}: ${l.title}`, '');
      if (sec && sec[1]) md.push(sec[1], '');
      if (!sec) md.push('Radio messages you find hidden on each map, read by other characters. Use a different voice, or ask a friend. Skip these if you like.', '');
    }
    const when = l.ev ? WHEN[l.ev] : l.who, done = recorded.has(l.file);
    md.push(`${++n}. ${done ? '✅ ' : ''}"${l.text}"  `, `   <sub>${when} · \`${l.file}.mp3\`${done ? ' · recorded' : ''}</sub>`);
  }
  md.push('', '---', '', 'Made by `node tools/voice.js script` from the lines in zombies.html.', '');
  fs.mkdirSync(DIR, { recursive: true });
  fs.writeFileSync(path.join(DIR, 'SCRIPT.md'), md.join('\n'));
  console.log(`voice/SCRIPT.md: ${all.length} lines`);
}

// cleanup: mono, trimmed, high-passed, levelled, small mp3
function clean(src, dst, from, to) {
  const args = ['-y', '-v', 'error'];
  if (from != null) args.push('-ss', String(from), '-to', String(to));
  args.push('-i', src, '-ac', '1', '-ar', '44100', '-af',
    [   // rumble out, hiss down, silence trimmed off both ends (keeping a breath), soft edges, even loudness
      'highpass=f=80', 'afftdn=nf=-30',
      'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05', 'afade=t=in:d=0.01',
      'areverse', 'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.15', 'afade=t=in:d=0.03', 'areverse',
      'loudnorm=I=-16:TP=-1.5:LRA=11',
    ].join(','),
    '-c:a', 'libmp3lame', '-b:a', '64k', dst);
  execFileSync('ffmpeg', args);
}

function split(take, sectionNo, opts) {
  const all = lines().filter(l => l.section === +sectionNo);
  if (!all.length) throw new Error(`no section ${sectionNo}`);
  const gap = +(opts.gap || 1.2), noise = opts.noise || '-38dB';
  const res = spawnSync('ffmpeg', ['-v', 'info', '-i', take, '-af', `silencedetect=n=${noise}:d=${gap}`, '-f', 'null', '-'], { encoding: 'utf8' });
  const text = res.stderr, dur = +(text.match(/Duration: (\d+):(\d+):([\d.]+)/) || []).slice(1).reduce((a, v) => a * 60 + +v, 0);
  const starts = [...text.matchAll(/silence_start: ([\d.]+)/g)].map(m => +m[1]), ends = [...text.matchAll(/silence_end: ([\d.]+)/g)].map(m => +m[1]);
  const pieces = []; let at = 0;   // speech is what lies between silences
  starts.forEach((s, i) => { if (s - at > .25) pieces.push([Math.max(0, at - .1), s + .1]); at = ends[i] ?? dur; });
  if (dur - at > .25) pieces.push([Math.max(0, at - .1), dur]);
  const order = opts.order ? opts.order.split(',').map(x => +x - 1) : all.map((_, i) => i);   // which line each piece is (redos)
  console.log(`${take}: ${pieces.length} pieces for ${order.length} lines${pieces.length !== order.length ? '  <-- counts differ, check --order / --gap' : ''}`);
  pieces.slice(0, order.length).forEach(([a, b], i) => {
    const l = all[order[i]]; if (!l) return;
    clean(take, path.join(DIR, l.file + '.mp3'), a.toFixed(3), b.toFixed(3));   // a later redo overwrites the flub
    console.log(`  ${a.toFixed(1)}-${b.toFixed(1)}s  ${l.file}.mp3  "${l.text}"`);
  });
}

function index() {
  const known = new Set(lines().map(l => l.file)), files = [], strays = [];
  for (const f of fs.readdirSync(DIR).sort()) {
    const m = f.match(/^(.+)\.(mp3|m4a|ogg|wav)$/i); if (!m) continue;
    (known.has(m[1]) ? files : strays).push(f);
  }
  fs.writeFileSync(path.join(DIR, 'voice.json'), JSON.stringify(files) + '\n');
  console.log(`voice/voice.json: ${files.length} of ${known.size} lines recorded`);
  if (strays.length) console.log('not matching any line (left out): ' + strays.join(', '));
}

const [cmd, ...rest] = process.argv.slice(2);
const opts = {}; const args = rest.filter(a => { const m = a.match(/^--(\w+)=(.*)$/); if (m) opts[m[1]] = m[2]; return !m; });
if (cmd === 'script') script();
else if (cmd === 'split') { split(args[0], args[1], opts); index(); }
else if (cmd === 'clean') { const [src, file] = args; clean(src, path.join(DIR, file.replace(/\.\w+$/, '') + '.mp3')); index(); }
else if (cmd === 'index') index();
else if (cmd === 'lines') console.log(JSON.stringify(lines(), null, 1));
else console.log('usage: node tools/voice.js script | split <take> <section> [--gap=1.2] [--noise=-38dB] [--order=1,2,2,3] | clean <file> <name> | index');
