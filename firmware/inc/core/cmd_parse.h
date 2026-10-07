/* =====================================================================
 *  inc/core/cmd_parse.h  ·  一行命令 -> 命令码（纯解析，只读输入、不改任何状态）
 *
 *  职责：把串口收到的一行（已按原版截断到 15 字符）映射成命令码 + 参数
 *  依赖：只依赖 <stdint.h>/<stdlib.h>（atoi），零硬件、零 HAL 调用
 *  被谁调用：inc/core/cmd_parse.h 的定义被 src/app/app_angle.c 使用 的 app_angle_loop()（解析后由 app 执行副作用）
 *
 *  与原 app_angle.c 的对应：原第 413~499 行 switch(t[0]) 的"分派部分"
 *  ★ p/w 的钳位（原第 460~462、479~481 行）也放在这里，因为它是"输入合法性"，
 *    属于解析；执行副作用（开电机、打 log）仍全部留在 app 层
 *  WALK_DUTY_MAX=40 与原版同值
 * ===================================================================== */
#ifndef __CMD_PARSE_H
#define __CMD_PARSE_H

#include <stdint.h>

#define WALK_DUTY_MAX 40      /* 慢转占空比上限（保护电机/驱动），与原版同值 */

typedef enum {
    CMD_NONE = 0,             /* 不会返回：cmd_ready 只在一行非空时置位 */
    CMD_MOTOR,                /* m/M */
    CMD_DIR,                  /* r/R */
    CMD_STOP,                 /* s/S */
    CMD_ZERO,                 /* z/Z */
    CMD_QUIET,                /* q/Q */
    CMD_SCAN,                 /* i/I */
    CMD_HELLO,                /* k/K */
    CMD_DUMP,                 /* d/D */
    CMD_EXP_FAST,             /* f/F */
    CMD_EXP_TX,               /* b/B */
    CMD_PULSE,                /* p<v>/P<v>：v 已钳位到 [-100,100] */
    CMD_WALK,                 /* w<v>/W<v>：v 已钳位到 [-WALK_DUTY_MAX,+WALK_DUTY_MAX] */
    CMD_UNKNOWN               /* 其它字符 */
} cmd_code_t;

typedef struct {
    cmd_code_t code;
    int        arg;           /* 仅 CMD_PULSE/CMD_WALK 有意义：atoi(&line[1]) 并钳位后的值 */
    char       ch;            /* 原始首字符（未知命令时用于打印 0x%02X） */
} cmd_t;

/* 输入 line[0] 必须是命令首字符；line 为 NUL 结尾、长度不超过 15 的字符串 */
cmd_t cmd_parse(const char *line);

#endif /* __CMD_PARSE_H */
