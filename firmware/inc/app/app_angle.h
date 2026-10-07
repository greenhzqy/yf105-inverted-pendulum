/* =====================================================================
 *  inc/app/app_angle.h  ·  对外接口：只有 init 与 loop 两个函数
 *
 *  职责：给 CubeMX 生成的 main.c 用的门面（main.c 只认这两个名字）
 *  依赖：main.h（HAL 类型）
 *  被谁调用：Core/Src/main.c 的 USER CODE 区（Include + 2 + 3 三处）
 *
 *  与原 app_angle.h 完全一致（函数原型、头文件保护名都不变，方便原地替换）
 * ===================================================================== */
#ifndef __APP_ANGLE_H
#define __APP_ANGLE_H

#include "main.h"

void app_angle_init(void);
void app_angle_loop(void);

#endif /* __APP_ANGLE_H */
