
# -*- coding: utf-8 -*-
"""摆杆-法兰连接方式对比图：方案A 端面攻丝单螺丝 / 方案B 双螺丝夹持"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

fig, (axA, axB) = plt.subplots(1, 2, figsize=(15, 8), dpi=140)

def base(ax, title):
    ax.set_title(title, fontsize=12.5)
    # 电机的轴（水平）
    ax.add_patch(Rectangle((0.040, -0.0035), 0.075, 0.007, fc='#9aa0a8', ec='k', lw=1.1))
    ax.text(0.030, -0.0015, '轴', ha='right', fontsize=10)
    # 法兰（垂直薄板）
    ax.add_patch(Rectangle((0.112, -0.030), 0.0045, 0.060, fc='#b8bcc4', ec='k', lw=1.3))
    ax.text(0.126, 0.033, '法兰片', fontsize=10, color='#4a5560')
    # 轴线
    ax.plot([0.040, 0.160], [0, 0], 'k-.', lw=0.8)
    ax.text(0.163, -0.002, '轴心线', fontsize=9)
    # 偏心尺寸
    ax.annotate('', xy=(0.100, 0.0), xytext=(0.100, -0.015),
                arrowprops=dict(arrowstyle='<->', color='#666', lw=1.0))
    ax.text(0.101, -0.009, '15mm', fontsize=9, color='#666')

# ================= 方案 A：端面攻丝 + 单颗 M4 =================
base(axA, '方案 A：摆杆端面攻 M4 内螺纹 → 单螺丝拧紧（省事）')
# 摆杆（下端面贴在法兰面上，偏心 15mm）
axA.add_patch(Rectangle((0.1165, -0.170), 0.006, 0.140, fc='#c96a1e', ec='k', lw=1.1))
axA.text(0.130, -0.130, '摆杆 6mm\n端面锉平、（端面）攻 M4', fontsize=10, color='#a0522d')
# 螺丝（沿轴方向穿法兰拧入摆杆端面）
axA.add_patch(Rectangle((0.104, -0.0175), 0.0135, 0.005, fc='#555', ec='k', lw=1.0))
axA.add_patch(Rectangle((0.1085, -0.021), 0.004, 0.012, fc='#777', ec='k', lw=0.8))   # 弹簧垫圈
axA.text(0.096, -0.028, 'M4 螺丝（+弹簧垫圈）', fontsize=10, ha='right', color='#222')
axA.text(0.096, -0.040, '穿过法兰孔 → 拧进摆杆端面螺纹', fontsize=9.5, ha='right', color='#555')
# 防转提示
axA.text(0.130, -0.058, '注意：只靠端面摩擦防转：\n轻摆杆够用；打滑就改方案 B', fontsize=10, color='#a00')
axA.set_xlim(0.020, 0.175); axA.set_ylim(-0.185, 0.045)
axA.set_aspect('equal'); axA.axis('off')

# ================= 方案 B：双螺丝夹持 =================
base(axB, '方案 B：摆杆打两个横孔 → 两颗 M4 夹紧（最稳，推荐）')
axB.add_patch(Rectangle((0.1165, -0.170), 0.006, 0.140, fc='#c96a1e', ec='k', lw=1.1))
axB.text(0.130, -0.135, '摆杆 6mm\n侧面打两个 4.2mm 横孔\n（孔距 12mm）', fontsize=10, color='#a0522d')
# 两颗螺丝
for zz in (-0.006, -0.018):
    axB.add_patch(Rectangle((0.104, zz - 0.0025), 0.0135, 0.005, fc='#555', ec='k', lw=1.0))
    axB.add_patch(Circle((0.1055, zz), 0.0035, fc='#888', ec='k', lw=0.8))     # 螺母
    axB.add_patch(Rectangle((0.1085, zz - 0.0055), 0.0035, 0.011, fc='#777', ec='k', lw=0.7))
axB.text(0.096, -0.030, '两颗 M4（+弹簧垫圈+螺母）', fontsize=10, ha='right', color='#222')
axB.text(0.096, -0.044, '两颗一起夹 → 摆杆不会自转', fontsize=9.5, ha='right', color='#555')
axB.text(0.130, -0.062, '摆杆端面顶住法兰面、两颗螺丝锁死\n拧紧后手拨一下：杆应毫无晃动', fontsize=10, color='#1a5c33')
axB.set_xlim(0.020, 0.175); axB.set_ylim(-0.185, 0.045)
axB.set_aspect('equal'); axB.axis('off')

plt.savefig(r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs\S1_摆杆锁法兰_方案对比.png', dpi=140, bbox_inches='tight')
print('saved')
