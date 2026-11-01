import json
import os
from skills.models import Skill

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, 'skill_bodies.json'), encoding='utf-8') as f:
    data = json.load(f)

updated, missing = [], []
for name, body in data.items():
    qs = Skill.objects.filter(name=name)
    if qs.exists():
        qs.update(body=body)
        updated.append(name)
    else:
        missing.append(name)

print('已写入 %d 条：' % len(updated))
for n in updated:
    print('  ✓', n)
if missing:
    print('未找到 %d 条（跳过，需核对名称）：' % len(missing))
    for n in missing:
        print('  ✗', n)
