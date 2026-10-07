/* =====================================================================
 *  S2 核心（阅读版）—— 一个"2ms 采集器"的全部本质
 *
 *  这份不参与编译，只为阅读：把 v9 里的 5 处主干抽出来，砍掉统计、命令、
 *  dump、实验开关。读懂这一份 ≈ 读懂了 S2；再回看 v9 就都是"装饰"。
 *
 *  主干 ① 一张 1us 精度的表（TIM2）
 *  主干 ② 主循环里的"硬节拍"（到点了吗）
 *  主干 ③ 快任务（每 2ms 干一次的活）
 *  主干 ④ 角度链（回绕修正 → 连续角度 → 低通 → 毛刺剔除）
 *  主干 ⑤ 速度（滤波后差分 + 限幅）
 * ===================================================================== */
#include "main.h"
#include <string.h>
#include <stdlib.h>

/* ---- 从 CubeMX 生成的 main.c 借来的外设句柄（extern = 借用声明） ---- */
extern I2C_HandleTypeDef  hi2c1;
extern TIM_HandleTypeDef  htim3;
extern UART_HandleTypeDef huart1;

/* ---- 参数：集中放这里，改只改一处 ---- */
#define SAMP_US       2000u    /* 采样周期 2ms = 500Hz */
#define ANG_JUMP_MAX  150      /* 单拍跳变上限（计数）：150 ≈ 13.2°，超过判毛刺 */
#define LPF_ALPHA     0.35f    /* 一阶低通系数：越小越平滑、越滞后 */
#define DPS_MAX       1500.0f  /* 速度限幅 deg/s */

/* ---- 程序的"记忆"（全局变量） ---- */
static uint32_t g_us_high  = 0;      /* micros() 的高位：把 16 位计数器扩成 32 位 */
static uint16_t g_us_last  = 0;
static uint32_t g_tick_next = 0;     /* 下一拍的"理论时刻"（us） */
static uint32_t g_tick_last = 0;     /* 上一拍的"实际时刻"（us） */
static uint16_t g_raw       = 0;     /* 最近一次【有效】的原始角度 0~4095 */
static float    g_unwrap    = 0.0f;  /* ★连续角度（计数）：把增量累加起来，可以到 720°、1080°… */
static float    g_th_f      = 0.0f;  /* 低通之后的角度（计数） */
static float    g_th_prev   = 0.0f;  /* 上一拍的滤波角度（算速度要用） */
static int16_t  g_dps       = 0;     /* 角速度 deg/s */

/* =====================================================================
 *  主干 ①：一张 1us 精度的"表"
 *
 *  为什么不用 HAL_GetTick()？它只有 1ms 分辨率——拿它量 2ms 的节拍，
 *  光量化误差就有 ±50%，测出来的"抖动"全是尺子自己的误差。
 * ===================================================================== */
void timebase_init(void)
{
    __HAL_RCC_TIM2_CLK_ENABLE();
    TIM2->PSC = 71;              /* 72MHz / (71+1) = 1MHz  → 一格 = 1us */
    TIM2->ARR = 0xFFFF;          /* 16 位计数器：每 65.5ms 绕一圈 */
    TIM2->EGR = TIM_EGR_UG;      /* 立刻把 PSC 装载生效 */
    TIM2->CR1 = TIM_CR1_CEN;     /* 启动，自由运行（不开中断） */
    g_us_last = (uint16_t)TIM2->CNT;
    g_us_high = 0;
}

uint32_t micros(void)
{
    uint16_t now = (uint16_t)TIM2->CNT;
    int16_t  d   = (int16_t)(now - g_us_last);          /* 这一圈走了几格 */
    if (d > 0) { g_us_high += (uint32_t)d; g_us_last = now; }   /* 累加到 32 位 */
    return g_us_high;
}
/* ★ 必须"频繁调用"（本项目每圈都调一次），否则 65.5ms 绕圈会被漏掉 */

/* ---- 打印：这里先用最简单的"阻塞版"，而且只放在慢任务里 ---- */
static void log_line(const char *s)
{
    HAL_UART_Transmit(&huart1, (uint8_t *)s, (uint16_t)strlen(s), 200);
}
/* ⚠️ 它是阻塞的：115200 下发一行 135 字符要 12ms —— 等于丢掉 6 拍！
   v9 的解法：HAL_UART_Transmit_IT（中断发送）+ 双缓冲 + 丢帧计数。
   这就是"脚手架"里最值得看的一个。 */

/* =====================================================================
 *  主干 ③④⑤：快任务 —— 每 2ms 干一次的活
 *  dt_us = 这一拍的实际间隔（由主循环量好传进来，不能假设"一定是 2000"）
 * ===================================================================== */
void fast_task(uint32_t dt_us)
{
    uint8_t b[2];

    /* ---------- 主干 ④：角度链 ---------- */
    /* 超时只给 2ms：快任务里的超时也必须短，不然一次失败就毁掉好几拍 */
    if (HAL_I2C_Mem_Read(&hi2c1, (0x36 << 1), 0x0C, I2C_MEMADD_SIZE_8BIT, b, 2, 2) == HAL_OK) {
        uint16_t raw  = (uint16_t)(((b[0] & 0x0F) << 8) | b[1]);   /* 12 位拼接 */
        int16_t  diff = (int16_t)raw - (int16_t)g_raw;

        /* ★ 回绕修正：差值绝对值超过半圈，说明其实是"跨过了 0/4096 边界" */
        if (diff >  2048) diff -= 4096;
        if (diff < -2048) diff += 4096;

        if (abs(diff) > ANG_JUMP_MAX) {
            /* 单拍跳太多 → 判为毛刺：这一拍**什么都不做**
               （g_raw / g_unwrap 都保持旧值 —— 宁可少一拍，不可喂进一个假值） */
        } else {
            g_raw     = raw;
            g_unwrap += (float)diff;                        /* ★ 累加 → 连续角度 */
            g_th_f   += LPF_ALPHA * (g_unwrap - g_th_f);    /* ★ 在连续角度上做低通 */

            /* ---------- 主干 ⑤：速度 = 滤波后角度差分 / 实测时间 ---------- */
            if (dt_us > 0) {
                float dps = (g_th_f - g_th_prev) * (360.0f / 4096.0f)   /* 计数 → 度 */
                          * (1000000.0f / (float)dt_us);                /* 每 us → 每秒 */
                if (dps >  DPS_MAX) dps =  DPS_MAX;     /* 限幅兜底 */
                if (dps < -DPS_MAX) dps = -DPS_MAX;
                g_dps = (int16_t)dps;
            }
            g_th_prev = g_th_f;
        }
    }
    /* v9 在这一行后面还会把样本写进环形缓冲（脚手架） */
}

/* =====================================================================
 *  主干 ②：主循环里的"硬节拍"—— 到点了吗？
 * ===================================================================== */
void app_loop(void)
{
    uint32_t now = micros();

    if ((int32_t)(now - g_tick_next) >= 0) {          /* 到点（int32 比较 → 回绕安全） */
        uint32_t dt = now - g_tick_last;              /* 实测间隔：给速度估计用 */
        g_tick_last = now;

        g_tick_next += SAMP_US;                       /* ★ 累加推进：长期不漂 */
        if ((int32_t)(now - g_tick_next) >= 0) {      /* 已经晚了一整拍以上 */
            g_tick_next = now + SAMP_US;              /* 落后太多 → 重新对齐（v9 还会 over++） */
        }
        fast_task(dt);
    }

    /* ---- 慢任务：低频的活放这儿（打印、命令处理、换档…） ----
       注意：慢任务和快节拍**共用同一圈时间**，所以它里面的活也必须短。
       这就是"打印会吃掉节拍"的根源：慢任务里一句 12ms 的阻塞打印 = 丢 6 拍。 */
}

/* ---- 开机：先起表，再起外设 ---- */
void app_init(void)
{
    timebase_init();                                  /* 主干 ①：先有表 */
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_3);         /* 占空比 0 → 电机不动 */
    HAL_UART_Receive_IT(&huart1, &rx, 1);             /* 串口收命令（中断方式） */
    HAL_NVIC_EnableIRQ(USART1_IRQn);

    g_tick_last = micros();
    g_tick_next = g_tick_last + SAMP_US;              /* 第一拍的时刻 */
}

/* =====================================================================
 *  读完自检（能答上来 = 真懂了）
 *  1. 为什么 micros() 要用"累加"的方式把 16 位扩成 32 位？不累加会怎样？
 *  2. g_tick_next += SAMP_US 和 g_tick_next = micros() 有什么区别？
 *     为什么前者"不漂"？
 *  3. 毛刺那一拍为什么"什么都不做"，而不是把 raw 也更新掉？
 *  4. 为什么低通滤波要放在 g_unwrap（连续角度）上，而不是直接滤 raw？
 *  5. dt_us 为什么用"实测值"而不是写死 2000？
 * ===================================================================== */
