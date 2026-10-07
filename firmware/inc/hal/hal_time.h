/* =====================================================================
 *  inc/hal/hal_time.h  ·  TIM2 微秒时间源（1us 一格，软件扩展到 32 位）
 *
 *  职责：把 16 位 TIM2 计数器拼成 32 位微秒计数，给节拍与窗口用
 *  依赖：HAL（TIM2 寄存器）+ main.h；不依赖任何其它模块
 *  被谁调用：src/app/app_angle.c（app_angle_init 初始化；loop/fast_task 读 micros）
 *
 *  与原 app_angle.c 的对应：原第 120~141 行
 *  注意：micros() 只在主循环里被调用（原版也是在主循环），不在中断里调用
 * ===================================================================== */
#ifndef __HAL_TIME_H
#define __HAL_TIME_H

#include <stdint.h>

/* 上电时调用一次：开 TIM2 时钟、1us 分频、自由运行（原第 124~134 行） */
void     timebase_init(void);

/* 32 位微秒时间戳（单调递增，回绕周期约 71 分钟，与原版一致） */
uint32_t micros(void);

#endif /* __HAL_TIME_H */
