
# -*- coding: utf-8 -*-
"""AS5600 安装位置图：磁铁-芯片同轴、间隙 1~2mm、摆杆垫高避让"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrow

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

fig, (axA, axB) = plt.subplots(1, 2, figsize=(15.5, 8), dpi=150)

# ============ 左：侧视剖面（轴水平向右） ============
axA.set_title('侧视剖面：沿轴线依次是  轴 → 法兰 → 磁铁 → 间隙 → 芯片', fontsize=12.5)
axA.add_patch(Rectangle((0.02, -0.045), 0.075, 0.090, fc='#4a6b8a', ec='k', lw=1.5))
axA.text(0.057, 0.058, '电机', ha='center', fontsize=11, color='#33507a')
axA.add_patch(Rectangle((0.095, -0.004), 0.070, 0.008, fc='#9aa0a8', ec='k', lw=1.2))   # 轴
axA.text(0.130, -0.022, '轴 6mm', ha='center', fontsize=10)

# 法兰
axA.add_patch(Rectangle((0.165, -0.055), 0.006, 0.110, fc='#b8bcc4', ec='k', lw=1.5))
axA.text(0.168, 0.070, '法兰', ha='center', fontsize=11, color='#4a5560')
# 磁铁（贴法兰外侧面中心 = 轴线上）
axA.add_patch(Rectangle((0.171, -0.008), 0.010, 0.016, fc='#f5c518', ec='k', lw=1.2))
axA.text(0.176, -0.035, '磁铁', ha='center', fontsize=10.5, color='#b8860b')
# 间隙
axA.annotate('', xy=(0.181, 0.030), xytext=(0.194, 0.030),
             arrowprops=dict(arrowstyle='<->', color='b', lw=1.4))
axA.text(0.1875, 0.040, '1~2mm', ha='center', fontsize=10.5, color='b')
# AS5600 模块（芯片朝左，正对磁铁）
axA.add_patch(Rectangle((0.194, -0.022), 0.006, 0.044, fc='#2e8b57', ec='k', lw=1.5))
axA.add_patch(Rectangle((0.1925, -0.009), 0.0025, 0.018, fc='#0d3b22', ec='k', lw=0.8))
axA.text(0.245, 0.012, 'AS5600 模块', fontsize=11, color='#1a5c33')
axA.text(0.245, 0.000, '（芯片面朝左，正对磁铁）', fontsize=10, color='#1a5c33')
# 支架：从下方伸上来
axA.add_patch(Rectangle((0.185, -0.100), 0.022, 0.080, fc='#aab4c0', ec='k', lw=1.2))
axA.add_patch(Rectangle((0.140, -0.100), 0.070, 0.006, fc='#aab4c0', ec='k', lw=1.2))
axA.text(0.205, -0.115, '支架（铝条/铜柱，弯成 L）', ha='center', fontsize=10.5, color='#4a5560')
# 摆杆：锁在法兰边上，用铜柱垫高，绕过传感器
axA.add_patch(Rectangle((0.183, -0.24), 0.006, 0.170, fc='#c96a1e', ec='k', lw=1.2))
axA.add_patch(Rectangle((0.171, -0.070), 0.012, 0.010, fc='#c0c0c0', ec='k', lw=1.0))
axA.annotate('', xy=(0.190, -0.062), xytext=(0.190, -0.100),
             arrowprops=dict(arrowstyle='<->', color='#a0522d', lw=1.3))
axA.text(0.196, -0.085, '垫高 6~10mm\n（让摆杆从传感器上方扫过）', fontsize=10.5, color='#a0522d')
axA.text(0.183, -0.255, '摆杆（偏心 15mm 锁在法兰上）', fontsize=11, color='#a0522d')
axA.plot([0.02, 0.30], [0, 0], 'k-.', lw=0.9)
axA.text(0.292, -0.012, '轴线', fontsize=10)
axA.set_xlim(0.0, 0.33); axA.set_ylim(-0.28, 0.095); axA.set_aspect('equal'); axA.axis('off')

# ============ 右：端面视图（沿轴线看过去） ============
axB.set_title('端面看：芯片对准正中心，支架从外侧绕进来', fontsize=12.5)
axB.add_patch(Circle((0, 0), 0.032, fc='#b8bcc4', ec='k', lw=1.6))          # 法兰
axB.add_patch(Circle((0, 0), 0.008, fc='#f5c518', ec='k', lw=1.2))          # 磁铁
axB.add_patch(Rectangle((-0.007, -0.007), 0.014, 0.014, fc='#2e8b57', ec='k', lw=1.2, alpha=0.85))
axB.text(0.014, 0.010, 'AS5600 芯片\n（对准磁铁正中心）', fontsize=10.5, color='#1a5c33')
axB.add_patch(Circle((0, -0.018), 0.0035, fc='#c96a1e', ec='k', lw=1.1))    # 摆杆截面
axB.text(0.010, -0.038, '摆杆（偏心 15mm）\n从支架上方扫过', fontsize=10.5, color='#a0522d')
# 支架绕行
axB.plot([-0.055, -0.020], [0.048, 0.048], color='#4a5560', lw=6, solid_capstyle='round')
axB.plot([-0.020, -0.020], [0.048, -0.020], color='#4a5560', lw=6, solid_capstyle='round')
axB.plot([-0.020, -0.004], [-0.020, -0.020], color='#4a5560', lw=6, solid_capstyle='round')
axB.text(-0.062, 0.058, '支架（贴法兰面 1~2mm 处伸进来）', fontsize=10.5, color='#4a5560')
axB.add_patch(FancyArrow(0.026, -0.050, -0.012, 0.012, width=0.0018, head_width=0.011,
                         color='#2e8b57'))
axB.text(0.030, -0.058, '法兰转向', fontsize=10, color='#2e8b57')
axB.set_xlim(-0.075, 0.085); axB.set_ylim(-0.075, 0.075); axB.set_aspect('equal'); axB.axis('off')

plt.tight_layout()
plt.savefig(r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs\S1_AS5600安装位置.png', dpi=150, bbox_inches='tight')
print('saved')
