"""Export Movers units -> app/data/movers/uNN.json (words + base64 small JPEG + base64 MP3) and index.json"""
import sys, os, json, base64, io, subprocess, glob
sys.path.insert(0, '/home/claude/movers/kit')
os.chdir('/home/claude/movers/kit')
import units_data, strips
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
AUD = '/home/claude/tts/audio'
OUT = '/home/claude/app/data/movers'
os.makedirs(OUT, exist_ok=True)
TMP = '/tmp/claude-0/-home-claude/34a351eb-1bd2-5a23-807c-f6bfa24ae5d2/scratchpad/strip'
os.makedirs(TMP, exist_ok=True)
NUMCOL = ["#D6336C", "#2E5C8A", "#E8760A", "#7B4B94", "#2B8A3E"]

def b64img(im, q=80, side=420):
    im = im.convert('RGB'); im.thumbnail((side, side), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()

def strip_img(en):
    p = f'{TMP}/{en}.pdf'; S = 300
    c = canvas.Canvas(p, pagesize=(S, S)); strips.draw(c, en, 0, 0, S); c.save()
    subprocess.run(['pdftoppm', '-r', '144', '-png', '-singlefile', p, p[:-4]], check=True)
    return Image.open(p[:-4] + '.png')

books = {1: range(1, 8), 2: range(8, 16), 3: range(16, 23)}
index = {'level': 'Movers', 'books': []}
for bn, rng in books.items():
    index['books'].append({'book': bn, 'units': list(rng)})
units = []
for u in units_data.parse():
    d = f"{AUD}/Unit {u['unit']:02d} - {u['title'].replace('?','').replace('–','-')}"
    words = []
    for i, w in enumerate(u['words'], 1):
        en = w['en']
        item = {'en': en, 'vi': w['vi']}
        if w.get('tricky'): item['tricky'] = w['tricky']
        if w.get('syl'): item['syl'] = w['syl']
        if u.get('numbers'):
            item['label'] = u['labels'][i - 1]; item['color'] = NUMCOL[i % len(NUMCOL)]
        elif en in strips.SPEC:
            item['img'] = b64img(strip_img(en), q=85)
        else:
            f = f"images/u{u['unit']}/{en.replace('/', '_')}.jpg"
            item['img'] = b64img(Image.open(f))
        name = en.replace('/', ' - ').replace("'", '')
        mp = f"{d}/{i:02d} {name}.mp3"
        assert os.path.exists(mp), mp
        item['audio'] = 'data:audio/mpeg;base64,' + base64.b64encode(open(mp, 'rb').read()).decode()
        words.append(item)
    data = {'unit': u['unit'], 'title': u['title'], 'sound': u['sound'], 'sound_name': u['sound_name'], 'words': words}
    json.dump(data, open(f"{OUT}/u{u['unit']:02d}.json", 'w'), ensure_ascii=False, separators=(',', ':'))
    units.append({'unit': u['unit'], 'title': u['title'], 'n': len(words), 'sound': u['sound'],
                  'cover': next((x['img'] for x in words if 'img' in x), None) and None})
index['units'] = [{'unit': x['unit'], 'title': x['title'], 'n': x['n']} for x in units]
json.dump(index, open(f"{OUT}/index.json", 'w'), ensure_ascii=False, indent=1)
# small unit thumbnails (first picture) for the home grid
thumbs = {}
for u in units_data.parse():
    for w in u['words']:
        f = f"images/u{u['unit']}/{w['en'].replace('/', '_')}.jpg"
        if not u.get('numbers') and os.path.exists(f):
            thumbs[u['unit']] = b64img(Image.open(f), q=75, side=160); break
json.dump(thumbs, open(f"{OUT}/thumbs.json", 'w'))
print('done')
