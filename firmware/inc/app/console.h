/* =====================================================================
 *  inc/app/console.h  ·  串口输出：双缓冲 + 非阻塞 IT 发送（可切回阻塞）
 *
 *  职责：格式化一行并送 UART；忙时丢帧并计数，绝不阻塞快节拍
 *  依赖：HAL UART + main.h；不依赖任何其它模块（被各层复用，视为通用输出工具）
 *  被谁调用：src/app/app_angle.c（状态行/命令回显/dump）、src/drivers/as5600.c（i2c_scan 打印）
 *
 *  与原 app_angle.c 的对应：原第 101~106 行（缓冲与计数）+ 第 143~167 行（log_printf + TxCplt）
 *  TXBUF=320 与原版同值
 * ===================================================================== */
#ifndef __CONSOLE_H
#define __CONSOLE_H

#include <stdint.h>

#define TXBUF 320             /* 单行缓冲上限（与原版同值） */

/* 与原版同名同行为：vsnprintf -> 阻塞发送 或 IT 发送（忙则丢帧计数） */
void     log_printf(const char *fmt, ...);

/* dump 泵用：当前是否有 IT 发送在途（原 tx_busy） */
uint8_t  console_tx_busy(void);

/* 'b' 命令用：阻塞开关的读写（原 g_nonblock） */
uint8_t  console_get_nonblock(void);
void     console_set_nonblock(uint8_t nonblock);

/* 计数（原 g_sent / g_drop；g_drop 会出现在状态行与 DUMP END 里） */
uint32_t console_sent(void);
uint32_t console_drop(void);

#endif /* __CONSOLE_H */
