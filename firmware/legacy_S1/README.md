# firmware · 倒立摆固件（STM32F103C8T6 蓝丸 + Keil + ST-Link）

| 文件 | 用途 |
|---|---|
| `CubeMX_配置清单.md` | CubeMX 里怎么点（时钟树/外设/引脚/工程设置） |
| `接线表.md` | 逐脚接线 + 通电前检查 |
| `app_motor.h` / `app_motor.c` | **S1 电机测试逻辑**（数字→力）：自动轮播 + 串口命令接管 |
| 接线图 / 装配图 | 见上级 `figs/` 目录 |

> ⚠️ **不要整份覆盖 CubeMX 生成的 `main.c`**（2026-09 踩过：会删掉 `SystemClock_Config`、`MX_*_Init`、`htim3`、`huart1` → 6 个 `L6218E: Undefined symbol`）。
> 正确做法：逻辑放在 `app_motor.c`，在 main.c 的 **USER CODE 区**挂三行——这两个区重新生成代码也不会被覆盖。

## 用法（4 步）
1. **CubeMX 先确认再生成**（Pinout 页）：TIM3 → `PWM Generation CH3`（PB0）；USART1 → `Asynchronous`（PA9/PA10）；PA0/PA1/PA2 → `GPIO_Output`（初始 Low）。然后 **GENERATE CODE**（会把 main.c 恢复成官方骨架）。
2. 拷贝：`app_motor.c` → `Core/Src/`；`app_motor.h` → `Core/Inc/`。
3. Keil：右键工程里的 **Application/User/Core** 组 → *Add Existing Files to Group…* → 选中 `app_motor.c`（Keil 不会自动收录新文件）。
4. 在生成的 `main.c` 里加三处：

```c
/* USER CODE BEGIN Includes */
#include "app_motor.h"
/* USER CODE END Includes */
...
  /* USER CODE BEGIN 2 */
  app_motor_init();
  /* USER CODE END 2 */

  while (1)
  {
    /* USER CODE BEGIN 3 */
    app_motor_loop();
    /* USER CODE END 3 */
  }
```

## 编码说明（2026-09 修订，踩过坑）
- **所有源文件统一 UTF-8（无 BOM）**——和 Keil 编辑器的默认编码保持一致；
- **串口输出字符串一律 ASCII**（如 `duty=40%`）：这条规矩让我们在 UTF-8 / GBK 两种编辑器下都不会触发
  `#870-D: invalid multibyte character sequence`（中文只出现在注释里，编译器不管）；
- 若 Keil 里中文注释仍显示乱码：Edit → Configuration → Editor → Encoding 选 **UTF-8**（或告诉我，我把源文件转回 ANSI/GBK）。
- **教训**：源码编码必须和"读它的人（编辑器）+ 编译它的编译器"约定一致；最稳的写法是**代码里不出现非 ASCII 的可执行内容**。

## 串口命令（115200 8N1，回车结束）
| 输入 | 作用 |
|---|---|
| `0`~`100` | 手动设定占空比 % |
| `r` | 换向 |
| `s` | 回到自动轮播 |
| `x` | 急停（占空比 0 + STBY 禁能） |
| `e` | 重新使能 |
