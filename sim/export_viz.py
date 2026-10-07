# -*- coding: utf-8 -*-
"""把直驱摆仿真结果导出为可视化 JSON（下采样到约 40fps 显示）。

角度约定（让动画直观，符合「从圆心下最低点 → 最高点」）：
  - 仿真 θ：0=直立(最高)，180°=下垂(最低)，正方向由符号约定决定
  - 可视化角 a：**0° = 下垂最低点，180° = 直立最高点**
    由 θ 折算：最低点(θ=180°)→a=0，直立(θ=0/360°)→a=180
  屏幕画法：a=0 杆指向正下，a=180 杆指向正上。
"""
import json
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'results_direct')
VIZ = os.path.join(HERE, 'viz')
os.makedirs(VIZ, exist_ok=True)

STRIDE = 12   # 2ms×12 ≈ 24ms/帧 ≈ 40fps 显示


def load(name):
    d = pd.read_csv(os.path.join(RES, name + '.csv'))
    return d.iloc[::STRIDE]


def th_to_a_cont(th_rad):
    """连续可视化角（用于起摆场景）：0=下垂最低点，180=直立最高点。
    用未回绕的连续 θ(rad)：a=(θ−π)·180/π。θ=π→0(低)，θ=0→180(直立)；平滑。"""
    return round((float(th_rad) - np.pi) * 180.0 / np.pi, 2)


def th_to_a_mod(th_rad):
    """模回绕可视化角（用于小角度平衡/死区场景）：0=最低点，180=直立。
    只对贴近直立的小角度有意义：θ≈0 → a≈180。"""
    d = float(np.degrees(th_rad)) % 360.0
    return round((d - 180.0) % 360.0, 2)


def pack_arr(d, f): return [round(float(x), 3) for x in d[f].tolist()]


def build_scene(d, extra_E=False, continuous=False):
    th_rad = d['th'].tolist()
    conv = th_to_a_cont if continuous else th_to_a_mod
    scene = {
        "t": pack_arr(d, 't'),
        "a": [conv(th) for th in th_rad],          # 0=最低, 180=直立（或连续）
        "du": [round(float(np.degrees(th)) % 360.0, 2) for th in th_rad],  # 距直立(小角度场景用)
        "duty": pack_arr(d, 'duty'),
    }
    if extra_E:
        scene["E"] = pack_arr(d, 'E')
        scene["mode"] = [str(x) for x in d['mode'].tolist()]
    return scene


data = {
    "swingup": {
        "title": "能量起摆：从圆心下最低点(0°) → 荡到最高点(180°·直立)并保持",
        "note": "角度从最低点算起：0°=最低点(杆垂在正下)，180°=最高点(杆竖直立起)",
        **build_scene(load('S5_swingup'), extra_E=True, continuous=True),
    },
    "balance": {
        "title": "平衡 + 脉冲扰动（2s 时刻给 2 rad/s 冲击，1.19s 恢复）",
        "note": "0°=最低点，180°=直立；摆杆在直立附近小幅平衡，受扰后自动回正",
        **build_scene(load('S2_impulse'), extra_E=True, continuous=True),
    },
    "deadzone": {
        "title": "摩擦死区：同样靠近直立(179°)，纯 PD 卡死 vs PID 收敛到直立(180°)",
        "note": "从接近直立的同一位置起步：纯 PD 因力矩压不过静摩擦停在原地；PID 加积分跨过死区回到直立",
        "pd": {**build_scene(load('S9_PD'), continuous=True)},
        "pid": {**build_scene(load('S9_PID'), continuous=True)},
    },
}

with open(os.path.join(VIZ, 'viz_data.json'), 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
print('viz_data.json bytes:', os.path.getsize(os.path.join(VIZ, 'viz_data.json')))
print('frames: swingup=%d balance=%d dz_pd=%d' % (
    len(data['swingup']['t']), len(data['balance']['t']), len(data['deadzone']['pd']['t'])))
