/* =====================================================================
 *  app_motor.h  ·  S1 电机测试（数字 -> 力）
 *  用法：本文件与 app_motor.c 属于"用户代码"，不放进 main.c，
 *        靠 CubeMX 的 USER CODE 区挂进去（重新生成代码也不会被覆盖）。
 * ===================================================================== */
#ifndef __APP_MOTOR_H
#define __APP_MOTOR_H

#include "main.h"

/* 初始化：启动 PWM、打开串口接收中断、打印启动信息（不阻塞） */
void app_motor_init(void);

/* 主循环：必须被 main() 的 while(1) 反复调用（内部非阻塞） */
void app_motor_loop(void);

#endif /* __APP_MOTOR_H */
