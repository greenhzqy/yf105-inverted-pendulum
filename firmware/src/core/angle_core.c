/* =====================================================================
 *  src/core/angle_core.c  ·  角度链纯算法实现（零硬件依赖，可在 PC 上编译）
 *
 *  职责：回绕修正 -> 毛刺剔除 -> 连续角度累加 -> 一阶低通 -> 差分测速限幅
 *  依赖：angle_core.h、<stdlib.h>（abs）。不包含 main.h，不访问任何寄存器
 *  被谁调用：src/app/app_angle.c 的 fast_task()
 *
 *  逐行对照原 app_angle.c 第 265~291 行；每一步的运算顺序、类型、常量都不改动
 * ===================================================================== */
#include "angle_core.h"
#include <stdlib.h>

void angle_core_init(angle_state_t *s, uint16_t raw0)
{
    s->raw      = raw0;
    s->unwrap   = (float)raw0;
    s->lpf      = s->unwrap;
    s->lpf_prev = s->lpf;
}

int16_t angle_unwrap_update(uint16_t raw, uint16_t raw_prev)
{
    int16_t diff = (int16_t)raw - (int16_t)raw_prev;
    if (diff > 2048)  diff -= 4096;              /* 回绕修正 */
    if (diff < -2048) diff += 4096;
    return diff;
}

uint8_t angle_spike_reject(int16_t diff)
{
    return (uint8_t)(abs(diff) > ANG_JUMP_MAX);
}

float angle_lpf_step(float y, float x)
{
    return y + LPF_ALPHA * (x - y);
}

float angle_speed_est(float lpf, float lpf_prev, uint32_t dt_us)
{
    float dps = (lpf - lpf_prev) * (360.0f / 4096.0f) * (1000000.0f / (float)dt_us);
    if (dps >  DPS_MAX) dps =  DPS_MAX;
    if (dps < -DPS_MAX) dps = -DPS_MAX;
    return dps;
}

int angle_step(angle_state_t *s, uint16_t raw, uint32_t dt_us)
{
    int16_t diff = angle_unwrap_update(raw, s->raw);

    if (angle_spike_reject(diff)) {              /* 毛刺：这一拍丢弃 */
        s->bad_run++;
        if (s->bad_run >= 3) s->raw = raw;       /* 连续 3 拍都"跳"：说明是真的大动作，接受它 */
        s->bad_total++;
        return 0;
    }

    s->bad_run = 0;
    s->raw = raw;
    s->unwrap += (float)diff;                    /* 先把回绕修正后的增量累加 -> 连续角度 */
    s->lpf = angle_lpf_step(s->lpf, s->unwrap);  /* 再对连续角度做一阶低通 */

    /* 速度：滤波后差分 -> deg/s（系数按实测 dt 归一化） */
    if (dt_us > 0) {
        s->dps = (int16_t)angle_speed_est(s->lpf, s->lpf_prev, dt_us);
    }
    s->lpf_prev = s->lpf;
    return 1;
}

void angle_mark_read_fail(angle_state_t *s)
{
    s->bad_total++;                              /* I2C 读失败也算无效 */
}
