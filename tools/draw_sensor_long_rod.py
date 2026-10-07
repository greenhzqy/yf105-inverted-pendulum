# -*- coding: utf-8 -*-
"""杆变长了，传感器放哪儿？—— 左：端面全景（杆扫过的大圆盘）  右：中心放大（传感器只待在这 15mm 小圈里）"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

fig, (axL, axR) = plt.subplots(1, 2, figsize=(15.5, 8), dpi=150)

# ---------------- 左：端面全景 ----------------
axL.set_title('端面看（从轴头往里看）：杆扫过的是一个大圆盘', fontsize=13)
axL.add_patch(Circle((0, 0), 250, fc='#ffeaea', ec='#d33', lw=1.6, ls='--'))
axL.add_patch(Rectangle((-4.5, -250), 9, 237, fc='#d8b47a', ec='k', lw=1.2))   # 杆
axL.add_patch(Circle((0, 0), 20, fc='#e6e9ee', ec='k', lw=1.4))                # 法兰
axL.add_patch(Rectangle((-7, -7), 14, 14, fc='#2e8b57', ec='k', lw=1.2))       # 中心：传感器所在
axL.text(30, -215, '摆杆（25cm）', fontsize=12, color='#a0522d')
axL.text(0, 268, '摆杆扫过的圆盘（半径 = 杆长）', fontsize=12.5, color='#d33', ha='center')
axL.annotate('传感器在这儿', xy=(9, 9), xytext=(90, 120), fontsize=12.5, color='#1a5c33',
             arrowprops=dict(arrowstyle='->', color='#1a5c33', lw=1.3))
axL.annotate('', xy=(-30, -30), xytext=(-95, -120), arrowprops=dict(arrowstyle='->', color='#11407e', lw=1.4))
axL.text(-100, -132, '放大看右边 →', fontsize=12, color='#11407e', ha='center')
axL.plot([-30, 30, 30, -30, -30], [-30, -30, 30, 30, -30], ls=':', color='#11407e', lw=1.2)
axL.text(0, -292, '杆再长，也只是外面这个圆环变大 —— 中心那个小圈永远空着', fontsize=12.5,
         color='#b00', ha='center')
axL.set_xlim(-300, 300); axL.set_ylim(-315, 300); axL.set_aspect('equal'); axL.axis('off')

# ---------------- 右：中心放大 ----------------
axR.set_title('中心放大（±30mm）：传感器和支架只许待在 15mm 小圈里', fontsize=13)
axR.add_patch(Circle((0, 0), 20, fc='#e6e9ee', ec='k', lw=1.5))                # 法兰
for i, (hx, hy) in enumerate([(0, 13), (0, -13), (13, 0), (-13, 0)]):
    axR.add_patch(Circle((hx, hy), 2.3, fc='white', ec='k', lw=1.1))
axR.add_patch(Circle((0, 0), 15, fc='none', ec='#0a7a3a', lw=1.8, ls='--'))    # 安全圈
axR.add_patch(Circle((0, 0), 5, fc='#f5c518', ec='k', lw=1.2))                 # 磁铁
axR.add_patch(Rectangle((-8, -8), 16, 16, fc='#2e8b57', ec='k', lw=1.2, alpha=0.45))  # AS5600
axR.add_patch(Rectangle((-2.5, -2.5), 5, 5, fc='#123f27', ec='k', lw=1.0))
axR.add_patch(Rectangle((-4.5, -30), 9, 26, fc='#d8b47a', ec='k', lw=1.2))     # 杆（从下面的孔出去）
axR.add_patch(Rectangle((-24, -3), 14, 6, fc='#5a6470', ec='k', lw=1.2))       # 支架（沿轴心伸进来）
axR.text(-26, -9, '支架', fontsize=10.5, color='#40485a', ha='center')
axR.annotate('安全圈：离轴心 15mm 以内\n（传感器 + 支架都塞在这里）', xy=(11, 11), xytext=(42, 62),
             fontsize=12, color='#0a7a3a', ha='center',
             arrowprops=dict(arrowstyle='->', color='#0a7a3a', lw=1.3))
axR.annotate('磁铁粘盘心', xy=(3.5, 3.5), xytext=(52, 14), fontsize=11.5, color='#8a6d00', ha='center',
             arrowprops=dict(arrowstyle='->', color='#8a6d00', lw=1.1))
axR.annotate('AS5600 芯片正对磁铁\n（间隙 1~2mm）', xy=(8, 8), xytext=(60, -30), fontsize=11.5,
             color='#1a5c33', ha='center', arrowprops=dict(arrowstyle='->', color='#1a5c33', lw=1.1))
axR.annotate('杆：装在盘边 13mm 的孔上\n（这条 15mm 线以外才是它的地盘）', xy=(4.5, -20), xytext=(-2, -66),
             fontsize=11.5, color='#a0522d', ha='center',
             arrowprops=dict(arrowstyle='->', color='#a0522d', lw=1.1))
axR.text(0, 84, '图上 AS5600 和杆重叠，是"沿轴心方向看"造成的\n—— 它们其实错开在前后两层，永远碰不到', fontsize=11.5,
         color='#b00', ha='center')
axR.set_xlim(-70, 70); axR.set_ylim(-80, 95); axR.set_aspect('equal'); axR.axis('off')

fig.suptitle('杆变长了，传感器放哪儿？—— 位置完全没变，还是盘心那 15mm', fontsize=15)
fig.savefig(r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs\S3_长杆怎么放传感器.png',
            facecolor='white', bbox_inches='tight')
print('OK')
