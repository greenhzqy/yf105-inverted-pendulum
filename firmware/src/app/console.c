/* =====================================================================
 *  src/app/console.c  ·  串口输出实现（双缓冲 + IT / 阻塞两模式）
 *
 *  职责：vsnprintf 到 txb[tx_which] -> 阻塞 HAL_UART_Transmit 或 HAL_UART_Transmit_IT
 *  依赖：console.h、main.h（HAL UART）
 *  被谁调用：src/app/app_angle.c、src/drivers/as5600.c；TxCpltCallback 由 HAL 中断调用
 *
 *  逐行对照原 app_angle.c 第 101~106 行 + 第 143~167 行
 *  ★ 刻意保留原版顺序与副作用：先格式化到 txb[tx_which]，再判断 tx_busy 丢帧，
 *    再 tx_which ^= 1 后发送。忙时格式化会覆盖在途缓冲——这是原版既有行为，
 *    本次重构不做"修正"，保证时序与丢帧统计与原版一致
 * ===================================================================== */
#include "console.h"
#include "main.h"
#include <stdio.h>
#include <stdarg.h>

extern UART_HandleTypeDef huart1;

static char     txb[2][TXBUF];
static volatile uint8_t tx_busy = 0;
static uint8_t  tx_which = 0;
static uint8_t  g_nonblock = 1;
static uint32_t g_sent = 0, g_drop = 0;

void log_printf(const char *fmt, ...)
{
    char *buf = txb[tx_which];
    va_list ap; int n;
    va_start(ap, fmt);
    n = vsnprintf(buf, TXBUF, fmt, ap);
    va_end(ap);
    if (n <= 0) return;
    if (n > TXBUF - 1) n = TXBUF - 1;

    if (!g_nonblock) {
        HAL_UART_Transmit(&huart1, (uint8_t *)buf, (uint16_t)n, 200);
        g_sent++;
        return;
    }
    if (tx_busy) { g_drop++; return; }
    tx_which ^= 1;
    tx_busy = 1; g_sent++;
    HAL_UART_Transmit_IT(&huart1, (uint8_t *)buf, (uint16_t)n);
}

void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART1) tx_busy = 0;
}

uint8_t  console_tx_busy(void)              { return tx_busy; }
uint8_t  console_get_nonblock(void)         { return g_nonblock; }
void     console_set_nonblock(uint8_t nb)   { g_nonblock = nb; }
uint32_t console_sent(void)                 { return g_sent; }
uint32_t console_drop(void)                 { return g_drop; }
