"""Export KET units -> data/ket/uNN.json (words + IPA + base64 JPEG + base64 MP3 normal/slow), index.json, thumbs.json"""
import sys, os, json, base64, io, subprocess
KIT = '/home/claude/ket/kit'; sys.path.insert(0, KIT); os.chdir(KIT)
import strips
from PIL import Image
from reportlab.pdfgen import canvas
AUD = '/home/claude/tts/audio_ket'; SLOW = '/home/claude/tts/slow_ket'
OUT = '/home/claude/ket/app/data/ket'; os.makedirs(OUT, exist_ok=True)
TMP = '/tmp/claude-0/-home-claude/15d2323b-8413-5749-9dfd-7e2882af7a6d/scratchpad/strip'; os.makedirs(TMP, exist_ok=True)
data = json.load(open('units.json', encoding='utf-8')); IPA = json.load(open('ipa.json', encoding='utf-8'))
from units_data import BOOKS
def b64img(im, q=80, side=420):
    im = im.convert('RGB'); im.thumbnail((side, side), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
def strip_img(en):
    p = f'{TMP}/{en}.pdf'; S = 300
    c = canvas.Canvas(p, pagesize=(S, S)); strips.draw(c, en, 0, 0, S); c.save()
    subprocess.run(['pdftoppm', '-r', '144', '-png', '-singlefile', p, p[:-4]], check=True)
    return Image.open(p[:-4] + '.png')
b64a = lambda f: 'data:audio/mpeg;base64,' + base64.b64encode(open(f, 'rb').read()).decode()
index = {'level': 'KET', 'books': [{'book': b, 'units': list(r)} for b, r in BOOKS], 'units': []}
thumbs = {}
for u in data:
    d = f"{AUD}/Unit {u['unit']:02d} - {u['title'].replace('?','').replace('–','-').replace(':',' -')}"
    words = []
    for i, w in enumerate(u['words'], 1):
        en = w['en']; item = {'en': en, 'vi': w['vi']}
        for k in ('tricky', 'syl', 'ex'):
            if w.get(k): item[k] = w[k]
        if IPA.get(en): item['ipa'] = IPA[en]
        f = f"images/u{u['unit']}/{en.replace('/', '_')}.jpg"
        if w.get('label'): item['label'] = w['label']; item['color'] = '#2E5C8A'
        else: item['img'] = b64img(Image.open(f)) if os.path.exists(f) else b64img(strip_img(en), q=85)
        name = en.replace('/', ' - ').replace("'", '').replace('?', '').replace('!', '')
        mp = f"{d}/{i:02d} {name}.mp3"; assert os.path.exists(mp), mp
        item['audio'] = b64a(mp); item['slow'] = b64a(f"{SLOW}/u{u['unit']:02d}_{i:02d}.mp3")
        words.append(item)
        if u['unit'] not in thumbs and os.path.exists(f): thumbs[u['unit']] = b64img(Image.open(f), q=75, side=160)
    out = {'unit': u['unit'], 'title': u['title'], 'sound': u.get('sound') or [], 'sound_name': u.get('sound_name', ''),
           'phrases': u.get('phrases', []), 'words': words}
    json.dump(out, open(f"{OUT}/u{u['unit']:02d}.json", 'w'), ensure_ascii=False, separators=(',', ':'))
    index['units'].append({'unit': u['unit'], 'title': u['title'], 'n': len(words)})
json.dump(index, open(f"{OUT}/index.json", 'w'), ensure_ascii=False, indent=1)
json.dump(thumbs, open(f"{OUT}/thumbs.json", 'w'))
print('done', len(index['units']))
