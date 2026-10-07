/* =====================================================================
 *  src/core/recorder.c  ·  环形缓冲实现（零硬件依赖，可在 PC 上编译）
 *
 *  职责：存样本、维护写指针/总数、为 dump 提供折回下标与字段读取
 *  依赖：recorder.h
 *  被谁调用：src/app/app_angle.c
 *
 *  逐行对照原 app_angle.c 第 108~116 / 293~299 / 445~446 / 505~509 行
 *  ★ 刻意保留原版的类型：rec_ang 是 uint16_t（负角度依旧按原版回绕显示），
 *    不做任何"顺手修正"，保证 dump 输出与原版逐字一致
 * ===================================================================== */
#include "recorder.h"

static uint16_t rec_ang[DSIZE];
static int16_t  rec_dps[DSIZE];
static uint8_t  rec_duty[DSIZE];
static uint16_t rec_idx = 0;                /* 下一个写入位置 */
static uint16_t rec_cnt = 0;                /* 已写入总数（最多 DSIZE） */
static uint32_t rec_total = 0;              /* 累计写入（含覆盖） */

void rec_push(int16_t ang10, int16_t dps, uint8_t duty)
{
    rec_ang[rec_idx]  = (uint16_t)ang10;    /* 0.1 度单位（原第 294 行的 (int16_t) 结果） */
    rec_dps[rec_idx]  = dps;
    rec_duty[rec_idx] = duty;
    rec_idx++; if (rec_idx >= DSIZE) rec_idx = 0;
    if (rec_cnt < DSIZE) rec_cnt++;
    rec_total++;
}

uint16_t rec_count(void) { return rec_cnt; }
uint16_t rec_head(void)  { return rec_idx; }
uint32_t rec_total_n(void) { return rec_total; }

void rec_dump_begin(uint16_t *start, uint16_t *n)
{
    *start = (rec_cnt < DSIZE) ? 0 : rec_idx;   /* 最老的那个样本 */
    *n     = rec_cnt;
}

uint16_t rec_dump_k(uint16_t start, uint16_t i)
{
    uint16_t k = (uint16_t)(start + i);
    if (k >= DSIZE) k = (uint16_t)(k - DSIZE);
    return k;
}

uint16_t rec_ang_at(uint16_t k)  { return rec_ang[k]; }
int16_t  rec_dps_at(uint16_t k)  { return rec_dps[k]; }
uint8_t  rec_duty_at(uint16_t k) { return rec_duty[k]; }
