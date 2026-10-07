# app_angle/ · 倒立摆固件（S2）分层重构版

> 把原来单文件 `firmware/app_angle.c`（v12，548 行）**按"搬家"原则**拆成 4 层 8 个 .c。
> **行为与原版逐字等价**：命令语义、串口输出格式串、时基与节拍逻辑一律不动。
> 逐条对照见 [`等价性对照.md`](等价性对照.md)，编译挂载见 [`main.md`](main.md)。

---

## 1. 文件清单（本机实测行数）

**目录约定：头文件进 `inc/`、实现文件进 `src/`，两边再按功能分 `hal / drivers / core / app`。**
（`.c` 与 `.h` 不放在同一目录里，各层一眼分得清"接口"和"实现"。）

```
firmware/app_angle/
├── inc/                      ← 头文件（接口）
│   ├── hal/hal_time.h        hal/hal_io.h
│   ├── drivers/as5600.h
│   ├── core/angle_core.h     core/recorder.h    core/cmd_parse.h
│   └── app/console.h         app/app_angle.h
└── src/                      ← 实现文件（.c）
    ├── hal/hal_time.c        hal/hal_io.c
    ├── drivers/as5600.c
    ├── core/angle_core.c     core/recorder.c     core/cmd_parse.c
    └── app/console.c         app/app_angle.c
                                        ↑
                    Keil 里把 app_angle/inc 加一次 Include Paths
```

| 头文件 | 实现 | 行数（h / c） | 一句话职责 | 依赖谁 | 被谁调用 |
|---|---|---|---|---|---|
| `inc/hal/hal_time.h` | `src/hal/hal_time.c` | 18 / 32 | TIM2 微秒时间源（1us 一格 → 32 位微秒） | HAL 寄存器、`main.h` | `src/app/app_angle.c` |
| `inc/hal/hal_io.h` | `src/hal/hal_io.c` | 35 / 54 | 电机执行器：PB0 PWM(CH3) 占空比 + PA0/1/2 方向与 STBY | HAL、`htim3`、`main.h` | `src/app/app_angle.c` |
| `inc/drivers/as5600.h` | `src/drivers/as5600.c` | 30 / 39 | AS5600 寄存器读、磁场状态串、I2C 扫描 | HAL I2C、`hi2c1`；`console` 仅用于打印 | `src/app/app_angle.c` |
| `inc/core/angle_core.h` | `src/core/angle_core.c` | 50 / 71 | **纯算法**：回绕展开 / 毛刺剔除 / 一阶低通 / 测速限幅 | 只有 `stdint.h`、`stdlib.h` | `src/app/app_angle.c` |
| `inc/core/recorder.h` | `src/core/recorder.c` | 38 / 46 | 1200 样本环形缓冲 + dump 取点 | 只有 `stdint.h` | `src/app/app_angle.c` |
| `inc/core/cmd_parse.h` | `src/core/cmd_parse.c` | 43 / 70 | 一行命令 → 命令码枚举（**纯解析，无副作用**） | 只有 `stdint.h`、`stdlib.h` | `src/app/app_angle.c` |
| `inc/app/console.h` | `src/app/console.c` | 28 / 52 | `log_printf` 双缓冲非阻塞 IT + `TxCpltCallback` + 阻塞开关 | HAL UART、`huart1` | `src/app/app_angle.c`、`src/drivers/as5600.c` |
| `inc/app/app_angle.h` | `src/app/app_angle.c` | 16 / 408 | 对外两个函数；持有全部状态、命令执行、dump 泵、状态行、定时 | 上面全部 | `Core/Src/main.c`（USER CODE 2/3） |

> ⚠️ **新布局带来的唯一额外配置**：因为头文件用"逻辑路径"引用（`#include "core/angle_core.h"`），
> 必须在 Keil 里把 **`…\firmware\app_angle\inc`** 加进 Include Paths 一次。命令行为 `-Iinc`。
> 增加头文件不需要再动工程设置——这正是把 `inc/` 集中成一个入口的好处。

---

## 2. 依赖方向（严格单向，可照着画）

```
                      main.c  (CubeMX 生成)
                         │  app_angle_init() / app_angle_loop()
                         ▼
   ┌─────────────────  app/app_angle.c  ─────────────────┐
   │  状态机 + 2ms 节拍 + 命令执行 + dump 泵 + 状态行      │
   └───┬────────┬────────┬─────────┬─────────┬───────────┘
       │        │        │         │         │
       ▼        ▼        ▼         ▼         ▼
  app/console  drivers/  core/     core/     core/
   (串口)      as5600    angle_core recorder cmd_parse
                  │        │         │         │
                  │        └─────────┴─────────┘
                  │        纯算法：不 include main.h、不碰寄存器
                  ▼
              hal/hal_time ── hal/hal_io      （只有这两个直接碰寄存器/HAL）
```

**唯一一处"向上"的依赖**：`drivers/as5600.c` 的 `i2c_scan()` 要打印扫描结果，所以 include 了
`app/console.h`。这里把 console 当作**通用串口输出工具**（它只依赖 HAL UART，不反向依赖任何模块），
按"等价性优先"保留原版的打印行为，不为分层好看而改输出。

---

## 3. 每个模块的对外接口（面试走读用）

| 模块 | 对外接口 |
|---|---|
| `hal_time` | `timebase_init()`、`micros()` |
| `hal_io` | `hal_io_motor_pwm_start()`、`hal_io_motor_duty(pct)`、`hal_io_motor_dir(dir)`、`hal_io_motor_coast()`、`hal_io_motor_stby(en)`、`hal_io_pwm_psc()/arr()`（只给 banner 用） |
| `as5600` | `as5600_rd_to()`、`as5600_rd()`、`as5600_magnet_str()`、`i2c_scan()` |
| `angle_core` | `angle_core_init()`、`angle_unwrap_update()`、`angle_spike_reject()`、`angle_lpf_step()`、`angle_speed_est()`、`angle_step()`、`angle_mark_read_fail()` |
| `recorder` | `rec_push()`、`rec_count()/rec_head()/rec_total_n()`、`rec_dump_begin()`、`rec_dump_k()`、`rec_ang_at()/rec_dps_at()/rec_duty_at()` |
| `cmd_parse` | `cmd_parse(line) -> cmd_t{code,arg,ch}` |
| `console` | `log_printf()`、`console_tx_busy()`、`console_get/set_nonblock()`、`console_sent()/console_drop()` |
| `app_angle` | `app_angle_init()`、`app_angle_loop()` |

---

## 4. 为什么这么拆（面试话术）

1. **改一个东西，影响范围可预测**：调滤波只碰 `core/angle_core.c`，换算占空比只碰 `hal/hal_io.c`，
   改命令语义只碰 `core/cmd_parse.c` + `app_angle.c` 的一个 case。
2. **算法零硬件依赖 → 能在 PC 上单测**：`core/*.c` 不 include `main.h`、不出现任何寄存器访问
   （自证：`grep -n "HAL_\|__HAL_\|->CR\|->SR" core/*` 输出为空），
   把 `angle_core.c` 丢进 PC 工程喂一串 raw 计数就能验证回绕/毛刺/低通。
3. **分层接口窄**：`hal` 只写寄存器，`drivers` 只读写器件，`core` 只有纯函数，`app` 才有状态与调度。

---

## 5. 纪律与自证（这次重构的边界）

| 约束 | 做法 |
|---|---|
| 数值/格式串/时序不变 | 见 `等价性对照.md` §1/§3/§6；字符串字面量做了集合比对，原文件 39 条纯 ASCII 字面量全部命中 |
| v10/v11/v12 的实验开关与诊断全部保留 | `f`/`b` 实验开关、`p`/`w` 命令、v12 ORE 兜底轮询 + `rx=/cmd=/rxerr=` 计数，逐条列在 `等价性对照.md` §7/§8 |
| 不"顺手修 bug" | 原版 10 处可疑行为（`uint16_t` 角度回绕、丢帧前覆盖在途缓冲、毛刺拍也记录…）**原样保留**，列在 §8 |
| 中文只在注释、串口输出纯 ASCII | 16 个源文件"删注释后非 ASCII 字符数 = 0" |
| 编码 | 全部 UTF-8 **无 BOM** |
| 原件只读 | `firmware/app_angle.c`、`app_angle.h`、`app_motor.*`、`README.md` **一个字节都没改** |

---

## 6. 编译验证（离线 arm-none-eabi-gcc，**已实测**）

用 STM32CubeIDE 1.19 自带的 `arm-none-eabi-gcc 13.3.1` + ST F1 HAL 头文件做 `-c`（只编译不链接）：

```powershell
# 检查脚本（只读使用，脚本自身带 BOM）
$p='D:\harness\学业\yf105招新\25级-倒立摆实物\firmware\_build\compile_check.ps1'
& $p -SrcDir 'D:\harness\学业\yf105招新\25级-倒立摆实物\firmware\app_angle' -Name mod_v3
# 也可以只查 8 个 .c，得到干净的"每模块未定义符号"表：
& $p -SrcDir '<...>\firmware\app_angle' -Name mod_files -Files hal/hal_time.c,hal/hal_io.c,drivers/as5600.c,core/angle_core.c,core/recorder.c,core/cmd_parse.c,app/console.c,app/app_angle.c
```

**结果（Lead 复核：v2 脚本，只编 `.c`、`.o` 按相对路径命名）**

```
=== COMPILE CHECK: lead_mod_v2 (8 .c files) ===
RESULT: all 8 .c files compiled OK           ← 0 FAIL
```

> ⚠️ 早期 v1 脚本报 "all 19 files" 是**脚本自身的 bug**（把 `.md`/`.h` 也当源文件编译，
> 且不同目录的同名文件生成同名 `.o` 互相覆盖，导致"全部 OK 但符号表为空"的假绿灯）。
> Lead 已修脚本并重跑：**真实的 8 个 `.c` 全部编译通过，0 FAIL**，结论不变。

8 个模块全部 `warnings=0`，只有 `app/app_angle.c` 有 **1 条** `'g_zero' defined but not used`
—— 这条是**故意继承**的：原 `app_angle.c` 编译后也只有这 1 条同款警告（`g_zero` 在原文件里
只出现在第 71 行的声明处）。**警告数量与原版一致**，也是等价性的一个信号。

**分层自证（`nm -u` 未定义符号 = 该模块还依赖谁）**

| .o | 未定义符号 | 判读 |
|---|---|---|
| `core/angle_core.o` | *（空）* | **零硬件依赖**，连 libc 都不用 |
| `core/recorder.o` | *（空）* | **零硬件依赖** |
| `core/cmd_parse.o` | `atoi` | 只依赖 libc |
| `hal/hal_time.o` | *（空）* | 只写 TIM2 寄存器，不需要外部 HAL 函数 |
| `hal/hal_io.o` | `HAL_GPIO_WritePin, HAL_TIM_PWM_Start, htim3` | 允许出现 HAL_* |
| `drivers/as5600.o` | `HAL_I2C_IsDeviceReady, HAL_I2C_Mem_Read, hi2c1, log_printf` | 器件层 |
| `app/console.o` | `HAL_UART_Transmit, HAL_UART_Transmit_IT, huart1, vsnprintf` | 串口输出 |
| `app/app_angle.o` | 上面全部模块的 API + HAL 胶水 | 应用层 |

**结论：`core/` 三个 .o 的依赖里没有 `HAL_*`、没有 `hi2c1/htim3/huart1`** ——
这正是"算法能在 PC 上单测"的硬证据（判据来自原版基线：原 `app_angle.o` 的依赖是
`atoi, HAL_Delay, HAL_GetTick, HAL_GPIO_WritePin, HAL_I2C_*, HAL_NVIC_*, HAL_RCC_GetPCLK1Freq,
HAL_TIM_PWM_Start, HAL_UART_*, hi2c1, htim3, huart1, vsnprintf`，被拆成了 4 个叶子模块）。

> ✅ 编译层已过。**仍未做**：Keil 工程级链接（AC5/AC6 语法差异、`USART1_IRQHandler` 是否与
> `stm32f1xx_it.c` 重复）与上板时序 —— 见 [`main.md`](main.md) §8 的手工清单。
> **Include Paths 现在需要配一次 `…\firmware\app_angle\inc`**（新布局的唯一额外配置，
> 见 §1 的警告框与 `main.md` §2）。
