# -*- coding: utf-8 -*-
"""远端仓库自检：README 里的图片/链接是否都能解析、有没有把不该传的传上去。"""
import json
import re
import subprocess
import urllib.request

REPO = 'greenhzqy/yf105-inverted-pendulum'
GH = r'D:\githubcli\gh.exe'

raw = urllib.request.urlopen(f'https://raw.githubusercontent.com/{REPO}/main/README.md').read().decode('utf-8')
out = subprocess.run([GH, 'api', f'repos/{REPO}/git/trees/main?recursive=1'],
                     capture_output=True, text=True, encoding='utf-8')
data = json.loads(out.stdout)
paths = {e['path'] for e in data['tree'] if e['type'] == 'blob'}
print('远端文件总数:', len(paths))
print('仓库体积(KB):', round(data.get('tree', [{}])[0].get('size', 0) / 1024, 1) if False else '—')

refs = re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', raw)
bad = 0
print('\nREADME 引用检查：')
for r in refs:
    if r.startswith('http'):
        print(f'  [外链] {r}')
        continue
    target = r.rstrip('/')
    ok = target in paths or any(p.startswith(target + '/') for p in paths)
    print(('  OK   ' if ok else '  MISS ') + r)
    if not ok:
        bad += 1

print('\n损坏引用数:', bad)
print('是否混入弃用的旧小车归档:', any('旧版小车' in p for p in paths))
print('是否混入 dll/__pycache__/tmp:', any(p.endswith(('.dll', '.tmp', '.o')) or '__pycache__' in p for p in paths))
print('\n顶层条目:')
for e in sorted({p.split('/')[0] for p in paths}):
    n = sum(1 for p in paths if p.split('/')[0] == e or p.startswith(e + '/'))
    print(f'  {e}  ({n} 个文件)')
