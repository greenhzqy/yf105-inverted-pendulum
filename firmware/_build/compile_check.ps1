# compile_check.ps1 - firmware offline compile check (no Keil, no board needed)
#
# Uses arm-none-eabi-gcc (bundled with STM32CubeIDE 1.19) + the ST F1 HAL headers to
# compile firmware sources into .o files, verifying:
#   1) each file compiles (syntax / types / missing headers)
#   2) which symbols each .o still needs (= what that module depends on)
# No linking (no startup / linker script needed) - compiling catches most mistakes
# made while moving code between files.
#
# v2 fixes (found while reviewing another agent's run):
#   - only *.c files are compiled (`-Include` with -Recurse also matched *.h/*.md)
#   - object files are named by RELATIVE path, not by BaseName, so two files with the
#     same base name in different directories no longer overwrite each other
#     (that bug produced a "all OK" result with empty symbol tables = false green)
#
# ASCII-only string literals on purpose: Windows PowerShell 5.1 reads .ps1 as GBK
# unless the file starts with a UTF-8 BOM, which would corrupt non-ASCII literals.
# This file contains non-ASCII paths, so it MUST keep its BOM.
#
# Usage:
#   & .\compile_check.ps1 -SrcDir <dir> -Name <tag>
#   & .\compile_check.ps1 -Files a.c,b.c -Name <tag>
param(
    [string]$SrcDir,
    [string[]]$Files,
    [string]$Name = 'firmware',
    [switch]$KeepGoing
)

$ErrorActionPreference = 'Continue'          # native stderr must not abort the script

$BIN = 'D:\STM32CubeIDE_1.19.0\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.gnu-tools-for-stm32.13.3.rel1.win32_1.0.0.202411081344\tools\bin'
$GCC = Join-Path $BIN 'arm-none-eabi-gcc.exe'
$NM = Join-Path $BIN 'arm-none-eabi-nm.exe'
$FW = 'D:\FreeRTOS learning\1.2 部署开发环境\stm32f1固件包\STM32Cube_FW_F1_V1.8.7'
$CONF = 'D:\STM32小车工程\blink\Core\Inc\stm32f1xx_hal_conf.h'

foreach ($p in @($GCC, $NM, $CONF, "$FW\Drivers\STM32F1xx_HAL_Driver\Inc", "$FW\Drivers\CMSIS\Device\ST\STM32F1xx\Include", "$FW\Drivers\CMSIS\Include")) {
    if (-not (Test-Path -LiteralPath $p)) { throw "missing dependency: $p" }
}

$work = Join-Path $env:TEMP "fwcheck_$Name"
if (Test-Path $work) { Remove-Item $work -Recurse -Force }
New-Item -ItemType Directory -Path $work | Out-Null
New-Item -ItemType Directory -Path "$work\stub" | Out-Null
$enc = New-Object System.Text.UTF8Encoding($false)

# ---- stub main.h: same shape as the CubeMX-generated one (declarations only) ----
$stub = @'
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

#include "stm32f1xx_hal.h"

void Error_Handler(void);

extern I2C_HandleTypeDef  hi2c1;
extern TIM_HandleTypeDef  htim3;
extern UART_HandleTypeDef huart1;

#ifdef __cplusplus
}
#endif
#endif /* __MAIN_H */
'@
[System.IO.File]::WriteAllText("$work\stub\main.h", $stub, $enc)

# ---- HAL conf: donor project config, force-enable exactly the modules we use ----
Copy-Item -LiteralPath $CONF -Destination "$work\stub\stm32f1xx_hal_conf.h" -Force
$confPath = "$work\stub\stm32f1xx_hal_conf.h"
$confTxt = [System.IO.File]::ReadAllText($confPath)
foreach ($mod in 'HAL_I2C_MODULE_ENABLED', 'HAL_TIM_MODULE_ENABLED', 'HAL_UART_MODULE_ENABLED') {
    $confTxt = $confTxt -replace "(?m)^\s*/\*\s*#define\s+$mod\s*\*/\s*$", "#define $mod"
}
[System.IO.File]::WriteAllText($confPath, $confTxt, $enc)

# include the stub dir plus every directory that contains a source we compile
$incDirs = @()
if ($SrcDir) {
    # 兼容"头文件与源文件分目录"的布局：<root>/inc 自动进 Include Paths
    foreach ($cand in @((Join-Path $SrcDir 'inc'), (Join-Path $SrcDir 'include'))) {
        if (Test-Path -LiteralPath $cand) { $incDirs += $cand
            Get-ChildItem -LiteralPath $cand -Recurse -Directory | ForEach-Object { $incDirs += $_.FullName }
        }
    }
}
$srcDirs = @()
if ($Files) {
    $srcs = foreach ($f in $Files) {
        $full = $f
        if (-not (Test-Path -LiteralPath $full)) { $full = Join-Path $SrcDir $f }
        Get-Item -LiteralPath $full
    }
    $srcDirs = @($srcs | ForEach-Object { $_.DirectoryName } | Sort-Object -Unique)
}
else {
    if (-not $SrcDir) { throw "give -SrcDir or -Files" }
    $srcs = Get-ChildItem -LiteralPath $SrcDir -Recurse -File |
            Where-Object { $_.Extension -eq '.c' -and $_.Name -notmatch '^_' -and $_.Name -ne 'app_motor.c' }
    $srcDirs = @($srcs | ForEach-Object { $_.DirectoryName } | Sort-Object -Unique)
}
if (-not $srcs) { throw "no .c files to check" }

$incs = @("-I$work\stub") + @($incDirs | Sort-Object -Unique | ForEach-Object { "-I$_" }) + @($srcDirs | ForEach-Object { "-I$_" }) + @(
    "-I$FW\Drivers\STM32F1xx_HAL_Driver\Inc",
    "-I$FW\Drivers\CMSIS\Device\ST\STM32F1xx\Include",
    "-I$FW\Drivers\CMSIS\Include"
)
$cflags = @('-c', '-mcpu=cortex-m3', '-mthumb', '-std=gnu11', '-Wall', '-Wextra',
            '-DSTM32F103xB', '-DUSE_HAL_DRIVER', '-O1', '-g0') + $incs

Write-Host "=== COMPILE CHECK: $Name ($(@($srcs).Count) .c files) ===" -ForegroundColor Cyan
$objs = @()
$fail = 0
$idx = 0
foreach ($s in @($srcs)) {
    $idx++
    $obj = Join-Path $work ("{0:d2}_{1}.o" -f $idx, $s.BaseName)
    $gccArgs = $cflags + @('-o', $obj, $s.FullName)
    $out = (& $GCC @gccArgs 2>&1 | Out-String)
    if ($LASTEXITCODE -ne 0) {
        $fail++
        Write-Host "[FAIL] $($s.Name)" -ForegroundColor Red
        foreach ($line in ($out -split "`r?`n" | Where-Object { $_ -match '\S' -and $_ -notmatch 'CategoryInfo|FullyQualifiedErrorId|^\s*\+' } | Select-Object -First 30)) {
            Write-Host "   $line" -ForegroundColor DarkRed
        }
        if (-not $KeepGoing) { }
    }
    else {
        $wl = @($out -split "`r?`n" | Where-Object { $_ -match 'warning:' })
        Write-Host ("[ OK ] {0,-40} warnings={1}" -f $s.Name, $wl.Count) -ForegroundColor Green
        $wl | Select-Object -First 8 | ForEach-Object { Write-Host "   $_" -ForegroundColor DarkYellow }
        $objs += [pscustomobject]@{ Obj = $obj; Src = $s }
    }
}

Write-Host ""
Write-Host "--- undefined symbols per .o (= what this module still needs) ---" -ForegroundColor Cyan
foreach ($o in $objs) {
    $u = @()
    $raw = (& $NM -u $o.Obj 2>&1 | Out-String) -split "`r?`n"
    foreach ($line in $raw) {
        if ($line -match '^\s*U\s+(\S+)\s*$') {
            $sym = $Matches[1]
            if ($sym -notmatch '^(__aeabi|_aeabi)') { $u += $sym }
        }
    }
    $u = @($u | Sort-Object -Unique)
    Write-Host ("  {0,-22} ({1,-16}) -> {2}" -f $o.Src.Name, (Split-Path (Split-Path $o.Src.FullName -Parent) -Leaf), ($u -join ', '))
}

Write-Host ""
if ($fail) { Write-Host "RESULT: $fail file(s) FAILED to compile" -ForegroundColor Red; exit 1 }
Write-Host "RESULT: all $(@($objs).Count) .c files compiled OK" -ForegroundColor Green
Write-Host "artifacts: $work"
