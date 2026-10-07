/* =====================================================================
 *  app_angle.c  ·  v11：S2 的 2ms 节拍 + 角度链 + 速度 + 记录
 *               v10 加"定值脉冲"命令 p（符号预验证）
 *               v11 加"慢转"命令 w（让电机自己转一圈）+ 状态行增加 |B| 的 lo/hi 统计
 *               v12 修"串口命令有时收不到"：加 ORE 错误回调重新武装 + 慢任务兜底轮询 RXNE，
 *                   状态行增加 rx=/cmd=/rxerr= 三个诊断计数
 *
 *  S2 四件事（部件图见 学习笔记/学习记录/S2 · 固定采样节拍.md）：
 *   ① 2ms 硬节拍（TIM2 微秒时间源，v6 起）+ 节拍实测
 *   ② 角度链：读 -> 毛刺剔除 -> 一阶低通
 *   ③ 速度：滤波后差分 + 限幅（治假尖峰）
 *   ④ 数据记录：环形缓冲 + 命令 d 一次性 dump（非阻塞发送，不拖累节拍）
 *
 *  串口（115200）：
 *    状态行：每 500ms 一行 ST ...（低频，不刷屏）
 *    命令：m=电机轮播 r=换向 s=停 z=零点 q=静音 i=扫总线 k=hello
 *          d=dump 数据(CSV)  f=实验：打印塞进快节拍  b=实验：阻塞/非阻塞发送
 *     ★ v10 新增：p=定值脉冲（p20 / p-20 / p0），给 300ms 就自动停 —— 符号预验证 / 测死区用
 *     ★ v11 新增：w=慢转（w15 / w-15 / w0），常转、最长 30s 自动停 —— 让电机自己转一圈查 |B|
 *                状态行尾部 lo=/hi= ：从上次发 w/p 起 |B| 的最小/最大值（磁铁装得正不正，看它）
 *     ★ v12 新增：状态行尾部 rx=<收到字节数> cmd=<解出命令数> rxerr=<串口出错次数>
 *                收到命令数不动 = 接收断了；字节数在涨但命令数不涨 = 少了回车换行
 *  dump 输出格式：i,th_deg,dps,duty    （每行一个样本，直接用 Excel/脚本画图）
 * ===================================================================== */
#include "app_angle.h"
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <stdlib.h>

extern I2C_HandleTypeDef hi2c1;
extern TIM_HandleTypeDef htim3;
extern UART_HandleTypeDef huart1;

#define AS5600_ADDR     (0x36 << 1)
#define REG_STATUS      0x0Bu
#define REG_RAWANGLE    0x0Cu
#define REG_AGC         0x1Au
#define REG_MAGNITUDE   0x1Bu

#define AIN1_PORT GPIOA
#define AIN1_PIN  GPIO_PIN_0
#define AIN2_PORT GPIOA
#define AIN2_PIN  GPIO_PIN_1
#define STBY_PORT GPIOA
#define STBY_PIN  GPIO_PIN_2

#define SAMP_US     2000u      /* ★ 采样周期 2ms = 500Hz */
#define STEP_MS     3000u      /* 电机换档周期 */
#define PULSE_MS     300u      /* ★ v10 定值脉冲持续时间：符号预验证给 20% 持续 0.3s */
#define WALK_MS      30000u    /* ★ v11 慢转最长持续时间（到点自动停，防止忘了关） */
#define WALK_DUTY_MAX 40       /* ★ v11 慢转占空比上限（保护电机/驱动） */
#define WIN_US      500000u    /* 状态行/统计窗口 500ms */
#define LVL_N       (sizeof(LEVELS) / sizeof(LEVELS[0]))

/* ---- ② 角度链 ---- */
#define ANG_JUMP_MAX 150       /* 单拍跳变上限（计数，150 ≈ 13.2°）：超过判为毛刺，丢弃该拍 */
#define LPF_ALPHA    0.35f     /* 一阶低通系数（0~1）：越小越平滑、越滞后 */
/* ---- ③ 速度 ---- */
#define DPS_MAX      1500.0f   /* 速度限幅 deg/s */
/* ---- ④ 记录 ---- */
#define DSIZE        1200      /* 环形缓冲样本数（2.4s @500Hz） */
/* ---- 打印 ---- */
#define TXBUF        320

static volatile uint8_t rx_byte;
static volatile char    cmd_buf[16];
static volatile uint8_t cmd_len = 0, cmd_ready = 0;
static uint32_t g_rx_n = 0, g_cmd_n = 0, g_rx_err = 0;   /* ★ v12 串口诊断计数 */

static uint16_t g_raw = 0, g_zero = 0;      /* 当前有效原始值 / 零点 */
static float    g_th_f = 0.0f, g_th_prev_f = 0.0f;   /* 滤波后角度（计数，展开量） */
static float    g_unwrap = 0.0f;            /* ★ 连续角度（计数）：把回绕增量累加起来的"真角度" */
static float    g_zero_f = 0.0f;            /* 浮点零点（相对连续角度） */
static int16_t  g_dps = 0;
static uint8_t  g_quiet = 0, g_motor = 0, g_enabled = 0;
static int      g_duty = 0, g_dir = 1;
static uint32_t step_t0 = 0;
static uint8_t  lvl = 0;
static const int LEVELS[5] = {0, 25, 50, 75, 100};
static uint8_t  g_pulse = 0;                /* ★ v10 定值脉冲进行中 */
static uint32_t g_pulse_t0 = 0;
static uint8_t  g_walk = 0;                 /* ★ v11 慢转进行中 */
static uint32_t g_walk_t0 = 0;
static uint16_t g_b_min = 0xFFFFu, g_b_max = 0;   /* ★ v11 |B| 的最小/最大值（发 w/p 时清零） */

/* ---- 节拍与统计 ---- */
static uint32_t g_tick_next = 0, g_tick_last = 0;
static uint32_t g_tick_n = 0, g_tick_over = 0;
static uint32_t g_dt_sum = 0, g_dt_max = 0, g_dt_min = 0xFFFFFFFFu;
static uint8_t  g_print_fast = 0;
static uint32_t g_win_t0 = 0;
static uint8_t  g_win_report = 0;
static uint32_t g_sum_n = 0;
static uint8_t  g_dt_skip = 5;

/* ---- 有效性统计 ---- */
static uint32_t g_bad_total = 0;            /* 累计无效拍（毛刺/读失败） */
static uint8_t  g_bad_run = 0;              /* 连续无效拍数 */

/* ---- 打印（阻塞/非阻塞可选） ---- */
static char     txb[2][TXBUF];
static volatile uint8_t tx_busy = 0;
static uint8_t  tx_which = 0;
static uint8_t  g_nonblock = 1;
static uint32_t g_sent = 0, g_drop = 0;

/* ---- ④ 记录缓冲 ---- */
static uint16_t rec_ang[DSIZE];
static int16_t  rec_dps[DSIZE];
static uint8_t  rec_duty[DSIZE];
static uint16_t rec_idx = 0;                /* 下一个写入位置 */
static uint16_t rec_cnt = 0;                /* 已写入总数（最多 DSIZE） */
static uint32_t rec_total = 0;              /* 累计写入（含覆盖） */
static uint8_t  g_dump_run = 0;
static uint16_t g_dump_i = 0, g_dump_start = 0, g_dump_n = 0;

static void log_printf(const char *fmt, ...);

/* ---------- 微秒级时间源：TIM2（1us 一格，软件扩展到 32 位） ---------- */
static uint32_t g_us_high = 0;
static uint16_t g_us_last = 0;

static void timebase_init(void)
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
static inline uint32_t micros(void)
{
    uint16_t now = (uint16_t)TIM2->CNT;
    int16_t  d   = (int16_t)(now - g_us_last);
    if (d > 0) { g_us_high += (uint32_t)d; g_us_last = now; }
    return g_us_high;
}

static void log_printf(const char *fmt, ...)
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

static uint8_t rd_to(uint8_t reg, uint8_t *buf, uint16_t len, uint32_t to_ms)
{
    return (HAL_I2C_Mem_Read(&hi2c1, AS5600_ADDR, reg, I2C_MEMADD_SIZE_8BIT, buf, len, to_ms) == HAL_OK);
}
static uint8_t rd(uint8_t reg, uint8_t *buf, uint16_t len) { return rd_to(reg, buf, len, 20); }

static const char *magnet_str(uint8_t st)
{
    if (st & 0x20) return "OK";
    if (st & 0x10) return "WEAK";
    if (st & 0x08) return "STRONG";
    return "NONE";
}

static void i2c_scan(void)
{
    uint16_t a; uint8_t n = 0;
    log_printf("I2C scan:");
    for (a = 0x08; a <= 0x77; a++) {
        if (HAL_I2C_IsDeviceReady(&hi2c1, (uint16_t)(a << 1), 3, 20) == HAL_OK) { log_printf(" 0x%02X", a); n++; }
    }
    if (!n) log_printf(" (none)");
    log_printf("\r\n");
}

/* ---------------- 电机 ---------------- */
static void motor_apply(int duty, int dir)
{
    uint32_t arr, pulse;
    if (duty < 0)   duty = 0;
    if (duty > 100) duty = 100;
    arr = htim3.Init.Period;
    pulse = (uint32_t)(((arr + 1u) * (uint32_t)duty) / 100u);
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_3, pulse);
    if (duty == 0) {
        HAL_GPIO_WritePin(AIN1_PORT, AIN1_PIN, GPIO_PIN_RESET);
        HAL_GPIO_WritePin(AIN2_PORT, AIN2_PIN, GPIO_PIN_RESET);
    } else if (dir > 0) {
        HAL_GPIO_WritePin(AIN1_PORT, AIN1_PIN, GPIO_PIN_SET);
        HAL_GPIO_WritePin(AIN2_PORT, AIN2_PIN, GPIO_PIN_RESET);
    } else {
        HAL_GPIO_WritePin(AIN1_PORT, AIN1_PIN, GPIO_PIN_RESET);
        HAL_GPIO_WritePin(AIN2_PORT, AIN2_PIN, GPIO_PIN_SET);
    }
    g_duty = duty; g_dir = dir;
}
static void motor_enable(uint8_t en)
{
    g_enabled = en;
    HAL_GPIO_WritePin(STBY_PORT, STBY_PIN, en ? GPIO_PIN_SET : GPIO_PIN_RESET);
    if (!en) motor_apply(0, g_dir);
}

/* ---------------- 状态行（每 500ms 一行，低频） ---------------- */
static void print_status(void)
{
    uint8_t st = 0, agc = 0, mag[2] = {0, 0};
    uint32_t avg = 0;
    rd(REG_STATUS, &st, 1);
    rd(REG_AGC, &agc, 1);
    rd(REG_MAGNITUDE, mag, 2);
    if (g_sum_n > 0) avg = g_dt_sum / g_sum_n;
    {
        uint16_t bv = (uint16_t)(((mag[0] & 0x0F) << 8) | mag[1]);
        if (bv < g_b_min) g_b_min = bv;
        if (bv > g_b_max) g_b_max = bv;
        log_printf("ST th=%6.1f dps=%5d duty=%3d%% mot=%d dir=%+d | dt avg=%4lu max=%5lu min=%4lu n=%lu over=%lu | bad=%lu drop=%lu | MAG=%s |B|=%4u lo=%4u hi=%4u | rx=%lu cmd=%lu rxerr=%lu\r\n",
                   (g_th_f - g_zero_f) * 360.0f / 4096.0f, g_dps, g_duty, g_motor, g_dir,
                   (unsigned long)avg, (unsigned long)g_dt_max,
                   (unsigned long)((g_dt_min == 0xFFFFFFFFu) ? 0 : g_dt_min),
                   (unsigned long)g_tick_n, (unsigned long)g_tick_over,
                   (unsigned long)g_bad_total, (unsigned long)g_drop,
                   magnet_str(st), (unsigned)bv, (unsigned)g_b_min, (unsigned)g_b_max,
                   (unsigned long)g_rx_n, (unsigned long)g_cmd_n, (unsigned long)g_rx_err);
    }
}

/* ---------------- ★ 快任务：每 2ms 一次 ---------------- */
static void fast_task(void)
{
    uint8_t b[2];
    uint32_t t = micros();
    uint32_t dt = t - g_tick_last;
    g_tick_last = t;

    /* 节拍统计 */
    g_tick_n++;
    if (g_dt_skip > 0) {
        g_dt_skip--;
    } else {
        if (dt > g_dt_max) g_dt_max = dt;
        if (dt < g_dt_min) g_dt_min = dt;
        g_dt_sum += dt; g_sum_n++;
    }
    if ((int32_t)(t - g_win_t0) >= (int32_t)WIN_US) g_win_report = 1;

    /* ② 角度链：读 -> 毛刺剔除 -> 低通 */
    if (rd_to(REG_RAWANGLE, b, 2, 2)) {
        uint16_t raw = (uint16_t)(((b[0] & 0x0F) << 8) | b[1]);
        int16_t  diff = (int16_t)raw - (int16_t)g_raw;
        if (diff > 2048)  diff -= 4096;              /* 回绕修正 */
        if (diff < -2048) diff += 4096;
        if (abs(diff) > ANG_JUMP_MAX) {              /* 毛刺：这一拍丢弃 */
            g_bad_run++;
            if (g_bad_run >= 3) g_raw = raw;         /* 连续 3 拍都"跳"：说明是真的大动作，接受它 */
            g_bad_total++;
        } else {
            g_bad_run = 0;
            g_raw = raw;
            g_unwrap += (float)diff;                        /* ★ 先把回绕修正后的增量累加 -> 连续角度 */
            g_th_f += LPF_ALPHA * (g_unwrap - g_th_f);      /* ★ 再对连续角度做一阶低通 */
            /* ③ 速度：滤波后差分 -> deg/s（系数按实测 dt 归一化） */
            if (dt > 0) {
                float dps = (g_th_f - g_th_prev_f) * (360.0f / 4096.0f) * (1000000.0f / (float)dt);
                if (dps >  DPS_MAX) dps =  DPS_MAX;
                if (dps < -DPS_MAX) dps = -DPS_MAX;
                g_dps = (int16_t)dps;
            }
            g_th_prev_f = g_th_f;
        }
    } else {
        g_bad_total++;                               /* I2C 读失败也算无效 */
    }

    /* ④ 记录：每个有效节拍存一个样本 */
    rec_ang[rec_idx]  = (int16_t)((g_th_f - g_zero_f) * 360.0f / 4096.0f * 10.0f);   /* 0.1 度单位 */
    rec_dps[rec_idx]  = g_dps;
    rec_duty[rec_idx] = (uint8_t)g_duty;
    rec_idx++; if (rec_idx >= DSIZE) rec_idx = 0;
    if (rec_cnt < DSIZE) rec_cnt++;
    rec_total++;

    /* ★ 实验开关：打印塞进快节拍（故意拖垮节拍） */
    if (g_print_fast) print_status();
}

void USART1_IRQHandler(void) { HAL_UART_IRQHandler(&huart1); }

/* ★ v12：收字节统一入口（中断和兜底轮询都走这里） */
static void rx_feed(char ch)
{
    g_rx_n++;
    if (ch == '\r' || ch == '\n') { if (cmd_len > 0) { cmd_buf[cmd_len] = 0; cmd_ready = 1; } }
    else if (ch >= 32 && cmd_len < sizeof(cmd_buf) - 1) cmd_buf[cmd_len++] = ch;
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART1) {
        rx_feed((char)rx_byte);
        HAL_UART_Receive_IT(&huart1, (uint8_t *)&rx_byte, 1);
    }
}

/* ★ v12：溢出/帧错误会让 HAL 停掉接收且不再武装 —— 这就是"有时候收得到、有时候收不到"的病根 */
void HAL_UART_ErrorCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART1) {
        volatile uint32_t tmp;
        tmp = huart1.Instance->SR;          /* 读 SR 再读 DR：清 ORE/NE/FE/PE（F1 标准做法） */
        tmp = huart1.Instance->DR;
        (void)tmp;
        huart->ErrorCode = HAL_UART_ERROR_NONE;
        g_rx_err++;
        HAL_UART_Receive_IT(&huart1, (uint8_t *)&rx_byte, 1);   /* 重新武装 */
    }
}

void app_angle_init(void)
{
    uint8_t b[2];
    uint32_t pclk1, timclk;

    motor_enable(0);
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_3);
    HAL_UART_Receive_IT(&huart1, (uint8_t *)&rx_byte, 1);
    HAL_NVIC_SetPriority(USART1_IRQn, 1, 0);
    HAL_NVIC_EnableIRQ(USART1_IRQn);
    timebase_init();
    g_tick_next = micros() + SAMP_US;
    g_tick_last = micros();
    g_win_t0 = micros();
    g_dt_skip = 5;
    step_t0 = HAL_GetTick();

    log_printf("\r\n==== app_angle v12 : tick + angle + p/w cmd + rx fix ====\r\n");
    pclk1  = HAL_RCC_GetPCLK1Freq();
    timclk = ((RCC->CFGR & RCC_CFGR_PPRE1) == RCC_CFGR_PPRE1_DIV1) ? pclk1 : (pclk1 * 2u);
    log_printf("TIM3 psc=%lu arr=%lu -> pwm=%luHz | sample=%luus (%luHz) | win=%lums\r\n",
               (unsigned long)htim3.Init.Prescaler, (unsigned long)htim3.Init.Period,
               (unsigned long)(timclk / ((htim3.Init.Prescaler + 1u) * (htim3.Init.Period + 1u))),
               (unsigned long)SAMP_US, (unsigned long)(1000000u / SAMP_US), (unsigned long)(WIN_US / 1000u));
    log_printf("filter: alpha=0.35 (1st-order LPF) | jump max=%d counts (~13.2deg) | dps limit=%d\r\n",
               ANG_JUMP_MAX, (int)DPS_MAX);
    log_printf("record buffer: %d samples (%.1fs @500Hz)\r\n", DSIZE, (float)DSIZE / 500.0f);

    HAL_Delay(200);
    i2c_scan();
    if (rd(REG_STATUS, b, 1)) log_printf("AS5600 STATUS=0x%02X MAG=%s\r\n", b[0], magnet_str(b[0]));
    else log_printf("AS5600 no answer!\r\n");
    if (rd(REG_RAWANGLE, b, 2)) {
        g_raw = (uint16_t)(((b[0] & 0x0F) << 8) | b[1]);
        g_unwrap = (float)g_raw;
        g_th_f = g_unwrap; g_th_prev_f = g_th_f;
    }
    log_printf("cmd: m r s z q i k | p<pct>=pulse | w<pct>=slow walk | d=dump CSV | f/b = exp\r\n");
    log_printf("tip: send with CR/LF (check 'append newline'); watch RX rx= cmd= rxerr=\r\n");
}

void app_angle_loop(void)
{
    uint32_t now_us = micros();
    uint32_t now_ms = HAL_GetTick();

    /* ================= 快节拍：每 2ms ================= */
    if ((int32_t)(now_us - g_tick_next) >= 0) {
        g_tick_next += SAMP_US;
        if ((int32_t)(now_us - g_tick_next) >= 0) {
            g_tick_over++;
            g_tick_next = now_us + SAMP_US;
        }
        fast_task();
    }

    /* ================= 慢任务 ================= */
    /* ★ v12 兜底：中断万一被卡住，这里直接看 RXNE 标志把字节捞出来 */
    {
        uint8_t got = 0;
        __disable_irq();
        while ((USART1->SR & USART_SR_RXNE) && got < 32) {
            rx_feed((char)(USART1->DR & 0xFF));
            got++;
        }
        __enable_irq();
    }

    if (cmd_ready) {
        char t[16];
        __disable_irq();
        memcpy(t, (const void *)cmd_buf, sizeof(t));
        cmd_ready = 0; cmd_len = 0;
        __enable_irq();
        t[15] = 0;
        g_cmd_n++;                                  /* ★ v12：解出一条命令 */
        switch (t[0]) {
        case 'm': case 'M':
            g_pulse = 0; g_walk = 0;
            g_motor = !g_motor;
            if (g_motor) { motor_enable(1); lvl = 0; step_t0 = now_ms; motor_apply(LEVELS[0], g_dir); }
            else motor_enable(0);
            log_printf("[CMD] motor auto-cycle = %d\r\n", g_motor);
            break;
        case 'r': case 'R':
            g_dir = -g_dir;
            if (g_motor) motor_apply(g_duty, g_dir);
            log_printf("[CMD] dir = %+d\r\n", g_dir);
            break;
        case 's': case 'S':
            g_motor = 0; g_pulse = 0; g_walk = 0; motor_enable(0);
            log_printf("[CMD] motor STOP\r\n");
            break;
        case 'z': case 'Z':
            g_zero_f = g_th_f;
            log_printf("[CMD] zero set (unwrap=%.0f)\r\n", g_zero_f);
            break;
        case 'q': case 'Q':
            g_quiet = !g_quiet;
            log_printf("[CMD] quiet=%d\r\n", g_quiet);
            break;
        case 'i': case 'I':
            i2c_scan();
            break;
        case 'k': case 'K':
            log_printf("[CMD] HALLO\r\n");
            break;
        case 'd': case 'D':
            g_dump_start = (rec_cnt < DSIZE) ? 0 : rec_idx;   /* 最老的那个样本 */
            g_dump_n     = rec_cnt;
            g_dump_i     = 0;
            g_dump_run   = 1;
            log_printf("DUMP BEGIN n=%u (i,th_deg,dps,duty)\r\n", (unsigned)g_dump_n);
            break;
        case 'f': case 'F':
            g_print_fast = !g_print_fast;
            log_printf("[EXP] print in fast tick = %d\r\n", g_print_fast);
            break;
        case 'b': case 'B':
            g_nonblock = !g_nonblock;
            log_printf("[EXP] tx mode = %s\r\n", g_nonblock ? "IT(nonblock)" : "BLOCKING");
            break;
        case 'p': case 'P': {                  /* ★ v10 定值脉冲：p<占空比>，如 p20 / p-20 / p0 */
            int v = atoi(&t[1]);
            if (v >  100) v =  100;
            if (v < -100) v = -100;
            g_motor = 0; g_walk = 0;           /* 与轮播/慢转互斥 */
            g_b_min = 0xFFFFu; g_b_max = 0;
            if (v == 0) {
                g_pulse = 0; motor_enable(0);
                log_printf("[PULSE] stop\r\n");
            } else {
                g_dir = (v > 0) ? 1 : -1;
                g_pulse = 1; g_pulse_t0 = HAL_GetTick();
                motor_enable(1);
                motor_apply((v > 0) ? v : -v, g_dir);
                log_printf("[PULSE] duty=%d%% dir=%+d for %lums\r\n",
                           (v > 0) ? v : -v, g_dir, (unsigned long)PULSE_MS);
            }
            break;
        }
        case 'w': case 'W': {                  /* ★ v11 慢转：w<占空比>，如 w15 / w-15 / w0 */
            int v = atoi(&t[1]);
            if (v >  WALK_DUTY_MAX) v =  WALK_DUTY_MAX;
            if (v < -WALK_DUTY_MAX) v = -WALK_DUTY_MAX;
            g_motor = 0; g_pulse = 0;
            if (v == 0) {
                g_walk = 0; motor_enable(0);
                log_printf("[WALK] stop\r\n");
            } else {
                g_dir = (v > 0) ? 1 : -1;
                g_walk = 1; g_walk_t0 = HAL_GetTick();
                g_b_min = 0xFFFFu; g_b_max = 0;      /* ★ 从这一刻起统计 |B| 的 lo/hi */
                motor_enable(1);
                motor_apply((v > 0) ? v : -v, g_dir);
                log_printf("[WALK] duty=%d%% dir=%+d, auto stop in %lums (send 's' to stop now)\r\n",
                           (v > 0) ? v : -v, g_dir, (unsigned long)WALK_MS);
            }
            break;
        }
        default:
            log_printf("[CMD] ? 0x%02X\r\n", (unsigned)(uint8_t)t[0]);
        }
    }

    /* dump：一次一行、只在串口空闲时发（非阻塞，不拖累节拍） */
    if (g_dump_run && !tx_busy) {
        if (g_dump_i < g_dump_n) {
            uint16_t k = (uint16_t)(g_dump_start + g_dump_i);
            if (k >= DSIZE) k = (uint16_t)(k - DSIZE);
            log_printf("%u,%.1f,%d,%u\r\n", (unsigned)g_dump_i,
                       (float)rec_ang[k] / 10.0f,
                       (int)rec_dps[k], (unsigned)rec_duty[k]);
            g_dump_i++;
        } else {
            g_dump_run = 0;
            log_printf("DUMP END n=%u total=%lu bad=%lu drop=%lu\r\n",
                       (unsigned)g_dump_n, (unsigned long)rec_total,
                       (unsigned long)g_bad_total, (unsigned long)g_drop);
        }
    }

    if (g_motor && (now_ms - step_t0 >= STEP_MS)) {
        step_t0 = now_ms;
        lvl++;
        if (lvl >= LVL_N) { lvl = 0; g_dir = -g_dir; log_printf("---- reverse: %+d ----\r\n", g_dir); }
        motor_apply(LEVELS[lvl], g_dir);
    }

    /* ★ v10：定值脉冲到点自动停 */
    if (g_pulse && (now_ms - g_pulse_t0 >= PULSE_MS)) {
        g_pulse = 0;
        motor_enable(0);
        log_printf("[PULSE] done, motor off\r\n");
    }

    /* ★ v11：慢转到点自动停 */
    if (g_walk && (now_ms - g_walk_t0 >= WALK_MS)) {
        g_walk = 0;
        motor_enable(0);
        log_printf("[WALK] timeout, motor off\r\n");
    }

    /* 状态行：每 500ms 一行（低频） */
    if (g_win_report) {
        g_win_report = 0;
        if (!g_quiet && !g_print_fast) print_status();
        g_dt_sum = 0; g_dt_max = 0; g_dt_min = 0xFFFFFFFFu;
        g_tick_n = 0; g_tick_over = 0; g_sum_n = 0;
        g_win_t0 = micros();
    }
}
