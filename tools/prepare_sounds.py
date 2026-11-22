#!/usr/bin/env python3
"""Builds sounds/ from CC0 recordings on OpenGameArt.org (see sounds/CREDITS.md).

  python3 tools/prepare_sounds.py <work-dir>

Downloads the packs into <work-dir>, cuts single events out of the longer recordings (individual
gunshots, groans), trims silence, fades the tails, levels each category, and writes small mono MP3s
plus sounds/sounds.json. Needs ffmpeg (with libmp3lame), numpy and py7zr.
"""
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
import zipfile

import numpy as np
import py7zr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'sounds')
SR = 44100
OGA = 'https://opengameart.org/sites/default/files/'

PACKS = {   # folder: (files, page, author)
    'firearms': (['Prepared%20SFX%20Library.7z'], 'the-free-firearm-sound-library', 'bart'),
    'zombies_pack': (['zombies.zip'], 'zombies-sound-pack', 'artisticdude'),
    'zombie_moans': (['darsycho__zombie-moans_0.ogg'], 'zombie-moans', 'Darsycho'),
    'zombie_voices': (['Voice%20Effects%20Zombie-Skeleton-Monster%20Human%20Male.zip'], 'zombie-skeleton-monster-voice-effects', 'ArcadeParty'),
    'steps': (['%5Bkdd%5DDifferentSteps_0.zip'], 'different-steps-on-wood-stone-leaves-gravel-and-mud', 'TinyWorlds'),
    'snow': (['qubodup-snow_steps_dry_0.7z'], '4-dry-snow-steps', 'qubodup'),
    'reloads': (['gunreload1.wav', 'assaultriflereload1_0.wav', 'shotguncock_0.wav'], 'gun-reload-sounds', 'SpringySpringo'),
    'explosion': (['NenadSimic%20-%20Muffled%20Distant%20Explosion.wav'], 'muffled-distant-explosion', 'NenadSimic'),
    'bangs': (['25-CC0-bang-sfx.zip'], '25-cc0-bang-firework-sfx', 'rubberduck'),
    'metal_wood': (['100-CC0-wood-metal-SFX.zip'], '100-cc0-metal-and-wood-sfx', 'rubberduck'),
    'squish': (['independent_nu_ljudbank-wet_squish_slurp_impacts.7z'], '8-wet-squish-slurp-impacts', 'qubodup'),
    'wood_cracks': (['independent_nu_ljudbank-wood_crack_hit_destruction.7z'], '35-wooden-crackshitsdestructions', 'qubodup'),
    'melee': (['melee%20sounds.zip'], '3-melee-sounds', 'remaxim'),
}

FA = 'firearms/Prepared SFX Library/'
ZV = 'zombie_voices/Voice Effects Zombie-Skeleton-Monster Human Male/'
# name: [(source file, start seconds or None for the whole file, max length)], peak level in dBFS, bitrate
SOUNDS = {
    'shot-pistol': ([(FA + '1911/A_42P.wav', .94, 1.0), (FA + '1911/A_42P.wav', 5.0, 1.0)], -1, 96),
    'shot-smg': ([(FA + 'Carl Gustav M45/G_31P.wav', t, .8) for t in (.31, 3.5, 6.72)], -1, 96),
    'shot-rifle': ([(FA + 'AR-15/D_32P.wav', .7, 1.2), (FA + 'AR-15/D_32P.wav', 5.65, 1.2), (FA + 'AK-47/C_28P.wav', .61, 1.2), (FA + 'AK-47/C_28P.wav', 3.25, 1.2)], -1, 96),
    'shot-lmg': ([(FA + 'AK-47/C_28P.wav', 6.02, 1.1), (FA + 'AK-47/C_28P.wav', 9.15, 1.1)], -1, 96),
    'shot-shotgun': ([(FA + 'Mossberg/N_26P.wav', t, 1.4) for t in (.78, 4.57, 7.95)] + [(FA + 'Nova/O_17P.wav', .69, 1.4)], -1, 96),
    'shot-sniper': ([(FA + 'Savage 10 .300 Blackout/T_27P.wav', .95, 1.8), (FA + 'Mosin Nagant/M_26P.wav', 1.14, 1.8)], -1, 96),
    'shot-cannon': ([(FA + 'Smith & Wesson 642/V_27P.wav', .8, 1.3), (FA + 'Smith & Wesson 642/V_27P.wav', 6.22, 1.3)], -1, 96),
    'reload': ([('reloads/gunreload1.wav', None, 2), ('reloads/assaultriflereload1_0.wav', None, 2)], -6, 64),
    'pump': ([('reloads/shotguncock_0.wav', None, 1)], -5, 64),
    'boom': ([('explosion/NenadSimic - Muffled Distant Explosion.wav', None, 3.5), ('bangs/cannon_02.ogg', None, 2), ('bangs/cannon_03.ogg', None, 2)], -1, 80),
    'groan': ([(f'zombies_pack/zombies/zombie-{i}.wav', None, 1.6) for i in range(1, 25)]
              + [('zombie_moans/darsycho__zombie-moans_0.ogg', t, 1.8) for t in (.49, 1.75, 3.8, 6.81, 9.51, 10.62, 14.84)], -4, 64),
    'zattack': ([(ZV + f'zombieYell{i}.wav', None, 1) for i in range(1, 11)], -4, 64),
    'zdeath': ([(ZV + f'zombieDeath{i}.wav', None, 1.2) for i in range(1, 5)], -4, 64),
    'hurt': ([(ZV + f'humanYell{i}.wav', None, 1) for i in range(1, 6)], -5, 64),
    'pdeath': ([(ZV + f'humanDeath{i}.wav', None, 1.5) for i in (1, 2)], -3, 64),
    'step-wood': ([(f'steps/wood0{i}.ogg', None, .5) for i in (1, 2, 3)], -10, 64),
    'step-tile': ([('steps/stone01.ogg', None, .5)], -10, 64),
    'step-asphalt': ([('steps/gravel.ogg', None, .6), ('steps/stone01.ogg', None, .5)], -11, 64),
    'step-dirt': ([('steps/mud02.ogg', None, .5), ('steps/leaves01.ogg', None, .5)], -10, 64),
    'step-snow': ([(f'snow/qubodup-snow_steps_dry/snow_step_dry-0{i}.flac', None, .7) for i in (1, 2, 3, 4)], -10, 64),
    'shuffle': ([('steps/mud02.ogg', None, .5), ('steps/leaves02.ogg', None, .5), ('steps/gravel.ogg', None, .6)], -14, 64),
    'hit': ([(f'squish/impsplat/impactsplat0{i}.mp3.flac', None, .5) for i in range(1, 9)], -6, 64),
    'head': ([(f'squish/impsplat/impactsplat0{i}.mp3.flac', None, .7) for i in (2, 4, 6, 8)], -3, 64),
    'board': ([(f'metal_wood/wood_cracking_0{i}.ogg', None, 1.2) for i in (1, 2, 3, 4)] + [('wood_cracks/wood_impact/crack07.mp3.flac', None, 1.2)], -5, 64),
    'hammer': ([(f'metal_wood/hammer_0{i}.ogg', None, .5) for i in (1, 2, 3, 4)] + [(f'metal_wood/wood_hammer_0{i}.ogg', None, .5) for i in (1, 2)], -7, 64),
    'knife': ([('melee/melee sounds/melee sound.wav', None, .7), ('melee/melee sounds/sword sound.wav', None, .7)], -6, 64),
    'impact': ([(f'metal_wood/wood_hit_0{i}.ogg', None, .4) for i in range(1, 6)], -10, 64),
    'impact-metal': ([(f'metal_wood/metal_hit_0{i}.ogg', None, .5) for i in range(1, 6)], -12, 64),
}


def download(work):
    for folder, (files, _, _) in PACKS.items():
        d = os.path.join(work, 'dl', folder)
        x = os.path.join(work, 'x', folder)
        os.makedirs(d, exist_ok=True); os.makedirs(x, exist_ok=True)
        for f in files:
            path = os.path.join(d, urllib.parse.unquote(f))
            if not os.path.exists(path):
                urllib.request.urlretrieve(OGA + f, path)
            real = os.path.realpath(x)
            if path.endswith('.7z'):
                with py7zr.SevenZipFile(path) as z:
                    z.extract(path=x, targets=[n for n in z.getnames() if os.path.realpath(os.path.join(x, n)).startswith(real)])
            elif path.endswith('.zip'):
                with zipfile.ZipFile(path) as z:
                    for n in z.namelist():
                        if os.path.realpath(os.path.join(x, n)).startswith(real):
                            z.extract(n, x)
            else:
                subprocess.run(['cp', path, x], check=True)


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def cut(x, start, length):
    """One event: starts just before its attack, ends when it decays (or at length), with fades."""
    if start is None:
        w = int(SR * .002)
        env = np.abs(x[:len(x) // w * w]).reshape(-1, w).max(1)
        first = int(np.argmax(env > env.max() * .05)) * w   # skip leading silence
        a = max(0, first - int(SR * .004))
    else:
        a = max(0, int((start - .008) * SR))
    y = x[a:a + int(length * SR)].copy()
    w = int(SR * .01)
    env = np.abs(y[:len(y) // w * w]).reshape(-1, w).max(1)
    loud = np.nonzero(env > env.max() * 10 ** (-48 / 20))[0]   # drop the tail once it has decayed by 48 dB
    if len(loud):
        y = y[:min(len(y), (loud[-1] + 2) * w)]
    fin, fout = int(SR * .003), min(len(y) // 3, int(SR * .12))
    y[:fin] *= np.linspace(0, 1, fin)
    y[-fout:] *= np.linspace(1, 0, fout) ** 2
    return y


def main(work):
    download(work)
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith('.mp3'):
            os.remove(os.path.join(OUT, f))
    listing = []
    for name, (takes, peak_db, kbps) in SOUNDS.items():
        for i, (src, start, length) in enumerate(takes, 1):
            y = cut(load(os.path.join(work, 'x', src)), start, length)
            y *= 10 ** (peak_db / 20) / max(1e-6, np.abs(y).max())
            fn = f'{name}-{i}.mp3' if len(takes) > 1 else f'{name}.mp3'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-',
                            '-c:a', 'libmp3lame', '-b:a', f'{kbps}k', os.path.join(OUT, fn)], input=y.astype(np.float32).tobytes(), check=True)
            listing.append(fn)
    with open(os.path.join(OUT, 'sounds.json'), 'w') as fh:
        json.dump(listing, fh, indent=0)
    size = sum(os.path.getsize(os.path.join(OUT, f)) for f in listing)
    print(f'wrote {len(listing)} sounds ({size // 1024} KB) to {OUT}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '.sound-work'))
