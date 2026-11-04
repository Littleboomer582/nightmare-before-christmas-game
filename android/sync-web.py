#!/usr/bin/env python3
"""Copy the game (zombies.html at the repo root) into the Android app's assets,
pointing the three.js script tags at the bundled copies so the app works offline."""
import pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent
src = (root / 'zombies.html').read_text()
src = src.replace('https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js', 'lib/three.min.js')
src = re.sub(r'https://cdn\.jsdelivr\.net/npm/three@0\.128\.0/examples/js/(?:shaders|postprocessing)/(\w+\.js)', r'lib/\1', src)
assert 'cdnjs' not in src and 'jsdelivr' not in src
out = root / 'android/app/src/main/assets/www/index.html'
out.write_text(src)
print('wrote', out.relative_to(root))
