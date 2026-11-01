#!/usr/bin/env python3
"""Packs the game into an unsigned APK without the Android SDK.

Writes the binary AndroidManifest.xml and resources.arsc directly (Android's documented binary
XML and resource-table formats), bundles the game as offline web assets, and lays the ZIP out the
way Android requires (resources.arsc stored uncompressed on a 4-byte boundary). Signing happens
afterwards with Google's apksig library (see Sign.java).

  apk.py web  <zombies.html> <npm-dir> <out-dir>       prepare offline web assets
  apk.py pack <classes.dex> <icon.png> <web-dir> <out.apk> <versionCode> <versionName>
"""
import os
import re
import shutil
import struct
import sys
import zipfile

PACKAGE = 'com.deadenddepot.zombies'
ACTIVITY = PACKAGE + '.MainActivity'
LABEL = 'Dead End Depot'
MIN_SDK, TARGET_SDK = 24, 34
ICON_PATH = 'res/mipmap-xxxhdpi-v4/ic_launcher.png'
ICON_ID = 0x7F010000   # package 0x7f, type 1 (mipmap), entry 0

ANDROID_NS = 'http://schemas.android.com/apk/res/android'
# android.R.attr IDs, checked against the published API stubs
ATTR = {
    'theme': 0x01010000, 'label': 0x01010001, 'icon': 0x01010002, 'name': 0x01010003,
    'exported': 0x01010010, 'screenOrientation': 0x0101001E, 'configChanges': 0x0101001F,
    'minSdkVersion': 0x0101020C, 'versionCode': 0x0101021B, 'versionName': 0x0101021C,
    'targetSdkVersion': 0x01010270, 'allowBackup': 0x01010280, 'hardwareAccelerated': 0x010102D3,
    'largeHeap': 0x0101035A,
}
THEME_BLACK_NOTITLE_FULLSCREEN = 0x0103000A   # android.R.style.Theme_Black_NoTitleBar_Fullscreen
SENSOR_LANDSCAPE = 6
# keyboard|keyboardHidden|navigation|orientation|screenLayout|uiMode|screenSize|smallestScreenSize|density|layoutDirection
CONFIG_CHANGES = 0x3FF0
T_REF, T_STRING, T_INT, T_BOOL = 0x01, 0x03, 0x10, 0x12


# ---------------------------------------------------------------- binary formats
def string_pool(strings):
    """ResStringPool, UTF-16."""
    offsets, data = [], b''
    for s in strings:
        offsets.append(len(data))
        enc = s.encode('utf-16-le')
        data += struct.pack('<H', len(enc) // 2) + enc + b'\0\0'
    data += b'\0' * (-len(data) % 4)
    start = 28 + 4 * len(strings)
    head = struct.pack('<HHIIIIII', 0x0001, 28, start + len(data), len(strings), 0, 0, start, 0)
    return head + b''.join(struct.pack('<I', o) for o in offsets) + data


class El:
    def __init__(self, name, attrs=(), children=()):
        self.name, self.attrs, self.children = name, list(attrs), list(children)


def a(name, kind, value):
    """An android: attribute."""
    return (True, name, kind, value)


def walk(el):
    yield el
    for c in el.children:
        yield from walk(c)


def axml(root):
    """Compile an element tree to Android binary XML."""
    res_names = sorted({at[1] for el in walk(root) for at in el.attrs if at[0]}, key=lambda n: ATTR[n])
    strings = list(res_names)   # attribute names with resource IDs come first, matching the resource map

    def sid(s):
        if s not in strings:
            strings.append(s)
        return strings.index(s)

    for s in ('android', ANDROID_NS):
        sid(s)
    for el in walk(root):
        sid(el.name)
        for is_android, name, kind, value in el.attrs:
            sid(name)
            if kind == T_STRING:
                sid(value)
    ns = sid(ANDROID_NS)
    body = struct.pack('<HHIIIII', 0x0100, 16, 24, 1, 0xFFFFFFFF, sid('android'), ns)

    def emit(el):
        nonlocal body
        attrs = sorted(el.attrs, key=lambda at: ATTR[at[1]] if at[0] else 0)   # sorted by resource ID
        out = b''
        for is_android, name, kind, value in attrs:
            raw = sid(value) if kind == T_STRING else 0xFFFFFFFF
            data = sid(value) if kind == T_STRING else (0xFFFFFFFF if (kind == T_BOOL and value) else int(value))
            out += struct.pack('<IIIHBBI', ns if is_android else 0xFFFFFFFF, sid(name), raw, 8, 0, kind, data & 0xFFFFFFFF)
        body += struct.pack('<HHIII', 0x0102, 16, 36 + len(out), 1, 0xFFFFFFFF)
        body += struct.pack('<IIHHHHHH', 0xFFFFFFFF, sid(el.name), 20, 20, len(attrs), 0, 0, 0) + out
        for c in el.children:
            emit(c)
        body += struct.pack('<HHIIIII', 0x0103, 16, 24, 1, 0xFFFFFFFF, 0xFFFFFFFF, sid(el.name))

    emit(root)
    body += struct.pack('<HHIIIII', 0x0101, 16, 24, 1, 0xFFFFFFFF, sid('android'), ns)
    pool = string_pool(strings)
    resmap = struct.pack('<HHI', 0x0180, 8, 8 + 4 * len(res_names)) + b''.join(struct.pack('<I', ATTR[n]) for n in res_names)
    payload = pool + resmap + body
    return struct.pack('<HHI', 0x0003, 8, 8 + len(payload)) + payload


def manifest(version_code, version_name):
    return axml(El('manifest', [
        (False, 'package', T_STRING, PACKAGE),
        a('versionCode', T_INT, version_code), a('versionName', T_STRING, version_name),
    ], [
        El('uses-sdk', [a('minSdkVersion', T_INT, MIN_SDK), a('targetSdkVersion', T_INT, TARGET_SDK)]),
        El('application', [
            a('theme', T_REF, THEME_BLACK_NOTITLE_FULLSCREEN), a('label', T_STRING, LABEL), a('icon', T_REF, ICON_ID),
            a('allowBackup', T_BOOL, True), a('hardwareAccelerated', T_BOOL, True), a('largeHeap', T_BOOL, True),
        ], [
            El('activity', [
                a('label', T_STRING, LABEL), a('name', T_STRING, ACTIVITY), a('exported', T_BOOL, True),
                a('screenOrientation', T_INT, SENSOR_LANDSCAPE), a('configChanges', T_INT, CONFIG_CHANGES),
            ], [
                El('intent-filter', [], [
                    El('action', [a('name', T_STRING, 'android.intent.action.MAIN')]),
                    El('category', [a('name', T_STRING, 'android.intent.category.LAUNCHER')]),
                ]),
            ]),
        ]),
    ]))


def resources_arsc():
    """A resource table with one entry: the launcher icon, as an xxxhdpi mipmap."""
    type_pool, key_pool = string_pool(['mipmap']), string_pool(['ic_launcher'])
    typespec = struct.pack('<HHIBBHI', 0x0202, 16, 20, 1, 0, 0, 1) + struct.pack('<I', 0x0100)   # varies by density
    config = bytearray(64)
    struct.pack_into('<I', config, 0, 64)
    struct.pack_into('<H', config, 14, 640)   # density: xxxhdpi
    struct.pack_into('<H', config, 24, 4)     # sdkVersion, as aapt adds for density qualifiers
    entry = struct.pack('<HHI', 8, 0, 0) + struct.pack('<HBBI', 8, 0, T_STRING, 0)
    head = 20 + len(config)
    start = head + 4
    type_chunk = struct.pack('<HHIBBHII', 0x0201, head, start + len(entry), 1, 0, 0, 1, start) + bytes(config) + struct.pack('<I', 0) + entry
    body = type_pool + key_pool + typespec + type_chunk
    name = PACKAGE.encode('utf-16-le').ljust(256, b'\0')
    pkg = struct.pack('<HHII', 0x0200, 288, 288 + len(body), 0x7F) + name + struct.pack('<IIIII', 288, 1, 288 + len(type_pool), 1, 0) + body
    values = string_pool([ICON_PATH])
    return struct.pack('<HHII', 0x0002, 12, 12 + len(values) + len(pkg), 1) + values + pkg


# ---------------------------------------------------------------- web assets
FONTS = [   # family, npm package dir prefix, file stem, weights
    ('Creepster', 'fontsource-creepster', 'creepster', [400]),
    ('Special Elite', 'fontsource-special-elite', 'special-elite', [400]),
    ('Oswald', 'fontsource-oswald', 'oswald', [400, 600]),
    ('Teko', 'fontsource-teko', 'teko', [400, 500, 600]),
]


def prepare_web(html_path, npm_dir, out):
    """Copy the game and swap its online dependencies (Google Fonts, the three.js CDN) for local files."""
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, 'fonts'))
    os.makedirs(os.path.join(out, 'licenses'))
    pkgs = {d.rsplit('-', 1)[0]: os.path.join(npm_dir, d, 'package') for d in os.listdir(npm_dir) if os.path.isdir(os.path.join(npm_dir, d))}
    css = []
    for family, pkg, stem, weights in FONTS:
        for w in weights:
            f = f'{stem}-latin-{w}-normal.woff2'
            shutil.copy(os.path.join(pkgs[pkg], 'files', f), os.path.join(out, 'fonts', f))
            css.append(f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{w};font-display:swap;src:url(./{f}) format('woff2')}}")
        shutil.copy(os.path.join(pkgs[pkg], 'LICENSE'), os.path.join(out, 'licenses', f'{stem}-OFL.txt'))
    with open(os.path.join(out, 'fonts', 'fonts.css'), 'w') as fh:
        fh.write('\n'.join(css) + '\n')
    shutil.copy(os.path.join(pkgs['three'], 'build', 'three.min.js'), os.path.join(out, 'three.min.js'))
    shutil.copy(os.path.join(pkgs['three'], 'LICENSE'), os.path.join(out, 'licenses', 'three.js-MIT.txt'))
    html = open(html_path, encoding='utf-8').read()
    html, n1 = re.subn(r'<link rel="preconnect" href="https://fonts\.googleapis\.com">\n<link href="https://fonts\.googleapis\.com/css2[^"]*" rel="stylesheet">',
                       '<link rel="stylesheet" href="fonts/fonts.css">', html)
    html, n2 = re.subn(r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/three\.js/r128/three\.min\.js"></script>',
                       '<script src="three.min.js"></script>', html)
    if (n1, n2) != (1, 1):
        sys.exit(f'could not localise the game\'s dependencies (fonts={n1}, three.js={n2})')
    if 'https://' in re.sub(r'<a [^>]*>', '', html).split('<script>')[0]:
        print('warning: the page head still references the network', file=sys.stderr)
    with open(os.path.join(out, 'index.html'), 'w', encoding='utf-8') as fh:
        fh.write(html)


# ---------------------------------------------------------------- APK zip
def pack(dex, icon, web, out, version_code, version_name):
    entries = [
        ('AndroidManifest.xml', manifest(version_code, version_name), False),
        ('classes.dex', open(dex, 'rb').read(), False),
        ('resources.arsc', resources_arsc(), True),    # Android 11+ requires this stored and 4-byte aligned
        (ICON_PATH, open(icon, 'rb').read(), True),
    ]
    for base, _, files in sorted(os.walk(web)):
        for f in sorted(files):
            p = os.path.join(base, f)
            entries.append(('assets/' + os.path.relpath(p, web).replace(os.sep, '/'), open(p, 'rb').read(), False))
    with zipfile.ZipFile(out, 'w') as z:
        for name, data, stored in entries:
            zi = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED
            if stored:   # pad with an alignment extra field (0xd935, as zipalign/apksig use) so data starts on 4 bytes
                data_at = z.fp.tell() + 30 + len(name.encode()) + 6
                pad = -data_at % 4
                zi.extra = struct.pack('<HHH', 0xD935, 2 + pad, 4) + b'\0' * pad
            z.writestr(zi, data)
    print(f'packed {out} ({os.path.getsize(out) // 1024} KB, {len(entries)} entries)')


if __name__ == '__main__':
    cmd, *args = sys.argv[1:]
    if cmd == 'web':
        prepare_web(*args)
    elif cmd == 'pack':
        pack(args[0], args[1], args[2], args[3], int(args[4]), args[5])
    else:
        sys.exit(__doc__)
