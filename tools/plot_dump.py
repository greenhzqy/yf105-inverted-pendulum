# -*- coding: utf-8 -*-
"""上位机：把固件 dump 出来的 CSV 画成曲线
用法：python plot_dump.py <dump.csv> [out.png]
CSV 格式（每行）：i,th_deg,dps,duty
"""
import sys, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

src = sys.argv[1] if len(sys.argv) > 1 else r'..\results\dump.csv'
out = sys.argv[2] if len(sys.argv) > 2 else r'..\figs\S2_dump_curve.png'

idx, th, dps, duty = [], [], [], []
for line in open(src, encoding='utf-8', errors='ignore'):
    p = line.strip().split(',')
    if len(p) != 4:
        continue
    try:
        idx.append(int(p[0])); th.append(float(p[1])); dps.append(float(p[2])); duty.append(float(p[3]))
    except ValueError:
        continue

t = np.array(idx) * 2e-3      # 每样本 2ms
th = np.array(th); dps = np.array(dps); duty = np.array(duty)
print('samples =', len(t), 'duration = %.2f s' % (t[-1] if len(t) else 0))

fig, ax = plt.subplots(3, 1, figsize=(12, 8.5), dpi=140, sharex=True)
ax[0].plot(t, th, lw=1.2, color='#1f6fd0'); ax[0].set_ylabel('摆角 (deg)')
ax[0].set_title('S2 数据回放：角度 / 速度 / 占空比（每样本 2ms，500Hz）', fontsize=12)
ax[0].grid(alpha=0.3)
ax[1].plot(t, dps, lw=1.0, color='#d2691e'); ax[1].set_ylabel('角速度 (deg/s)'); ax[1].grid(alpha=0.3)
ax[2].plot(t, duty, lw=1.2, color='#2e8b57'); ax[2].set_ylabel('占空比 (%)'); ax[2].set_xlabel('时间 (s)'); ax[2].grid(alpha=0.3)
ax[2].set_ylim(-5, 105)
plt.tight_layout()
plt.savefig(out, bbox_inches='tight')
print('saved ->', out)
