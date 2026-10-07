
# -*- coding: utf-8 -*-
"""法兰安装装配图 v2：头部放大 + 端面视图"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrow

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7.5), dpi=140)
fig.subplots_adjust(wspace=0.05)

# ================= 左：轴端头部放大（侧视剖面） =================
ax1.set_title('① 侧视（头部放大）：法兰套上轴 → 顶丝顶住 D 面 → 摆杆锁在法兰偏心处', fontsize=12)
ax1.add_patch(Rectangle((0.070, -0.026), 0.014, 0.052, fc='#5d7ea0', ec='k', lw=1.2))   # 减速头
ax1.text(0.077, 0.032, '减速头/电机', ha='center', fontsize=10, color='#33507a')
# 轴 + D 面
ax1.add_patch(Rectangle((0.084, -0.0035), 0.062, 0.007, fc='#9aa0a8', ec='k', lw=1.1))
ax1.add_patch(Rectangle((0.084, 0.0035), 0.062, 0.002, fc='#cfd4da', ec='k', lw=0.8))
ax1.text(0.150, 0.0135, 'D 面（原厂铣平的平面）', fontsize=10, color='#a00')
ax1.plot([0.150, 0.143], [0.011, 0.0058], color='#a00', lw=1.0)
ax1.text(0.116, -0.014, '出轴 6mm', ha='center', fontsize=10)
# 法兰片（垂直轴）
ax1.add_patch(Rectangle((0.131, -0.024), 0.0045, 0.052, fc='#b8bcc4', ec='k', lw=1.3))
ax1.text(0.140, 0.036, '法兰片（铝，厚 2mm）\n中心孔 6.2mm', fontsize=10, color='#4a5560')
# 顶丝
ax1.add_patch(Rectangle((0.1295, 0.0055), 0.0075, 0.010, fc='#666', ec='k', lw=1.0))
ax1.plot([0.1335, 0.1335], [0.0055, 0.0035], 'k-', lw=1.2)
ax1.annotate('M4 顶丝\n（顶死在 D 面上）', xy=(0.132, 0.010), xytext=(0.100, 0.048),
             fontsize=10, color='#222', arrowprops=dict(arrowstyle='->', color='#333', lw=1.2))
# 磁铁（法兰中心 = 轴线上）
ax1.add_patch(Rectangle((0.1355, -0.0022), 0.0075, 0.0075, fc='#f5c518', ec='k', lw=1.1))
ax1.annotate('磁铁贴法兰中心\n（正好在轴线上，随法兰转）', xy=(0.139, -0.001), xytext=(0.104, -0.030),
             fontsize=10, color='#b8860b', arrowprops=dict(arrowstyle='->', color='#b8860b', lw=1.2))
# AS5600
ax1.add_patch(Rectangle((0.1455, -0.0055), 0.0045, 0.011, fc='#2e8b57', ec='k', lw=1.1))
ax1.add_patch(Rectangle((0.1455, 0.0235), 0.0045, 0.030, fc='#aab4c0', ec='k', lw=0.8))
ax1.text(0.163, 0.040, 'AS5600 芯片\n（固定在支架上，不转）', fontsize=10, color='#1a5c33')
ax1.annotate('间隙 1~2mm', xy=(0.1435, 0.001), xytext=(0.150, -0.026), fontsize=10, color='b',
             arrowprops=dict(arrowstyle='->', color='b', lw=1.2))
# 摆杆
ax1.add_patch(Rectangle((0.1335, -0.145), 0.006, 0.121, fc='#c96a1e', ec='k', lw=1.0))
ax1.annotate('', xy=(0.1335, -0.024), xytext=(0.1335, -0.060),
             arrowprops=dict(arrowstyle='<->', color='#a0522d', lw=1.1))
ax1.text(0.144, -0.100, '摆杆 6mm×450mm\n离轴心 15mm 偏心安装\n（M4 螺丝穿过法兰边孔）', fontsize=10, color='#a0522d')
ax1.plot([0.130, 0.130], [-0.150, 0.058], 'k-.', lw=0.8)
ax1.text(0.126, 0.062, '旋转轴线', fontsize=9.5, ha='center')
ax1.set_xlim(0.062, 0.185); ax1.set_ylim(-0.150, 0.075)
ax1.set_aspect('equal'); ax1.axis('off')

# ================= 右：端面视图 =================
ax2.set_title('② 端面看：摆杆在偏心处，磁铁在正中心', fontsize=12)
ax2.add_patch(Circle((0, 0), 0.030, fc='#b8bcc4', ec='k', lw=1.5, alpha=0.95))
ax2.add_patch(Circle((0, 0), 0.018, fc='#e8eaee', ec='k', lw=0.8, ls='--'))
ax2.add_patch(Circle((0, 0), 0.0075, fc='#9aa0a8', ec='k', lw=1.0))
ax2.plot([-0.0075, 0.0075], [0.0055, 0.0055], 'r-', lw=2.0)
ax2.text(0.021, 0.008, 'D 面', fontsize=9.5, color='r')
ax2.add_patch(Circle((0, 0), 0.0035, fc='#f5c518', ec='k', lw=1.0))
ax2.text(-0.056, -0.004, '磁铁\n(轴心)', fontsize=9.5, color='#b8860b', ha='center')
ax2.add_patch(Circle((0, -0.020), 0.003, fc='#c96a1e', ec='k', lw=1.0))
ax2.add_patch(Circle((0, -0.020), 0.0045, fc='none', ec='#666', lw=0.8, ls=':'))
ax2.text(0.012, -0.031, '摆杆（偏心 15mm）', fontsize=9.5, color='#a0522d')
ax2.add_patch(Circle((0.024, 0.008), 0.0022, fc='#666', ec='k', lw=0.8))
ax2.annotate('顶丝孔', xy=(0.024, 0.008), xytext=(0.040, 0.030), fontsize=9.5,
             arrowprops=dict(arrowstyle='->', color='#333', lw=1.0))
ax2.add_patch(FancyArrow(0.034, -0.034, -0.012, 0.010, width=0.0015,
                         head_width=0.009, color='#2e8b57'))
ax2.text(0.040, -0.046, '转向', fontsize=9.5, color='#2e8b57')
ax2.set_xlim(-0.066, 0.078); ax2.set_ylim(-0.066, 0.056)
ax2.set_aspect('equal'); ax2.axis('off')

plt.savefig(r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs\S1_法兰安装_示意.png', dpi=140, bbox_inches='tight')
print('saved')
