/* =====================================================================
 *  src/hal/hal_io.c  ·  电机执行器引脚层实现
 *
 *  职责：PWM 比较值写入 + AIN1/AIN2/STBY 三根 GPIO 的电平写入
 *  依赖：hal_io.h、main.h（HAL、htim3）
 *  被谁调用：src/app/app_angle.c
 *
 *  逐行对照原 app_angle.c 第 195~220 行；引脚宏（PA0/PA1/PA2）与原版一致
 * ===================================================================== */
#include "hal_io.h"
#include "main.h"

extern TIM_HandleTypeDef htim3;

#define AIN1_PORT GPIOA
#define AIN1_PIN  GPIO_PIN_0
#define AIN2_PORT GPIOA
#define AIN2_PIN  GPIO_PIN_1
#define STBY_PORT GPIOA
#define STBY_PIN  GPIO_PIN_2

void hal_io_motor_pwm_start(void)
{
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_3);
}

void hal_io_motor_duty(uint32_t duty_pct)
{
    uint32_t arr   = htim3.Init.Period;
    uint32_t pulse = (uint32_t)(((arr + 1u) * duty_pct) / 100u);
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_3, pulse);
}

void hal_io_motor_dir(int8_t dir)
{
    if (dir > 0) {
        HAL_GPIO_WritePin(AIN1_PORT, AIN1_PIN, GPIO_PIN_SET);
        HAL_GPIO_WritePin(AIN2_PORT, AIN2_PIN, GPIO_PIN_RESET);
    } else {
        HAL_GPIO_WritePin(AIN1_PORT, AIN1_PIN, GPIO_PIN_RESET);
        HAL_GPIO_WritePin(AIN2_PORT, AIN2_PIN, GPIO_PIN_SET);
    }
}

void hal_io_motor_coast(void)
{
    HAL_GPIO_WritePin(AIN1_PORT, AIN1_PIN, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(AIN2_PORT, AIN2_PIN, GPIO_PIN_RESET);
}

void hal_io_motor_stby(uint8_t en)
{
    HAL_GPIO_WritePin(STBY_PORT, STBY_PIN, en ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

uint32_t hal_io_pwm_psc(void) { return htim3.Init.Prescaler; }
uint32_t hal_io_pwm_arr(void) { return htim3.Init.Period; }
