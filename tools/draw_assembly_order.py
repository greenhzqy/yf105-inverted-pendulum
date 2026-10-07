# -*- coding: utf-8 -*-
"""装配工序图：①固定电机 ②联轴器+法兰 ③磁铁+AS5600 ④锁摆杆+全周检查"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Ellipse, FancyArrow, FancyArrowPatch

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

FIG_W, FIG_H = 16, 10
fig, axes = plt.subplots(2, 2, figsize=(FIG_W, FIG_H), dpi=150)
(ax1, ax2), (ax3, ax4) = axes

ax1.set_title('① 固定电机：轴心悬空、伸出底板外', fontsize=13.5, pad=8)
ax2.set_title('② 装联轴器 + 法兰：不能晃', fontsize=13.5, pad=8)
ax3.set_title('③ 磁铁 + AS5600：同轴、间隙 1~2mm、支架不转', fontsize=13.5, pad=8)
ax4.set_title('④ 锁摆杆 + 全周检查', fontsize=13.5, pad=8)

for ax in (ax1, ax2, ax3, ax4):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

fig.tight_layout(rect=[0.006, 0.055, 0.994, 0.955])
fig.canvas.draw()

AR = {}
for ax in (ax1, ax2, ax3, ax4):
    _p = ax.get_position()
    AR[ax] = (_p.width * FIG_W) / (_p.height * FIG_H)

def circ(ax, xy, r, **kw):
    """画视觉上为正圆的圆（补偿子图纵横比）"""
    e = Ellipse(xy, 2 * r / AR[ax], 2 * r, **kw)
    ax.add_patch(e)
    return e

def crit(ax, x, y, s, fs=10.5, ha='left', va='bottom'):
    ax.text(x, y, s, fontsize=fs, color='#b00', ha=ha, va=va,
            bbox=dict(boxstyle='round', fc='#fff4f4', ec='#d33', lw=1.4))

# ==================== ① 固定电机 ====================
ax1.add_patch(Rectangle((0.03, 0.16), 0.37, 0.055, fc='#d9b382', ec='k', lw=1.5))
ax1.text(0.16, 0.187, '木底板', ha='center', va='center', fontsize=9.5, color='#6b4f24')

ax1.add_patch(Rectangle((0.13, 0.215), 0.21, 0.035, fc='#2b2b2b', ec='k', lw=1.2))
ax1.add_patch(Rectangle((0.305, 0.25), 0.030, 0.20, fc='#2b2b2b', ec='k', lw=1.2))
ax1.text(0.02, 0.265, '黑色 L 支架', ha='left', va='center', fontsize=9.5, color='#444')

ax1.add_patch(Rectangle((0.16, 0.25), 0.145, 0.16, fc='#4a6b8a', ec='k', lw=1.4))
ax1.text(0.2325, 0.432, '12V 减速电机', ha='center', va='bottom', fontsize=10, color='#33507a')

ax1.add_patch(Rectangle((0.34, 0.215), 0.045, 0.30, fc='#c9a06a', ec='k', lw=1.4))
ax1.add_patch(Rectangle((0.28, 0.320), 0.46, 0.020, fc='#9aa0a8', ec='k', lw=1.2))

ax1.annotate('', xy=(0.355, 0.50), xytext=(0.245, 0.60),
             arrowprops=dict(arrowstyle='->', color='#33507a', lw=1.2))
ax1.text(0.02, 0.615, '固定竖板：把电机垫高，\n轴（6mm）穿过竖板向右伸出，\n轴心高于底板平面',
         ha='left', va='bottom', fontsize=10, color='#33507a')

ax1.plot([0.40, 0.98], [0.215, 0.215], ls=(0, (5, 4)), color='#8a6a3a', lw=1.0)
ax1.text(0.975, 0.228, '底板平面（延长）', ha='right', va='bottom', fontsize=9.5, color='#8a6a3a')

circ(ax1, (0.60, 0.33), 0.30, fill=False, ec='#c0392b', lw=1.6, ls=(0, (6, 5)))
ax1.add_patch(Circle((0.60, 0.33), 0.007, fc='#c0392b', ec='none'))
ax1.text(0.60, 0.352, '轴心', ha='center', va='bottom', fontsize=9.5, color='#c0392b')

ax1.add_patch(FancyArrowPatch((0.655, 0.135), (0.715, 0.44), connectionstyle='arc3,rad=-0.35',
                              arrowstyle='-|>', mutation_scale=13, color='#c0392b', lw=1.4))
ax1.text(0.775, 0.19, '360°', ha='left', va='center', fontsize=10.5, color='#c0392b')

ax1.annotate('', xy=(0.752, 0.46), xytext=(0.745, 0.72),
             arrowprops=dict(arrowstyle='->', color='#c0392b', lw=1.3))
ax1.text(0.60, 0.795, '摆杆扫过的整个圆盘：\n半径 0.45m 内不许有任何东西（包括底板）',
         ha='center', va='bottom', fontsize=10.5, color='#c0392b')

crit(ax1, 0.02, 0.02, '判据：手拨摆杆能转满 360°，\n任何角度都不碰桌面和底板')

# ==================== ② 联轴器 + 法兰 ====================
ax2.plot([0.03, 0.97], [0.50, 0.50], ls=(0, (6, 4)), color='#3b6ea5', lw=1.2)
ax2.text(0.965, 0.512, '轴心线', ha='right', va='bottom', fontsize=10, color='#3b6ea5')

ax2.add_patch(Rectangle((0.02, 0.40), 0.055, 0.20, fc='#4a6b8a', ec='k', lw=1.2))
ax2.text(0.047, 0.385, '电机', ha='center', va='top', fontsize=10, color='#33507a')

ax2.add_patch(Rectangle((0.075, 0.468), 0.185, 0.064, fc='#9aa0a8', ec='k', lw=1.2))
ax2.text(0.15, 0.545, '轴 6mm', ha='center', va='bottom', fontsize=10, color='#4a5560')

ax2.add_patch(Rectangle((0.26, 0.43), 0.16, 0.14, fc='#c0c6cc', ec='k', lw=1.4))
ax2.plot([0.295, 0.295], [0.43, 0.57], color='#7a828c', lw=1.2)
ax2.plot([0.385, 0.385], [0.43, 0.57], color='#7a828c', lw=1.2)
ax2.add_patch(Circle((0.325, 0.580), 0.009, fc='#555', ec='k', lw=0.8))
ax2.add_patch(Circle((0.360, 0.580), 0.009, fc='#555', ec='k', lw=0.8))
ax2.text(0.34, 0.400, '联轴器（拧紧顶丝／夹紧）', ha='center', va='top', fontsize=10, color='#4a5560')

ax2.add_patch(Rectangle((0.42, 0.24), 0.032, 0.52, fc='#b8bcc4', ec='k', lw=1.4))
ax2.plot([0.436, 0.436], [0.07, 0.93], ls=(0, (5, 4)), color='#3b6ea5', lw=1.3)
ax2.plot([0.436, 0.454], [0.520, 0.520], color='#3b6ea5', lw=1.1)
ax2.plot([0.454, 0.454], [0.500, 0.520], color='#3b6ea5', lw=1.1)
ax2.text(0.47, 0.905, '法兰面必须垂直于轴心线', ha='left', va='center', fontsize=10.5, color='#3b6ea5')

ax2.add_patch(Rectangle((0.452, 0.22), 0.018, 0.26, fc='#c96a1e', ec='k', lw=1.1))
ax2.text(0.478, 0.285, '摆杆（偏心 15mm 锁在法兰上）', ha='left', va='center', fontsize=10, color='#a0522d')

ax2.annotate('', xy=(0.55, 0.66), xytext=(0.55, 0.80),
             arrowprops=dict(arrowstyle='<->', color='#d33', lw=1.5))
ax2.annotate('', xy=(0.46, 0.845), xytext=(0.60, 0.845),
             arrowprops=dict(arrowstyle='<->', color='#d33', lw=1.5))
ax2.text(0.625, 0.725, '捏住法兰左右上下扳动', ha='left', va='center', fontsize=10, color='#b00')

crit(ax2, 0.03, 0.03, '判据：捏住法兰左右上下扳，手感应为刚性；\n径向跳动 < 0.5mm，无旷量')

# ==================== ③ 磁铁 + AS5600 ====================
ax3.add_patch(Rectangle((0.03, 0.16), 0.045, 0.30, fc='#2b2b2b', ec='k', lw=1.3))
ax3.text(0.015, 0.472, '固定竖板\n（静止件）', ha='left', va='bottom', fontsize=9.5, color='#333')

ax3.add_patch(Rectangle((0.075, 0.578), 0.14, 0.045, fc='#9aa0a8', ec='k', lw=1.2))
ax3.text(0.095, 0.638, '轴 6mm', ha='left', va='bottom', fontsize=9.5, color='#4a5560')

ax3.add_patch(Rectangle((0.215, 0.34), 0.030, 0.52, fc='#b8bcc4', ec='k', lw=1.4))
ax3.annotate('', xy=(0.235, 0.355), xytext=(0.24, 0.325),
             arrowprops=dict(arrowstyle='->', color='#4a5560', lw=1.2))
ax3.text(0.10, 0.275, '法兰（竖直圆盘）', ha='left', va='bottom', fontsize=9.5, color='#4a5560')

ax3.add_patch(Rectangle((0.245, 0.565), 0.028, 0.070, fc='#f5c518', ec='k', lw=1.2))
ax3.annotate('', xy=(0.259, 0.645), xytext=(0.22, 0.865),
             arrowprops=dict(arrowstyle='->', color='#b8860b', lw=1.2))
ax3.text(0.17, 0.88, '磁铁（贴法兰朝外一面正中心）', ha='left', va='bottom', fontsize=9.5, color='#b8860b')

ax3.plot([0.273, 0.273], [0.64, 0.765], ls=':', color='b', lw=0.9)
ax3.plot([0.313, 0.313], [0.64, 0.765], ls=':', color='b', lw=0.9)
ax3.annotate('', xy=(0.273, 0.745), xytext=(0.313, 0.745),
             arrowprops=dict(arrowstyle='<->', color='b', lw=1.5))
ax3.text(0.293, 0.762, '1~2mm', ha='center', va='bottom', fontsize=10, color='b')

ax3.add_patch(Rectangle((0.313, 0.46), 0.022, 0.28, fc='#2e8b57', ec='k', lw=1.4))
ax3.add_patch(Rectangle((0.306, 0.565), 0.007, 0.070, fc='#0d3b22', ec='k', lw=0.8))
ax3.annotate('', xy=(0.34, 0.70), xytext=(0.37, 0.70),
             arrowprops=dict(arrowstyle='->', color='#1a5c33', lw=1.2))
ax3.text(0.372, 0.605, 'AS5600 模块\n（芯片面朝左，正对磁铁）', ha='left', va='bottom',
         fontsize=9.5, color='#1a5c33')

ax3.add_patch(Rectangle((0.335, 0.16), 0.022, 0.30, fc='#4a5560', ec='k', lw=1.1))
ax3.add_patch(Rectangle((0.075, 0.16), 0.282, 0.022, fc='#4a5560', ec='k', lw=1.1))
ax3.text(0.372, 0.30, 'L 形支架（深灰）\n底部固定在静止件上\n不随轴转', ha='left', va='bottom',
         fontsize=9.5, color='#4a5560')

ax3.add_patch(Rectangle((0.60, 0.06), 0.022, 0.88, fc='#c96a1e', ec='k', lw=1.1))
ax3.text(0.635, 0.72, '摆杆（偏心 15mm）\n所在平面与传感器错开，\n扫过时不碰支架',
         ha='left', va='bottom', fontsize=9.5, color='#a0522d')

ax3.plot([0.02, 0.58], [0.60, 0.60], ls=(0, (6, 4)), color='#3b6ea5', lw=1.2)
ax3.text(0.42, 0.520, '轴心线', ha='left', va='bottom', fontsize=9.5, color='#3b6ea5')

crit(ax3, 0.02, 0.02, '判据：串口显示 MAG=OK 且 |B| 几百~几千；\n手转一整圈 |B| 波动小、deg 平滑不跳')

# ==================== ④ 锁摆杆 + 全周检查 ====================
circ(ax4, (0.50, 0.52), 0.30, fc='#b8bcc4', ec='k', lw=1.8)
circ(ax4, (0.50, 0.52), 0.257, fill=False, ec='#d33', lw=1.4, ls=(0, (5, 4)))

ax4.add_patch(Rectangle((0.479, 0.484), 0.042, 0.072, fc='#f5c518', ec='k', lw=1.2))
ax4.add_patch(Rectangle((0.486, 0.496), 0.028, 0.048, fc='#2e8b57', ec='k', lw=1.0))

ax4.plot([0.03, 0.245], [0.94, 0.72], color='#4a5560', lw=5, solid_capstyle='round')
ax4.plot([0.245, 0.465], [0.72, 0.545], color='#4a5560', lw=3.2, ls=(0, (5, 3)))
ax4.add_patch(Circle((0.245, 0.72), 0.011, fc='#4a5560', ec='k', lw=0.8))
ax4.annotate('', xy=(0.245, 0.715), xytext=(0.20, 0.66),
             arrowprops=dict(arrowstyle='->', color='#4a5560', lw=1.2))
ax4.text(0.04, 0.545, '深灰支架\n转折点在半径 15mm 以外\n（该段实际从背面绕行）', ha='left', va='bottom',
         fontsize=9.5, color='#4a5560')

ax4.annotate('', xy=(0.604, 0.712), xytext=(0.625, 0.775),
             arrowprops=dict(arrowstyle='->', color='#b00', lw=1.2))
ax4.text(0.635, 0.775, '支架只能进中心小圈；\n半径 15mm 以外是摆杆\n扫过的圆环，不能进',
         ha='left', va='bottom', fontsize=9.5, color='#b00')

ax4.plot([0.50, 0.50], [0.263, 0.02], color='#c96a1e', lw=7, solid_capstyle='butt')
circ(ax4, (0.50, 0.263), 0.020, fc='w', ec='#c96a1e', lw=1.8)
ax4.text(0.53, 0.075, '摆杆 6mm×450mm\n（向外延伸）', ha='left', va='bottom', fontsize=10, color='#a0522d')
ax4.annotate('', xy=(0.488, 0.252), xytext=(0.30, 0.235),
             arrowprops=dict(arrowstyle='->', color='#a0522d', lw=1.2))
ax4.text(0.29, 0.215, '摆杆孔（偏心 15mm）', ha='right', va='center', fontsize=9.5, color='#a0522d')

ax4.text(0.635, 0.285, '法兰 φ35mm', ha='left', va='bottom', fontsize=10, color='#4a5560')
ax4.add_patch(FancyArrowPatch((0.66, 0.335), (0.73, 0.475), connectionstyle='arc3,rad=-0.32',
                              arrowstyle='-|>', mutation_scale=13, color='#c0392b', lw=1.4))
ax4.text(0.735, 0.40, '整圈转动无刮碰', ha='left', va='center', fontsize=10, color='#c0392b')

crit(ax4, 0.02, 0.02, '判据：拧紧后手拨摆杆，\n摆杆与外圆盘一起走、不相对转动；\n整圈转动无刮碰')

fig.text(0.5, 0.025,
         '正确组装工序：①固定电机 → ②联轴器+法兰 → ③磁铁+传感器 → ④锁摆杆+全周检查',
         ha='center', va='center', fontsize=15, color='#222', weight='bold')

OUT = r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs\S3_正确组装_工序图.png'
plt.savefig(OUT, dpi=150)
print('saved', OUT)
