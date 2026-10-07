# main.md · 把 `firmware/app_angle/` 挂进 CubeMX + Keil 的手工验证清单

> ⚠️ 本机**没有** ARM/Keil 工具链，也没有主机 C 编译器 —— 这份清单是**唯一**的编译/上板验证途径，
> 请按顺序做完并在 §8 的勾选框上打勾。任何一步的输出与"期望"不一致，先停下来查 §9 的报错对照表。

前置假设（与 `firmware/CubeMX_配置清单.md` 一致）：
- 芯片 STM32F103C8Tx，HCLK 72MHz，APB1 36MHz；TIM3 CH3 = PB0（PSC=0, ARR=3599）；
  USART1 115200 8N1（PA9/PA10）；PA0/PA1/PA2 = GPIO_Output 初始 Low；I2C1 = PB6/PB7（AS5600）。
- 工程是 CubeMX 生成的 MDK-ARM 工程，`Core/Inc/main.h`、`htim3`、`huart1`、`hi2c1` 都已存在。

---

## 1. 把目录放进工程

推荐做法（不动 CubeMX 的目录约定）：把整个 `firmware/app_angle` 文件夹复制到 Keil 工程目录旁边，
例如工程在 `...\MDK-ARM\`，就放成 `...\firmware\app_angle\`（本仓库就是这种相对关系，直接用即可）。

```
firmware/
  app_angle.c            ← 原件保留（只读对照件，不要加进工程）
  app_angle.h            ← 原件保留（只读对照件）
  app_motor.c/.h         ← S1 遗留，不要与新模块同时编译（见 §4）
  app_angle/             ← 新模块
    README.md   main.md   等价性对照.md
    inc/  hal/{hal_time,hal_io}.h   drivers/as5600.h
          core/{angle_core,recorder,cmd_parse}.h   app/{console,app_angle}.h
    src/  hal/{hal_time,hal_io}.c   drivers/as5600.c
          core/{angle_core,recorder,cmd_parse}.c   app/{console,app_angle}.c
```

---

## 2. Keil：新建 Group 并加入 8 个 .c

`Project` 面板里右键工程名 → **Manage Project Items…**（或右键某个 Group → *Add Group…*）

- 新建一个 Group，命名为 `app_angle`
- 选中它 → 右键 → **Add Existing Files to Group 'app_angle'…**，文件类型选 `All files (*.*)`，依次加入：

| 顺序 | 文件 |
|---|---|
| 1 | `app_angle/src/hal/hal_time.c` |
| 2 | `app_angle/src/hal/hal_io.c` |
| 3 | `app_angle/src/drivers/as5600.c` |
| 4 | `app_angle/src/core/angle_core.c` |
| 5 | `app_angle/src/core/recorder.c` |
| 6 | `app_angle/src/core/cmd_parse.c` |
| 7 | `app_angle/src/app/console.c` |
| 8 | `app_angle/src/app/app_angle.c` |

> Keil **不会**自动收录新文件 —— 只把文件夹拷过去是编不进去的，必须手工 Add。
> 头部文件（.h）不用加，靠 Include Paths 找。

---

## 3. Keil：Include Paths（本版**必须加一条**）

因为头文件已按"**inc/ 放接口、src/ 放实现**"分目录，源文件里用**逻辑路径**引用头文件
（例如 `src/app/app_angle.c` 里写的是 `#include "core/angle_core.h"`）。
所以要把**头文件根目录**加进 Include Paths：

- `Options for Target` → **C/C++** → `Include Paths` → 添加：
  `..\..\25级-倒立摆实物\firmware\app_angle\inc`（用 Keil 的浏览按钮选到 `app_angle\inc` 这一层即可）
- `Core\Inc` 原本就在 Include Paths 里，**别删**（`main.h` 靠它）。

> 只需加**一条**（`inc/` 的根），`hal/hal_time.h`、`core/angle_core.h` 这些子路径 Keil 会自己拼。
> 以后新增头文件不用再改工程设置——这就是 `inc/` 集中成一个入口的好处。
>
> ⚠️ 新旧两个 `app_angle.h` 同名：如果 `firmware` 根目录也在 Include Paths 里，Keil 按顺序取其中一个。
> 两个文件内容一致（含相同的 include guard），**不会报重定义**；
> 但为了走读不串味，建议把 `firmware` 根目录从 Include Paths 里去掉。

## 4. Keil：把旧的两个文件移出编译（**不要删磁盘文件**）

| 文件 | 处理 | 原因 |
|---|---|---|
| `firmware/app_angle.c` | 右键 → **Remove File 'app_angle.c'** | 与新 `src/app/app_angle.c` 里的 `app_angle_init/loop`、`USART1_IRQHandler`、`HAL_UART_*Callback` 全部重复 → 一堆 L6200E |
| `firmware/app_motor.c` | 同样 Remove | 它定义了 `HAL_UART_RxCpltCallback`（第 105 行）和 `app_motor_init/loop`，与新版**符号冲突**；S1 已由 S2 取代 |

> 面试要讲的点：**app_motor.c 是 S1 遗留版，不和 app_angle 新版同时编译**（重复 UART 回调符号）。
> 用新版替代它不是"旧版不好"，是**接口冲突**。

---

## 5. main.c 三处 USER CODE 挂载（before / after）

CubeMX 重新生成代码**不会**覆盖 USER CODE 区，所以只改这三处。**不要整份覆盖 main.c**
（`firmware/README.md` 里记过这个坑：会删掉 `SystemClock_Config` 与 `MX_*_Init` → 6 个 L6218E）。

**① USER CODE BEGIN Includes**

```c
/* >>> before（CubeMX 骨架原样） */
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* >>> after */
/* USER CODE BEGIN Includes */
#include "app_angle.h"
/* USER CODE END Includes */
```

**② USER CODE BEGIN 2**（`MX_*_Init()` 都跑完之后）

```c
/* >>> before */
  /* USER CODE BEGIN 2 */

  /* USER CODE END 2 */

/* >>> after */
  /* USER CODE BEGIN 2 */
  app_angle_init();
  /* USER CODE END 2 */
```

**③ USER CODE BEGIN 3**（`while (1)` 里）

```c
/* >>> before */
  while (1)
  {
    /* USER CODE BEGIN 3 */

    /* USER CODE END 3 */
  }

/* >>> after */
  while (1)
  {
    /* USER CODE BEGIN 3 */
    app_angle_loop();
    /* USER CODE END 3 */
  }
```

改完：**Rebuild**（不是 Build，避免旧对象文件残留）→ 0 Error 0 Warning 后再下载。

---

## 6. 期望开机 banner（逐字）

打开串口助手：**115200 8N1**，勾上"发送新行 / 追加回车换行"，复位板子，应当看到：

```

==== app_angle v12 : tick + angle + p/w cmd + rx fix ====
TIM3 psc=0 arr=3599 -> pwm=20000Hz | sample=2000us (500Hz) | win=500ms
filter: alpha=0.35 (1st-order LPF) | jump max=150 counts (~13.2deg) | dps limit=1500
record buffer: 1200 samples (2.4s @500Hz)
I2C scan: 0x36
AS5600 STATUS=0x20 MAG=OK
cmd: m r s z q i k | p<pct>=pulse | w<pct>=slow walk | d=dump CSV | f/b = exp
tip: send with CR/LF (check 'append newline'); watch RX rx= cmd= rxerr=
```

逐字核对要点：
- 第 2 行 `pwm=20000Hz`（`psc/arr` 是实读 `htim3`，不是写死的）；
- `sample=2000us (500Hz)`、`win=500ms`；
- 第 3 行 `alpha=0.35`、`jump max=150`、`dps limit=1500`（都是宏实参）；
- `I2C scan:` 后面应当出现 ` 0x36`；如果打 ` (none)`，先查 PB6/PB7 与 AS5600 供电；
- `AS5600 STATUS=0x20 MAG=OK`（磁铁没装好会是 `WEAK`/`STRONG`/`NONE`，不影响后续命令）；
- `AS5600 no answer!` 说明第一次读 STATUS 失败 —— 但**这不是新引入的问题**，原件行为相同（原 368 行）。

随后每 500ms 一行状态行，形状如下（数值随现场变化）：

```
ST th=  -0.3 dps=    0 duty=  0% mot=0 dir=+1 | dt avg=2000 max=2003 min=1998 n=250 over=0 | bad=0 drop=0 | MAG=OK |B|=1234 lo=1234 hi=1234 | rx=0 cmd=0 rxerr=0
```

核对：字段顺序 = `th / dps / duty / mot / dir / dt avg,max,min,n,over / bad,drop / MAG / |B|,lo,hi / rx,cmd,rxerr`；
`dt avg` 应贴近 **2000us**、`max` 别超过 2100 太多；`rx=/cmd=` 要跟着你的敲键增长。

---

## 7. 五步冒烟（k / i / z / w15 / d）

| # | 发送 | 期望输出（逐字） | 要确认什么 |
|---|---|---|---|
| 1 | `k⏎` | `[CMD] HALLO` | 接收链路通；同时 `cmd=` 计数 +1（不是 `rx=` 涨而 `cmd=` 不动） |
| 2 | `i⏎` | `I2C scan: 0x36` | 扫描函数与打印格式；` (none)` 说明器件没应答 |
| 3 | `z⏎` | `[CMD] zero set (unwrap=<某整数>)` | `z` 把当前滤波角度记成零点；随后状态行 `th` 应回到 ≈0.0 |
| 4 | `w15⏎` | `[WALK] duty=15% dir=+1, auto stop in 30000ms (send 's' to stop now)` | 电机以 15% 慢转；状态行尾部 `lo=/hi=` 开始随磁铁起伏（`|B|` 的 min/max）；发 `s⏎` 可立即停（`[CMD] motor STOP`），不发则 30s 后 `[WALK] timeout, motor off` |
| 5 | `d⏎` | `DUMP BEGIN n=1200 (i,th_deg,dps,duty)` → 1200 行 `0,<th>,<dps>,<duty>` … → `DUMP END n=1200 total=<累计> bad=<…> drop=<…>` | 环形缓冲与 dump 泵；**上电后先等 3 秒**再发 `d`，`n` 才会满 1200 |

补充说明（都是**原版行为**，不是新引入的）：
- dump 过程中每 500ms 的 `ST ...` 状态行会**插在数据行中间**（dump 只是"串口空闲就发一行"）；
  画图脚本按"行首是数字"过滤即可。
- 每行 dump 之间要等上一帧 IT 发完，1200 行大约几秒才发完。
- `d` 期间若 `drop=` 在涨，说明丢帧（非阻塞发送的既有机制）。

额外可选（v10/v11/v12 的面试演示点）：`p20`（脉冲 300ms 后 `[PULSE] done, motor off`）、
`f`（`[EXP] print in fast tick = 1`，状态行刷屏、`dt avg` 变差 —— 故意拖垮节拍的实验）、
`b`（`[EXP] tx mode = BLOCKING`，切阻塞发送）、`q`（`[CMD] quiet=1` 静音状态行）。

---

## 8. 手工验证清单（打勾用）

- [ ] **离线编译**先过：`compile_check.ps1` → `all 8 .c files compiled OK`，8 个 .c 里只有 `src/app/app_angle.c` 1 条 `g_zero` 警告
- [ ] `core/*.o` 的未定义符号里没有 `HAL_*` / `hi2c1` / `htim3` / `huart1`（脚本的 `--- undefined symbols ---` 段可直接看）
- [ ] 8 个 .c 已加入 Group `app_angle`
- [ ] 旧 `app_angle.c` 与 `app_motor.c` 已 Remove File（磁盘文件仍在）
- [ ] `main.c` 三处 USER CODE 已改（Includes / 2 / 3）
- [ ] Rebuild **0 Error / 0 Warning**
- [ ] 下载后 banner **逐字**与 §6 一致（尤其 `pwm=20000Hz`、`jump max=150`）
- [ ] 状态行每 500ms 一行、字段顺序与 §6 一致、`dt avg≈2000`
- [ ] 冒烟 1 `k` → `[CMD] HALLO`
- [ ] 冒烟 2 `i` → `I2C scan: 0x36`
- [ ] 冒烟 3 `z` → `[CMD] zero set (unwrap=…)`，之后 `th≈0.0`
- [ ] 冒烟 4 `w15` → `[WALK] duty=15% dir=+1, auto stop in 30000ms (send 's' to stop now)`；`lo=/hi=` 有变化；`s` 能停
- [ ] 冒烟 5 `d` → `DUMP BEGIN n=1200` / 1200 行 CSV / `DUMP END n=1200 total=… bad=… drop=…`
- [ ] 反复发命令 20 次，`cmd=` 每次都 +1（v12 的 ORE 兜底生效）

---

## 9. 报错对照表

| 报错 | 原因 | 处理 |
|---|---|---|
| 离线编译出 FAIL，或出现 `g_zero` 以外的 warning | 新代码被动过 | 先跑 §3b 对答案：8 个 .c 应当 **0 FAIL**，warning 只有 `src/app/app_angle.c` 那 1 条 `g_zero` |
| `L6200E: Symbol HAL_UART_RxCpltCallback multiply defined` | `app_motor.c` 与 `src/app/app_angle.c` 同时编译 | §4：把 `app_motor.c` 从工程移除 |
| `L6200E: Symbol app_angle_init multiply defined` | 旧的 `firmware/app_angle.c` 还在工程里 | §4：Remove File |
| `L6200E: Symbol USART1_IRQHandler multiply defined` | `Core/Src/stm32f1xx_it.c` 里也写了 `USART1_IRQHandler` | 二者只能留一个：注释掉 `it.c` 里那个（保留新版，它转 `HAL_UART_IRQHandler`） |
| `L6218E: Undefined symbol htim3 / huart1 / hi2c1` | CubeMX 里对应外设没生成（TIM3/USART1/I2C1） | 回 CubeMX 勾上外设重新生成，再按 §5 重挂三行 USER CODE |
| `#870-D: invalid multibyte character sequence` | 源文件编码与 Keil 编辑器不一致 | 本目录所有文件都是 **UTF-8 无 BOM**；Keil → Edit → Configuration → Editor → Encoding 选 UTF-8 |
| `cannot open source input file "console.h"` | Include Paths 少了一条 | §3 |
| 命令发过去没反应 | 串口助手没勾"发送新行"；或 `rx=` 在涨但 `cmd=` 不涨 | 勾上追加 CR/LF；看状态行 `rx=/cmd=/rxerr=` 定位（v12 就是为这个加的） |
| 编译不过且报 `angle_core.c` 里的 HAL 相关符号 | 不应该发生 | 该文件只 include `stdint.h`/`stdlib.h`，若报错说明 Include Paths 里混进了同名文件 |

---

## 10. 回退方案

1. Keil 里 Remove 新 Group `app_angle` 的 8 个文件；
2. 把 `firmware/app_angle.c` 与 `app_motor.c`（或按 S2 场景只留 `app_angle.c`）重新 Add 回工程；
3. Include Paths 去掉 `firmware/app_angle/*` 四条；
4. `main.c` 的三处 USER CODE **不用改**（新旧头文件同名、原型一致）。
