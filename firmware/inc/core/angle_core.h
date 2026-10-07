/* =====================================================================
 *  inc/core/angle_core.h  ·  角度链纯算法：回绕展开 / 毛刺剔除 / 一阶低通 / 测速
 *
 *  职责：给"一整拍角度处理"一个不碰硬件的实现（输入 raw 计数，输出连续角度与 dps）
 *  依赖：只依赖 <stdint.h>/<stdlib.h>，零硬件、零 HAL 调用 -> 可在 PC 上编译单测
 *  被谁调用：src/app/app_angle.c 的 fast_task()（每 2ms 一拍）
 *
 *  与原 app_angle.c 的对应：原第 265~291 行"② 角度链 + ③ 速度"
 *  常量数值逐字保留：ANG_JUMP_MAX=150 / LPF_ALPHA=0.35f / DPS_MAX=1500.0f
 * ===================================================================== */
#ifndef __ANGLE_CORE_H
#define __ANGLE_CORE_H

#include <stdint.h>

/* ---- 与原 app_angle.c 同名同值（原第 57~60 行） ---- */
#define ANG_JUMP_MAX 150       /* 单拍跳变上限（计数，150 约 13.2 度）：超过判为毛刺，丢弃该拍 */
#define LPF_ALPHA    0.35f     /* 一阶低通系数（0~1）：越小越平滑、越滞后 */
#define DPS_MAX      1500.0f   /* 速度限幅 deg/s */

/* 角度链的全部状态（对应原文件的 g_raw/g_unwrap/g_th_f/g_th_prev_f/g_dps/g_bad_run/g_bad_total） */
typedef struct {
    uint16_t raw;        /* 当前有效原始值（计数） */
    float    unwrap;     /* 连续角度（计数）：把回绕增量累加起来的"真角度" */
    float    lpf;        /* 滤波后角度（计数，展开量） */
    float    lpf_prev;   /* 上一拍滤波值（测速用） */
    int16_t  dps;        /* 速度 deg/s */
    uint8_t  bad_run;    /* 连续无效拍数 */
    uint32_t bad_total;  /* 累计无效拍（毛刺 + 读失败） */
} angle_state_t;

/* 上电初始化：原第 369~373 行（读到 RAWANGLE 成功后调用） */
void    angle_core_init(angle_state_t *s, uint16_t raw0);

/* 回绕修正：由 raw 与上一拍 raw 求最短增量（原第 267~270 行） */
int16_t angle_unwrap_update(uint16_t raw, uint16_t raw_prev);

/* 毛刺判据：|diff| > ANG_JUMP_MAX 返回 1（原第 271 行） */
uint8_t angle_spike_reject(int16_t diff);

/* 一阶低通一步：y + LPF_ALPHA * (x - y)（原第 279 行） */
float   angle_lpf_step(float y, float x);

/* 测速 + 限幅：滤波后差分 -> deg/s（原第 281~285 行） */
float   angle_speed_est(float lpf, float lpf_prev, uint32_t dt_us);

/* 一整拍：返回 1 = 本拍有效（已更新角度与速度）；返回 0 = 本拍被丢弃（毛刺） */
int     angle_step(angle_state_t *s, uint16_t raw, uint32_t dt_us);

/* I2C 读失败（也算一拍无效，原第 290 行） */
void    angle_mark_read_fail(angle_state_t *s);

#endif /* __ANGLE_CORE_H */
