# -*- coding: utf-8 -*-
"""摆杆怎么锁在法兰盘上：左=正视（杆的中心线对准盘上的孔）  右=侧视剖面（螺杆穿盘+穿杆，前面拧螺母）"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyArrow

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

fig, (axL, axR) = plt.subplots(1, 2, figsize=(15.5, 7.6), dpi=150)

# ================= 左：正视 =================
axL.set_title('正视：杆的中心线对准盘上的孔（偏心距离 = 盘心到孔心）', fontsize=12.5)
axL.add_patch(Circle((0, 0), 20, fc='#dfe3e8', ec='k', lw=1.6))
for a in (90, 180, 270, 0):
    import math
    hx, hy = 13 * math.cos(math.radians(a)), 13 * math.sin(math.radians(a))
    axL.add_patch(Circle((hx, hy), 2.2, fc='white', ec='k', lw=1.1))
axL.add_patch(Circle((0, 0), 3.2, fc='#b9bfc7', ec='k', lw=1.2))
axL.text(0, 0, '磁铁\n粘这里', ha='center', va='center', fontsize=9, color='#8a6d00')

# 摆杆（竖直向下，中心线 x=0 正好穿过下面那个孔）
axL.add_patch(Rectangle((-3, -45), 6, 39, fc='#c96a1e', ec='k', lw=1.2))
axL.text(0, -35, '摆杆\n6×6mm', ha='center', va='center', fontsize=10.5, color='white')

# 螺杆 + 螺母（就在下面的孔里）
axL.add_patch(Circle((0, -13), 4.6, fc='#e8e8e8', ec='k', lw=1.1))
axL.add_patch(Circle((0, -13), 3.0, fc='#9aa0a8', ec='k', lw=1.1))
axL.annotate('M4 螺杆穿过\n盘孔 + 杆上的横孔\n前面加平垫+弹垫+螺母',
             xy=(2.5, -14.5), xytext=(24, -26), fontsize=10.5, color='#11407e', ha='center',
             arrowprops=dict(arrowstyle='->', color='#11407e', lw=1.2))

# 偏心距离标注
axL.annotate('', xy=(0, 0), xytext=(0, -13), arrowprops=dict(arrowstyle='<->', color='#b00', lw=1.4))
axL.text(-4.5, -7.5, '偏心距离\n(量出来，约 13mm)', fontsize=10.5, color='#b00', ha='right')
axL.plot([-19, 19], [-13, -13], ls=':', color='#11407e', lw=1.0)
axL.text(-19, -11.2, '杆的中心线', fontsize=9.5, color='#11407e')
axL.text(0, 22.5, '盘 φ40（量一下） 4 个孔 均布', ha='center', fontsize=11)
axL.text(-28, -42, '注意：杆的端头不要盖住盘心\n（磁铁和传感器要在中心）', fontsize=10.5, color='#333')
axL.set_xlim(-32, 32); axL.set_ylim(-48, 27); axL.set_aspect('equal'); axL.axis('off')

# ================= 右：侧视剖面 =================
axR.set_title('侧视剖面：杆平贴在盘的前面，螺杆从后面穿过来', fontsize=12.5)
axR.add_patch(Rectangle((-9, -8), 5, 16, fc='#4a6b8a', ec='k', lw=1.2))          # 电机/套筒
axR.text(-6.5, 10.5, '电机/套筒', ha='center', fontsize=10.5, color='#33507a')
axR.add_patch(Rectangle((0, -20), 3, 40, fc='#dfe3e8', ec='k', lw=1.6))          # 白盘截面
axR.text(1.5, 24, '白盘(法兰)', ha='center', fontsize=10.5)
axR.add_patch(Rectangle((3, -3.2), 5, 6.4, fc='#b9bfc7', ec='k', lw=1.2))        # 中心凸起(轴端)
axR.text(5.5, -6.5, '轴端/中心螺丝', ha='center', fontsize=9.5, color='#4a5560')
axR.add_patch(Rectangle((8, -5), 3, 10, fc='#f5c518', ec='k', lw=1.2))           # 磁铁
axR.text(9.5, 8.5, '磁铁', ha='center', fontsize=10.5, color='#8a6d00')
axR.add_patch(Rectangle((11.5, -4), 1.5, 8, fc='#123f27', ec='k', lw=1.0))       # 芯片
axR.add_patch(Rectangle((13, -8), 2, 16, fc='#2e8b57', ec='k', lw=1.2))          # 传感器板
axR.text(14.5, 14.5, 'AS5600', ha='center', fontsize=10.5, color='#1a5c33')
axR.annotate('', xy=(11, 6.2), xytext=(13, 6.2), arrowprops=dict(arrowstyle='<->', color='b', lw=1.4))
axR.text(12, 6.9, '1~2mm', ha='center', fontsize=9.5, color='b')

# 摆杆（贴在盘前面）与螺杆
axR.add_patch(Rectangle((3, -19), 6, 6, fc='#c96a1e', ec='k', lw=1.2))
axR.text(4, -26.5, '摆杆平贴在盘的前面上', ha='center', fontsize=10.5, color='#a0522d')
axR.add_patch(Rectangle((-4.5, -17.2), 3, 3.4, fc='#9aa0a8', ec='k', lw=1.1))    # 螺杆头
axR.add_patch(Rectangle((-1.5, -16.2), 11, 1.4, fc='#9aa0a8', ec='k', lw=1.0))   # 螺杆
axR.add_patch(Rectangle((9.5, -17.4), 1.2, 3.8, fc='#c0c8d0', ec='k', lw=1.0))   # 平垫
axR.add_patch(Rectangle((10.7, -17.4), 1.0, 3.8, fc='#e0c060', ec='k', lw=1.0))  # 弹垫
axR.add_patch(Rectangle((11.7, -17.6), 3.0, 4.2, fc='#9aa0a8', ec='k', lw=1.1))  # 螺母
axR.text(14, -31.5, '螺母在杆的前面', ha='center', fontsize=10.5, color='#4a5560')
axR.text(-11, -35, '螺母在半径 13mm 处，传感器只伸到半径 11mm —— 不打架', fontsize=10, color='#b00')
axR.set_xlim(-12, 24); axR.set_ylim(-36, 30); axR.set_aspect('equal'); axR.axis('off')

fig.text(0.5, 0.045, '判据：拧死后手扳摆杆，杆和盘之间不能有任何相对转动；拔掉电源手拨一整圈，不碰任何东西',
         fontsize=12.5, color='#b00', ha='center',
         bbox=dict(boxstyle='round', fc='#fff4f4', ec='#d33', lw=1.3))

out = r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs\S3_摆杆锁法兰_具体做法.png'
fig.savefig(out, facecolor='white')
print('OK', out)
