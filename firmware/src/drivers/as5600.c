/* =====================================================================
 *  src/drivers/as5600.c  ·  AS5600 驱动实现
 *
 *  职责：I2C 读写 AS5600（STATUS/RAWANGLE/AGC/MAGNITUDE）+ 磁场状态翻译 + 总线扫描
 *  依赖：as5600.h、main.h（HAL I2C）、inc/app/console.h（仅 i2c_scan 打印用）
 *  被谁调用：src/app/app_angle.c
 *
 *  逐行对照原 app_angle.c 第 169~192 行；扫描范围 0x08~0x77、试 3 次、20ms 超时都不变
 * ===================================================================== */
#include "as5600.h"
#include "app/console.h"          
#include "main.h"

extern I2C_HandleTypeDef hi2c1;

uint8_t as5600_rd_to(uint8_t reg, uint8_t *buf, uint16_t len, uint32_t to_ms)
{
    return (HAL_I2C_Mem_Read(&hi2c1, AS5600_ADDR, reg, I2C_MEMADD_SIZE_8BIT, buf, len, to_ms) == HAL_OK);
}

uint8_t as5600_rd(uint8_t reg, uint8_t *buf, uint16_t len) { return as5600_rd_to(reg, buf, len, 20); }

const char *as5600_magnet_str(uint8_t st)
{
    if (st & 0x20) return "OK";
    if (st & 0x10) return "WEAK";
    if (st & 0x08) return "STRONG";
    return "NONE";
}

void i2c_scan(void)
{
    uint16_t a; uint8_t n = 0;
    log_printf("I2C scan:");
    for (a = 0x08; a <= 0x77; a++) {
        if (HAL_I2C_IsDeviceReady(&hi2c1, (uint16_t)(a << 1), 3, 20) == HAL_OK) { log_printf(" 0x%02X", a); n++; }
    }
    if (!n) log_printf(" (none)");
    log_printf("\r\n");
}
