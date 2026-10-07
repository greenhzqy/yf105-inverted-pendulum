# -*- coding: utf-8 -*-
"""倒立摆正确组装 3D 图：左=整装斜视（装完长什么样）  右=沿轴心线爆炸（装配顺序）"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

C = dict(board='#c8a263', motor='#4a6b8a', gear='#5d7ea0', black='#3a4148',
         silver='#c2c8d0', plate='#eef1f5', mag='#f5c518', pcb='#2e8b57',
         chip='#123f27', brk='#5a6470', base2='#ddd0b0', rod='#c96a1e')

ZC = 0.045          # 轴心高度
ROFF = 0.014        # 摆杆偏心


def box(ax, x0, x1, y0, y1, z0, z1, color, alpha=1.0, ec='k', lw=0.4):
    v = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                  [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]])
    f = [[v[j] for j in i] for i in
         [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (1, 2, 6, 5), (0, 3, 7, 4)]]
    ax.add_collection3d(Poly3DCollection(f, facecolor=color, edgecolor=ec,
                                         linewidth=lw, alpha=alpha))


def cyl_x(ax, y0, z0, r, x0, x1, color, n=36, alpha=1.0):
    t = np.linspace(0, 2 * np.pi, n)
    Y, X = np.meshgrid(y0 + r * np.cos(t), [x0, x1], indexing='ij')
    Z, _ = np.meshgrid(z0 + r * np.sin(t), [x0, x1], indexing='ij')
    ax.plot_surface(X, Y, Z, color=color, alpha=alpha, shade=True, linewidth=0)
    rr = np.linspace(0, 1, 5)
    Yd = y0 + r * np.outer(rr, np.cos(t))
    Zd = z0 + r * np.outer(rr, np.sin(t))
    for xx in (x0, x1):
        ax.plot_surface(np.full_like(Yd, xx), Yd, Zd, color=color, alpha=alpha, linewidth=0)


def cyl_z(ax, x0, y0, r, z0, z1, color, n=28, alpha=1.0):
    t = np.linspace(0, 2 * np.pi, n)
    X, Z = np.meshgrid(x0 + r * np.cos(t), [z0, z1], indexing='ij')
    Y, _ = np.meshgrid(y0 + r * np.sin(t), [z0, z1], indexing='ij')
    ax.plot_surface(X, Y, Z, color=color, alpha=alpha, shade=True, linewidth=0)
    rr = np.linspace(0, 1, 5)
    Xd = x0 + r * np.outer(rr, np.cos(t))
    Yd = y0 + r * np.outer(rr, np.sin(t))
    for zz in (z0, z1):
        ax.plot_surface(Xd, Yd, np.full_like(Xd, zz), color=color, alpha=alpha, linewidth=0)


def lead(ax, p, t, s, color='#222', fs=10.2):
    ax.plot([p[0], t[0]], [p[1], t[1]], [p[2], t[2]], color='#909090', lw=0.8)
    ax.text(t[0], t[1], t[2], s, fontsize=fs, color=color, ha='center', va='center',
            bbox=dict(fc='white', alpha=0.9, ec='none', pad=1.3))


def railnum(ax, anchor, pos, s):
    ax.plot([anchor[0], pos[0]], [anchor[1], pos[1]], [anchor[2], pos[2]],
            color='#7f8ea3', lw=0.9, ls='-')
    ax.plot([anchor[0]], [anchor[1]], [anchor[2]], marker='o', ms=2.6,
            color='#11407e', mec='none')
    num(ax, pos, s)


def num(ax, p, s, r=1.0):
    ax.text(p[0], p[1], p[2], s, fontsize=12.5, color='#11407e', ha='center', va='center',
            bbox=dict(boxstyle='circle', fc='white', ec='#11407e', lw=1.1))


def scene(ax, sh=None, disc=False):
    sh = sh or {}
    g = lambda k: sh.get(k, 0.0)

    # 底板 / 黑 L 支架 / 电机
    box(ax, -0.100, -0.006, -0.062, 0.062, 0.0, 0.012, C['board'])
    box(ax, -0.070, -0.026, -0.034, 0.034, 0.012, 0.018, C['black'])
    box(ax, -0.070, -0.026, -0.034, -0.028, 0.018, 0.036, C['black'])
    box(ax, -0.070, -0.026, 0.028, 0.034, 0.018, 0.036, C['black'])
    cyl_x(ax, 0, ZC, 0.021, -0.062, -0.020, C['motor'])
    box(ax, -0.020, -0.010, -0.015, 0.015, ZC - 0.015, ZC + 0.015, C['gear'])
    cyl_x(ax, 0, ZC, 0.005, -0.010, 0.000, C['silver'], n=20)

    px = 0.017 + g('r')                      # 垫柱起点（白盘外面）
    rodx = px + 0.0155                       # 摆杆中心

    cyl_x(ax, 0, ZC, 0.010, 0.000 + g('c'), 0.014 + g('c'), C['silver'])          # (1) 套筒
    cyl_x(ax, 0, ZC, 0.018, 0.014 + g('f'), 0.017 + g('f'), C['plate'])           # (2) 白盘
    cyl_x(ax, 0, ZC, 0.005, 0.017 + g('m'), 0.020 + g('m'), C['mag'])             # (3) 磁铁
    box(ax, 0.0225 + g('s'), 0.024 + g('s'), -0.0075, 0.0075,                      # (4) 传感器
        ZC - 0.0075, ZC + 0.0075, C['pcb'])
    box(ax, 0.0215 + g('s'), 0.0225 + g('s'), -0.0032, 0.0032,
        ZC - 0.0032, ZC + 0.0032, C['chip'])
    b = g('b')                                                                    # (5) 支架
    box(ax, 0.026 + b, 0.062 + b, -0.004, 0.026, 0.0, 0.010, C['base2'])
    box(ax, 0.050 + b, 0.056 + b, 0.004, 0.014, 0.010, ZC - 0.0028, C['brk'])
    box(ax, 0.024 + b, 0.056 + b, 0.005, 0.011, ZC - 0.0028, ZC + 0.0028, C['brk'])
    cyl_x(ax, 0, ZC - ROFF, 0.0032, px, px + 0.011, C['silver'], n=20)            # (6) 垫柱
    cyl_z(ax, rodx, 0, 0.003, -0.062, ZC - ROFF, C['rod'])                        # (6) 摆杆

    ax.plot([-0.095, 0.075], [0, 0], [ZC, ZC], '-.', color='#333', lw=1.1)        # 轴心线

    if disc:
        t = np.linspace(0, 2 * np.pi, 60)
        rr = np.linspace(0, 0.050, 10)
        Yd = np.outer(rr, np.cos(t))
        Zd = ZC + np.outer(rr, np.sin(t))
        Xd = np.full_like(Yd, rodx)
        ax.plot_surface(Xd, Yd, Zd, color='#e03030', alpha=0.07, linewidth=0)
        ax.plot(np.full_like(t, rodx), 0.050 * np.cos(t), ZC + 0.050 * np.sin(t),
                '--', color='#cc2222', lw=1.1)
    return rodx, px


fig = plt.figure(figsize=(17, 9.2), dpi=140)

# ================= 左：整装 =================
axA = fig.add_axes([0.005, 0.235, 0.445, 0.715], projection='3d')
rodxA, pxA = scene(axA, disc=True)
RA = [((0.007, 0, ZC), (0.002, 0.060, 0.098), '1'),
      ((0.0155, 0, ZC + 0.017), (0.022, 0.044, 0.112), '2'),
      ((0.0185, 0, ZC), (0.040, 0.020, 0.124), '3'),
      ((0.0233, 0, ZC + 0.0075), (0.058, -0.006, 0.120), '4'),
      ((0.046, 0.012, 0.006), (0.064, -0.036, 0.104), '5'),
      ((rodxA, 0, -0.018), (rodxA + 0.022, -0.030, -0.036), '6')]
for a, q, s in RA:
    railnum(axA, a, q, s)
lead(axA, (-0.030, 0.030, 0.012), (-0.010, -0.084, -0.036), '木底板')
lead(axA, (-0.030, 0.008, ZC + 0.016), (-0.042, -0.080, 0.090), '减速电机\n+ 黑色 L 支架')
lead(axA, (rodxA + 0.02, 0.028, ZC + 0.026), (0.086, 0.055, ZC + 0.030),
     '红面 = 摆杆扫过的这一层\n(支架不能从它里面穿过)')
axA.text(-0.034, 0.0, ZC + 0.010, '轴心线', fontsize=10, color='#333')
axA.text(rodxA - 0.020, -0.030, -0.046, '杆长 0.45m\n(图中截短)', fontsize=9.5, color='#a0522d', ha='center')
axA.set_title('左：装好以后是什么样', fontsize=14, color='#11407e', pad=0)
axA.set_xlim(-0.050, 0.092); axA.set_ylim(-0.092, 0.092); axA.set_zlim(-0.052, 0.145)
axA.set_box_aspect((0.142, 0.184, 0.197))
axA.view_init(elev=17, azim=-62)
axA.set_axis_off()

# ================= 右：爆炸 =================
axB = fig.add_axes([0.455, 0.235, 0.545, 0.715], projection='3d')
SH = dict(c=0.0, f=0.036, m=0.072, s=0.105, b=0.105, r=0.185)
rodxB, pxB = scene(axB, SH)
RB = [((0.007, 0, ZC), (0.002, 0.060, 0.098), '1'),
      ((0.0155 + SH['f'], 0, ZC + 0.017), (0.022 + SH['f'], 0.044, 0.112), '2'),
      ((0.0185 + SH['m'], 0, ZC), (0.040 + SH['m'], 0.020, 0.124), '3'),
      ((0.0233 + SH['s'], 0, ZC + 0.0075), (0.058 + SH['s'], -0.006, 0.120), '4'),
      ((0.046 + SH['b'], 0.012, 0.006), (0.064 + SH['b'], -0.036, 0.104), '5'),
      ((rodxB, 0, -0.018), (rodxB + 0.022, -0.030, -0.036), '6')]
for a, q, s in RB:
    railnum(axB, a, q, s)
axB.text(0.0185 + SH['m'], 0.026, ZC - 0.030, '在轴心线上', fontsize=9.5, color='#8a6d00', ha='center')
axB.text(0.0233 + SH['s'], -0.026, ZC - 0.032, '芯片朝左正对磁铁', fontsize=9.5, color='#1a5c33', ha='center')
axB.text(0.062 + SH['b'], 0.0, -0.036, '支架固定在这块小板上（不转）', fontsize=9.5, color='#40485a', ha='center')
axB.text(rodxB, 0.0, -0.052, '摆杆', fontsize=9.5, color='#a0522d', ha='center')
axB.set_title('右：按这个顺序装（沿轴心线依次套上去）', fontsize=14, color='#11407e', pad=0)
axB.set_xlim(-0.050, 0.270); axB.set_ylim(-0.092, 0.092); axB.set_zlim(-0.052, 0.145)
axB.set_box_aspect((0.320, 0.184, 0.197))
axB.view_init(elev=17, azim=-64)
axB.set_axis_off()

# ================= 底部图例 =================
LG = [('1', '套筒(联轴器)', '套上轴，顶丝必须顶在轴的 D 面上拧死；打滑 = 角度数据直接作废'),
      ('2', '白盘(法兰)', '手扳不能晃、径向跳动 <0.5mm'),
      ('3', '磁铁', '粘在白盘外面正中心（轴心线上，随轴一起转）'),
      ('4', 'AS5600', '芯片正对磁铁，间隙 1~2mm'),
      ('5', '传感器支架', '从轴头前面沿轴心伸进来，只走离轴心 15mm 的中间小圈；底座固定在不转的地方'),
      ('6', '摆杆', 'M4 螺杆 + 10~13mm 垫柱锁在白盘边上的孔（偏心 15mm），不能用扎带')]
for i, (n, t, d) in enumerate(LG):
    col, row = i % 3, i // 3
    x = 0.055 + col * 0.325
    y = 0.150 - row * 0.060
    fig.text(x, y, n, fontsize=12, color='#11407e', ha='center', va='center',
             bbox=dict(boxstyle='circle', fc='white', ec='#11407e', lw=1.1))
    fig.text(x + 0.016, y + 0.015, t, fontsize=11.5, color='#11407e', va='center')
    fig.text(x + 0.016, y - 0.011, d, fontsize=10, color='#333', va='center')

fig.text(0.5, 0.030, '判据：手拨摆杆能转满 360° 不碰任何东西；手转白盘，串口 deg 平滑、MAG=OK',
         fontsize=12.5, color='#b00', ha='center',
         bbox=dict(boxstyle='round', fc='#fff4f4', ec='#d33', lw=1.3))

out = r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs\S3_正确组装_3D图.png'
fig.savefig(out, facecolor='white')
print('OK', out)