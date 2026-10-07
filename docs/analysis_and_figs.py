# -*- coding: utf-8 -*-
"""倒立摆设计报告：从仿真结果 CSV 计算关键指标并生成报告插图。
输入：25级-倒立摆控制/results（新跑的结果）
输出：_报告工作/figs/*.png + _报告工作/关键数据.txt
"""
import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle, FancyBboxPatch

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '25级-倒立摆控制', 'results')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figs')
os.makedirs(OUT, exist_ok=True)

def load(name):
    return pd.read_csv(os.path.join(BASE, name + '.csv'))

def savefig(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=170, bbox_inches='tight')
    plt.close(fig)
    print('fig ->', name)

lines = []
def note(s):
    lines.append(s)
    print(s)

# ============ 1. 系统框图（方案级，含实物链与仿真链） ============
def fig_system_block():
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.2); ax.axis('off')
    def box(x, y, w, h, text, fc='#eaf2fb', ec='#2f6db3', fs=9.5, bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.04',
                                    fc=fc, ec=ec, lw=1.3))
        ax.text(x + w/2, y + h/2, text, ha='center', va='center',
                fontsize=fs, weight='bold' if bold else 'normal')
    def arrow(x1, y1, x2, y2, label='', ls='-', color='#333333'):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>',
                                     mutation_scale=14, lw=1.4, color=color, linestyle=ls))
        if label:
            ax.text((x1+x2)/2 + 0.08, (y1+y2)/2 + 0.10, label, fontsize=8, color='#555555')
    # 主控
    box(3.6, 3.1, 2.8, 1.3, 'STM32F103C8T6 主控\n2ms 硬节拍 · 状态机\n(500Hz 控制)', fc='#e8f5e9', ec='#2e7d32', bold=True)
    # 执行链
    box(7.0, 3.1, 2.6, 1.3, 'TB6612 驱动\nPWM 20kHz + 方向', fc='#fff3e0', ec='#e65100')
    box(8.6, 1.0, 1.2, 1.2, '12V 减速电机\n(直驱摆杆)')
    # 感知链
    box(0.6, 3.1, 2.4, 1.3, 'AS5600 磁编码器\nI2C · 12bit · 绝对角度', fc='#fce4ec', ec='#ad1457')
    # 摆杆/负载
    box(0.4, 0.9, 2.6, 1.3, '摆杆 6mm×450mm\n(含小车/底座模型)')
    # 电脑
    box(3.4, 0.9, 3.2, 1.3, '上位机\n串口 115200 · 命令/CSV 曲线', fc='#ede7f6', ec='#4527a0')
    arrow(4.8, 4.4, 7.0, 4.15, 'PWM/方向')
    arrow(7.0, 4.15, 8.6, 4.15)   # 驱动->电机画歪了,改用下方
    arrow(8.3, 3.1, 7.4, 2.25, '力矩', ls=':')  # 电机->摆杆示意
    arrow(1.8, 3.1, 2.0, 2.2, '', ls=':')       # 摆杆->编码器（转轴联动）
    arrow(1.2, 4.4, 3.6, 4.15, 'I2C 角度 RAW')
    arrow(6.2, 4.4, 5.2, 4.4, '', ls='-')       # 串口（上行）
    arrow(5.0, 3.1, 6.2, 3.1, '', ls='-')
    ax.text(5.6, 4.55, '串口命令/数据', fontsize=8, color='#555555')
    ax.text(4.05, 3.05, 'USB-TTL 双向', fontsize=8, color='#555555')
    ax.text(2.15, 2.15, '转轴联动\n(磁铁随轴)', fontsize=7.5, color='#555555')
    ax.text(7.85, 2.05, '数字→力', fontsize=7.5, color='#555555')
    ax.text(0.25, 4.95, '角度→数：I2C 读 0x36，deg = RAW/4096×360 − z0（绝对角度，上电即知位置）',
            fontsize=8.5, color='#333333')
    ax.text(0.25, 0.15, '实物链路已完成：电机驱动 / 角度采集 / 2ms 硬节拍采样滤波 / 数据记录（S1~S2）',
            fontsize=8.5, color='#2e7d32')
    savefig(fig, '图1_系统框图.png')

# ============ 2. 控制结构（状态机 + LQR 反馈） ============
def fig_control():
    fig, ax = plt.subplots(figsize=(10.5, 4.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 4.4); ax.axis('off')
    def box(x, y, w, h, text, fc='#eaf2fb', ec='#2f6db3', fs=9):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.04', fc=fc, ec=ec, lw=1.3))
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fs)
    def arrow(x1, y1, x2, y2, label='', color='#333'):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=13, lw=1.3, color=color))
        if label: ax.text((x1+x2)/2+0.05, (y1+y2)/2+0.12, label, fontsize=8, color='#555')
    # 控制回路（平衡模式）
    box(0.3, 2.2, 1.9, 1.3, '角度/位置\n测量 y\n(2ms)', fc='#fce4ec', ec='#ad1457')
    box(2.6, 2.2, 1.9, 1.3, '卡尔曼滤波\n状态估计 x̂', fc='#fff3e0', ec='#e65100')
    box(4.9, 2.2, 1.9, 1.3, 'LQR 反馈\nu = −K·xhat\n(限幅 ±10N)', fc='#e8f5e9', ec='#2e7d32')
    box(7.2, 2.2, 1.9, 1.3, '被控对象\n(小车+摆杆)', fc='#eaf2fb', ec='#2f6db3')
    box(4.9, 0.3, 3.4, 1.2, '安全监控：摆角/位置/速度\n电流/传感器/看门狗\n(FAULT 锁存·断电抱闸)', fc='#fdecea', ec='#c62828')
    arrow(2.2, 2.85, 2.6, 2.85)
    arrow(4.5, 2.85, 4.9, 2.85)
    arrow(6.8, 2.85, 7.2, 2.85)
    arrow(8.15, 2.2, 8.15, 1.55, 'u', color='#c62828')
    arrow(5.0, 1.5, 5.0, 2.2, 'x, u, valid', color='#c62828')
    arrow(8.15, 2.85, 8.6, 3.35, '状态 x')
    ax.text(8.95, 3.15, '测量反馈', fontsize=8, color='#555')
    # 状态机说明
    ax.text(0.3, 4.05, '模式状态机：PUMP（能量起摆）→ 捕获条件（E≥E*, |θ|<0.2rad）→ BALANCE（LQR）→ 失衡降级回摆起 → 连败 N 次/硬故障 → FAULT（人工复位）',
            fontsize=8.8, color='#333333')
    savefig(fig, '图2_控制结构图.png')

# ============ 3. 结果曲线 ============
def fig_s1():
    df = load('S1_offset')
    t, th, x, u = df['t'], df['th'], df['x'], df['u_cmd']
    fig, axs = plt.subplots(3, 1, figsize=(7.2, 6.6), sharex=True)
    axs[0].plot(t, th*57.2958, color='#2e7d32', lw=1.0); axs[0].set_ylabel('摆角 θ (°)')
    axs[0].axhline(0, color='gray', lw=0.5); axs[0].grid(alpha=0.3)
    axs[0].set_title('S1 初始偏差恢复（LQR，θ0=5°）')
    axs[1].plot(t, x, color='#ad1457', lw=1.0); axs[1].set_ylabel('小车位置 x (m)'); axs[1].grid(alpha=0.3)
    axs[2].plot(t, u, color='#e65100', lw=0.8); axs[2].set_ylabel('控制力 u (N)'); axs[2].grid(alpha=0.3)
    axs[2].set_xlabel('时间 (s)')
    savefig(fig, '图3_S1初始偏差恢复.png')

def fig_s8():
    d1, d2 = load('S8_LQR'), load('S8_PD')
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.plot(d1['t'], d1['th']*57.2958, color='#2e7d32', lw=1.1, label='LQR 状态反馈')
    ax.plot(d2['t'], d2['th']*57.2958, color='#c62828', lw=0.9, label='串级 PD（未收敛）')
    ax.axhline(0, color='gray', lw=0.5); ax.grid(alpha=0.3)
    ax.set_xlabel('时间 (s)'); ax.set_ylabel('摆角 θ (°)')
    ax.set_title('S8 LQR vs 串级 PD（同一 5° 初始偏差）')
    ax.legend(); ax.set_ylim(-90, 90)
    savefig(fig, '图4_LQRvsPD.png')

def fig_s9():
    d1, d2 = load('S9_LQR'), load('S9_LQRI')
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.plot(d1['t'], d1['th']*57.2958, color='#2e7d32', lw=1.0, label='LQR')
    ax.plot(d2['t'], d2['th']*57.2958, color='#1565c0', lw=1.0, label='LQR + 位置积分 (LQRI)')
    ax.axhline(0, color='gray', lw=0.5); ax.grid(alpha=0.3)
    ax.set_xlabel('时间 (s)'); ax.set_ylabel('摆角 θ (°)')
    ax.set_title('S9 LQR vs 增广积分 LQRI（库仑摩擦稳态偏差对比）')
    ax.legend()
    savefig(fig, '图5_LQRvsLQRI.png')

def fig_s7():
    with open(os.path.join(BASE, 'S7_sampling.json'), encoding='utf-8') as f:
        rows = json.load(f)
    ts = [r['Ts_ms'] for r in rows]; st = [1 if r['stable'] else 0 for r in rows]
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    colors = ['#2e7d32' if s else '#c62828' for s in st]
    ax.bar([str(t) for t in ts], st, color=colors)
    ax.axhline(0.5, color='gray', ls='--', lw=0.8)
    for i, r in enumerate(rows):
        v = f"{r['peak_theta']*57.2958:.2f}°" if r['stable'] else '发散'
        ax.text(i, 0.62, v, ha='center', fontsize=7.5)
    ax.set_ylim(0, 1.15); ax.set_yticks([0, 1]); ax.set_yticklabels(['发散', '稳定'])
    ax.set_xlabel('采样周期 Ts (ms)'); ax.set_title('S7 采样周期扫描：2ms 设计点裕量充足（≤22ms 稳定）')
    savefig(fig, '图6_S7采样扫描.png')

def fig_s5():
    df = load('S5_swingup')
    t, th, x, mode = df['t'], df['th'], df['x'], df['mode_id']
    fig, axs = plt.subplots(2, 1, figsize=(7.2, 4.6), sharex=True)
    axs[0].plot(t, th*57.2958, color='#1565c0', lw=0.8)
    axs[0].set_ylabel('摆角 θ (°)'); axs[0].grid(alpha=0.3)
    axs[1].plot(t, x, color='#e65100', lw=0.8)
    axs[1].set_ylabel('小车位置 x (m)'); axs[1].grid(alpha=0.3)
    axs[1].set_xlabel('时间 (s)')
    # 标记故障点
    for m, txt, col in [(2, 'FAULT 停机', '#c62828')]:
        ft = t[mode.values == m]
        if len(ft):
            ft0 = float(ft.iloc[0])
            axs[0].axvline(ft0, color=col, ls='--', lw=1.0)
            axs[0].text(ft0+0.02, 330, f'{txt} @{ft0:.2f}s', color=col, fontsize=8)
    axs[0].set_title('S5 能量起摆：泵摆使摆杆大幅摆动，但小车漂移超限触发 FAULT（待整定）')
    savefig(fig, '图7_S5起摆.png')

def fig_s6():
    d = load('S6_b_sensor')
    t, th, mode = d['t'], d['th'], d['mode_id']
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.plot(t, th*57.2958, color='#1565c0', lw=0.9)
    ft = t[mode.values == 2]
    if len(ft):
        ft0 = float(ft.iloc[0])
        ax.axvline(ft0, color='#c62828', ls='--', lw=1.1)
        ax.text(ft0+0.01, 2.2, f'传感器断连→FAULT @{ft0:.3f}s', color='#c62828', fontsize=8.5)
    ax.set_xlabel('时间 (s)'); ax.set_ylabel('摆角 θ (°)'); ax.grid(alpha=0.3)
    ax.set_title('S6b 传感器断连 80ms：38ms 内检测并停机（拒绝不可信闭环）')
    savefig(fig, '图8_S6b传感器断连.png')

def fig_estimation():
    df = load('S4_estimation')
    t, th, xh2 = df['t'], df['th'], df['xh2']
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.plot(t, th*57.2958, color='#888888', lw=0.9, label='真实 θ')
    ax.plot(t, xh2*57.2958, color='#2e7d32', lw=0.9, ls='--', label='卡尔曼估计 θhat')
    ax.grid(alpha=0.3); ax.set_xlabel('时间 (s)'); ax.set_ylabel('角度 (°)')
    ax.set_title('S4 卡尔曼滤波：仅用角度/位置编码器测量恢复全状态')
    ax.legend()
    savefig(fig, '图9_卡尔曼估计.png')

if __name__ == '__main__':
    fig_system_block()
    fig_control()
    fig_s1()
    fig_s8()
    fig_s9()
    fig_s7()
    fig_s5()
    fig_s6()
    fig_estimation()
    print('ALL FIGS DONE')
