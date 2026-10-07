# -*- coding: utf-8 -*-
"""把固件/装配的关键图挑出来、压成适合进仓库的尺寸。

原图留在工作目录（D:\\harness\\学业\\yf105招新\\25级-倒立摆实物\\figs）不动，
这里只生成仓库用的压缩副本。
"""
import os
from PIL import Image

SRC = r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs'
DST = r'D:\harness\学业\yf105招新\25级-倒立摆\assets\rig'
os.makedirs(DST, exist_ok=True)

PICK = [
    'S1_实物标注_法兰与磁铁位置.png',
    'S1_接线图.png',
    'S1_AS5600安装位置.png',
    'S1_供电接线_对照.png',
    'S1_运动与采集原理.png',
    'S1_装配示意_3D.png',
    'S3_正确组装_3D图.png',
    'S3_正确组装_工序图.png',
    'S3_长杆怎么放传感器.png',
    'S2_dump_v9.png',
    'S2_阻塞vs非阻塞.png',
]

for name in PICK:
    p = os.path.join(SRC, name)
    if not os.path.exists(p):
        print('  [skip] 不存在:', name)
        continue
    im = Image.open(p).convert('RGB')
    w, h = im.size
    if w > 1100:
        im = im.resize((1100, int(h * 1100 / w)), Image.LANCZOS)
    out = os.path.join(DST, os.path.splitext(name)[0] + '.jpg')
    im.save(out, 'JPEG', quality=82, optimize=True)
    print(f'  {name}: {os.path.getsize(p)//1024} KB -> {os.path.getsize(out)//1024} KB ({im.size[0]}x{im.size[1]})')

# 顶部 README 用的一张主图
hero_src = os.path.join(SRC, 'S1_实物标注_法兰与磁铁位置.png')
hero = os.path.join(DST, 'hero_法兰与磁铁位置.jpg')
im = Image.open(hero_src).convert('RGB')
w, h = im.size
im = im.resize((1200, int(h * 1200 / w)), Image.LANCZOS)
im.save(hero, 'JPEG', quality=85, optimize=True)
print(f'  hero: {os.path.getsize(hero_src)//1024} KB -> {os.path.getsize(hero)//1024} KB')

tot = sum(os.path.getsize(os.path.join(DST, f)) for f in os.listdir(DST))
print(f'\nassets/rig 合计 {len(os.listdir(DST))} 张、{tot/1024/1024:.2f} MB')
