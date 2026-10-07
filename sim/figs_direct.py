# -*- coding: utf-8 -*-
"""直驱摆仿真的报告插图。"""
import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'results_direct')
FIG = os.path.join(HERE, 'figs')
os.makedirs(FIG, exist_ok=True)


def load(name):
    return pd.read_csv(os.path.join(RES, name + '.csv'))


def save(fig, name):
    fig.savefig(os.path.join(FIG, name), dpi=170, bbox_inches='tight')
    plt.close(fig)
    print('fig ->', name)


# ---------- 图 A：实物结构 + 控制回路 ----------
def fig_structure():
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.set_xlim(0, 11); ax.set_ylim(0, 4.6); ax.axis('off')

    def box(x, y, w, h, text, fc='#eaf2fb', ec='#2f6db3', fs=9):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.05', fc=fc, ec=ec, lw=1.3))
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fs)

    def arrow(x1, y1, x2, y2, label='', color='#333'):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=13,
                                     lw=1.3, color=color))
        if label:
            ax.text((x1+x2)/2 + 0.06, (y1+y2)/2 + 0.13, label, fontsize=8, color='#555')

    # 左：机械结构
    ax.add_patch(Rectangle((0.3, 0.7), 1.4, 0.35, fc='#d7ccc8', ec='#6d4c41'))
    ax.text(1.0, 0.875, '固定底座（木底板+角铁）', ha='center', va='center', fontsize=7.5)
    box(1.55, 1.35, 1.0, 0.85, '减速电机\n(基座固定)', fc='#fff3e0', ec='#e65100', fs=8.5)
    ax.plot([2.55, 3.6], [1.775, 1.775], color='#333', lw=2.5)   # 电机轴
    ax.add_patch(Circle((3.7, 1.775), 0.12, fc='#b0bec5', ec='k'))  # 法兰
    ax.plot([3.7, 3.7], [1.775, 3.3], color='#8d6e63', lw=5)      # 摆杆
    ax.add_patch(Circle((3.7, 3.35), 0.11, fc='#455a64', ec='k')) # 尖端配重
    ax.text(3.9, 3.35, '尖端配重', fontsize=8)
    ax.text(3.9, 1.95, '法兰/白盘', fontsize=8)
    ax.text(2.9, 1.55, '联轴器', fontsize=8)
    ax.plot([3.7, 3.7], [1.775, 1.775], marker='o', ms=4, color='#c62828')
    ax.text(3.15, 1.0, '摆杆绕电机轴转动\n（无小车、无轨道）', fontsize=8.5, color='#c62828')
    ax.add_patch(Rectangle((3.45, 1.62), 0.5, 0.3, fc='#fce4ec', ec='#ad1457', lw=1.0))
    ax.text(3.7, 1.77, 'AS5600', ha='center', va='center', fontsize=7.5)

    ax.text(0.25, 4.35, '实物结构：电机轴 → 联轴器 → 法兰 → 摆杆；编码器测轴端磁铁角度；基座固定不动',
            fontsize=9, weight='bold')

    # 右：控制回路
    box(6.0, 3.0, 2.0, 1.1, '控制律\nPD / PID\n(u = kp·e + kd·ω + ki∫e)', fc='#e8f5e9', ec='#2e7d32', fs=8.5)
    box(8.4, 3.0, 2.2, 1.1, '占空比 → 电机力矩\nPWM 20kHz · TB6612', fc='#fff3e0', ec='#e65100', fs=8.5)
    box(8.4, 1.5, 2.2, 1.0, '被控对象\nI·θdd = k_g·sinθ − τ_f − τ_m', fc='#eaf2fb', ec='#2f6db3', fs=8.5)
    box(6.0, 1.5, 2.0, 1.0, '角度链\n回绕→展开→低通→差分', fc='#fce4ec', ec='#ad1457', fs=8.5)
    box(6.0, 0.3, 4.6, 0.9, '安全监控（独立一层）：超角降级 / 传感器断连 / 占空比饱和 / 看门狗 → 断电锁存',
        fc='#fdecea', ec='#c62828', fs=8.5)
    arrow(8.0, 3.55, 8.4, 3.55)
    arrow(9.5, 3.0, 9.5, 2.5)
    arrow(8.4, 2.0, 8.0, 2.0)
    arrow(7.0, 2.5, 7.0, 3.0)
    ax.text(9.05, 1.22, '2ms（500Hz）闭环', fontsize=8, color='#555')
    save(fig, 'D1_结构与控制回路.png')


# ---------- 图 B：S1 阶跃响应 ----------
def fig_s1():
    d = load('S1_PID')
    fig, axs = plt.subplots(3, 1, figsize=(7.2, 6.4), sharex=True)
    axs[0].plot(d.t, np.rad2deg(d.th), color='#2e7d32', lw=1.0)
    axs[0].set_ylabel('摆角 θ (°)'); axs[0].grid(alpha=0.3); axs[0].axhline(0, color='gray', lw=0.5)
    axs[0].set_title('S1 初始偏差 10° → PID 闭环（0.51s 收敛）')
    axs[1].plot(d.t, d.om, color='#1565c0', lw=0.9)
    axs[1].set_ylabel('角速度 ω (rad/s)'); axs[1].grid(alpha=0.3)
    axs[2].plot(d.t, d.duty, color='#e65100', lw=0.8)
    axs[2].set_ylabel('占空比 (%)'); axs[2].set_xlabel('时间 (s)'); axs[2].grid(alpha=0.3)
    save(fig, 'D2_S1阶跃响应.png')


# ---------- 图 C：死区对比 PD vs PID（核心图） ----------
def fig_deadzone():
    dpd, dpid = load('S9_PD'), load('S9_PID')
    fig, axs = plt.subplots(2, 1, figsize=(7.4, 5.2), sharex=True)
    axs[0].plot(dpd.t, np.rad2deg(dpd.th), color='#c62828', lw=1.1, label='纯 PD（卡在死区）')
    axs[0].plot(dpid.t, np.rad2deg(dpid.th), color='#2e7d32', lw=1.1, label='PID（积分跨死区）')
    axs[0].axhline(0, color='gray', lw=0.5); axs[0].grid(alpha=0.3)
    axs[0].set_ylabel('摆角 θ (°)'); axs[0].legend()
    axs[0].set_title('摩擦死区：从 2° 起步，PD 收不回去（卡在 2.03°），PID 1.20s 收到 −0.51°')
    axs[1].plot(dpd.t, dpd.duty, color='#c62828', lw=0.8, label='PD 占空比')
    axs[1].plot(dpid.t, dpid.duty, color='#2e7d32', lw=0.8, label='PID 占空比')
    axs[1].grid(alpha=0.3); axs[1].set_ylabel('占空比 (%)'); axs[1].set_xlabel('时间 (s)')
    axs[1].legend(fontsize=8)
    save(fig, 'D3_死区PDvsPID.png')


# ---------- 图 D：S8 纯 PD / LQR 卡在死区 ----------
def fig_s8():
    dpd, dlqr = load('S8_PD'), load('S8_LQR')
    fig, ax = plt.subplots(figsize=(7.4, 3.4))
    ax.plot(dpd.t, np.rad2deg(dpd.th), color='#c62828', lw=1.0, label='纯 PD')
    ax.plot(dlqr.t, np.rad2deg(dlqr.th), color='#1565c0', lw=1.0, label='LQR（2 状态状态反馈）')
    ax.axhline(0, color='gray', lw=0.5); ax.grid(alpha=0.3)
    ax.set_xlabel('时间 (s)'); ax.set_ylabel('摆角 θ (°)')
    ax.set_title('S8 从 10° 起步：纯 PD 与 LQR 都停在 ±6.5°（力矩压不过静摩擦）')
    ax.legend()
    save(fig, 'D4_纯PD与LQR卡死区.png')


# ---------- 图 E：S5 能量起摆 ----------
def fig_s5():
    d = load('S5_swingup')
    fig, axs = plt.subplots(3, 1, figsize=(7.4, 6.4), sharex=True)
    axs[0].plot(d.t, np.rad2deg(d.th), color='#1565c0', lw=0.8)
    axs[0].set_ylabel('摆角 θ (°)'); axs[0].grid(alpha=0.3)
    axs[0].set_title('S5 能量起摆：从下垂 180° 泵到直立（18.0s 站住）')
    axs[1].plot(d.t, d.E, color='#6a1b9a', lw=0.9)
    axs[1].axhline(0, color='green', ls='--', lw=0.8)
    axs[1].set_ylabel('机械能 E (J)'); axs[1].grid(alpha=0.3)
    axs[2].plot(d.t, d.duty, color='#e65100', lw=0.7)
    axs[2].set_ylabel('占空比 (%)'); axs[2].set_xlabel('时间 (s)'); axs[2].grid(alpha=0.3)
    save(fig, 'D5_能量起摆.png')


# ---------- 图 F：S3 参数失配 ----------
def fig_s3():
    d = load('S3_mismatch')
    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    ax.plot(d.t, np.rad2deg(d.th), color='#ad1457', lw=1.0)
    ax.axhline(0, color='gray', lw=0.5); ax.grid(alpha=0.3)
    ax.set_xlabel('时间 (s)'); ax.set_ylabel('摆角 θ (°)')
    ax.set_title('S3 参数失配（杆质量+50%、长+20%、摩擦×2）：0.91s 收敛，残差 −1.65°')
    save(fig, 'D6_参数失配.png')


# ---------- 图 G：S7 采样扫描 ----------
def fig_s7():
    rows = json.load(open(os.path.join(RES, 'S7_sampling.json'), encoding='utf-8'))
    ts = [r['Ts_ms'] for r in rows]
    st = [1 if r['stable'] else 0 for r in rows]
    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    ax.bar([str(t) for t in ts], st, color=['#2e7d32' if s else '#c62828' for s in st])
    for i, r in enumerate(rows):
        txt = f"{r['final_theta_deg']:.1f}°" if r['stable'] else '发散'
        ax.text(i, 0.62, txt, ha='center', fontsize=7.5)
    ax.set_ylim(0, 1.15); ax.set_yticks([0, 1]); ax.set_yticklabels(['发散', '稳定'])
    ax.set_xlabel('采样周期 Ts (ms)')
    ax.set_title('S7 采样周期扫描：稳定到 30ms（设计点 2ms，裕量约 15 倍）')
    save(fig, 'D7_采样扫描.png')


# ---------- 图 H：S6b 传感器断连 ----------
def fig_s6b():
    d = load('S6_b_sensor')
    fig, axs = plt.subplots(2, 1, figsize=(7.4, 4.6), sharex=True)
    axs[0].plot(d.t, np.rad2deg(d.th), color='#1565c0', lw=1.0)
    axs[0].axvline(2.0, color='#c62828', ls='--', lw=1.0)
    axs[0].axvline(2.038, color='#c62828', ls='-', lw=1.2)
    axs[0].text(2.01, 6, '传感器断连 @2.000s', color='#c62828', fontsize=8)
    axs[0].text(2.05, 3, 'FAULT @2.038s（38ms）', color='#c62828', fontsize=8)
    axs[0].set_ylabel('摆角 θ (°)'); axs[0].grid(alpha=0.3)
    axs[0].set_title('S6b 传感器断连 80ms：38ms 内检测并急停（拒绝不可信闭环）')
    axs[1].plot(d.t, d.duty, color='#e65100', lw=0.9)
    axs[1].axvline(2.038, color='#c62828', ls='-', lw=1.2)
    axs[1].set_ylabel('占空比 (%)'); axs[1].set_xlabel('时间 (s)'); axs[1].grid(alpha=0.3)
    save(fig, 'D8_传感器断连.png')


# ---------- 图 I：S4 噪声与估计 ----------
def fig_s4():
    d = load('S4_noise')
    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    ax.plot(d.t, np.rad2deg(d.th), color='#888', lw=0.9, label='真实 θ')
    ax.plot(d.t, np.rad2deg(d.th_hat), color='#2e7d32', lw=0.9, ls='--', label='角度链输出 θhat')
    ax.set_xlim(0, 1.0); ax.grid(alpha=0.3)
    ax.set_xlabel('时间 (s)'); ax.set_ylabel('角度 (°)')
    ax.set_title('S4 角度链（展开+低通）：峰值估计误差 1.48°，RMS 0.08°')
    ax.legend()
    save(fig, 'D9_角度链估计.png')


if __name__ == '__main__':
    fig_structure()
    fig_s1()
    fig_deadzone()
    fig_s8()
    fig_s5()
    fig_s3()
    fig_s7()
    fig_s6b()
    fig_s4()
    print('ALL DONE')
