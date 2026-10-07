/* =====================================================================
 *  inc/drivers/as5600.h  ·  AS5600 磁编码器：寄存器读、磁场状态、总线扫描
 *
 *  职责：把"读 AS5600 寄存器"封装成几个函数（返回 0/1，不抛错、不阻塞重试）
 *  依赖：HAL I2C + main.h；i2c_scan() 还依赖 inc/app/console.h 打印扫描结果
 *  被谁调用：src/app/app_angle.c（fast_task 读 RAWANGLE、print_status 读状态/AGC/|B|、'i' 命令扫描）
 *
 *  与原 app_angle.c 的对应：原第 35~39 行（寄存器地址）+ 第 169~192 行（rd_to/rd/magnet_str/i2c_scan）
 *  ★ 器件地址与寄存器地址与原版逐字同值
 * ===================================================================== */
#ifndef __AS5600_H
#define __AS5600_H

#include <stdint.h>

#define AS5600_ADDR     (0x36 << 1)
#define REG_STATUS      0x0Bu
#define REG_RAWANGLE    0x0Cu
#define REG_AGC         0x1Au
#define REG_MAGNITUDE   0x1Bu

/* 读寄存器，带超时（原 rd_to）：返回 1 = 成功 */
uint8_t as5600_rd_to(uint8_t reg, uint8_t *buf, uint16_t len, uint32_t to_ms);

/* 读寄存器，默认 20ms 超时（原 rd）：返回 1 = 成功 */
uint8_t as5600_rd(uint8_t reg, uint8_t *buf, uint16_t len);

/* STATUS 字节 -> 磁场状态字符串："OK" / "WEAK" / "STRONG" / "NONE" */
const char *as5600_magnet_str(uint8_t st);

/* 扫描 I2C 总线 0x08~0x77 并打印结果（原 i2c_scan） */
void i2c_scan(void);

#endif /* __AS5600_H */
