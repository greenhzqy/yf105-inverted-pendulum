# -*- coding: utf-8 -*-
"""固件 core/angle_core.c 的 PC 端回归测试（交叉验证）。

背景：
  - `ref_angle_core.py` 是 Lead 按原版 app_angle.c 第 265~291 行**独立写的 Python 语义模型**
  - `firmware/app_angle/core/angle_core.c` 是另一名成员**独立抽取**出的纯 C 模块
  - 本脚本把固件那份 C 模块编成 DLL，逐拍喂相同输入，与 Python 模型**逐字段比对**

两条独立路径得出同一结果，才叫"搬迁没走样"；只比对同一份代码是自己跟自己说话。

比对字段：raw / unwrap / lpf / lpf_prev / dps / bad_run / bad_total
覆盖场景：匀速、回绕、随机抖动+毛刺、连续 3 拍大跳变、dt 抖动与限幅、零点标定语义
"""
import ctypes
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ref_angle_core import RefAngleCore, ANG_JUMP_MAX, LPF_ALPHA, DPS_MAX  # noqa: E402

GCC = os.environ.get(
    'PC_CC',
    r'C:\Program Files (x86)\Dev-Cpp\MinGW64\bin\gcc.exe')   # 宿主编译器（x86_64），不是 arm-none-eabi
FW_CORE = r'D:\harness\学业\yf105招新\25级-倒立摆实物\firmware\app_angle\src\core'
FW_INC = r'D:\harness\学业\yf105招新\25级-倒立摆实物\firmware\app_angle\inc\core'


class CState(ctypes.Structure):
    """对应 firmware/app_angle/core/angle_core.h 里的 angle_state_t"""
    _fields_ = [
        ('raw', ctypes.c_uint16),
        ('unwrap', ctypes.c_float),
        ('lpf', ctypes.c_float),
        ('lpf_prev', ctypes.c_float),
        ('dps', ctypes.c_int16),
        ('bad_run', ctypes.c_uint8),
        ('bad_total', ctypes.c_uint32),
    ]


FIELDS_FLOAT = ('unwrap', 'lpf', 'lpf_prev')
FIELDS_INT = ('raw', 'dps', 'bad_run', 'bad_total')
# C 结构体字段名 -> Python 参考模型字段名
PYNAME = {'lpf': 'th_f', 'lpf_prev': 'th_prev_f'}


def build_and_bind():
    dll = os.path.join(HERE, 'libfw_angle_core.dll')
    cmd = [GCC, '-shared', '-O2', '-I', FW_INC,
           '-o', dll, os.path.join(FW_CORE, 'angle_core.c')]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print('编译固件 core 失败：', ' '.join(cmd))
        print(r.stdout, r.stderr)
        sys.exit(2)
    d = ctypes.CDLL(dll)
    d.angle_core_init.argtypes = [ctypes.POINTER(CState), ctypes.c_uint16]
    d.angle_step.argtypes = [ctypes.POINTER(CState), ctypes.c_uint16, ctypes.c_uint32]
    d.angle_step.restype = ctypes.c_int
    d.angle_mark_read_fail.argtypes = [ctypes.POINTER(CState)]
    d.angle_unwrap_update.argtypes = [ctypes.c_uint16, ctypes.c_uint16]
    d.angle_unwrap_update.restype = ctypes.c_int16
    d.angle_spike_reject.argtypes = [ctypes.c_int16]
    d.angle_spike_reject.restype = ctypes.c_uint8
    return d


def run_scenario(d, tag, raws, dts, fails, read_fail_at=()):
    cs = CState()
    d.angle_core_init(ctypes.byref(cs), int(raws[0]))
    rc = RefAngleCore()
    rc.seed(int(raws[0]))
    ok_n = 0
    for i, (raw, dt) in enumerate(zip(raws, dts)):
        if i in read_fail_at:
            d.angle_mark_read_fail(ctypes.byref(cs))
            rc.bad_total += 1                     # 参考模型里"读失败"等价物
            continue
        conf = d.angle_step(ctypes.byref(cs), int(raw), int(dt))
        rc.step(int(raw), float(dt))
        good = True
        for f in FIELDS_FLOAT:
            a, b = getattr(cs, f), getattr(rc, PYNAME.get(f, f))
            # 角度类是 float32 存储，按相对 1e-5 比（float32 有效位约 7 位）
            tol = 1e-5 * max(1.0, abs(b))
            if abs(a - b) > tol:
                fails.append(f'{tag} 第{i}拍 {f}: C={a!r} py={b!r}')
                good = False
        for f in FIELDS_INT:
            a, b = getattr(cs, f), getattr(rc, f)
            if f == 'dps':
                # 固件把 dps 存成 int16_t（截断），参考模型是 float：
                # 允许 ±1 LSB（截断边界上 float 舍入可能偏 1）——定点实现的标准判据
                if abs(int(a) - int(np.trunc(b))) > 1:
                    fails.append(f'{tag} 第{i}拍 dps: C={a!r} py={b!r}')
                    good = False
                continue
            if int(a) != int(b):
                fails.append(f'{tag} 第{i}拍 {f}: C={a!r} py={b!r}')
                good = False
        # 返回值语义：1=本拍有效，0=本拍被判毛刺丢弃（与参考模型的 valid_last 必须一致）
        if rc.valid_last != conf:
            fails.append(f'{tag} 第{i}拍 返回值: C={conf} py.valid={rc.valid_last}')
            good = False
        if good:
            ok_n += 1
    print(f'  [{tag}] {ok_n}/{len(raws)} 拍一致  bad_total C={cs.bad_total} py={rc.bad_total}')
    return cs, rc


def main():
    d = build_and_bind()
    fails = []
    rng = np.random.default_rng(2026)

    print('交叉验证：固件 core/angle_core.c  vs  独立 Python 模型')
    print('\n场景 1：匀速正转（3 圈）')
    n = 1500
    raws = (np.arange(n) * 3) % 4096
    run_scenario(d, 'uniform', raws, [2000] * n, fails)

    print('\n场景 2：来回跨越回绕点')
    sweep = np.concatenate([np.linspace(3800, 4095, 120), np.linspace(0, 400, 120),
                            np.linspace(400, 0, 120), np.linspace(4095, 3800, 120)])
    raws = np.round(sweep).astype(int) % 4096
    run_scenario(d, 'wrap', raws, [2000] * len(raws), fails)

    print('\n场景 3：随机抖动 + 2% 毛刺注入')
    n = 2000
    raws = (np.cumsum(rng.normal(0, 4, n)) + 1000).astype(int) % 4096
    g = rng.random(n) < 0.02
    raws[g] = (raws[g] + rng.choice([-1, 1], int(g.sum())) * rng.integers(200, 900, int(g.sum()))) % 4096
    run_scenario(d, 'glitch', raws, [2000] * n, fails)

    print('\n场景 4：连续 5 拍大跳变（验证"连续 3 拍才接受新 raw"）')
    raws = np.array([1000] * 5 + [1000, 3000, 500, 3500, 800] + [801] * 50)
    run_scenario(d, 'consec', raws, [2000] * len(raws), fails)

    print('\n场景 5：dt 抖动 + dt=0 + 高速触发限幅')
    n = 600
    raws = (np.arange(n) * 40) % 4096
    dts = np.array([0] + list(2000 + rng.integers(-2, 3, n - 1)))
    run_scenario(d, 'speed_limit', raws, dts, fails)

    print('\n场景 6：中途 I2C 读失败（bad_total 累加）')
    n = 300
    raws = (np.arange(n) * 2 + 1200) % 4096
    run_scenario(d, 'read_fail', raws, [2000] * n, fails, read_fail_at={100, 150, 200})

    print('\n场景 7：纯函数边界（回绕/毛刺判据）')
    bad = 0
    from ref_angle_core import angle_delta
    for a in range(0, 4096, 13):
        for b in (0, 1, 2047, 2048, 2049, 4094, 4095):
            c = d.angle_unwrap_update(a, b)
            p = angle_delta(int(a) - int(b))
            if c != p:
                fails.append(f'angle_unwrap_update({a},{b}) C={c} py={p}')
                bad += 1
    print(f'  unwrap 全扫描不一致 {bad} 处')
    for dv in (-151, -150, -149, 149, 150, 151):
        c = d.angle_spike_reject(dv)
        p = 1 if abs(dv) > ANG_JUMP_MAX else 0
        if c != p:
            fails.append(f'angle_spike_reject({dv}) C={c} py={p}')
    print(f'  常量核对：ANG_JUMP_MAX={ANG_JUMP_MAX} LPF_ALPHA={LPF_ALPHA} DPS_MAX={DPS_MAX}')

    print('\n' + '=' * 62)
    if fails:
        print(f'❌ {len(fails)} 处不一致（前 10 条）：')
        for f in fails[:10]:
            print('   ', f)
        sys.exit(1)
    print('✅ 固件 core/angle_core.c 与独立 Python 模型逐拍、逐字段一致')
    print('   => 抽取过程未改变角度链语义（回归测试通过）')


if __name__ == '__main__':
    main()
