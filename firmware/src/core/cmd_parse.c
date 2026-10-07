/* =====================================================================
 *  src/core/cmd_parse.c  ·  命令码解析实现（纯函数：同一输入永远同一输出）
 *
 *  职责：switch(line[0]) -> cmd_code_t，并对 p/w 的数值参数做原版同样的钳位
 *  依赖：cmd_parse.h、<stdlib.h>（atoi）
 *  被谁调用：src/app/app_angle.c
 *
 *  逐行对照原 app_angle.c 第 413~499 行（case 分支与钳位条件一一对应）
 *  ★ 这里不执行任何副作用：不开电机、不打印、不改全局
 * ===================================================================== */
#include "cmd_parse.h"
#include <stdlib.h>

cmd_t cmd_parse(const char *line)
{
    cmd_t c;

    c.code = CMD_NONE;
    c.arg  = 0;
    c.ch   = line[0];

    switch (line[0]) {
    case 'm': case 'M':
        c.code = CMD_MOTOR;
        break;
    case 'r': case 'R':
        c.code = CMD_DIR;
        break;
    case 's': case 'S':
        c.code = CMD_STOP;
        break;
    case 'z': case 'Z':
        c.code = CMD_ZERO;
        break;
    case 'q': case 'Q':
        c.code = CMD_QUIET;
        break;
    case 'i': case 'I':
        c.code = CMD_SCAN;
        break;
    case 'k': case 'K':
        c.code = CMD_HELLO;
        break;
    case 'd': case 'D':
        c.code = CMD_DUMP;
        break;
    case 'f': case 'F':
        c.code = CMD_EXP_FAST;
        break;
    case 'b': case 'B':
        c.code = CMD_EXP_TX;
        break;
    case 'p': case 'P': {                 /* 定值脉冲：p<占空比>，如 p20 / p-20 / p0 */
        int v = atoi(&line[1]);
        if (v >  100) v =  100;
        if (v < -100) v = -100;
        c.arg  = v;
        c.code = CMD_PULSE;
        break;
    }
    case 'w': case 'W': {                 /* 慢转：w<占空比>，如 w15 / w-15 / w0 */
        int v = atoi(&line[1]);
        if (v >  WALK_DUTY_MAX) v =  WALK_DUTY_MAX;
        if (v < -WALK_DUTY_MAX) v = -WALK_DUTY_MAX;
        c.arg  = v;
        c.code = CMD_WALK;
        break;
    }
    default:
        c.code = CMD_UNKNOWN;
        break;
    }
    return c;
}
