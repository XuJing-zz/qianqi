import os, re, uuid, json
from django.conf import settings
from skills.models import Skill

IMG_DIR = os.path.join(settings.MEDIA_ROOT, 'skill_images')
os.makedirs(IMG_DIR, exist_ok=True)

KEY2NAME = {
    'fengxiang': '凤翔罩金漆器制作技艺',
    'diaotian':  '雕填漆器髹饰技艺',
    'tuotai':    '脱胎漆器髹饰技艺',
    'weifang':   '漆器髹饰技艺（潍坊嵌银髹漆技艺）',
    'guilin':    '桂林漆器制作技艺',
    'shanghai':  '上海漆器制作技艺',
    'yangjiang': '漆器髹饰技艺（阳江漆器髹饰技艺）',
    'puning':    '金漆画（普宁铁笔金漆画）',
}
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '_imgwork', 'gen8', 'out')

def norm_copy(src_path, name):
    from PIL import Image
    ext = os.path.splitext(src_path)[1].lower()
    if ext in ('.jpg', '.jpeg', '.png', '.webp'):
        im = Image.open(src_path)
    else:
        raise ValueError('unsupported ext %s' % src_path)
    im = im.convert('RGB')
    fn = uuid.uuid4().hex + '.png'
    im.save(os.path.join(IMG_DIR, fn), 'PNG')
    return 'skill_images/' + fn

def url_of(rel):
    return 'http://127.0.0.1:8001/media/' + rel

def slots_order(entries):
    return ['cover'] + \
        sorted([s for s in entries if re.fullmatch(r's\d+', s)], key=lambda x: int(x[1:])) + \
        sorted([s for s in entries if re.fullmatch(r'c\d+', s)], key=lambda x: int(x[1:]))

def ingest_for(key):
    name = KEY2NAME[key]
    sk = Skill.objects.filter(name=name).first()
    if not sk:
        print('!! skill not found', name); return 0
    d = os.path.join(SRC, key)
    if not os.path.isdir(d):
        print('!! no src dir', d); return 0
    imgs = {s for s in os.listdir(d) if os.path.splitext(s)[1].lower() in ('.png', '.jpg', '.jpeg') and not s.endswith('_v.png') and not s.endswith('_t.png')}
    base = {os.path.splitext(x)[0]: os.path.join(d, x) for x in imgs}
    cnt = 0
    body = dict(sk.body or {})
    if 'cover' in base:
        rel = norm_copy(base['cover'], name)
        sk.image = url_of(rel); cnt += 1
    steps = list(body.get('steps', []))
    step_keys = sorted([s for s in base if re.fullmatch(r's\d+', s)], key=lambda x: int(x[1:]))
    for i, k in enumerate(step_keys):
        if i < len(steps):
            rel = norm_copy(base[k], name)
            st = dict(steps[i]); st['image'] = url_of(rel); steps[i] = st; cnt += 1
    if steps:
        body['steps'] = steps
    cards = list(body.get('cards', []))
    card_keys = sorted([c for c in base if re.fullmatch(r'c\d+', c)], key=lambda x: int(x[1:]))
    for i, k in enumerate(card_keys):
        if i < len(cards):
            rel = norm_copy(base[k], name)
            ca = dict(cards[i]); ca['image'] = url_of(rel); cards[i] = ca; cnt += 1
    if cards:
        body['cards'] = cards
    sk.body = body
    sk.save(update_fields=['image', 'body'])
    print('ingested %s (%d/%d imgs)' % (name, cnt, len(base)))
    return cnt

def main():
    total = 0
    for key in KEY2NAME:
        total += ingest_for(key)
    print('=== ingested total', total)

def dump_manifest():
    MANIFEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'skill_images_manifest.json')
    out = {}
    for s in Skill.objects.all():
        b = s.body or {}
        steps = b.get('steps', [])
        cards = b.get('cards', [])
        has = s.image or any(x.get('image') for x in steps) or any(x.get('image') for x in cards)
        if not has:
            continue
        out[s.name] = {
            'cover': s.image or '',
            'steps': [x.get('image', '') for x in steps],
            'cards': [x.get('image', '') for x in cards],
        }
    with open(MANIFEST, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print('manifest dumped %d crafts -> %s' % (len(out), MANIFEST))

if __name__ == '__main__':
    main()
    dump_manifest()
