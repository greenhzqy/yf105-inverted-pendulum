/* =====================================================================
 *  src/app/app_angle.c  ·  v12 等价重构版（模块化）：2ms 节拍 + 角度链 + 速度 + 记录 + 命令
 *                     原 firmware/app_angle.c（548 行）逐行搬家，行为不变
 *                     v10 定值脉冲 p / v11 慢转 w 与 |B| 统计 / v12 ORE 兜底 + rx= cmd= rxerr=
 *
 *  职责：持有全部状态与调度；每 2ms 走一拍角度链、每 500ms 出一行状态、解析并执行串口命令
 *  依赖：console(串口) / hal_time(微秒) / hal_io(电机引脚) / as5600(读角度) /
 *        angle_core(纯算法) / recorder(环形缓冲) / cmd_parse(命令解析)
 *  被谁调用：Core/Src/main.c 的 USER CODE 2（app_angle_init）与 USER CODE 3（app_angle_loop）
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
/* 目录约定：头文件在 inc/、实现文件在 src/，各自按功能分 hal / drivers / core / app。
 * 引头文件用"逻辑路径"（inc/ 的下一层），Keil 里把 app_angle/inc 加进 Include Paths 一次即可。
 * include guard 与原 app_angle.h 相同，原地替换不会重定义。 */
#include "app_angle.h"        /* inc/app/     */
#include "console.h"          /* inc/app/     */
#include "hal/hal_time.h"     /* inc/hal/     */
#include "hal/hal_io.h"       /* inc/hal/     */
#include "drivers/as5600.h"   /* inc/drivers/ */
#include "core/angle_core.h"  /* inc/core/    */
#include "core/recorder.h"    /* inc/core/    */
#include "core/cmd_parse.h"   /* inc/core/    */
#include "main.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

extern UART_HandleTypeDef huart1;

/* ---- 常量（与原 app_angle.c 第 48~64 行逐字同值） ---- */
#define SAMP_US     2000u      /* ★ 采样周期 2ms = 500Hz */
#define STEP_MS     3000u      /* 电机换档周期 */
#define PULSE_MS     300u      /* ★ v10 定值脉冲持续时间：符号预验证给 20% 持续 0.3s */
#define WALK_MS      30000u    /* ★ v11 慢转最长持续时间（到点自动停，防止忘了关） */
#define WIN_US      500000u    /* 状态行/统计窗口 500ms */
#define LVL_N       (sizeof(LEVELS) / sizeof(LEVELS[0]))
/* 注：WALK_DUTY_MAX=40 随 p/w 的钳位一起搬到了 inc/core/cmd_parse.h（数值不变） */

/* ---- 串口接收（原第 66~69 行） ---- */
static volatile uint8_t rx_byte;
static volatile char    cmd_buf[16];
static volatile uint8_t cmd_len = 0, cmd_ready = 0;
static uint32_t g_rx_n = 0, g_cmd_n = 0, g_rx_err = 0;   /* ★ v12 串口诊断计数 */

/* ---- 角度/零点和电机状态（原第 71~85 行；角度链状态搬进 g_ang） ---- */
static angle_state_t g_ang;                  /* 原 g_raw/g_unwrap/g_th_f/g_th_prev_f/g_dps/g_bad_* */
static uint16_t g_zero = 0;                  /* 原第 71 行的 g_zero：全文件只有这一处出现（未使用）。
                                              * 原样保留 —— 连 arm-none-eabi-gcc 的那条
                                              * "'g_zero' defined but not used" 警告都与原版一致 */
static float    g_zero_f = 0.0f;             /* 浮点零点（相对连续角度） */
static uint8_t  g_quiet = 0, g_motor = 0, g_enabled = 0;
static int      g_duty = 0, g_dir = 1;
static uint32_t step_t0 = 0;
static uint8_t  lvl = 0;
static const int LEVELS[5] = {0, 25, 50, 75, 100};
static uint8_t  g_pulse = 0;                 /* ★ v10 定值脉冲进行中 */
static uint32_t g_pulse_t0 = 0;
static uint8_t  g_walk = 0;                  /* ★ v11 慢转进行中 */
static uint32_t g_walk_t0 = 0;
static uint16_t g_b_min = 0xFFFFu, g_b_max = 0;   /* ★ v11 |B| 的最小/最大值（发 w/p 时清零） */

/* ---- 节拍与统计（原第 87~95 行） ---- */
static uint32_t g_tick_next = 0, g_tick_last = 0;
static uint32_t g_tick_n = 0, g_tick_over = 0;
static uint32_t g_dt_sum = 0, g_dt_max = 0, g_dt_min = 0xFFFFFFFFu;
static uint8_t  g_print_fast = 0;
static uint32_t g_win_t0 = 0;
static uint8_t  g_win_report = 0;
static uint32_t g_sum_n = 0;
static uint8_t  g_dt_skip = 5;

/* ---- dump 泵状态（原第 115~116 行；缓冲本身在 src/core/recorder.c） ---- */
static uint8_t  g_dump_run = 0;
static uint16_t g_dump_i = 0, g_dump_start = 0, g_dump_n = 0;

static void motor_apply(int duty, int dir);
static void motor_enable(uint8_t en);
static void print_status(void);
static void fast_task(void);

/* ---------------- 电机（原第 195~220 行） ---------------- */
static void motor_apply(int duty, int dir)
{
    if (duty < 0)   duty = 0;
    if (duty > 100) duty = 100;
    hal_io_motor_duty((uint32_t)duty);
    if (duty == 0) {
        hal_io_motor_coast();
    } else if (dir > 0) {
        hal_io_motor_dir(1);
    } else {
        hal_io_motor_dir(-1);
    }
    g_duty = duty; g_dir = dir;
}
static void motor_enable(uint8_t en)
{
    g_enabled = en;
    hal_io_motor_stby(en);
    if (!en) motor_apply(0, g_dir);
}

/* ---------------- 状态行（每 500ms 一行，低频）（原第 223~244 行） ---------------- */
static void print_status(void)
{
    uint8_t st = 0, agc = 0, mag[2] = {0, 0};
    uint32_t avg = 0;
    as5600_rd(REG_STATUS, &st, 1);
    as5600_rd(REG_AGC, &agc, 1);
    as5600_rd(REG_MAGNITUDE, mag, 2);
    if (g_sum_n > 0) avg = g_dt_sum / g_sum_n;
    {
        uint16_t bv = (uint16_t)(((mag[0] & 0x0F) << 8) | mag[1]);
        if (bv < g_b_min) g_b_min = bv;
        if (bv > g_b_max) g_b_max = bv;
        log_printf("ST th=%6.1f dps=%5d duty=%3d%% mot=%d dir=%+d | dt avg=%4lu max=%5lu min=%4lu n=%lu over=%lu | bad=%lu drop=%lu | MAG=%s |B|=%4u lo=%4u hi=%4u | rx=%lu cmd=%lu rxerr=%lu\r\n",
                   (g_ang.lpf - g_zero_f) * 360.0f / 4096.0f, g_ang.dps, g_duty, g_motor, g_dir,
                   (unsigned long)avg, (unsigned long)g_dt_max,
                   (unsigned long)((g_dt_min == 0xFFFFFFFFu) ? 0 : g_dt_min),
                   (unsigned long)g_tick_n, (unsigned long)g_tick_over,
                   (unsigned long)g_ang.bad_total, (unsigned long)console_drop(),
                   as5600_magnet_str(st), (unsigned)bv, (unsigned)g_b_min, (unsigned)g_b_max,
                   (unsigned long)g_rx_n, (unsigned long)g_cmd_n, (unsigned long)g_rx_err);
    }
}

/* ---------------- ★ 快任务：每 2ms 一次（原第 247~303 行） ---------------- */
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

    /* ② 角度链：读 -> 毛刺剔除 -> 低通（算法在 src/core/angle_core.c） */
    if (as5600_rd_to(REG_RAWANGLE, b, 2, 2)) {
        uint16_t raw = (uint16_t)(((b[0] & 0x0F) << 8) | b[1]);
        angle_step(&g_ang, raw, dt);
    } else {
        angle_mark_read_fail(&g_ang);            /* I2C 读失败也算无效 */
    }

    /* ④ 记录：每个有效节拍存一个样本（0.1 度单位） */
    rec_push((int16_t)((g_ang.lpf - g_zero_f) * 360.0f / 4096.0f * 10.0f),
             g_ang.dps, (uint8_t)g_duty);

    /* ★ 实验开关：打印塞进快节拍（故意拖垮节拍） */
    if (g_print_fast) print_status();
}

void USART1_IRQHandler(void) { HAL_UART_IRQHandler(&huart1); }

/* ★ v12：收字节统一入口（中断和兜底轮询都走这里）（原第 308~313 行） */
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

/* ---------------- 初始化（原第 337~376 行） ---------------- */
void app_angle_init(void)
{
    uint8_t b[2];
    uint32_t pclk1, timclk;

    motor_enable(0);
    hal_io_motor_pwm_start();
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
               (unsigned long)hal_io_pwm_psc(), (unsigned long)hal_io_pwm_arr(),
               (unsigned long)(timclk / ((hal_io_pwm_psc() + 1u) * (hal_io_pwm_arr() + 1u))),
               (unsigned long)SAMP_US, (unsigned long)(1000000u / SAMP_US), (unsigned long)(WIN_US / 1000u));
    log_printf("filter: alpha=0.35 (1st-order LPF) | jump max=%d counts (~13.2deg) | dps limit=%d\r\n",
               ANG_JUMP_MAX, (int)DPS_MAX);
    log_printf("record buffer: %d samples (%.1fs @500Hz)\r\n", DSIZE, (float)DSIZE / 500.0f);

    HAL_Delay(200);
    i2c_scan();
    if (as5600_rd(REG_STATUS, b, 1)) log_printf("AS5600 STATUS=0x%02X MAG=%s\r\n", b[0], as5600_magnet_str(b[0]));
    else log_printf("AS5600 no answer!\r\n");
    if (as5600_rd(REG_RAWANGLE, b, 2)) {
        angle_core_init(&g_ang, (uint16_t)(((b[0] & 0x0F) << 8) | b[1]));
    }
    log_printf("cmd: m r s z q i k | p<pct>=pulse | w<pct>=slow walk | d=dump CSV | f/b = exp\r\n");
    log_printf("tip: send with CR/LF (check 'append newline'); watch RX rx= cmd= rxerr=\r\n");
}

/* ---------------- 主循环（原第 378~548 行） ---------------- */
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
        cmd_t c;
        __disable_irq();
        memcpy(t, (const void *)cmd_buf, sizeof(t));
        cmd_ready = 0; cmd_len = 0;
        __enable_irq();
        t[15] = 0;
        g_cmd_n++;                                  /* ★ v12：解出一条命令 */
        c = cmd_parse(t);                           /* 纯解析：只给命令码与参数 */
        switch (c.code) {
        case CMD_MOTOR:                             /* 'm' / 'M' */
            g_pulse = 0; g_walk = 0;
            g_motor = !g_motor;
            if (g_motor) { motor_enable(1); lvl = 0; step_t0 = now_ms; motor_apply(LEVELS[0], g_dir); }
            else motor_enable(0);
            log_printf("[CMD] motor auto-cycle = %d\r\n", g_motor);
            break;
        case CMD_DIR:                               /* 'r' / 'R' */
            g_dir = -g_dir;
            if (g_motor) motor_apply(g_duty, g_dir);
            log_printf("[CMD] dir = %+d\r\n", g_dir);
            break;
        case CMD_STOP:                              /* 's' / 'S' */
            g_motor = 0; g_pulse = 0; g_walk = 0; motor_enable(0);
            log_printf("[CMD] motor STOP\r\n");
            break;
        case CMD_ZERO:                              /* 'z' / 'Z' */
            g_zero_f = g_ang.lpf;
            log_printf("[CMD] zero set (unwrap=%.0f)\r\n", g_zero_f);
            break;
        case CMD_QUIET:                             /* 'q' / 'Q' */
            g_quiet = !g_quiet;
            log_printf("[CMD] quiet=%d\r\n", g_quiet);
            break;
        case CMD_SCAN:                              /* 'i' / 'I' */
            i2c_scan();
            break;
        case CMD_HELLO:                             /* 'k' / 'K' */
            log_printf("[CMD] HALLO\r\n");
            break;
        case CMD_DUMP:                              /* 'd' / 'D' */
            rec_dump_begin(&g_dump_start, &g_dump_n);   /* 最老的那个样本 */
            g_dump_i   = 0;
            g_dump_run = 1;
            log_printf("DUMP BEGIN n=%u (i,th_deg,dps,duty)\r\n", (unsigned)g_dump_n);
            break;
        case CMD_EXP_FAST:                          /* 'f' / 'F' */
            g_print_fast = !g_print_fast;
            log_printf("[EXP] print in fast tick = %d\r\n", g_print_fast);
            break;
        case CMD_EXP_TX:                            /* 'b' / 'B' */
            console_set_nonblock((uint8_t)!console_get_nonblock());
            log_printf("[EXP] tx mode = %s\r\n", console_get_nonblock() ? "IT(nonblock)" : "BLOCKING");
            break;
        case CMD_PULSE: {                           /* ★ v10 定值脉冲：p<占空比>，如 p20 / p-20 / p0 */
            int v = c.arg;
            g_motor = 0; g_walk = 0;                /* 与轮播/慢转互斥 */
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
        case CMD_WALK: {                            /* ★ v11 慢转：w<占空比>，如 w15 / w-15 / w0 */
            int v = c.arg;
            g_motor = 0; g_pulse = 0;
            if (v == 0) {
                g_walk = 0; motor_enable(0);
                log_printf("[WALK] stop\r\n");
            } else {
                g_dir = (v > 0) ? 1 : -1;
                g_walk = 1; g_walk_t0 = HAL_GetTick();
                g_b_min = 0xFFFFu; g_b_max = 0;     /* ★ 从这一刻起统计 |B| 的 lo/hi */
                motor_enable(1);
                motor_apply((v > 0) ? v : -v, g_dir);
                log_printf("[WALK] duty=%d%% dir=%+d, auto stop in %lums (send 's' to stop now)\r\n",
                           (v > 0) ? v : -v, g_dir, (unsigned long)WALK_MS);
            }
            break;
        }
        default:                                    /* 未知命令 */
            log_printf("[CMD] ? 0x%02X\r\n", (unsigned)(uint8_t)t[0]);
            break;
        }
    }

    /* dump：一次一行、只在串口空闲时发（非阻塞，不拖累节拍） */
    if (g_dump_run && !console_tx_busy()) {
        if (g_dump_i < g_dump_n) {
            uint16_t k = rec_dump_k(g_dump_start, g_dump_i);
            log_printf("%u,%.1f,%d,%u\r\n", (unsigned)g_dump_i,
                       (float)rec_ang_at(k) / 10.0f,
                       (int)rec_dps_at(k), (unsigned)rec_duty_at(k));
            g_dump_i++;
        } else {
            g_dump_run = 0;
            log_printf("DUMP END n=%u total=%lu bad=%lu drop=%lu\r\n",
                       (unsigned)g_dump_n, (unsigned long)rec_total_n(),
                       (unsigned long)g_ang.bad_total, (unsigned long)console_drop());
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
