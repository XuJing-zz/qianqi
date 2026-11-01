import base64, os, re
from django.conf import settings
from skills.models import Skill

ORDER = [188, 186, 185, 184, 183, 182, 181, 180, 179, 178, 177, 176]
LAYOUT = [
    (5, 2), (3, 3), (4, 2), (2, 3), (4, 2), (3, 3),
    (3, 2), (5, 3), (4, 2), (2, 3), (5, 2), (3, 2),
]

def disk_of(url):
    if not url:
        return ''
    m = re.search(r'/media/(.+)$', url)
    if not m:
        return ''
    return os.path.join(settings.MEDIA_ROOT, m.group(1))

def b64(path):
    with open(path, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()

def main():
    craft_bg = r'C:/Users/yu_an/Desktop/qianqi/frontend/public/imgs/home/craft-bg.jpg'
    bg_css = ''
    if os.path.exists(craft_bg):
        with open(craft_bg, 'rb') as f:
            b = base64.b64encode(f.read()).decode()
        bg_css = ("url('data:image/jpeg;base64,%s') center / cover no-repeat, " % b)
    cards = []
    for i, sid in enumerate(ORDER):
        s = Skill.objects.filter(id=sid).first()
        if not s:
            continue
        c, r = LAYOUT[i % len(LAYOUT)]
        disk = disk_of(s.image)
        img = b64(disk) if disk and os.path.exists(disk) else ''
        name = s.name
        tag = s.level or s.category or ''
        glyph = s.glyph or name[0]
        desc = s.desc or s.abstract or ''
        cards.append(dict(id=sid, c=c, r=r, img=img, name=name, tag=tag,
                          glyph=glyph, desc=desc))
    items = []
    for cd in cards:
        style = 'grid-column:span %d;grid-row:span %d;' % (cd['c'], cd['r'])
        if cd['img']:
            style += 'background-image:url(%s);' % cd['img']
            inner = ('<div class="craft-scrim"></div>'
                     '<div class="craft-info craft-info-img">'
                     '<h3 class="craft-name craft-name-img">%s</h3>'
                     '<span class="craft-tag craft-tag-img">%s</span>'
                     '</div>') % (cd['name'], cd['tag'])
        else:
            inner = ('<div class="craft-glyph">%s</div>'
                     '<div class="craft-info">'
                     '<h3 class="craft-name">%s</h3>'
                     '<p class="craft-desc">%s</p>'
                     '<span class="craft-tag">%s</span>'
                     '</div>') % (cd['glyph'], cd['name'], cd['desc'], cd['tag'])
        items.append('<div class="craft-item craft-hasimg" style="%s">%s</div>' % (style, inner))
    items_html = '\n        '.join(items)

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>技艺档案 · 漆器非遗首页区块复刻</title>
<style>
* { box-sizing: border-box; }
body { margin:0; font-family: "Noto Serif SC","Source Han Serif SC","Songti SC","SimSun",serif; background:#f5efe4; color:#2b2117; }
.craft { padding: 72px 8vw; background:
  linear-gradient(180deg, rgba(245,239,228,.55), rgba(245,239,228,.85)),
  BGBG#f5efe4; }
.craft-title { margin:0; font-size:34px; letter-spacing:10px; color:#2b2117; }
.craft-en { display:block; margin-top:6px; font-size:12px; letter-spacing:4px; color:#b3a383; }
.craft-list { margin-top:44px; display:grid; grid-template-columns:repeat(12,1fr);
  grid-auto-rows:96px; gap:20px; max-width:1280px; margin-left:auto; margin-right:auto; }
.craft-item { display:flex; flex-direction:column; justify-content:center; align-items:center;
  gap:10px; padding:18px; text-decoration:none; cursor:pointer; background:#fff;
  border:1px solid #e8dec8; overflow:hidden;
  opacity:0; transform:translateY(80px) scale(.8);
  transition: transform .9s cubic-bezier(.34,1.56,.64,1), opacity .7s ease, box-shadow .3s ease; }
.craft-item:nth-child(odd) { transform:translateX(-120px) translateY(40px) scale(.85); }
.craft-item:nth-child(even){ transform:translateX(120px) translateY(40px) scale(.85); }
.craft-item.in { opacity:1; transform:translateX(0) translateY(0) scale(1); }
.craft-item:hover { box-shadow:0 18px 40px rgba(43,33,23,.18); }
.craft-item.craft-hasimg { position:relative; justify-content:flex-end; align-items:stretch;
  gap:0; padding:0; background-size:cover; background-position:center; border:none; }
.craft-scrim { position:absolute; inset:0;
  background:linear-gradient(180deg, rgba(43,33,23,0) 28%, rgba(43,33,23,.45) 72%, rgba(43,33,23,.78) 100%); }
.craft-hasimg .craft-info { position:relative; width:100%; align-self:stretch;
  justify-content:flex-end; align-items:flex-start; text-align:left; padding:28px 18px 16px; }
.craft-info { display:flex; flex-direction:column; align-items:center; text-align:center; }
.craft-name { margin:0 0 4px; font-size:20px; letter-spacing:4px; color:#2b2117; }
.craft-name-img { color:#fff; text-shadow:0 1px 8px rgba(0,0,0,.4); margin:0 0 8px; }
.craft-desc { margin:0 0 6px; font-size:14px; line-height:1.6; color:#6b5a42;
  max-width:22em; overflow:hidden; }
.craft-glyph { width:56px; height:56px; display:flex; align-items:center; justify-content:center;
  background:#8b2e1c; color:#f5efe4; font-size:28px; flex-shrink:0; }
.craft-tag { display:inline-block; padding:2px 12px; border:1px solid #8b2e1c; color:#8b2e1c;
  font-size:11px; letter-spacing:1px; }
.craft-tag-img { color:#fff; border-color:rgba(255,255,255,.9); background:rgba(43,33,23,.18); }
.craft-more { margin-top:44px; text-align:center; }
.craft-more-btn { display:inline-block; padding:12px 44px; border:1px solid #8b2e1c; color:#8b2e1c;
  font-size:15px; letter-spacing:4px; text-decoration:none; transition:background .25s ease,color .25s ease; }
.craft-more-btn:hover { background:#8b2e1c; color:#f5efe4; }
.note { padding:14px 8vw 0; font-size:12px; letter-spacing:2px; color:#a2947e; }
@media (max-width:768px){ .craft-list{ grid-template-columns:repeat(2,1fr); grid-auto-rows:150px; }
  .craft-item,.craft-item.offset{ margin-left:0; align-items:flex-start; } }
</style>
</head>
<body>
  <div class="note">▍复刻自漆器非遗平台首页「技艺档案」区块 · 封面图内嵌, 双击即可离线查看</div>
  <section class="craft">
    <h2 class="craft-title">技 艺 档 案</h2>
    <span class="craft-en">CRAFT ARCHIVES</span>
    <div class="craft-list">
        {ITEMS}
    </div>
    <div class="craft-more">
      <a class="craft-more-btn" href="http://localhost:5173/archive" target="_blank">查看更多技艺</a>
    </div>
  </section>
<script>
// 单文件首屏即技艺区: 打开后错峰自动入场(0.12s×4 轮), 无需滚动
(function(){
  var cards = Array.prototype.slice.call(document.querySelectorAll('.craft-item'));
  if(!cards.length) return;
  cards.forEach(function(c,i){
    setTimeout(function(){ c.style.transitionDelay = (i%4)*0.12+'s'; c.classList.add('in'); }, 120 + i*70);
  });
})();
</script>
</body>
</html>
"""
    html = html.replace('BGBG', bg_css).replace('{ITEMS}', items_html)
    out = r'C:/Users/yu_an/Desktop/技艺档案·首页复刻.html'
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print('wrote', out, '%.1f KB' % (os.path.getsize(out) / 1024), 'cards=%d' % len(cards))

if __name__ == '__main__':
    main()
