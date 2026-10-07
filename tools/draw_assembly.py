
# -*- coding: utf-8 -*-
"""3D 装配示意图 v2：电机直驱倒立摆"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

def box(ax, x0, x1, y0, y1, z0, z1, color, alpha=1.0, ec='k', lw=0.4):
    v = np.array([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],
                  [x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]])
    faces = [[v[j] for j in idx] for idx in
             [(0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(1,2,6,5),(0,3,7,4)]]
    ax.add_collection3d(Poly3DCollection(faces, facecolor=color, edgecolor=ec,
                                         linewidth=lw, alpha=alpha))

def cyl_y(ax, x0, z0, r, y0, y1, color, alpha=1.0, n=28):
    t = np.linspace(0, 2*np.pi, n)
    X = x0 + r*np.outer(np.cos(t), np.ones(2))
    Z = z0 + r*np.outer(np.sin(t), np.ones(2))
    Y = np.zeros_like(X); Y[:,0] = y0; Y[:,1] = y1
    ax.plot_surface(X, Y, Z, color=color, alpha=alpha, shade=True)
    # 端面封盖
    for yy in (y0, y1):
        ax.plot_surface(X[:, 0:1], np.full_like(X, yy), Z[:, 0:1], color=color, alpha=alpha)

def cyl_z(ax, x0, y0, r, z0, z1, color, alpha=1.0, n=18):
    t = np.linspace(0, 2*np.pi, n)
    X = x0 + r*np.outer(np.cos(t), np.ones(2))
    Y = y0 + r*np.outer(np.sin(t), np.ones(2))
    Z = np.zeros_like(X); Z[:,0] = z0; Z[:,1] = z1
    ax.plot_surface(X, Y, Z, color=color, alpha=alpha, shade=True)
    for zz in (z0, z1):
        ax.plot_surface(X[:, 0:1], Y[:, 0:1], np.full_like(X, zz), color=color, alpha=alpha)

def lbl(ax, x, y, z, xl, yl, zl, s, color='#222'):
    ax.plot([x, xl], [y, yl], [z, zl], color='#999', lw=0.7)
    ax.text(xl, yl, zl, s, fontsize=9.5, ha='center', va='center',
            color=color, bbox=dict(fc='white', alpha=0.8, ec='none', pad=1.5))

fig = plt.figure(figsize=(15, 10), dpi=140)

# =============== 左：总装斜视图 ===============
ax = fig.add_subplot(1, 2, 1, projection='3d')
BOX = '#c8a263'; PLATE = '#aab4c0'; MOTOR = '#4a6b8a'; GEAR = '#5d7ea0'
FLANGE = '#77828f'; RODC = '#c96a1e'; MAG = '#f5c518'; CHIP = '#2e8b57'; WIRE = '#888'

box(ax, -0.09, 0.09, -0.13, 0.09, 0.0, 0.015, BOX, alpha=0.92)                 # 底板
box(ax, -0.05, 0.05, 0.068, 0.072, 0.015, 0.115, PLATE, alpha=0.95)            # 立板
cyl_y(ax, 0.0, 0.070, 0.023, 0.008, 0.058, MOTOR, alpha=0.95)                  # 电机本体
box(ax, -0.017, 0.017, 0.058, 0.066, 0.056, 0.084, GEAR)                       # 减速头
cyl_y(ax, 0.0, 0.070, 0.004, 0.072, 0.095, '#9aa0a8', n=16)                    # 出轴
box(ax, -0.018, 0.018, 0.095, 0.097, 0.052, 0.088, FLANGE, alpha=0.98)         # 转盘
cyl_z(ax, 0.012, 0.096, 0.0036, -0.31, 0.062, RODC, alpha=1.0, n=14)           # 摆杆
cyl_z(ax, 0.012, 0.096, 0.0044, 0.062, 0.076, '#a0522d', n=14)                 # 杆上段
cyl_y(ax, 0.0, 0.070, 0.0036, 0.097, 0.0985, MAG, n=16)                        # 磁铁
box(ax, -0.007, 0.007, 0.1015, 0.1035, 0.063, 0.077, CHIP)                     # AS5600
box(ax, -0.009, 0.009, 0.072, 0.106, 0.089, 0.091, PLATE, alpha=0.95)          # 支持舌
cyl_z(ax, 0.0045, 0.103, 0.0012, 0.077, 0.089, '#c0c0c0', n=10)
cyl_z(ax, -0.0045, 0.103, 0.0012, 0.077, 0.089, '#c0c0c0', n=10)
box(ax, -0.062, -0.002, -0.118, -0.078, 0.015, 0.032, '#1e7a46', ec='#0a3d1f', lw=0.8)  # STM32
box(ax, -0.036, 0.010, -0.068, -0.038, 0.015, 0.030, '#8b2f2f', ec='#4d0f0f', lw=0.8)  # TB6612
cyl_z(ax, 0.055, -0.022, 0.009, 0.015, 0.036, '#d33')                          # 按钮
cyl_z(ax, 0.055, -0.078, 0.006, 0.015, 0.030, '#444')                          # 保险丝
box(ax, -0.16, -0.10, -0.08, -0.02, 0.0, 0.034, '#999')                        # 适配器
w = lambda p, c, lw=2.0: ax.plot(*zip(*p), color=c, lw=lw)
w([(-0.09,-0.05,0.034), (-0.02,-0.05,0.026), (0.05,-0.05,0.026), (0.055,-0.078,0.030)], 'r')
w([(0.055,-0.022,0.036), (0.02,-0.04,0.028)], 'r')
w([(-0.006,0.1035,0.070), (-0.006,0.05,0.070), (-0.006,-0.05,0.070), (-0.002,-0.08,0.020)], 'y')
w([(0.006,0.1035,0.070), (0.006,0.05,0.070), (0.006,-0.05,0.070), (0.002,-0.08,0.020)], 'g')
w([(0.0,0.058,0.0565), (-0.03,-0.05,0.02)], '#2040c0')
w([(0.0,0.058,0.0835), (-0.03,-0.05,0.02)], '#8a4b28')
w([(-0.10,-0.05,0.034), (-0.10,-0.09,0.034)], 'gray')
# 摆动角示意
t = np.linspace(0, np.radians(35), 40)
ax.plot(0.012 + 0.12*np.sin(t), np.full_like(t, 0.096), 0.070 - 0.12*np.cos(t), 'r--', lw=1.6)
ax.plot([0.012, 0.012+0.11*np.sin(np.radians(35))], [0.096, 0.096],
        [0.062, 0.062-0.11*np.cos(np.radians(35))], 'r--', lw=1.4)
ax.text(0.055, 0.096, 0.005, 'θ', color='red', fontsize=13, style='italic')
# 标签（带引线）
lbl(ax, 0.0, 0.02, -0.31, 0.10, -0.02, -0.31, '摆杆 6mm×0.45m\n(悬垂状态)', RODC)
lbl(ax, 0.0, 0.030, 0.105, -0.14, 0.03, 0.15, '电机+减速头', MOTOR)
lbl(ax, 0.0, 0.0, 0.075, 0.0, -0.09, 0.055, '立板(铝条)', '#66707d')
lbl(ax, 0.09, 0.08, 0.09, 0.15, 0.10, 0.12, '磁铁+AS5600', '#1a5c33')
lbl(ax, -0.05, -0.10, 0.030, -0.16, -0.12, 0.075, 'STM32 蓝丸+TB6612', '#333')
lbl(ax, 0.055, -0.022, 0.040, 0.13, -0.03, 0.07, '急停按钮', '#a00')
lbl(ax, 0.055, -0.078, 0.032, 0.15, -0.09, 0.05, '保险丝(3A)', '#333')
lbl(ax, -0.13, -0.05, 0.034, -0.20, -0.05, 0.09, '12V适配器', '#333')
lbl(ax, 0.0, -0.06, 0.0, 0.0, -0.12, -0.05, '底板', '#8a6d3b')
ax.set_xlim(-0.24, 0.20); ax.set_ylim(-0.20, 0.20); ax.set_zlim(-0.36, 0.20)
ax.set_box_aspect((2.4, 2.0, 3.2))
ax.view_init(elev=26, azim=-38)
ax.set_axis_off()
ax.set_title('① 总装：摆杆挂在底板外沿摆动，磁铁+AS5600 在轴端背侧', fontsize=12)

# =============== 右：轴端细节 ===============
ax2 = fig.add_subplot(1, 2, 2, projection='3d')
box(ax2, -0.022, 0.022, 0.0, 0.003, 0.052, 0.058, PLATE, alpha=0.9)
box(ax2, -0.014, 0.014, 0.0, 0.014, 0.058, 0.082, GEAR, alpha=0.9)     # 减速头(剖)
cyl_y(ax2, 0.0, 0.070, 0.004, 0.004, 0.030, '#9aa0a8', n=16)
box(ax2, -0.017, 0.017, 0.030, 0.032, 0.053, 0.087, FLANGE, alpha=0.98)
cyl_y(ax2, 0.0, 0.070, 0.0036, 0.032, 0.0335, MAG, n=16)
box(ax2, -0.006, 0.006, 0.0365, 0.0385, 0.064, 0.076, CHIP)
box(ax2, -0.008, 0.008, 0.0385, 0.042, 0.086, 0.088, PLATE)
cyl_z(ax2, 0.004, 0.040, 0.0012, 0.076, 0.086, '#c0c0c0', n=10)
cyl_z(ax2, -0.004, 0.040, 0.0012, 0.076, 0.086, '#c0c0c0', n=10)
# 轴线参考
ax2.plot([-0.02, 0.045], [0.070, 0.070], [0.070, 0.070], 'k-.', lw=1.0)
# 间隙标注
ax2.plot([0.008, 0.008], [0.0335, 0.0365], [0.088, 0.088], 'b-', lw=1.2)
ax2.text(0.016, 0.035, 0.090, '≈2mm 间隙', color='b', fontsize=9)
lbl(ax2, 0.0, 0.0328, 0.070, 0.05, 0.033, 0.045, '磁铁(随轴转)', '#b8860b')
lbl(ax2, 0.0, 0.0, 0.075, -0.06, -0.005, 0.05, '减速头/电机', '#33507a')
lbl(ax2, 0.006, 0.040, 0.082, 0.05, 0.052, 0.10, 'AS5600(固定)', '#1a5c33')
lbl(ax2, 0.0, 0.006, 0.071, -0.055, 0.0, 0.10, '电机出轴(随摆杆转)', '#55606c')
ax2.set_xlim(-0.05, 0.05); ax2.set_ylim(-0.005, 0.05); ax2.set_zlim(0.050, 0.100)
ax2.set_box_aspect((1.5, 1.05, 1.0))
ax2.view_init(elev=18, azim=-78)
ax2.set_axis_off()
ax2.set_title('② 关键细节：磁铁-芯片同轴、间隙 1~2mm', fontsize=12)

plt.tight_layout()
plt.savefig(r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs\S1_装配示意_3D.png', dpi=140, bbox_inches='tight')
print('saved')
