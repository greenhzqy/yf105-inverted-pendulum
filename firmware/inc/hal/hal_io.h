/* =====================================================================
 *  inc/hal/hal_io.h  ·  电机执行器引脚层：PB0 PWM(CH3) 占空比 + PA0/PA1/PA2
 *
 *  职责：只做"写寄存器/写引脚"这一件事，不含任何状态与判断
 *  依赖：HAL（htim3、GPIO）+ main.h；不依赖任何其它模块
 *  被谁调用：src/app/app_angle.c 的 motor_apply() / motor_enable() / app_angle_init()
 *
 *  与原 app_angle.c 的对应：原第 195~220 行 motor_apply/motor_enable 中的"硬件动作部分"
 *  ★ 占空比钳位、g_duty/g_dir 记账、方向判断仍在 app 层（保证与原版执行顺序一致）
 * ===================================================================== */
#ifndef __HAL_IO_H
#define __HAL_IO_H

#include <stdint.h>

/* 启动 TIM3 CH3 PWM（原第 343 行 HAL_TIM_PWM_Start） */
void hal_io_motor_pwm_start(void);

/* 设定 PWM 占空比（0~100，%）：内部按 arr 换算成比较值（原第 200~202 行） */
void hal_io_motor_duty(uint32_t duty_pct);

/* 方向：dir > 0 -> AIN1=1/AIN2=0；dir <= 0 -> AIN1=0/AIN2=1（原第 206~212 行） */
void hal_io_motor_dir(int8_t dir);

/* 两个方向脚都拉低（原第 204~205 行，duty==0 时的滑行） */
void hal_io_motor_coast(void);

/* STBY 使能脚（原第 218 行） */
void hal_io_motor_stby(uint8_t en);

/* 给开机 banner 用的 TIM3 参数（原第 358 行的 htim3.Init.Prescaler / Period） */
uint32_t hal_io_pwm_psc(void);
uint32_t hal_io_pwm_arr(void);

#endif /* __HAL_IO_H */
