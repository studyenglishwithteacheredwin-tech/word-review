"""Export Starters units -> starters/data/starters/uNN.json (words + base64 JPEG + base64 MP3 + slow MP3), index.json, thumbs.json"""
import sys, os, json, base64, io
sys.path.insert(0, '/home/claude/tts')
import units_data
from PIL import Image
IMG = '/home/claude/starters/images'
AUD = '/home/claude/tts/audio5'
SLOW = '/home/claude/tts/slow5'
OUT = '/home/claude/app_st/starters/data/starters'
os.makedirs(OUT, exist_ok=True)
NUMCOL = ["#D6336C", "#2E5C8A", "#E8760A", "#7B4B94", "#2B8A3E"]


def b64img(path, q=80, side=420):
    im = Image.open(path)
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA'); bg = Image.new('RGB', im.size, 'white'); bg.paste(im, mask=im.split()[3]); im = bg
    im = im.convert('RGB'); im.thumbnail((side, side), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()


def b64mp3(p):
    assert os.path.exists(p), p
    return 'data:audio/mpeg;base64,' + base64.b64encode(open(p, 'rb').read()).decode()


index = {'level': 'Starters', 'units': []}
thumbs = {}
for u in units_data.parse():
    d = f"{AUD}/Unit {u['unit']:02d} - {u['title'].replace('?', '').replace('–', '-')}"
    words = []
    for i, w in enumerate(u['words'], 1):
        en = w['en']
        item = {'en': en, 'vi': w['vi']}
        if w.get('tricky'): item['tricky'] = w['tricky']
        if w.get('syl'): item['syl'] = w['syl']
        if u.get('numbers'):
            item['label'] = str(i); item['color'] = NUMCOL[i % len(NUMCOL)]
        else:
            f = f"{IMG}/u{u['unit']}/{en.replace('/', '_')}.png"
            item['img'] = b64img(f)
            if u['unit'] not in thumbs:
                thumbs[u['unit']] = b64img(f, q=75, side=160)
        name = en.replace('/', ' - ').replace("'", '')
        item['audio'] = b64mp3(f"{d}/{i:02d} {name}.mp3")
        item['slow'] = b64mp3(f"{SLOW}/u{u['unit']:02d}_{i:02d}.mp3")
        words.append(item)
    data = {'unit': u['unit'], 'title': u['title'], 'sound': u['sound'], 'sound_name': u['sound_name'], 'words': words}
    json.dump(data, open(f"{OUT}/u{u['unit']:02d}.json", 'w'), ensure_ascii=False, separators=(',', ':'))
    index['units'].append({'unit': u['unit'], 'title': u['title'], 'n': len(words)})
json.dump(index, open(f"{OUT}/index.json", 'w'), ensure_ascii=False, indent=1)
json.dump(thumbs, open(f"{OUT}/thumbs.json", 'w'))
print('done', len(index['units']), 'units')
