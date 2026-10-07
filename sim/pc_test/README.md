# PC 端回归测试 · 角度链（不接板子，也能验证算法没被改坏）

> 这一叠东西回答一个问题：**「我把算法搬进模块之后，行为还和原来一样吗？」**
> 答案不是"我看了两遍代码"，而是**跑出来的数字**。

## 这里有什么

| 文件 | 作用 |
|---|---|
| `ref_angle_core.py` | Lead 按原版 `app_angle.c` 第 265~291 行**独立写的 Python 语义模型**（第二条路径） |
| `test_fw_angle_core.py` | **交叉验证**：把固件里真正在用的 `firmware/app_angle/src/core/angle_core.c` 编成 DLL，逐拍逐字段与 Python 模型比对 |

> 固件模块已按"**头文件 inc/、实现 src/**"分目录：
> 被测文件是 `firmware/app_angle/src/core/angle_core.c`，头文件在 `firmware/app_angle/inc/core/`。
> 这里**不再保留第二份 C 副本**——只测真正会上板的那一份，避免两处代码各自漂移。

两条独立路径（Python 模型 / C 模块）得出同一串数字，才敢说"搬迁没走样"。

## 怎么跑

宿主编译器用 Dev-Cpp 自带的 MinGW64（x86_64）——**不能用 arm-none-eabi-gcc**，
它产出的是 ARM 机器码，Python 的 `ctypes` 加载会报 `WinError 193`（不是有效的 Win32 程序）。

```powershell
$py = 'D:\mathmodel\tools\Python312\python.exe'

# 交叉验证：固件 src/core/angle_core.c  vs  独立 Python 模型
& $py -B .\test_fw_angle_core.py
```

## 判据（工程口径，不是"浮点完全相等"）

| 量 | 判据 | 为什么 |
|---|---|---|
| `unwrap` / `lpf` / `lpf_prev` | 相对 1e-5 | 固件是 `float`（32 位），Python 是 64 位 |
| `dps` | **±1 LSB** | 固件存 `int16_t`（截断），参考模型存 float，截断边界上会差 1 |
| `raw` / `bad_run` / `bad_total` | 完全相等 | 整数逻辑，没有精度借口 |

速度公式里的 `1000000.0f`、`360.0f` 等**单精度常量**会让 C 与 double 版差到 1e-4 量级，
这是"两边常量类型不同"，不是"算法不同"——所以要按 LSB 比，而不是要求逐位相同。

## 覆盖场景

1. 匀速正转 3 圈（1500 拍）
2. 来回跨越回绕点（4095↔0）
3. 随机抖动 + 2% 毛刺注入（2000 拍）
4. 连续 5 拍大跳变 → 验证"连续 3 拍才接受新 raw"
5. `dt` 抖动 + `dt=0` + 高速触发 ±1500°/s 限幅
6. 中途 I2C 读失败（`bad_total` 累加）
7. 纯函数边界：`angle_unwrap_update` 全扫描 0 处不一致、毛刺判据 ±150/±151

## 最近一次结果

```
(A) ✅ 全部场景逐拍一致：C 版 angle_core == Python 参考实现
(B) ✅ 固件 core/angle_core.c 与独立 Python 模型逐拍、逐字段一致
```

## 这份测试真正挡住了什么

- 抽取时**运算顺序**写错（先低通后展开、毛刺拍也更新 `unwrap`）→ 前者在稳态看不出来，这里第 2/3 场景立刻红
- **`dps` 类型**从 `int16_t` 变成 `float` → 判据会暴露
- **`dt=0` / dt 抖动**下速度归一化写错 → 场景 5
- **连续 3 拍接受**这条"怪癖"被当成 bug 顺手"优化"掉 → 场景 4

## 还没验证的（诚实清单）

- 浮点**逐位**一致（这里按 1e-5 相对 / ±1 LSB 判，不是 bit-exact）
- 整机链接（`arm-none-eabi-ld`）与上板时序 —— 需要 Keil 与实物
- `console.c` 的双缓冲/丢帧相位、`recorder.c` 的环形缓冲语义，本叠测试未覆盖（只覆盖角度链）
