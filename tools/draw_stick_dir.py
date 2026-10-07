# -*- coding: utf-8 -*-
"""雪糕棍怎么摆在法兰盘上：左=现在这样（✗）  右=正确（✓）"""
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

fig, (axL, axR) = plt.subplots(1, 2, figsize=(14.5, 7.4), dpi=150)


def disc(ax):
    ax.add_patch(Circle((0, 0), 20, fc='#e6e9ee', ec='k', lw=1.6))
    for a in (90, 180, 270, 0):
        ax.add_patch(Circle((13 * math.cos(math.radians(a)), 13 * math.sin(math.radians(a))),
                            2.2, fc='white', ec='k', lw=1.1))
    ax.add_patch(Circle((0, 0), 3.4, fc='#9aa0a8', ec='k', lw=1.2))
    ax.text(0, 0, '磁铁', ha='center', va='center', fontsize=8.5, color='white')


def stick(ax, angle_deg, cx, cy, length=64, w=9):
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    order = [(cx + ux * 0 + px * (-w / 2), cy + uy * 0 + py * (-w / 2)),
             (cx + ux * 0 + px * (w / 2), cy + uy * 0 + py * (w / 2)),
             (cx + ux * length + px * (w / 2), cy + uy * length + py * (w / 2)),
             (cx + ux * length + px * (-w / 2), cy + uy * length + py * (-w / 2))]
    ax.add_patch(Polygon(order, closed=True, fc='#d8b47a', ec='k', lw=1.2))


# ---------- 左：✗ 斜着搭 ----------
disc(axL)
stick(axL, 32, -14, -26)          # 斜着横穿盘面
axL.text(0, 27, '× 现在这样：斜着搭过去', ha='center', fontsize=14, color='#b00')
axL.text(0, -40, '① 杆的中心线没有对准任何一个孔的圆心\n'
                 '② 杆盖住了盘心 —— 磁铁和传感器就在那儿\n'
                 '③ 偏心距离成了个说不清的斜距（不是 13mm）',
         ha='center', fontsize=11, color='#b00')
axL.set_xlim(-40, 40); axL.set_ylim(-46, 32); axL.set_aspect('equal'); axL.axis('off')

# ---------- 右：✓ 沿半径 ----------
disc(axR)
stick(axR, -90, 0, -7)            # 中心线 x=0，正好穿过下面那个孔的圆心
axR.add_patch(Circle((0, -13), 4.6, fc='#e8e8e8', ec='k', lw=1.1))
axR.add_patch(Circle((0, -13), 3.0, fc='#9aa0a8', ec='k', lw=1.1))
axR.plot([-19, 19], [0, 0], ls=':', color='#11407e', lw=1.0)
axR.annotate('', xy=(0, 0), xytext=(0, -13), arrowprops=dict(arrowstyle='<->', color='#b00', lw=1.4))
axR.text(1.5, -6.5, '偏心 13mm', fontsize=10.5, color='#b00')
axR.text(0, 27, '√ 正确：沿半径伸出去', ha='center', fontsize=14, color='#0a7a3a')
axR.text(0, -40, '① 杆的端头离盘心留 7~8mm，别盖住中间的凸起\n'
                 '② 杆的中心线正好穿过某个孔的圆心\n'
                 '③ 在杆上对应位置打孔，M4 螺杆从盘背面穿过来\n'
                 '     + 垫片 + 螺母拧死（画的就是这颗）',
         ha='center', fontsize=11, color='#0a7a3a')
axR.set_xlim(-40, 40); axR.set_ylim(-46, 32); axR.set_aspect('equal'); axR.axis('off')

fig.suptitle('雪糕棍装在法兰盘上：方向要对，还要真的锁住', fontsize=15)
fig.savefig(r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs\S3_雪糕棍安装方向.png',
            facecolor='white', bbox_inches='tight')
print('OK')
