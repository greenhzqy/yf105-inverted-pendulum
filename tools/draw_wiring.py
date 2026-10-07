
# -*- coding: utf-8 -*-
"""S1 接线图 v2：STM32 蓝丸 + TB6612 + 电机 + 电源 + 串口（+ AS5600 虚线待接）"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

C12V, CGND, CPWM, CDIR, CSTBY, CUART, C3V3, CI2C = (
    '#d62728', '#000000', '#ff8c00', '#1f6fd0', '#2e8b57', '#8e44ad', '#7f8c8d', '#16a085')

fig, ax = plt.subplots(figsize=(15, 10.5), dpi=150)

def module(x0, y0, x1, y1, title, fc, ec='k', ls='-', tsize=13, tdy=0.028):
    ax.add_patch(Rectangle((x0, y0), x1-x0, y1-y0, fc=fc, ec=ec, lw=2.0, ls=ls, zorder=2))
    ax.text((x0+x1)/2, y1-tdy, title, ha='center', va='top', fontsize=tsize, weight='bold', zorder=3)

def pin(x, y, name, side, color='#333'):
    """引脚名一律画在模块内侧，避免和导线打架。"""
    dx = -0.014 if side == 'r' else (0.014 if side == 'l' else 0)
    dy = -0.014 if side == 't' else (0.014 if side == 'b' else 0)
    ax.plot([x, x+dx], [y, y+dy], color=color, lw=1.6, zorder=4)
    if side == 'l':
        ha, ox = 'left', 0.010
    elif side == 'r':
        ha, ox = 'right', -0.010
    else:
        ha, ox = 'center', 0
    va = 'bottom' if side == 'b' else ('top' if side == 't' else 'center')
    oy = 0.010 if side == 'b' else (-0.010 if side == 't' else 0)
    ax.text(x+ox, y+oy, name, ha=ha, va=va, fontsize=11, zorder=5)

def wire(pts, color, lw=2.6, ls='-', label=None, lab_at=None, lab_off=(0, 0.012), fs=10.5):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle='round', zorder=1)
    if label:
        lx, ly = lab_at
        ax.text(lx+lab_off[0], ly+lab_off[1], label, fontsize=fs, color=color,
                ha='center', va='bottom', zorder=6,
                bbox=dict(fc='white', ec='none', alpha=0.8, pad=1.0))

# ---------------- ST-Link（SWD 下载） ----------------
module(-0.215, 0.385, -0.052, 0.625, 'ST-Link V2（下载器）', '#cfd8dc', tsize=12, tdy=0.028)
for y, n in [(0.575, '3V3'), (0.525, 'GND'), (0.475, 'SWDIO'), (0.425, 'SWCLK')]:
    pin(-0.055, y, n, 'r')
ax.text(-0.135, 0.375, '接蓝丸 SWD 口\n（4 线）', fontsize=10.5, ha='center', color='#37474f')

# ---------------- 模块 ----------------
module(0.05, 0.32, 0.27, 0.80, 'STM32 蓝丸 (F103C8T6)', '#1e7a46')
for y, n in [(0.575, '3V3'), (0.525, 'GND'), (0.475, 'PA13/SWDIO'), (0.425, 'PA14/SWCLK')]:
    pin(0.05, y, n, 'l', '#455a64')
module(0.50, 0.42, 0.76, 0.80, 'TB6612 驱动模块', '#8b2f2f')
module(0.46, 0.24, 0.72, 0.38, 'USB-TTL 模块', '#e8e8f5', tsize=12, tdy=0.026)
module(0.74, 0.05, 0.97, 0.19, 'AS5600 编码器（下一轮再接）', '#dff0e6', ls='--', tsize=11, tdy=0.024)

# SWD 四线
wire([(-0.055, 0.575), (0.05, 0.575)], '#455a64', 2.4, ls='--')
wire([(-0.055, 0.525), (0.05, 0.525)], '#455a64', 2.4)
wire([(-0.055, 0.475), (0.05, 0.475)], '#455a64', 2.4)
wire([(-0.055, 0.425), (0.05, 0.425)], '#455a64', 2.4)
ax.text(-0.0025, 0.60, '4 线一一对应\n（3V3 虚=可选用 USB 供电代替）', fontsize=9.5,
        ha='center', va='bottom', color='#455a64')

# STM32 引脚
for y, n in [(0.80, '3V3'), (0.74, 'PB0'), (0.68, 'PA0'), (0.62, 'PA1'), (0.56, 'PA2'),
             (0.46, 'PA9 (TX)'), (0.40, 'PA10 (RX)')]:
    pin(0.27, y, n, 'r')
pin(0.10, 0.32, 'GND', 'b')
pin(0.155, 0.32, 'PB6', 'b', CI2C)
pin(0.205, 0.32, 'PB7', 'b', CI2C)

# TB6612 引脚
for y, n in [(0.80, 'VCC'), (0.74, 'PWMA'), (0.68, 'AIN1'), (0.62, 'AIN2'), (0.56, 'STBY')]:
    pin(0.50, y, n, 'l')
pin(0.76, 0.62, 'A01', 'r'); pin(0.76, 0.56, 'A02', 'r')
pin(0.63, 0.80, 'VM', 't'); pin(0.745, 0.42, 'GND', 'b')

# 电机
ax.add_patch(Circle((0.90, 0.59), 0.052, fc='#4a6b8a', ec='k', lw=2.0, zorder=2))
ax.text(0.90, 0.59, '电机\nM', ha='center', va='center', fontsize=12, color='w', zorder=3)

# ---------------- 电源链（顶部） ----------------
module(0.03, 0.865, 0.16, 0.955, '12V 适配器', '#dddddd', tsize=12, tdy=0.026)
module(0.19, 0.875, 0.27, 0.945, '保险丝 3A', '#f5d76e', tsize=11, tdy=0.024)
ax.add_patch(Circle((0.35, 0.91), 0.030, fc='#d62728', ec='k', lw=1.6, zorder=2))
ax.text(0.35, 0.91, '按钮', ha='center', va='center', fontsize=10, color='w', zorder=3)
wire([(0.16, 0.91), (0.19, 0.91)], C12V, 3.4)
wire([(0.27, 0.91), (0.32, 0.91)], C12V, 3.4)
wire([(0.38, 0.91), (0.63, 0.91), (0.63, 0.80)], C12V, 3.4,
     label='12V 动力（粗红）', lab_at=(0.505, 0.913))
wire([(0.03, 0.885), (0.015, 0.885), (0.015, 0.20), (0.06, 0.20)], CGND, 3.0)

# ---------------- 公共地母线 ----------------
ax.plot([0.06, 0.88], [0.20, 0.20], color=CGND, lw=4.0, zorder=1)
ax.text(0.885, 0.20, ' GND 公共地\n（所有 GND 都接这里）', fontsize=11.5, va='center', ha='left', color=CGND)
wire([(0.10, 0.32), (0.10, 0.20)], CGND, 2.6)
wire([(0.745, 0.42), (0.745, 0.20)], CGND, 2.6)
wire([(0.52, 0.24), (0.52, 0.20)], CGND, 2.6)
wire([(0.80, 0.19), (0.80, 0.20)], CGND, 2.0, ls='--')

# ---------------- 信号线 ----------------
wire([(0.27, 0.80), (0.50, 0.80)], C3V3, 2.6, label='3V3 逻辑电源', lab_at=(0.385, 0.803))
wire([(0.27, 0.74), (0.50, 0.74)], CPWM, 2.6, label='PWM = 劲大小', lab_at=(0.385, 0.743))
wire([(0.27, 0.68), (0.50, 0.68)], CDIR, 2.6, label='AIN1', lab_at=(0.385, 0.683))
wire([(0.27, 0.62), (0.50, 0.62)], CDIR, 2.6, label='AIN2', lab_at=(0.385, 0.623))
wire([(0.27, 0.56), (0.50, 0.56)], CSTBY, 2.6, label='STBY = 使能', lab_at=(0.385, 0.563))
wire([(0.76, 0.62), (0.855, 0.605)], '#2040c0', 3.0)
wire([(0.76, 0.56), (0.855, 0.578)], '#8a4b28', 3.0)
ax.text(0.812, 0.672, '电机两根线\n（正反随意）', fontsize=10.5, ha='center')
ax.text(0.59, 0.295, 'USB-TTL → 电脑串口助手 115200', fontsize=11, ha='center')
wire([(0.27, 0.46), (0.36, 0.46), (0.36, 0.345), (0.46, 0.345)], CUART, 2.4,
     label='TX → RXD', lab_at=(0.325, 0.352), fs=10)
wire([(0.27, 0.40), (0.325, 0.40), (0.325, 0.285), (0.46, 0.285)], CUART, 2.4,
     label='RX ← TXD', lab_at=(0.315, 0.262), fs=10)
# I2C 虚线（下一轮）
wire([(0.155, 0.32), (0.155, 0.135), (0.74, 0.135)], CI2C, 2.0, ls='--',
     label='SCL → PB6（下一轮接 AS5600）', lab_at=(0.46, 0.137), fs=10)
wire([(0.205, 0.32), (0.205, 0.095), (0.74, 0.095)], CI2C, 2.0, ls='--',
     label='SDA → PB7', lab_at=(0.42, 0.058), fs=10)

ax.text(-0.22, 0.02, '注意\n① 12V 只能进 VM，绝不能进 VCC（VCC 只吃 3.3V）\n'
        '② 所有 GND 必须接到同一条公共地\n③ 上电前万用表量：VM-GND = 12V、VCC-GND = 3.3V\n'
        '④ 保险丝 + 按钮串在 12V 正极上（按钮按下 = 断电）\n'
        '⑤ Keil：Options for Target → Debug → ST-Link Debugger → Port 选 SW → Flash Download 勾 Reset and Run',
        fontsize=11, color='#a00', va='bottom', ha='left',
        bbox=dict(fc='#fff5f5', ec='#a00', lw=1.2, pad=6), zorder=7)

ax.set_xlim(-0.245, 1.02); ax.set_ylim(0, 1.0)
ax.axis('off')
plt.tight_layout()
plt.savefig(r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs\S1_接线图.png', dpi=150, bbox_inches='tight')
print('saved')
