
# -*- coding: utf-8 -*-
"""原理图：左=运动与力链（一个自由度），右=磁编码器怎么测角度"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Wedge, FancyArrow, Arc

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7.6), dpi=140)

# ================= 左：运动与力链 =================
ax1.set_title('① 怎么运动：全装置只有一个自由度——摆杆绕电机轴转', fontsize=12.5)
# 电机 + 轴
ax1.add_patch(Rectangle((-0.115, -0.030), 0.075, 0.060, fc='#4a6b8a', ec='k', lw=1.2))
ax1.text(-0.077, 0.040, '电机', ha='center', fontsize=10.5, color='#33507a')
ax1.add_patch(Rectangle((-0.040, -0.0035), 0.030, 0.007, fc='#9aa0a8', ec='k', lw=1.0))
ax1.add_patch(Rectangle((-0.012, -0.026), 0.005, 0.052, fc='#b8bcc4', ec='k', lw=1.2))  # 法兰
ax1.plot([-0.115, 0.075], [0, 0], 'k-.', lw=0.8)
ax1.text(0.070, -0.006, '轴心线', fontsize=9)
# 摆杆：实线=下垂（自然状态）；虚线=直立（要控制才站得住）
ax1.add_patch(Rectangle((-0.0095, -0.185), 0.006, 0.160, fc='#c96a1e', ec='k', lw=1.1))
ax1.add_patch(Rectangle((0.030, -0.010), 0.006, 0.150, fc='none', ec='#888', lw=1.4, ls='--'))
ax1.add_patch(Circle((0.033, 0.140), 0.006, fc='#c96a1e', ec='k', lw=1.0, alpha=0.9))
ax1.text(0.045, 0.130, '直立（θ=0°）\n不稳定：不控制就倒', fontsize=10, color='#444')
ax1.text(0.012, -0.145, '下垂（θ=180°）\n自然状态：稳定', fontsize=10, color='#a0522d')
# 力矩与重力
ax1.add_patch(FancyArrow(0.010, 0.030, -0.002, -0.045, width=0.0012,
                         head_width=0.010, color='#1a5c33'))
ax1.text(0.016, 0.006, '电机力矩 τ', fontsize=10, color='#1a5c33')
ax1.add_patch(FancyArrow(-0.0065, -0.100, 0, -0.030, width=0.0012,
                         head_width=0.010, color='#a00'))
ax1.text(-0.048, -0.118, '重力 mg（永远把杆往下拉）', fontsize=10, color='#a00')
# 转动弧线
ax1.add_patch(Arc((-0.0095, 0), 0.115, 0.115, theta1=250, theta2=330, color='#2e8b57', lw=1.8))
ax1.text(-0.070, -0.062, '只有一个转角 θ\n由电机轴直接驱动', fontsize=10, color='#2e8b57')
ax1.set_xlim(-0.140, 0.150); ax1.set_ylim(-0.200, 0.175)
ax1.set_aspect('equal'); ax1.axis('off')

# ================= 右：磁编码器怎么测角 =================
ax2.set_title('② 怎么采集：磁铁随杆转 → 芯片测"磁场方向" → 就知道转角', fontsize=12.5)
# 摆杆(端面) + 法兰 + 磁铁（对径充磁：一半 N 一半 S）
ax2.add_patch(Circle((0, 0), 0.052, fc='#e8eaee', ec='k', lw=1.2, ls='--'))   # 法兰投影
ax2.add_patch(Circle((0, 0), 0.026, fc='#f5c518', ec='k', lw=1.2))            # 磁铁
ax2.add_patch(Wedge((0, 0), 0.026, 90, 270, fc='#e05555', ec='none'))          # N 半
ax2.add_patch(Wedge((0, 0), 0.026, 270, 450, fc='#4a7fe0', ec='none'))         # S 半
ax2.add_patch(Circle((0, 0), 0.026, fc='none', ec='k', lw=1.0))
ax2.text(0.0, 0.012, 'N', ha='center', fontsize=11, color='w', weight='bold')
ax2.text(0.0, -0.020, 'S', ha='center', fontsize=11, color='w', weight='bold')
ax2.annotate('磁铁贴在法兰中心\n（随摆杆一起转）', xy=(0.020, 0.020), xytext=(0.062, 0.058),
             fontsize=10, color='#b8860b', arrowprops=dict(arrowstyle='->', color='#b8860b', lw=1.1))
# 旋转箭头
ax2.add_patch(Arc((0, 0), 0.140, 0.140, theta1=20, theta2=110, color='#2e8b57', lw=1.8))
ax2.add_patch(FancyArrow(0.056, 0.050, 0.012, 0.014, width=0.0012,
                         head_width=0.010, color='#2e8b57'))
ax2.text(0.052, 0.086, '摆杆转 → 磁场方向跟着转', fontsize=10, color='#2e8b57')
# 芯片（固定在支架上，不转）
ax2.add_patch(Rectangle((-0.030, 0.070), 0.060, 0.020, fc='#2e8b57', ec='k', lw=1.2))
ax2.text(0.0, 0.080, 'AS5600', ha='center', va='center', fontsize=10, color='w', weight='bold')
ax2.annotate('芯片不动，只"感觉"磁场方向\n→ 换算成 0~360° 的数字', xy=(0.0, 0.072), xytext=(-0.135, 0.115),
             fontsize=10, color='#1a5c33', arrowprops=dict(arrowstyle='->', color='#1a5c33', lw=1.1))
# I2C 到主控
for i, c in enumerate(['#d33', '#333', '#e8a33d', '#3a7']):
    ax2.plot([-0.020 + i*0.013, -0.020 + i*0.013], [0.070, 0.048], color=c, lw=1.6)
ax2.plot([-0.020, 0.019], [0.048, 0.048], color='#888', lw=1.4)
ax2.plot([-0.0005, -0.0005], [0.048, 0.030], color='#888', lw=1.4)
ax2.plot([-0.0005, 0.000], [0.030, 0.030], color='#888', lw=1.4)
ax2.add_patch(Rectangle((-0.042, -0.100), 0.084, 0.052, fc='#1e7a46', ec='k', lw=1.2))
ax2.text(0.0, -0.074, 'STM32（每 2ms 读一次）', ha='center', va='center', fontsize=10, color='w')
ax2.text(0.052, -0.005, '间隙 1~2mm\n（同轴对正才有准数）', fontsize=10, color='b')
ax2.set_xlim(-0.145, 0.155); ax2.set_ylim(-0.115, 0.135)
ax2.set_aspect('equal'); ax2.axis('off')

plt.savefig(r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs\S1_运动与采集原理.png', dpi=140, bbox_inches='tight')
print('saved')
