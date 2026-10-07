/* =====================================================================
 *  src/hal/hal_time.c  ·  TIM2 微秒时间源实现
 *
 *  职责：直接操作 TIM2（PSC/ARR/CNT）做 1us 计数，并把 16 位差值累加进 32 位
 *  依赖：hal_time.h、main.h（HAL 与寄存器宏）
 *  被谁调用：src/app/app_angle.c
 *
 *  逐行对照原 app_angle.c 第 120~141 行，寄存器写值（PSC=71、ARR=0xFFFF）与顺序不变
 * ===================================================================== */
#include "hal_time.h"
#include "main.h"

static uint32_t g_us_high = 0;
static uint16_t g_us_last = 0;

void timebase_init(void)
{
    __HAL_RCC_TIM2_CLK_ENABLE();
    TIM2->PSC = 71;                 /* 72MHz/(71+1) = 1MHz -> 1 格 = 1us */
    TIM2->ARR = 0xFFFF;
    TIM2->EGR = TIM_EGR_UG;
    TIM2->SR  = 0;
    TIM2->CR1 = TIM_CR1_CEN;
    g_us_last = (uint16_t)TIM2->CNT;
    g_us_high = 0;
}

uint32_t micros(void)
{
    uint16_t now = (uint16_t)TIM2->CNT;
    int16_t  d   = (int16_t)(now - g_us_last);
    if (d > 0) { g_us_high += (uint32_t)d; g_us_last = now; }
    return g_us_high;
}
