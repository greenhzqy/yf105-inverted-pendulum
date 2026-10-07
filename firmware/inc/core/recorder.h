/* =====================================================================
 *  inc/core/recorder.h  ·  1200 样本环形缓冲 + dump 取点
 *
 *  职责：把每拍的角度/速度/占空比存进环形缓冲，并为命令 d 的 dump 泵提供取点
 *  依赖：只依赖 <stdint.h>，零硬件、零 HAL 调用（可在 PC 上编译）
 *  被谁调用：src/app/app_angle.c（fast_task 存点、'd' 命令开 dump、dump 泵取点）
 *
 *  与原 app_angle.c 的对应：原第 108~116 行（缓冲与下标）+ 第 293~299 行（存点）
 *  DSIZE=1200 与原版同值
 * ===================================================================== */
#ifndef __RECORDER_H
#define __RECORDER_H

#include <stdint.h>

#define DSIZE 1200            /* 环形缓冲样本数（2.4s @500Hz） */

/* 存一个样本（原第 294~299 行）。ang10 = 0.1 度单位的角度计数，dps = deg/s，duty = 0~100 */
void     rec_push(int16_t ang10, int16_t dps, uint8_t duty);

/* 已写入总数（最多 DSIZE）= 原 rec_cnt */
uint16_t rec_count(void);

/* 下一个写入位置 = 原 rec_idx（也是"最老样本"的位置，当缓冲已满时） */
uint16_t rec_head(void);

/* 累计写入（含覆盖）= 原 rec_total（函数名带 _n 以免与同名静态变量重名） */
uint32_t rec_total_n(void);

/* 命令 d：定起止（原第 445~446 行）。*start = 最老样本下标，*n = 样本数 */
void     rec_dump_begin(uint16_t *start, uint16_t *n);

/* dump 泵取点：把 (start + i) 折回环内（原第 505~506 行） */
uint16_t rec_dump_k(uint16_t start, uint16_t i);

/* 三个字段的读接口（保持原文件的类型：角度是 uint16_t，负数按原版一样回绕） */
uint16_t rec_ang_at(uint16_t k);
int16_t  rec_dps_at(uint16_t k);
uint8_t  rec_duty_at(uint16_t k);

#endif /* __RECORDER_H */
