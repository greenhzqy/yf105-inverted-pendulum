# -*- coding: utf-8 -*-
"""angle_core 的 Python 参考实现（逐行对应原版 app_angle.c 的 fast_task）。

用途：与编译出来的 C 版本做**逐拍数值比对**。两边都按同一份原始代码搬，
所以能抓住"搬错行"这类错误（C 手写最容易出错的正是这类问题）。

原版对应关系（D:\\harness\\学业\\yf105招新\\25级-倒立摆实物\\firmware\\app_angle.c）：
    266-291 行  角度链 + 毛刺剔除 + 测速
    294-299 行  记录（本模块不含，见 recorder）
"""
import numpy as np

CNT_PER_REV = 4096.0
HALF_REV = 2048
ANG_JUMP_MAX = 150
LPF_ALPHA = 0.35
DPS_MAX = 1500.0


def angle_delta(diff):
    if diff > HALF_REV:
        diff -= int(CNT_PER_REV + 0.5)
    if diff < -HALF_REV:
        diff += int(CNT_PER_REV + 0.5)
    return diff


def angle_is_glitch(diff, jump_max=ANG_JUMP_MAX):
    return diff > jump_max or diff < -jump_max


def angle_lpf_step(y, x, alpha=LPF_ALPHA):
    return y + alpha * (x - y)


def angle_speed(th_f, th_prev_f, dt_us, dps_max=DPS_MAX):
    if dt_us <= 0.0:
        return 0.0
    dps = (th_f - th_prev_f) * (360.0 / CNT_PER_REV) * (1000000.0 / dt_us)
    return float(np.clip(dps, -dps_max, dps_max))


class RefAngleCore:
    """与 C 结构体 angle_core_t 一一对应。"""

    def __init__(self, alpha=LPF_ALPHA, jump_max=ANG_JUMP_MAX, dps_max=DPS_MAX):
        self.alpha, self.jump_max, self.dps_max = alpha, jump_max, dps_max
        self.raw = 0
        self.unwrap = 0.0
        self.th_f = 0.0
        self.th_prev_f = 0.0
        self.zero_f = 0.0
        self.dps = 0.0
        self.bad_total = 0
        self.bad_run = 0
        self.started = 0
        self.valid_last = 0

    def seed(self, raw):
        self.raw = raw
        self.unwrap = float(raw)
        self.th_f = self.unwrap
        self.th_prev_f = self.th_f
        self.started = 1
        self.valid_last = 1

    def step(self, raw, dt_us):
        raw = int(raw) & 0xFFFF
        if not self.started:
            self.seed(raw)
            self.bad_run = 0
            return
        diff = angle_delta(raw - self.raw)
        if angle_is_glitch(diff, self.jump_max):
            self.bad_run += 1
            if self.bad_run >= 3:
                self.raw = raw
            self.bad_total += 1
            self.valid_last = 0
            return
        self.bad_run = 0
        self.raw = raw
        self.unwrap += float(diff)
        self.th_f = angle_lpf_step(self.th_f, self.unwrap, self.alpha)
        if dt_us > 0.0:
            self.dps = angle_speed(self.th_f, self.th_prev_f, dt_us, self.dps_max)
        self.th_prev_f = self.th_f
        self.valid_last = 1

    def deg(self):
        return (self.th_f - self.zero_f) * (360.0 / CNT_PER_REV)

    def set_zero(self):
        self.zero_f = self.th_f
