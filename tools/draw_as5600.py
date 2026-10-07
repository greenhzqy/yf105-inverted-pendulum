
# -*- coding: utf-8 -*-
"""AS5600 七脚模块接线示意"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(13.5, 7.5), dpi=150)

RED, BLK, GRN, GRY = '#d62728', '#111111', '#2e8b57', '#9aa0a8'

# AS5600 模块
ax.add_patch(Rectangle((0.08, 0.16), 0.22, 0.66, fc='#1e5c3a', ec='k', lw=2))
ax.text(0.19, 0.865, 'AS5600 磁编码器模块', ha='center', fontsize=13, weight='bold')
pins = ['VCC', 'OUT', 'GND', 'DIR', 'SCL', 'SDA', 'GPO']
ys = [0.74, 0.655, 0.57, 0.485, 0.40, 0.315, 0.23]
for name, y in zip(pins, ys):
    ax.plot([0.30, 0.325], [y, y], color='#ffd700', lw=3)
    ax.text(0.285, y, name, ha='right', va='center', fontsize=12, color='w', weight='bold')

# STM32 蓝丸
ax.add_patch(Rectangle((0.70, 0.30), 0.22, 0.46, fc='#1e7a46', ec='k', lw=2))
ax.text(0.81, 0.72, 'STM32 蓝丸', ha='center', fontsize=13, weight='bold', color='w')
for name, y in zip(['3V3', 'GND', 'PB6', 'PB7'], [0.655, 0.57, 0.415, 0.33]):
    ax.plot([0.70, 0.675], [y, y], color='#ffd700', lw=3)
    ax.text(0.715, y, name, ha='left', va='center', fontsize=12, color='w')

def wire(y0, y1, color, label=None, lx=0.50):
    ax.plot([0.325, 0.50, 0.50, 0.675], [y0, y0, y1, y1], color=color, lw=2.8,
            solid_capstyle='round')
    if label:
        ax.text(lx, (y0 + y1) / 2 + 0.028, label, ha='center', fontsize=11.5, color=color,
                bbox=dict(fc='white', ec='none', alpha=0.85, pad=1.5))

ax.plot([0.325, 0.36, 0.36, 0.50, 0.50, 0.675], [0.74, 0.74, 0.885, 0.885, 0.655, 0.655],
        color=RED, lw=2.8, solid_capstyle='round')
ax.text(0.50, 0.895, 'VCC → 3V3（3.3V）', ha='center', fontsize=11.5, color=RED)
wire(0.57, 0.57, BLK, 'GND → GND（共地）')
wire(0.40, 0.415, GRN, 'SCL → PB6')
wire(0.315, 0.33, GRN, 'SDA → PB7')
ax.plot([0.325, 0.40, 0.40, 0.55, 0.55, 0.675], [0.485, 0.485, 0.135, 0.135, 0.57, 0.57],
        color=BLK, lw=2.8, solid_capstyle='round')
ax.text(0.47, 0.115, 'DIR → GND（固定方向极性）', ha='center', fontsize=11.5, color=BLK)

# 不接的两个脚
for y, name in ((0.655, 'OUT'), (0.23, 'GPO')):
    ax.plot([0.325, 0.385], [y, y], color=GRY, lw=2, ls='--')
    ax.plot([0.390, 0.418], [y - 0.020, y + 0.020], color='#a00', lw=3)
    ax.plot([0.390, 0.418], [y + 0.020, y - 0.020], color='#a00', lw=3)
    ax.text(0.435, y, name + ' 不接（悬空）', fontsize=11.5, color='#a00', va='center')

ax.text(0.06, 0.075, '别忘了机械：磁铁贴法兰正中心（轴线上），芯片对正轴心、间隙 1~2mm —— 装歪了 MAG 会显示 NONE/WEAK/STRONG',
        fontsize=11.5, color='#333')
ax.text(0.06, 0.025, '确认丝印再插：按名字接，不要按位置（不同模块引脚顺序不一样）',
        fontsize=11.5, color='#a00')

ax.set_xlim(0.03, 0.98); ax.set_ylim(-0.01, 0.95); ax.axis('off')
plt.tight_layout()
plt.savefig(r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs\S1_AS5600接线.png', dpi=150, bbox_inches='tight')
print('saved')
