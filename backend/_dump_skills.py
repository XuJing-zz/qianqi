import os, django, json, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()
from skills.models import Skill
rows=[]
for s in Skill.objects.all().order_by('id'):
    b = s.body or {}
    rows.append({
      'id': s.id, 'name': s.name, 'status': s.status,
      'owner': getattr(s.owner,'name',None) or (s.owner_id and str(s.owner_id)),
      'level': getattr(s,'level',None), 'region': getattr(s,'region',None),
      'cat': getattr(s,'category',None),
      'image': bool(getattr(s,'image',None)),
      'hist': len(b.get('history') or []),
      'steps': len(b.get('steps') or []),
      'steps_img': len([x for x in (b.get('steps') or []) if x.get('image')]),
      'cards': len(b.get('cards') or []),
      'cards_img': len([x for x in (b.get('cards') or []) if x.get('image')]),
      'has_body': bool(b),
    })
out = r'C:\Users\yu_an\Desktop\小工具\_skills_dump.json'
json.dump(rows, open(out,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('WROTE', out, len(rows))
print('with body:', sum(1 for r in rows if r['has_body']))
