# -*- coding: utf-8 -*-
"""电机直驱摆（转轴直驱）闭环仿真 —— 与实物同结构、同采样节拍。

与"小车倒立摆"的区别（这是本项目实物的真实结构）：
  实物：电机轴 → 联轴器 → 法兰 → 摆杆，**基座固定**，电机力矩直接作用在摆杆转轴上；
        没有小车、没有轨道。状态只有 2 个：摆角 θ、角速度 ω；控制量是**电机力矩**。

动力学（θ=0 为直立，逆时针为正）：
    I·θ̈ = k_g·sinθ − b·θ̇ − τ_c·tanh(θ̇/ε) − K_m·(duty/100)
  其中 k_g = (m_s·L/2 + m_t·L)·g 为重力矩系数，K_m 为 100% 占空比对应的力矩。
  **符号约定与实物实测一致：正的占空比 → θ 减小**（见 S3 笔记：
  "符号关系：正占空比（dir=+1，AIN1 高）→ θ 减小"）。

输出：results_direct/*.csv + metrics_direct.json
"""
import json
import os
import numpy as np
import pandas as pd
from dataclasses import dataclass, field, replace

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'results_direct')
os.makedirs(OUT, exist_ok=True)

# =====================================================================
# 1. 参数
# =====================================================================
@dataclass
class RigParams:
    """实物参数（雪糕棍摆杆 + 尖端配重 + JGB37-520 减速电机）。
    标注 [设定] 的为按笔记数量级设定、待实测修正的值。"""
    L: float = 0.20            # 摆杆长度 m（两根雪糕棍叠粘 + 接长到约 20cm）[设定]
    m_s: float = 0.004         # 杆身质量 kg（约 2g/根 × 2）[设定]
    m_t: float = 0.004         # 尖端配重 kg（2~3 颗 M4 螺母）[设定]
    g: float = 9.81
    b: float = 1.0e-5          # 转轴黏性摩擦 N·m·s/rad [设定]
    tau_c: float = 5.0e-3      # 库仑/静摩擦 N·m（减速箱输出轴"几~十几 mN·m"，取 5）[设定]
    eps: float = 0.005         # tanh 平滑尺度 rad/s（动摩擦过渡）
    K_m: float = 0.08          # 100% 占空比对应的电机力矩 N·m [设定：需 > 重力矩]

    @property
    def I(self):
        """绕转轴转动惯量：均匀杆(端部为轴) + 尖端质点。"""
        return self.m_s * self.L**2 / 3.0 + self.m_t * self.L**2

    @property
    def k_g(self):
        """重力矩系数 = 重力矩幅值 = (m_s·L/2 + m_t·L)·g"""
        return (self.m_s * self.L / 2.0 + self.m_t * self.L) * self.g

    def summary(self):
        return dict(I=self.I, k_g=self.k_g, tau_c=self.tau_c, K_m=self.K_m,
                    gravity_over_friction=self.k_g / self.tau_c)


@dataclass
class SimParams:
    Ts: float = 0.002          # 控制周期 2ms（500Hz）
    tau_a: float = 0.015       # 电机力矩一阶滞后 s（电流环+机械）
    duty_max: float = 100.0    # 占空比饱和 %
    t_end: float = 6.0
    seed: int = 2026


@dataclass
class SensorParams:
    """AS5600：12bit 绝对角度 + 安装/量化噪声 + 可编程故障。"""
    quant: float = 2.0 * np.pi / 4096.0     # 0.0879° / count
    sigma: float = 2.0 * np.pi / 4096.0     # 噪声标准差 ≈ 1 count
    glitch_p: float = 0.004                 # 单拍毛刺概率（实测 bad 计数来源）
    glitch_amp: float = np.deg2rad(8.0)     # 毛刺幅度（>13°的由阈值剔除）


@dataclass
class CtrlParams:
    # PD：u = kp·θ + kd·ω（% / rad, % / (rad/s)），符号按实物实测（+duty → θ 减小）
    kp: float = 60.0
    kd: float = 8.0
    # 积分项（克服库仑摩擦死区 → 消除稳态误差）；带抗饱和
    ki: float = 100.0
    z_max: float = 0.5           # 积分限幅
    # LQR 加权（2 状态）：角度权重高，控制代价小
    q_theta: float = 40.0
    q_omega: float = 1.0
    R: float = 0.02
    # 能量起摆（渐进泵摆：每次小幅加能，摆幅逐次增大，多次后荡到直立再捕获）
    k_sw: float = 4.5e4        # 能量泵增益（%/J）；高增益确保每次摆动净增能量
    E_capture: float = -0.25   # 捕获能量阈值 J（相对直立 E*=0）
    theta_cap: float = np.deg2rad(45.0)   # 捕获窗口：摆幅过 45° 且能量够时捕获
    omega_cap: float = 25.0
    duty_sw: float = 26.0      # 起摆占空比限幅 %（限制单次加能 → 需多次摆动逐步荡高）
    ramp_s: float = 0.5        # 切换后限幅放松时间


@dataclass
class SafetyParams:
    theta_warn: float = np.deg2rad(35.0)
    theta_fault: float = np.deg2rad(60.0)   # 平衡中超角 → 急停
    duty_fault: float = 95.0                # 占空比接近饱和
    duty_fault_n: int = 30                  # 连续 N 拍 → 电流/堵转异常
    sensor_bad_n: int = 20                  # 连续 N 拍无效 → 断连
    watchdog_ms: float = 20.0


# =====================================================================
# 2. 被控对象
# =====================================================================
class Plant:
    def __init__(self, p: RigParams):
        self.p = p
        self.theta = 0.0
        self.omega = 0.0
        self.tau_act = 0.0        # 执行器实际力矩（一阶滞后）
        self.time = 0.0

    def reset(self, theta=0.0, omega=0.0):
        self.theta, self.omega, self.tau_act, self.time = theta, omega, 0.0, 0.0

    def _tau_friction(self, omega):
        p = self.p
        return p.b * omega + p.tau_c * np.tanh(omega / p.eps)

    def _deriv(self, theta, omega, tau_m, tau_f):
        p = self.p
        acc = (p.k_g * np.sin(theta) - tau_f - tau_m) / p.I
        return omega, acc

    def step(self, dt, duty):
        """执行 dt：占空比 → 一阶滞后力矩 → (静摩擦锁定 / RK4 积分)。"""
        p = self.p
        duty_lim = float(np.clip(duty, -100.0, 100.0))
        tau_cmd = p.K_m * duty_lim / 100.0          # +duty → 力矩指向 −θ
        self.tau_act += (tau_cmd - self.tau_act) * dt / 0.015
        th, om = self.theta, self.omega
        tau = self.tau_act
        # 驱动力矩（不含摩擦）：重力矩 − 电机力矩
        driving = p.k_g * np.sin(th) - tau
        # ---- 静摩擦（stiction）：速度≈0 且驱动力矩不足以克服静摩擦 → 锁住 ----
        if abs(om) < 1.0e-3 and abs(driving) <= p.tau_c:
            self.omega = 0.0
            self.duty_cmd = duty_lim
            self.time += dt
            return self.theta, self.omega
        # ---- 动摩擦 + RK4 ----
        tau_f = self._tau_friction(om)
        k1 = self._deriv(th, om, tau, tau_f)
        k2 = self._deriv(th + 0.5 * dt * k1[0], om + 0.5 * dt * k1[1], tau, tau_f)
        k3 = self._deriv(th + 0.5 * dt * k2[0], om + 0.5 * dt * k2[1], tau, tau_f)
        k4 = self._deriv(th + dt * k3[0], om + dt * k3[1], tau, tau_f)
        self.theta = th + dt * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]) / 6.0
        self.omega = om + dt * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]) / 6.0
        self.time += dt
        self.duty_cmd = duty_lim
        return self.theta, self.omega


# =====================================================================
# 3. 传感器 + 角度链（与固件同结构）
# =====================================================================
class Sensor:
    def __init__(self, sp: SensorParams, rng):
        self.sp, self.rng = sp, rng
        self.fault_mode, self.t0, self.dur = None, -1.0, 0.0
        self.last = 0.0

    def schedule(self, mode, t0, dur):
        self.fault_mode, self.t0, self.dur = mode, t0, dur

    def measure(self, theta, t):
        sp = self.sp
        v = theta + self.rng.normal(0, sp.sigma)
        v = np.round(v / sp.quant) * sp.quant
        if self.rng.random() < sp.glitch_p:
            v += self.rng.normal(0, sp.glitch_amp)
        if self.fault_mode and self.t0 <= t < self.t0 + self.dur:
            if self.fault_mode == 'dropout':
                v = np.nan
            elif self.fault_mode == 'frozen':
                v = self.last
        if np.isfinite(v):
            self.last = v
        return v


class AngleChain:
    """回绕修正 → 展开 → 低通 → 差分 → 限幅 + 单拍毛刺剔除（对应固件 app_angle.c）。"""
    def __init__(self, sp: SensorParams, Ts, lpf_alpha=0.35, jump_max=np.deg2rad(13.2),
                 dps_max=1500.0):
        self.quant_full = 2 * np.pi
        self.Ts = Ts
        self.alpha = lpf_alpha
        self.jump_max = jump_max
        self.dps_max = dps_max
        self.unwrap = 0.0
        self.th_f = 0.0
        self.prev_f = 0.0
        self.raw_prev = None
        self.dps = 0.0
        self.bad = 0

    def reset(self, theta0=0.0):
        self.unwrap = theta0
        self.th_f = theta0
        self.prev_f = theta0
        self.raw_prev = theta0
        self.dps = 0.0
        self.bad = 0

    def update(self, raw, dt):
        if not np.isfinite(raw):
            self.bad += 1
            return self.th_f, self.dps, False
        if self.raw_prev is None:
            self.reset(raw)
            return self.th_f, self.dps, True
        diff = raw - self.raw_prev
        if diff > np.pi:
            diff -= self.quant_full
        elif diff < -np.pi:
            diff += self.quant_full
        if abs(diff) > self.jump_max:          # 毛刺剔除：保持旧值
            self.bad += 1
            return self.th_f, self.dps, False
        self.raw_prev = raw
        self.unwrap += diff                     # 先展开
        self.th_f += self.alpha * (self.unwrap - self.th_f)   # 再低通
        if dt > 0:
            dps = (self.th_f - self.prev_f) / dt
            dps = float(np.clip(dps, -self.dps_max, self.dps_max))
            self.dps = dps
        self.prev_f = self.th_f
        return self.th_f, self.dps, True


# =====================================================================
# 4. 控制器
# =====================================================================
def design_lqr(rig: RigParams, ctrl: CtrlParams, Ts):
    """2 状态 LQR：线性化（忽略摩擦）后 ZOH 离散 + DARE。
    θ̈ = (k_g·θ − K_m·duty/100)/I  →  A=[[0,1],[k_g/I,0]], B=[[0],[-K_m/(100·I)]]"""
    from scipy.linalg import solve_discrete_are
    I, k_g, K_m = rig.I, rig.k_g, rig.K_m
    A = np.array([[0.0, 1.0], [k_g / I, 0.0]])
    B = np.array([[0.0], [-K_m / (100.0 * I)]])
    n = 2
    M = np.zeros((n + 1, n + 1))
    M[:n, :n] = A * Ts
    M[:n, n:] = B * Ts
    Md = np.eye(n + 1)
    P = np.eye(n + 1)
    for k in range(1, 25):
        P = P @ M / k
        Md = Md + P
    Phi, Gamma = Md[:n, :n], Md[:n, n:]
    Q = np.diag([ctrl.q_theta, ctrl.q_omega]) * Ts
    R = np.array([[ctrl.R * Ts]])
    Pk = solve_discrete_are(Phi, Gamma, Q, R)
    K = np.linalg.solve(R + Gamma.T @ Pk @ Gamma, Gamma.T @ Pk @ Phi).ravel()
    return K


class PDController:
    def __init__(self, cp: CtrlParams):
        self.kp, self.kd = cp.kp, cp.kd

    def compute(self, th, om):
        # 实物实测符号：+duty → θ 减小；要压住 +θ 就得给 +duty
        return self.kp * th + self.kd * om


class PIDController:
    """PD + 积分：积分项累积到足以跨过静摩擦死区，从而消除稳态误差。
    抗饱和：输出接近限幅且积分仍在加深同方向时冻结积分。"""
    def __init__(self, cp: CtrlParams, duty_max=100.0):
        self.kp, self.kd, self.ki = cp.kp, cp.kd, cp.ki
        self.z_max = cp.z_max
        self.duty_max = duty_max
        self.z = 0.0

    def reset(self):
        self.z = 0.0

    def compute(self, th, om, Ts):
        u_pd = self.kp * th + self.kd * om
        u = u_pd + self.ki * self.z
        sat = abs(u) > 0.95 * self.duty_max
        if sat and np.sign(self.ki * self.z) == np.sign(u) and abs(self.z) > 1e-6:
            pass                                  # 冻结积分（anti-windup）
        else:
            self.z += th * Ts
        self.z = float(np.clip(self.z, -self.z_max, self.z_max))
        return u_pd + self.ki * self.z


class LQRController:
    def __init__(self, K):
        self.K = K

    def compute(self, th, om):
        return -float(self.K @ np.array([th, om]))


class EnergySwingup:
    """转轴力矩泵能量：dE/dt = τ_motor·ω，取 τ 与 ω 同相即可给能量。
    E = 0.5·I·ω² + k_g·(cosθ−1)，直立 E*=0、下垂 E=−2k_g。"""
    def __init__(self, rig: RigParams, cp: CtrlParams):
        self.rig, self.cp = rig, cp

    def energy(self, th, om):
        return 0.5 * self.rig.I * om**2 + self.rig.k_g * (np.cos(th) - 1.0)

    def compute(self, th, om):
        cp = self.cp
        E = self.energy(th, om)
        # τ_motor 需与 ω 同相；τ_motor = −K_m·duty/100 ⇒ duty ∝ −ω
        duty = -cp.k_sw * (0.0 - E) * np.tanh(om / 0.5)
        return float(np.clip(duty, -cp.duty_sw, cp.duty_sw)), E


class Machine:
    """模式：PUMP（力矩泵摆）/ BALANCE（PD 或 LQR）/ FAULT（锁存断电）。"""
    def __init__(self, rig, cp, ctrl='pd', start='BALANCE'):
        self.rig, self.cp, self.ctrl = rig, cp, ctrl
        self.pd = PDController(cp)
        self.pid = PIDController(cp)
        self.lqr = LQRController(design_lqr(rig, cp, 0.002))
        self.swing = EnergySwingup(rig, cp)
        self.mode = start
        self.t_capture = 0.0
        self.events = []
        self.kick_until = -1.0
        self.kick_sign = 1.0
        self.stagnant = 0.0

    def log(self, t, code, msg):
        self.events.append((t, code, msg))

    def compute(self, th, om, t):
        if self.mode == 'FAULT':
            return 0.0, 'FAULT'
        if self.mode == 'PUMP':
            E = self.swing.energy(th, om)
            if t < self.kick_until:
                duty = self.kick_sign * self.cp.duty_sw * 0.6
            else:
                if abs(om) < 0.3:
                    self.stagnant += 0.002
                else:
                    self.stagnant = 0.0
                if self.stagnant > 0.25:
                    self.kick_until = t + 0.3
                    self.kick_sign = 1.0 if om >= 0 else -1.0
                    self.stagnant = 0.0
                    self.log(t, 'KICK', '唤醒踢（打破停滞）')
                    duty = self.kick_sign * self.cp.duty_sw * 0.6
                else:
                    duty, _ = self.swing.compute(th, om)
            ok = (E >= self.cp.E_capture and abs(th) < self.cp.theta_cap
                  and abs(om) < self.cp.omega_cap)
            if ok:
                self.mode = 'BALANCE'
                self.t_capture = t
                self.pid.reset()
                self.log(t, 'CATCH_OK', f'捕获成功 E={E:.3f} J, θ={np.rad2deg(th):.1f}°')
            return duty, 'PUMP'
        # BALANCE
        ramp = np.clip(0.25 + 0.75 * (t - self.t_capture) / self.cp.ramp_s, 0.25, 1.0)
        if self.ctrl == 'pd':
            base = self.pd.compute(th, om)
        elif self.ctrl == 'pid':
            base = self.pid.compute(th, om, 0.002)
        else:
            base = self.lqr.compute(th, om)
        duty = base * ramp
        if abs(th) > np.deg2rad(35.0):
            self.mode = 'PUMP'
            self.log(t, 'LOSE_BALANCE', f'失衡回摆起 |θ|={np.rad2deg(th):.1f}°')
        return float(np.clip(duty, -100.0, 100.0)), self.mode


# =====================================================================
# 5. 安全监控（监测与执行分离；故障锁存）
# =====================================================================
class Safety:
    def __init__(self, sp: SafetyParams):
        self.sp = sp
        self.fault = None
        self.events = []
        self.n_bad = 0
        self.n_over = 0
        self.watchdog_ok = True

    def check(self, duty, valid, t, mode):
        sp = self.sp
        ok = True
        if not valid:
            self.n_bad += 1
            self.events.append((t, 'SENSOR_INVALID', '采样无效'))
        else:
            self.n_bad = 0
        if self.n_bad >= sp.sensor_bad_n:
            self.fault, ok = 'FAULT_SENSOR', False
            self.events.append((t, 'SENSOR_FAULT', '传感器断连/冻结，停机'))
        over = abs(duty) >= sp.duty_fault
        self.n_over = self.n_over + 1 if over else 0
        if self.n_over >= sp.duty_fault_n:
            self.fault, ok = 'FAULT_DUTY', False
            self.events.append((t, 'DUTY_FAULT', f'占空比持续饱和 {abs(duty):.0f}%'))
        if not self.watchdog_ok:
            self.fault, ok = 'FAULT_WATCHDOG', False
            self.events.append((t, 'WATCHDOG_FAULT', '控制任务超时未喂狗'))
            self.watchdog_ok = True
        return ok


# =====================================================================
# 6. 闭环
# =====================================================================
class Loop:
    def __init__(self, rig: RigParams, sim: SimParams, sp: SensorParams, cp: CtrlParams,
                 sad: SafetyParams, ctrl='pd', start='BALANCE', theta0=0.0, omega0=0.0):
        self.rig, self.sim, self.sp, self.sad = rig, sim, sp, sad
        self.plant = Plant(rig)
        self.plant.reset(theta0, omega0)
        self.sensor = Sensor(sp, np.random.default_rng(sim.seed))
        self.chain = AngleChain(sp, sim.Ts)
        self.chain.reset(theta0)
        self.machine = Machine(rig, cp, ctrl=ctrl, start=start)
        self.safety = Safety(sad)
        self.duty_prev = 0.0
        self.R = {k: [] for k in ('t', 'th', 'om', 'th_meas', 'th_hat', 'om_hat',
                                  'duty', 'mode', 'valid', 'E')}

    def step(self, t, duty_override=None, freeze=False):
        th_meas = self.sensor.measure(self.plant.theta, t)
        th_hat, om_hat, valid = self.chain.update(th_meas, self.sim.Ts)
        if freeze:
            duty, mode = self.duty_prev, self.machine.mode
            if t >= self.freeze_t + self.sad.watchdog_ms / 1000.0:
                self.safety.watchdog_ok = False
        elif duty_override is not None:
            duty, mode = float(duty_override), self.machine.mode
        else:
            duty, mode = self.machine.compute(th_hat, om_hat, t)
        duty = float(np.clip(duty, -self.sim.duty_max, self.sim.duty_max))
        ok = self.safety.check(duty, valid, t, mode)
        if not ok:
            mode = 'FAULT'
            duty = 0.0
        duty_apply = 0.0 if not ok else self.duty_prev      # 1 拍计算延迟
        self.plant.step(self.sim.Ts, duty_apply)
        self.duty_prev = duty
        self._record(t, mode, th_meas, th_hat, om_hat, duty_apply, valid)
        return duty

    def _record(self, t, mode, th_meas, th_hat, om_hat, duty_apply, valid):
        R = self.R
        R['t'].append(t)
        R['th'].append(self.plant.theta)
        R['om'].append(self.plant.omega)
        R['th_meas'].append(th_meas if np.isfinite(th_meas) else np.nan)
        R['th_hat'].append(th_hat)
        R['om_hat'].append(om_hat)
        R['duty'].append(duty_apply)
        R['mode'].append(mode)
        R['valid'].append(1 if valid else 0)
        R['E'].append(self.machine.swing.energy(self.plant.theta, self.plant.omega))

    @property
    def events(self):
        return sorted(list(self.machine.events) + list(self.safety.events), key=lambda e: e[0])

    def arrays(self):
        return {k: np.array(v) for k, v in self.R.items()}


def default_cfg():
    return RigParams(), SimParams(), SensorParams(), CtrlParams(), SafetyParams()


def run(name, fn):
    R, ev, met = fn()
    df = pd.DataFrame(R)
    df.to_csv(os.path.join(OUT, name + '.csv'), index=False)
    if ev:
        with open(os.path.join(OUT, name + '_events.json'), 'w', encoding='utf-8') as f:
            json.dump([{'t': round(e[0], 4), 'code': e[1], 'msg': e[2]} for e in ev],
                      f, ensure_ascii=False, indent=1)
    return met


# =====================================================================
# 7. 场景
# =====================================================================
def metrics(R, t_dist=0.0, band=np.deg2rad(2.0)):
    t, th, om, duty = R['t'], R['th'], R['om'], R['duty']
    m = t >= t_dist
    idx = np.where(m)[0]
    settle = np.inf
    if len(idx):
        ok = np.abs(th) < band
        for i in idx:
            if ok[i] and ok[idx[idx >= i]].all():
                settle = float(t[i] - t_dist)
                break
    return dict(settle=settle,
                peak_theta_deg=float(np.rad2deg(np.max(np.abs(th[m])))),
                rms_duty=float(np.sqrt(np.mean(duty[m]**2))),
                peak_duty=float(np.max(np.abs(duty[m]))),
                final_theta_deg=float(np.rad2deg(th[-1])),
                steady_theta_deg=float(np.rad2deg(np.mean(th[t >= max(t_dist, t[-1]-1.0)]))),
                final_omega=float(om[-1]))


def _run_base(rig, sim, sp, cp, sad, t_end, theta0=0.0, omega0=0.0,
              ctrl='pd', start='BALANCE', impulse=None, override=None,
              sensor_fault=None, freeze_win=None, seed=None):
    if seed is not None:
        sim = replace(sim, seed=seed)
    loop = Loop(rig, sim, sp, cp, sad, ctrl=ctrl, start=start, theta0=theta0, omega0=omega0)
    if sensor_fault:
        loop.sensor.schedule(*sensor_fault)
    n = int(round(t_end / sim.Ts))
    for k in range(n):
        t = k * sim.Ts
        if impulse and abs(t - impulse[0]) < sim.Ts / 2:
            loop.plant.omega += impulse[1]
        ov = None
        if override is not None:
            lo, hi, val = override
            if lo <= t < hi:
                ov = val
        if freeze_win and freeze_win[0] <= t < freeze_win[1]:
            loop.freeze_t = freeze_win[0]
            loop.step(t, freeze=True)
        else:
            loop.step(t, duty_override=ov)
    return loop


def s1_offset(ctrl='pd'):
    rig, sim, sp, cp, sad = default_cfg()
    loop = _run_base(rig, sim, sp, cp, sad, 6.0, theta0=np.deg2rad(10.0), ctrl=ctrl)
    R = loop.arrays()
    return R, loop.events, metrics(R)


def s2_impulse():
    rig, sim, sp, cp, sad = default_cfg()
    t0, dv = 2.0, 2.0
    loop = _run_base(rig, sim, sp, cp, sad, 6.0, theta0=0.0, impulse=(t0, dv), ctrl='pid')
    R = loop.arrays()
    return R, loop.events, metrics(R, t_dist=t0)


def s3_mismatch():
    rig, sim, sp, cp, sad = default_cfg()
    rig2 = replace(rig, m_s=rig.m_s * 1.5, m_t=rig.m_t * 1.5, L=rig.L * 1.2,
                   tau_c=rig.tau_c * 2.0)
    loop = _run_base(rig2, sim, sp, cp, sad, 6.0, theta0=np.deg2rad(10.0), ctrl='pid')
    R = loop.arrays()
    return R, loop.events, metrics(R)


def s4_noise():
    rig, sim, sp, cp, sad = default_cfg()
    loop = _run_base(rig, sim, sp, cp, sad, 3.0, theta0=np.deg2rad(10.0), ctrl='pid')
    R = loop.arrays()
    err = np.rad2deg(R['th_hat'] - R['th'])
    met = dict(peak_est_err_deg=float(np.max(np.abs(err))),
               rms_est_err_deg=float(np.sqrt(np.mean(err**2))))
    return R, loop.events, met


def s5_swingup():
    rig, sim, sp, cp, sad = default_cfg()
    loop = _run_base(rig, sim, sp, cp, sad, 20.0, theta0=np.pi, ctrl='pid', start='PUMP')
    R = loop.arrays()
    return R, loop.events, metrics(R)


def s6_safety():
    rig, sim, sp, cp, sad = default_cfg()
    out = {}
    # a 摆角超限：强扰动把摆角推过 60° 硬限 → 急停
    loop = _run_base(rig, sim, sp, cp, sad, 4.0, theta0=np.deg2rad(10.0),
                     impulse=(2.0, 60.0), ctrl='pid')
    out['a_theta'] = (loop.arrays(), loop.events)
    # b 传感器断连 80ms
    loop = _run_base(rig, sim, sp, cp, sad, 4.0, theta0=np.deg2rad(10.0),
                     sensor_fault=('dropout', 2.0, 0.08), ctrl='pid')
    out['b_sensor'] = (loop.arrays(), loop.events)
    # c 占空比饱和（堵转/电流异常）
    loop = _run_base(rig, sim, sp, cp, sad, 4.0, theta0=np.deg2rad(10.0),
                     override=(2.0, 2.1, 100.0), ctrl='pid')
    out['c_duty'] = (loop.arrays(), loop.events)
    # d 看门狗
    loop = _run_base(rig, sim, sp, cp, sad, 4.0, theta0=np.deg2rad(10.0),
                     freeze_win=(2.0, 2.03), ctrl='pid')
    out['d_watchdog'] = (loop.arrays(), loop.events)
    return out


def s7_sampling():
    rig, sim, sp, cp, sad = default_cfg()
    rows = []
    for Ts_ms in [1, 2, 4, 6, 8, 10, 14, 18, 22, 26, 30, 36, 44]:
        sim2 = replace(sim, Ts=Ts_ms / 1000.0)
        loop = Loop(rig, sim2, sp, cp, sad, ctrl='pd', theta0=np.deg2rad(10.0))
        n = int(round(5.0 / sim2.Ts))
        ok = True
        for k in range(n):
            loop.step(k * sim2.Ts)
            if abs(loop.plant.theta) > np.deg2rad(35.0):
                ok = False
                break
        R = loop.arrays()
        rows.append(dict(Ts_ms=Ts_ms, stable=bool(ok),
                         peak_theta_deg=None if not ok else float(np.rad2deg(np.max(np.abs(R['th'])))),
                         final_theta_deg=None if not ok else float(np.rad2deg(R['th'][-1]))))
    return rows


def s8_compare():
    out = {}
    for name, ctrl in (('PD', 'pd'), ('LQR', 'lqr')):
        R, ev, met = s1_offset(ctrl=ctrl)
        out[name] = (R, ev, met)
    return out


def s9_integral():
    """摩擦死区补偿对照：PD（无积分，靠 PD 力矩越过静摩擦）vs PID（积分累积跨死区）。"""
    out = {}
    for name, ctrl in (('PD', 'pd'), ('PID', 'pid')):
        rig, sim, sp, cp, sad = default_cfg()
        loop = _run_base(rig, sim, sp, cp, sad, 6.0, theta0=np.deg2rad(2.0), ctrl=ctrl)
        R = loop.arrays()
        out[name] = (R, loop.events, metrics(R))
    return out


def run_all():
    res = {}
    rows = {}
    for name, fn in [('S1_PID', lambda: s1_offset('pid')),
                     ('S2_impulse', s2_impulse),
                     ('S3_mismatch', s3_mismatch),
                     ('S4_noise', s4_noise)]:
        res[name] = run(name, fn)
    res['S5_swingup'] = run('S5_swingup', s5_swingup)
    for k, (R, ev) in s6_safety().items():
        run('S6_' + k, lambda R=R, ev=ev: (R, ev, None))
    rows = s7_sampling()
    with open(os.path.join(OUT, 'S7_sampling.json'), 'w') as f:
        json.dump(rows, f, indent=1)
    for k, (R, ev, met) in s8_compare().items():
        res['S8_' + k] = run('S8_' + k, lambda R=R, ev=ev, met=met: (R, ev, met))
    for k, (R, ev, met) in s9_integral().items():
        res['S9_' + k] = run('S9_' + k, lambda R=R, ev=ev, met=met: (R, ev, met))
    with open(os.path.join(OUT, 'metrics_direct.json'), 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    return res, rows


if __name__ == '__main__':
    rig = RigParams()
    print('被控对象参数:', json.dumps(rig.summary(), indent=1))
    res, rows = run_all()
    print(json.dumps(res, ensure_ascii=False, indent=1))
