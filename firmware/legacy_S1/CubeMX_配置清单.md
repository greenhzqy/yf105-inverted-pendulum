# CubeMX 配置清单 · S1 电机测试（STM32F103C8T6 蓝丸 + Keil）

> 照着点，生成 MDK-ARM 工程，然后用本文件夹的 `main.c` 覆盖 `Core/Src/main.c`。
> 注意：以后再用 CubeMX 重新生成代码会覆盖 main.c——本项目约定：**改配置后重新生成，再把 main.c 换回来**（或者把我们的代码写在 USER CODE 区外的新文件里）。

## 芯片与时钟
| 项 | 设置 |
|---|---|
| MCU | STM32F103C8Tx |
| RCC → HSE | Crystal/Ceramic Resonator（蓝丸板载 8MHz 晶振） |
| Clock Configuration | HCLK = **72MHz**，APB1 = 36MHz，APB2 = 72MHz（PLL ×9） |
| SYS → Debug | **Serial Wire**（保留 SWD 下载口） |

## 外设
| 外设 | 配置 | 引脚 |
|---|---|---|
| **TIM3** | Channel3 = **PWM Generation CH3**；Prescaler=0；Counter Period(ARR)=**3599**；PWM Mode 1；Pulse=0 | **PB0** |
| **USART1** | Asynchronous；**115200**、8N1 | **PA9**(TX) / **PA10**(RX) |
| **GPIO** | PA0、PA1、PA2 = Output Push-Pull，初始电平 **Low**，无上下拉 | PA0/PA1/PA2 |

> PWM 频率 = 72MHz / (0+1) / (3599+1) = **20kHz**（人耳听不见啸叫；直流电机常用 10~20kHz）。

## 工程设置
- Project Manager → Toolchain = **MDK-ARM V5**；Code Generator 勾 "Copy only the necessary library files"。
- 生成后：Keil 里 Options for Target → Debug 选 ST-Link Debugger，下载即可。

## 下一轮要加的（先不配也行）
- **I2C1**：I2C，Standard Mode 400kHz → **PB6(SCL) / PB7(SDA)**，用于 AS5600 读角度。
