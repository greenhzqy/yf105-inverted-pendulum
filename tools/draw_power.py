
# -*- coding: utf-8 -*-
"""供电接线对照图：正确（适配器/电池组直供电机） vs 错误（AMS1117 供电机）"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrow

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

fig, (axA, axB) = plt.subplots(1, 2, figsize=(15.5, 8), dpi=150)

def box(ax, x0, y0, x1, y1, t, fc, fs=11.5, ec='k'):
    ax.add_patch(Rectangle((x0, y0), x1-x0, y1-y0, fc=fc, ec=ec, lw=1.8, zorder=2))
    ax.text((x0+x1)/2, (y0+y1)/2, t, ha='center', va='center', fontsize=fs, zorder=3)

def seg(ax, p, c, lw=2.6, ls='-'):
    ax.plot([q[0] for q in p], [q[1] for q in p], color=c, lw=lw, ls=ls, zorder=1,
            solid_capstyle='round')

RED, BLK, GRY, BLU, GRN = '#d62728', '#111111', '#9aa0a8', '#1f6fd0', '#2e8b57'

# ================== 左：正确 ==================
axA.set_title('正确：电机吃"大电流电源"，逻辑单独供', fontsize=13, weight='bold')
box(axA, 0.03, 0.80, 0.30, 0.93, '12V ≥2A 适配器', '#dddddd')
box(axA, 0.36, 0.82, 0.46, 0.91, '保险丝 3A', '#f5d76e', fs=10.5)
axA.add_patch(Circle((0.55, 0.865), 0.032, fc=RED, ec='k', lw=1.5, zorder=2))
axA.text(0.55, 0.865, '按钮', ha='center', va='center', fontsize=12, color='w', zorder=3)
box(axA, 0.68, 0.78, 0.93, 0.95, 'TB6612\nVM  /  GND\nVCC / STBY\nPWMA/AIN1/AIN2\nA01 / A02', '#8b2f2f', fs=10.5)
seg(axA, [(0.30, 0.865), (0.33, 0.865)], RED, 3.2)
seg(axA, [(0.33, 0.865), (0.36, 0.865)], RED, 3.2)
seg(axA, [(0.46, 0.865), (0.52, 0.865)], RED, 3.2)
seg(axA, [(0.58, 0.865), (0.68, 0.865)], RED, 3.6)
axA.text(0.63, 0.885, 'VM 12V', fontsize=10.5, color=RED, ha='center')

box(axA, 0.06, 0.22, 0.30, 0.40, 'STM32 蓝丸\n(USB 供电)', '#1e7a46', fs=11)
axA.text(0.33, 0.215, '电脑 USB 供电（也可用 ST-Link 的 3V3）', fontsize=10.5, ha='left', color='#0a3d1f')
seg(axA, [(0.30, 0.34), (0.45, 0.34), (0.45, 0.60), (0.68, 0.60)], GRY, 2.6)
axA.text(0.565, 0.615, '3V3 → VCC（几十 mA）', fontsize=10.5, ha='center', color='#555')
seg(axA, [(0.30, 0.28), (0.40, 0.28), (0.40, 0.55), (0.50, 0.55), (0.50, 0.42), (0.68, 0.42)], GRN, 2.4)
axA.text(0.50, 0.35, '信号：PB0→PWMA, PA0→AIN1,\nPA1→AIN2, PA2→STBY', fontsize=10, ha='center', color=GRN)

axA.add_patch(Circle((0.98, 0.62), 0.035, fc='#4a6b8a', ec='k', lw=1.5, zorder=2))
axA.text(0.98, 0.62, 'M', ha='center', va='center', fontsize=13, color='w', zorder=3)
seg(axA, [(0.93, 0.88), (0.98, 0.66)], BLU, 2.8)
seg(axA, [(0.93, 0.82), (0.98, 0.59)], '#8a4b28', 2.8)
axA.text(1.0, 0.72, 'A01/A02', fontsize=10.5, ha='center')

axA.plot([0.02, 0.93], [0.10, 0.10], color=BLK, lw=4.0, zorder=1)
axA.text(0.47, 0.055, 'GND 公共地：适配器 −、TB6612 GND、蓝丸 GND 全部接这里',
         fontsize=11, ha='center', color=BLK)
seg(axA, [(0.06, 0.80) if False else (0.03, 0.80), (0.018, 0.80), (0.018, 0.10)], BLK, 3.0)
seg(axA, [(0.30, 0.22), (0.30, 0.14), (0.30, 0.10)], BLK, 2.6)
seg(axA, [(0.80, 0.78), (0.80, 0.10)], BLK, 2.6)
axA.set_xlim(0, 1.13); axA.set_ylim(0, 1.0); axA.axis('off')

# ================== 右：错误 ==================
axB.set_title('错误：AMS1117 给电机 → 只响不转 / 主控复位', fontsize=13, weight='bold', color='#a00')
box(axB, 0.03, 0.80, 0.24, 0.93, '电池', '#dddddd')
box(axB, 0.30, 0.80, 0.56, 0.93, 'AMS1117 模块\n(线性稳压 ≤1A)', '#f5d76e', fs=10.5)
box(axB, 0.66, 0.78, 0.92, 0.95, 'TB6612\nVM ← 3.3V', '#8b2f2f', fs=11)
seg(axB, [(0.24, 0.865), (0.30, 0.865)], RED, 3.0)
seg(axB, [(0.56, 0.865), (0.66, 0.865)], RED, 3.0)
axB.text(0.61, 0.865, 'X', fontsize=20, color='#a00', ha='center', va='center', weight='bold')
axB.add_patch(Rectangle((0.29, 0.70), 0.65, 0.055, fc='#fff5f5', ec='#a00', lw=1.2, zorder=4))
axB.text(0.615, 0.727, '电机一启动要 1~2.5A，AMS1117 只有 ≤1A → 电压塌陷',
         fontsize=11, color='#a00', ha='center', va='center', zorder=5)
box(axB, 0.06, 0.30, 0.30, 0.46, 'STM32 蓝丸', '#1e7a46', fs=11)
seg(axB, [(0.30, 0.865), (0.30, 0.60), (0.20, 0.60), (0.20, 0.46)], RED, 2.6, '--')
axB.text(0.33, 0.62, '3.3V 还要分给主控 → 一起被拖垮', fontsize=10, color='#a00', ha='left')
axB.text(0.06, 0.22, '症状对照：\n• 电机高频"滋滋"但不转（收到 PWM，没劲）\n'
         '• 主控莫名重启（电压跌到复位阈值以下）\n• 驱动/稳压块发烫',
         fontsize=11, color='#a00', va='top')

axB.add_patch(Rectangle((0.52, 0.20), 0.42, 0.24, fc='#f2fbf4', ec=GRN, lw=1.4, zorder=2))
axB.text(0.73, 0.415, '电池要用也行，这样接：', fontsize=11.5, color='#0a3d1f', ha='center', va='top', weight='bold')
axB.text(0.73, 0.365, '2~3 节 18650 串联（7.4~11.1V）\n→ 直接进 VM（不经过 AMS1117）\n'
         '电池 → AMS1117 → 3.3V → 只给主控', fontsize=10.5, color='#0a3d1f', ha='center', va='top')
axB.set_xlim(0, 1.13); axB.set_ylim(0, 1.0); axB.axis('off')

plt.tight_layout()
plt.savefig(r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs\S1_供电接线_对照.png', dpi=150, bbox_inches='tight')
print('saved')
