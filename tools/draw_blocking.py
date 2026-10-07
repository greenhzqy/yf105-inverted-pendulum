
# -*- coding: utf-8 -*-
"""阻塞发送 vs 非阻塞发送：为什么打印会吃掉 2ms 节拍"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7.6), dpi=150,
                               gridspec_kw={'hspace': 0.55})

T = 30.0   # ms

def axis_base(ax, title, tcolor='#333'):
    ax.set_title(title, fontsize=13, weight='bold', color=tcolor, loc='left')
    ax.set_xlim(-0.6, T + 0.6); ax.set_ylim(-1.5, 2.2)
    ax.set_yticks([]); ax.set_xlabel('时间 (ms)', fontsize=10.5)
    for t in np.arange(0, T + 0.01, 2.0):
        ax.plot([t, t], [-0.06, 0.06], color='#999', lw=1.0)
    ax.set_xticks(np.arange(0, T + 0.01, 4.0))
    ax.spines[['left','right','top']].set_visible(False)

# ============ 上：阻塞发送 ============
ax1 = ax1
axis_base(ax1, '① 阻塞发送：主循环被"打印"占住 12ms → 中间的节拍全丢', '#a00')
# 快任务小块
for t in [0, 2]:
    ax1.add_patch(Rectangle((t, 0.5), 0.25, 0.5, fc='#2e8b57', ec='k', lw=0.8))
ax1.text(0.35, 1.25, '快任务（读角，约 0.2ms）', fontsize=10.5, color='#1a5c33')

# 打印阻塞块 4ms ~ 16ms
ax1.add_patch(Rectangle((4.0, 0.5), 12.0, 0.5, fc='#d62728', ec='k', lw=1.0))
ax1.text(10.0, 1.25, '打印：阻塞发送，整整 12ms 里 CPU 卡在这儿等', fontsize=10.5,
         color='#a00', ha='center')

# 丢失的节拍
for t in [6, 8, 10, 12, 14]:
    ax1.plot([t], [0.75], marker='x', color='#a00', ms=13, mew=3)
    ax1.text(t, 0.18, '丢', color='#a00', ha='center', fontsize=11)
ax1.annotate('本该每 2ms 一拍，这里连续丢了 6 拍',
             xy=(10, 0.75), xytext=(17.0, 0.75), fontsize=10.5, color='#a00',
             arrowprops=dict(arrowstyle='->', color='#a00', lw=1.2))

# ============ 下：非阻塞发送 ============
axis_base(ax2, '② 非阻塞发送（中断发送）：主循环立刻返回，串口在"后台"慢慢发', '#1a5c33')
for t in np.arange(0, T + 0.01, 2.0):
    ax2.add_patch(Rectangle((t, 0.5), 0.25, 0.5, fc='#2e8b57', ec='k', lw=0.8))
    ax2.plot([t + 0.1], [1.35], marker='o', color='#2e8b57', ms=5)
ax2.text(0.35, 1.55, '每一拍都准时（0.2ms 就返回，剩下的时间随便干别的）',
         fontsize=10.5, color='#1a5c33')
# 后台发送带
ax2.add_patch(Rectangle((4.0, 0.05), 12.0, 0.28, fc='#4a7fe0', ec='k', lw=0.8, alpha=0.75))
ax2.text(10.0, -0.35, '串口在后台一个字节一个字节地发（由中断驱动，CPU 不用等）',
         fontsize=10.5, color='#2b5599', ha='center')
ax2.text(T - 0.2, 1.35, '→ 节拍稳如老狗', fontsize=11, color='#1a5c33', ha='right')

plt.savefig(r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs\S2_阻塞vs非阻塞.png', dpi=150, bbox_inches='tight')
print('saved')
