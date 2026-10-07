# -*- coding: utf-8 -*-
"""轴的方向决定一切：左=轴竖直（杆在水平面里转，永远不倒）  右=轴水平（杆像钟摆，必然往下掉）"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse, FancyArrowPatch, Arc

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

fig, (axL, axR) = plt.subplots(1, 2, figsize=(15, 7.4), dpi=150)


def ground(ax):
    ax.plot([-60, 60], [0, 0], color='#8a6a3a', lw=3)
    ax.text(52, -5, '桌面', fontsize=10.5, color='#8a6a3a', ha='center')


def garrow(ax, x, y, s=16, txt='重力'):
    ax.add_patch(FancyArrowPatch((x, y), (x, y - s), arrowstyle='-|>', mutation_scale=16,
                                 color='#c02020', lw=2.0))
    ax.text(x + 3, y - s / 2, txt, fontsize=11, color='#c02020', va='center')


# ---------------- 左：轴竖直 ----------------
axL.set_title('× 轴竖直（电机躺着、轴朝上）', fontsize=14, color='#b00')
ground(axL)
axL.add_patch(Rectangle((-45, 2), 34, 24, fc='#8f979f', ec='k', lw=1.3))         # 电机躺着
axL.add_patch(Rectangle((-31, 26), 6, 16, fc='#b9bfc7', ec='k', lw=1.2))         # 轴朝上
axL.add_patch(Ellipse((-28, 44), 62, 12, fc='#e6e9ee', ec='k', lw=1.5))          # 法兰（水平盘）
axL.add_patch(Rectangle((-28, 46), 64, 5, fc='#d8b47a', ec='k', lw=1.2))         # 杆（水平）
garrow(axL, 8, 47)
axL.add_patch(Arc((-28, 44), 86, 30, theta1=200, theta2=340, color='#11407e', lw=2.0, ls='--'))
axL.add_patch(FancyArrowPatch((14, 34), (17, 32), arrowstyle='-|>', mutation_scale=14, color='#11407e', lw=2))
axL.text(-56, 84, '杆在水平面里转圈\n（像放在桌上的钟表指针）', fontsize=12, color='#11407e', va='top')
axL.text(-56, 66, '重力方向和转轴平行\n→ 对转轴没有力矩\n→ 松手停在哪就是哪，\n   加多重都不倒', fontsize=12, color='#b00', va='top')
axL.set_xlim(-60, 60); axL.set_ylim(-12, 100); axL.set_aspect('equal'); axL.axis('off')

# ---------------- 右：轴水平 ----------------
axR.set_title('√ 轴水平（电机立着、轴水平）', fontsize=14, color='#0a7a3a')
ground(axR)
axR.add_patch(Rectangle((-48, 2), 10, 62, fc='#c8a263', ec='k', lw=1.3))          # 立板
axR.add_patch(Rectangle((-36, 30), 26, 22, fc='#8f979f', ec='k', lw=1.3))         # 电机
axR.add_patch(Rectangle((-10, 37), 14, 7, fc='#b9bfc7', ec='k', lw=1.2))          # 轴（水平）
axR.add_patch(Ellipse((6, 40), 10, 46, fc='#e6e9ee', ec='k', lw=1.5))             # 法兰（竖直盘）
axR.add_patch(Rectangle((4, 3), 6, 37, fc='#d8b47a', ec='k', lw=1.2))            # 杆（垂下去）
garrow(axR, 20, 26)
axR.add_patch(Arc((7, 40), 60, 60, theta1=180, theta2=360, color='#0a7a3a', lw=2.0, ls='--'))
axR.add_patch(FancyArrowPatch((37, 40), (39, 44), arrowstyle='-|>', mutation_scale=14, color='#0a7a3a', lw=2))
axR.text(-58, 84, '杆上下荡\n（像挂钟的摆锤）', fontsize=12, color='#0a7a3a', va='top')
axR.text(-58, 66, '重力方向和转轴垂直\n→ 对转轴有力矩\n→ 松手一定往下掉，\n   最后停在最低点', fontsize=12, color='#0a7a3a', va='top')
axR.set_xlim(-60, 60); axR.set_ylim(-12, 100); axR.set_aspect('equal'); axR.axis('off')

fig.suptitle('“松手不倒”先查这一件事：转轴到底是竖直还是水平', fontsize=15)
fig.savefig(r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs\S3_轴的方向_竖直vs水平.png',
            facecolor='white', bbox_inches='tight')
print('OK')
