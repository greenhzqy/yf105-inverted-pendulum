/* =====================================================================
 *  app_motor.c  ·  S1 第一炮：把"0~100 的数字"变成电机的力
 *
 *  配合 CubeMX 生成的 main.c 使用（main.c 已有 SystemClock_Config / MX_*_Init）：
 *      /* USER CODE BEGIN Includes *\/   ->  #include "app_motor.h"
 *      /* USER CODE BEGIN 2 *\/         ->  app_motor_init();
 *      /* USER CODE BEGIN 3 *\/         ->  app_motor_loop();
 *
 *  逻辑：
 *    占空比(0~100) -> TIM3 比较寄存器 -> PB0 出 PWM          （劲大小）
 *    方向         -> PA0/PA1 (AIN1/AIN2)                    （正/反转）
 *    使能         -> PA2 (STBY)，上电默认低，3 秒后才放行   （安全习惯）
 *
 *  v2 改动（排查"只响不转"）：
 *    1) 占空比按【实际 ARR】计算，不再写死 3599 —— 换任何 PWM 频率都不会错；
 *    2) 开机打印 TIM3 的真实 PSC/ARR/时钟/实际 PWM 频率，日志里带 pulse 值。
 *
 *  串口 115200 命令（回车结束）：
 *     0~100 = 设定占空比   r = 换向   s = 回自动轮播   x = 急停   e = 重新使能
 *  注意：串口输出一律用 ASCII，避免 Keil 中文编码问题（中文只出现在注释里）
 * ===================================================================== */
#include "app_motor.h"
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <stdlib.h>

extern TIM_HandleTypeDef htim3;
extern UART_HandleTypeDef huart1;

#define AIN1_PORT   GPIOA
#define AIN1_PIN    GPIO_PIN_0
#define AIN2_PORT   GPIOA
#define AIN2_PIN    GPIO_PIN_1
#define STBY_PORT   GPIOA
#define STBY_PIN    GPIO_PIN_2

#define LOG_BUF     160
#define START_DELAY 3000u

static volatile uint8_t rx_byte;
static volatile char    cmd_buf[16];
static volatile uint8_t cmd_len = 0;
static volatile uint8_t cmd_ready = 0;

static int      g_duty = 0;
static int      g_dir = 1;
static uint8_t  g_manual = 0;
static uint8_t  g_enabled = 0;
static uint8_t  g_started = 0;
static uint32_t g_t0 = 0;
static uint32_t g_pulse = 0;

static const int LEVELS[4] = {0, 40, 70, 100};
static uint8_t   lvl_idx = 0;
static uint32_t  lvl_t0 = 0;
static uint32_t  last_log = 0;

static void log_printf(const char *fmt, ...)
{
    char buf[LOG_BUF];
    va_list ap;
    int n;
    va_start(ap, fmt);
    n = vsnprintf(buf, sizeof(buf), fmt, ap);
    va_end(ap);
    if (n > 0) HAL_UART_Transmit(&huart1, (uint8_t *)buf, (uint16_t)n, 100);
}

/* ---------- 把"数字"变成"力"：唯一真正碰硬件的地方 ---------- */
static void motor_apply(int duty_percent, int dir)
{
    uint32_t arr, pulse;

    if (duty_percent < 0)   duty_percent = 0;
    if (duty_percent > 100) duty_percent = 100;

    arr   = htim3.Init.Period;                                      /* 实际 ARR */
    pulse = (uint32_t)(((arr + 1u) * (uint32_t)duty_percent) / 100u);
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_3, pulse);
    g_pulse = pulse;

    if (duty_percent == 0) {
        HAL_GPIO_WritePin(AIN1_PORT, AIN1_PIN, GPIO_PIN_RESET);
        HAL_GPIO_WritePin(AIN2_PORT, AIN2_PIN, GPIO_PIN_RESET);
    } else if (dir > 0) {
        HAL_GPIO_WritePin(AIN1_PORT, AIN1_PIN, GPIO_PIN_SET);
        HAL_GPIO_WritePin(AIN2_PORT, AIN2_PIN, GPIO_PIN_RESET);
    } else {
        HAL_GPIO_WritePin(AIN1_PORT, AIN1_PIN, GPIO_PIN_RESET);
        HAL_GPIO_WritePin(AIN2_PORT, AIN2_PIN, GPIO_PIN_SET);
    }

    g_duty = duty_percent;
    if (dir != 0) g_dir = dir;
}

static void motor_enable(uint8_t en)
{
    g_enabled = en;
    HAL_GPIO_WritePin(STBY_PORT, STBY_PIN, en ? GPIO_PIN_SET : GPIO_PIN_RESET);
    if (!en) motor_apply(0, g_dir);
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART1) {
        char ch = (char)rx_byte;
        if (ch == '\r' || ch == '\n') {
            if (cmd_len > 0) { cmd_buf[cmd_len] = 0; cmd_ready = 1; }
        } else if (cmd_len < sizeof(cmd_buf) - 1) {
            cmd_buf[cmd_len++] = ch;
        }
        HAL_UART_Receive_IT(&huart1, (uint8_t *)&rx_byte, 1);
    }
}

static void handle_command(char *s)
{
    if (s[0] == 'r' || s[0] == 'R') {
        g_dir = -g_dir;
        log_printf("[CMD] reverse -> dir=%s\r\n", g_dir > 0 ? "FWD" : "REV");
        motor_apply(g_duty, g_dir);
    } else if (s[0] == 's' || s[0] == 'S') {
        g_manual = 0;
        log_printf("[CMD] back to auto cycle\r\n");
    } else if (s[0] == 'x' || s[0] == 'X') {
        g_manual = 1;
        motor_enable(0);
        log_printf("[CMD] STOP: duty=0, STBY=low\r\n");
    } else if (s[0] == 'e' || s[0] == 'E') {
        motor_enable(1);
        log_printf("[CMD] enabled\r\n");
    } else {
        int v = atoi(s);
        if (v >= 0 && v <= 100) {
            g_manual = 1;
            if (!g_enabled) motor_enable(1);
            motor_apply(v, g_dir);
            log_printf("[CMD] manual duty = %d%%  pulse=%lu\r\n", v, (unsigned long)g_pulse);
        } else {
            log_printf("[CMD] unknown: %s  (0-100 / r / s / x / e)\r\n", s);
        }
    }
}

static void auto_sequence(void)
{
    uint32_t now = HAL_GetTick();

    if (now - lvl_t0 >= 3000u) {
        lvl_t0 = now;
        lvl_idx++;
        if (lvl_idx >= 4) {
            lvl_idx = 0;
            g_dir = -g_dir;
            log_printf("---- reverse: %s ----\r\n", g_dir > 0 ? "FWD" : "REV");
        }
        motor_apply(LEVELS[lvl_idx], g_dir);
    }
    if (now - last_log >= 500u) {
        last_log = now;
        log_printf("t=%lums  duty=%d%%  pulse=%lu  dir=%s  stby=%d\r\n",
                   (unsigned long)now, g_duty, (unsigned long)g_pulse,
                   g_dir > 0 ? "+" : "-", g_enabled);
    }
}

void app_motor_init(void)
{
    uint32_t pclk1, timclk, arr, psc, f;

    motor_enable(0);
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_3);
    HAL_UART_Receive_IT(&huart1, (uint8_t *)&rx_byte, 1);
    g_t0 = HAL_GetTick();

    log_printf("\r\n==== S1 : number -> force (PWM/DIR test) ====\r\n");

    pclk1  = HAL_RCC_GetPCLK1Freq();
    timclk = ((RCC->CFGR & RCC_CFGR_PPRE1) == RCC_CFGR_PPRE1_DIV1) ? pclk1 : (pclk1 * 2u);
    arr    = htim3.Init.Period;
    psc    = htim3.Init.Prescaler;
    f      = timclk / ((psc + 1u) * (arr + 1u));
    log_printf("TIM3: psc=%lu  arr=%lu  timclk=%luHz  ->  pwm=%luHz\r\n",
               (unsigned long)psc, (unsigned long)arr, (unsigned long)timclk, (unsigned long)f);
    log_printf("SYSCLK=%luHz  HCLK=%luHz  PCLK1=%luHz\r\n",
               (unsigned long)HAL_RCC_GetSysClockFreq(),
               (unsigned long)HAL_RCC_GetHCLKFreq(), (unsigned long)pclk1);

    log_printf("motor enables in 3s, then auto cycle 0/40/70/100%%\r\n");
    log_printf("cmd: 0-100=duty  r=reverse  s=auto  x=stop  e=enable\r\n");
}

void app_motor_loop(void)
{
    if (!g_started && (HAL_GetTick() - g_t0 >= START_DELAY)) {
        g_started = 1;
        motor_enable(1);
        lvl_t0 = HAL_GetTick();
        last_log = lvl_t0;
        motor_apply(LEVELS[0], g_dir);
        log_printf("[INIT] motor enabled, start auto cycle\r\n");
    }

    if (cmd_ready) {
        char tmp[16];
        __disable_irq();
        memcpy(tmp, (const void *)cmd_buf, sizeof(tmp));
        cmd_ready = 0;
        cmd_len = 0;
        __enable_irq();
        tmp[15] = 0;
        handle_command(tmp);
    }

    if (g_started && g_enabled && !g_manual) auto_sequence();
}
