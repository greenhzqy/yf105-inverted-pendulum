# -*- coding: utf-8 -*-
"""生成《电机直驱倒立摆自动平衡控制系统》设计报告 docx（直驱摆版本）。
结构：封面 / 摘要 / 一、系统方案设计与论证 / 二、理论分析与计算 /
三、电路与程序设计 / 四、测试方案与测试结果 / 五、结论 / 六、参考文献 / 附录。
"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, 'figs')                      # 旧（小车）图，仅在需要时用
SIM = os.path.join(HERE, '..', '25级-倒立摆控制', 'direct_sim', 'figs')   # 直驱摆仿真图
PHYS = os.path.join(HERE, '..', '25级-倒立摆实物', 'figs')
OUT = os.path.join(HERE, '电机直驱倒立摆自动平衡控制系统-设计报告-曾庆源.docx')

SONG, HEI = '宋体', '黑体'


def set_font(run, name_cn=SONG, size=12, bold=False, name_en='Times New Roman'):
    run.font.name = name_en
    run.font.size = Pt(size)
    run.font.bold = bold
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:eastAsia'), name_cn)
    rFonts.set(qn('w:ascii'), name_en)
    rFonts.set(qn('w:hAnsi'), name_en)


def para(doc, text, size=12, bold=False, cn=SONG, align=None, space_after=6,
         line=1.5, first_indent=None):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.line_spacing = line
    if first_indent:
        pf.first_line_indent = Pt(first_indent)
    r = p.add_run(text)
    set_font(r, cn, size, bold)
    return p


def h1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.5
    set_font(p.add_run(text), HEI, 14, True)
    return p


def h2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.5
    set_font(p.add_run(text), HEI, 12, True)
    return p


def body(doc, text, indent=24):
    return para(doc, text, size=12, first_indent=indent)


def body_noindent(doc, text):
    return para(doc, text, size=12)


def caption(doc, text):
    return para(doc, text, size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10, line=1.2)


def add_fig(doc, path, width_cm, cap):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.add_run().add_picture(path, width=Cm(width_cm))
    caption(doc, cap)


def table(doc, rows, widths=None, font_size=10.5, cap=None):
    if cap:
        para(doc, cap, size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4, line=1.2)
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = t.cell(i, j)
            p = cell.paragraphs[0]
            p.text = ''
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            set_font(p.add_run(str(val)), SONG, font_size, bold=(i == 0))
    if widths:
        for j, w in enumerate(widths):
            for i in range(len(rows)):
                t.cell(i, j).width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


# =====================================================================
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(3.17)
sec.top_margin = sec.bottom_margin = Cm(2.54)

# ---------------- 封面 ----------------
for _ in range(3):
    doc.add_paragraph()
para(doc, '重庆邮电大学', size=26, bold=True, cn=HEI, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=30)
para(doc, '电机直驱倒立摆自动平衡控制系统', size=22, bold=True, cn=HEI,
     align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)
para(doc, '设 计 报 告', size=18, bold=True, cn=HEI, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=40)
for _ in range(2):
    doc.add_paragraph()
para(doc, '作　者：曾庆源', size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
para(doc, '学　院：自动化学院', size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
para(doc, '专　业：智能车辆工程', size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
para(doc, '学　号：2025216060', size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
para(doc, '（2025 级）', size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
doc.add_page_break()

# ---------------- 摘要 ----------------
h1(doc, '摘　要')
body(doc, '本设计完成一套“电机直驱倒立摆”系统：12V 减速电机的输出轴经联轴器、法兰直接驱动摆杆，'
          '基座固定不动（不使用小车与导轨），AS5600 磁编码器测量摆杆绝对角度，STM32F103C8T6 以 2ms（500Hz）'
          '周期完成“测量—角度链—控制—安全—执行”闭环。')
body(doc, '实物部分（已完成并实机验收）：打通“数字→力”（TIM3 20kHz PWM → TB6612 → 电机）与“角度→数”'
          '（轴端磁铁 → AS5600 → I2C → 角度）两条链路；建立 2ms 硬节拍（实测 dt=2000±2µs、零漏拍），'
          '并实现回绕修正、展开量低通、差分限幅的角度/角速度链路与环形缓冲数据记录。')
body(doc, '控制算法部分在与实物同结构的仿真平台上完成设计与验证（Python，2 状态模型：'
          'I·θ̈ = k_g·sinθ − τ_f − τ_m）。实物参数决定了本系统的核心矛盾：摆杆重力矩仅约 11.8 mN·m，'
          '而减速箱输出轴静摩擦约 5 mN·m、占重力矩 40% 以上，使系统存在明显的摩擦死区。'
          '仿真结果表明：纯 PD 与 2 状态 LQR 的力矩在小角度下压不过静摩擦，摆杆会停在死区内（残差 2~6.5°）；'
          '引入积分（PID）后，积分项累积到足以跨过死区：10° 初始偏差 0.52s 进入 ±3° 带，此后在直立附近呈 ±2° 量级的摩擦极限环；小角度起步另有定点残差，2° 起步 1.20s 收敛到 −0.51°；'
          '参数失配（杆质量 +50%、杆长 +20%、摩擦×2）下仍 0.91s 收敛；能量起摆可从下垂 180° 泵到直立'
          '并在 18.0s 稳定（残差 +0.23°）；采样周期稳定到 30ms（设计点 2ms，裕量约 15 倍）；'
          '传感器断连、占空比持续饱和、看门狗分别可在 38ms、58ms、20ms 内检测并急停；'
          '强扰动下可先降级回起摆再自动重新捕获。')
para(doc, '关键词：倒立摆；STM32；AS5600；PID；摩擦死区；能量起摆；安全监控', size=12, bold=True, space_after=12)
doc.add_page_break()

# ---------------- 一、方案设计与论证 ----------------
h1(doc, '一、系统方案设计与论证')

h2(doc, '1.1 系统总体方案')
body(doc, '本任务要求制作一台由电机直驱摆杆的倒立摆：让摆杆从下垂荡起并保持直立，轻推后能自动回正，'
          '并具备必要的安全保护。系统总体方案如图 1 所示：主控 STM32F103C8T6 通过 TIM3 输出 20kHz PWM，'
          '经 TB6612 驱动 12V 减速电机；电机轴经联轴器、法兰与摆杆刚性连接，电机力矩直接作用于摆杆转轴；'
          '轴端磁铁随轴转动，AS5600 经 I2C 输出 12bit 绝对角度；上位机通过串口（115200）双向通信。')
body(doc, '与“小车倒立摆”不同，本系统的基座固定接地，不存在小车位置与导轨，'
          '因此被控对象只有 2 个状态（摆角 θ、角速度 ω），控制量是电机力矩（由占空比映射）。'
          '硬件链路（S1~S2）已完成并实测验收；平衡控制、起摆与安全逻辑在与实物同结构的仿真平台上完成'
          '设计与验证，作为移植到实物的依据。')
add_fig(doc, os.path.join(SIM, 'D1_结构与控制回路.png'), 15.0,
        '图 1　系统结构与控制回路（基座固定、电机直驱摆杆，2ms 闭环）')

h2(doc, '1.2 角度检测方案论证与选择')
body(doc, '方案一：AS5600 磁编码器。芯片测量轴端磁铁的磁场方向，经 I2C 输出 12bit 数字量，'
          'deg = RAW/4096×360 再减标定零点；绝对角度，上电即知摆杆位置、转多少圈都不累计误差；'
          '直驱结构下转轴与编码器天然同轴，安装只需对径充磁磁铁与 1~2mm 间隙（|B| 读数 1000+ 为合格）。'
          '实物验证：角度从 0° 平滑扫至 360°、转动一整圈 |B| 波动小于 10%、MAG=OK。')
body(doc, '方案二：MPU6050 六轴 IMU。可融合出姿态角，但存在温漂与积分漂移，且传感器需随摆杆运动、'
          '额外走线，对轻质摆杆还会引入配重与惯量误差。')
body(doc, '方案三：增量式光电编码器。安装在电机尾部需占用轴向空间，上电需回零，无法直接得到绝对角度。')
body(doc, '综合比较，直驱结构下 AS5600 的绝对角度特性最契合“上电即知位置”的需求，故选方案一（表 1）。')
table(doc, [
    ['方案', '精度/特性', '安装复杂度', '累计误差', '结论'],
    ['AS5600 磁编码器', '12bit 绝对角度，0.088°/count', '低（轴端磁铁）', '无', '√ 选用'],
    ['MPU6050 六轴 IMU', '姿态融合，受温漂影响', '中（随摆杆走线）', '有（积分）', '不选'],
    ['增量式编码器', '精度高，但需回零', '中（电机尾部）', '无（相对量）', '不选'],
], widths=[3.6, 4.2, 3.4, 2.0, 1.8], cap='表 1　角度检测方案对比')

h2(doc, '1.3 电机驱动方案论证与选择')
body(doc, '方案一：直流减速电机 + TB6612 双 H 桥驱动。TB6612 由 20kHz PWM 控制占空比、AIN1/AIN2 控制方向、'
          'STBY 使能；控制简单、成本低、动态响应快，且减速箱输出力矩足以驱动摆杆并克服自身摩擦。'
          '本项目选用，实测电机按档位转动、换向与急停均正常。')
body(doc, '方案二：步进电机。开环定位好，但力矩波动、响应慢，且驱动器成本高，不适合连续力矩输出的镇定任务。')
body(doc, '方案三：FOC 无刷云台电机。力矩纹波小、响应快，但驱动与算法复杂、成本高，超出本任务需要。')
table(doc, [
    ['方案', '响应/力矩特性', '驱动复杂度', '成本', '结论'],
    ['直流减速电机+TB6612', '连续力矩，响应快', '低（PWM+方向）', '低', '√ 选用'],
    ['步进电机', '低速力矩波动，响应慢', '中（需驱动器）', '中', '不选'],
    ['FOC 无刷云台电机', '力矩纹波小，响应极快', '高（FOC 算法）', '高', '不选'],
], widths=[3.6, 4.4, 3.2, 1.6, 1.8], cap='表 2　电机驱动方案对比')

h2(doc, '1.4 控制算法方案论证与选择')
body(doc, '方案一：纯 PD（u = kp·e + kd·ω）。这是转轴直驱摆最直观的方案（符号确定后即可闭环）。'
          '但仿真表明：本系统重力矩（约 11.8 mN·m）与减速箱静摩擦（约 5 mN·m）同量级，'
          '在小角度下 PD 输出力矩压不过静摩擦，摆杆会停在死区内不再回中——实测残差 2.0°（2° 起步）'
          '到 6.5°（10° 起步）。')
body(doc, '方案二：PID（PD + 位置积分）。积分项随时间累积，直到输出力矩足以跨过静摩擦死区。'
          '其表现与初始偏差大小有关：10° 起步时 0.52s 进入 ±3° 带，此后在直立附近呈 ±2° 量级的'
          '摩擦极限环（受摩擦限制不会严格收敛到 0°）；小角度起步则可消除稳态误差，'
          '2° 起步 1.20s 收敛到 −0.51°。本项目选用为平衡控制器。')
body(doc, '方案三：LQR 状态反馈。对 2 状态对象，LQR 得到的是“用加权矩阵系统性设计出来的一组 PD 增益”，'
          '结构上与 PD 等价；它同样不含积分，仿真中同样卡在死区（末值 6.51°）。'
          '故本项目中 LQR 作为系统性设计的对照与验证，而非最终方案。')
body(doc, '综合比较：选择方案二 PID 作为平衡控制器，并以 PD、LQR 作为对照组用数据说明取舍（表 3）。')
table(doc, [
    ['方案', '结构', '能否跨摩擦死区', '仿真残差', '结论'],
    ['纯 PD', '角度+角速度反馈', '否（力矩不够）', '2.03° / 6.55°', '对照'],
    ['PID（PD+积分）', '增加积分项', '是（累积出力）', '±2° 极限环 / −0.51°', '√ 选用'],
    ['LQR（2 状态）', '加权最优状态反馈', '否（无积分）', '6.51°', '对照'],
], widths=[3.2, 3.8, 3.6, 3.2, 1.6], cap='表 3　控制算法方案对比')

# ---------------- 二、理论分析与计算 ----------------
h1(doc, '二、理论分析与计算')

h2(doc, '2.1 被控对象建模（转轴直驱摆）')
body(doc, '摆杆绕固定转轴转动，取 θ 为相对直立的偏角（θ=0 直立，逆时针为正），ω = θ̇。'
          '由转动定律（含重力矩、摩擦与电机力矩）：')
body_noindent(doc, '　　I·θ̈ = k_g·sinθ − b·θ̇ − τ_c·tanh(θ̇/ε) − τ_m')
body(doc, '其中：I 为绕转轴转动惯量（均匀杆绕端部 + 尖端质点）；k_g = (m_s·L/2 + m_t·L)·g 为重力矩幅值；'
          'b、τ_c 分别为黏性摩擦与库仑摩擦系数；τ_m = K_m·duty/100 为电机力矩，'
          '符号按实物实测确定（正占空比使 θ 减小）。实物参数与推导结果如表 4 所示。')
table(doc, [
    ['参数', '符号', '数值', '参数', '符号', '数值'],
    ['摆杆长度', 'L', '0.20 m', '重力矩幅值', 'k_g', '11.8 mN·m'],
    ['杆身质量', 'm_s', '4 g', '静摩擦（库仑）', 'τ_c', '5 mN·m'],
    ['尖端配重', 'm_t', '4 g', '电机力矩(100%)', 'K_m', '0.08 N·m'],
    ['转动惯量', 'I', '2.13×10⁻⁴ kg·m²', '执行器滞后', 'τ_a', '15 ms'],
    ['采样周期', 'T_s', '2 ms', '占空比饱和', 'duty_max', '±100 %'],
], widths=[3.0, 1.8, 3.0, 3.0, 1.9, 2.4], cap='表 4　实物参数（标注为设定值的项待实测修正）')
body(doc, '由表 4 可见本系统的核心矛盾：重力矩 11.8 mN·m 与静摩擦 5 mN·m 同量级。'
          '这意味着在 |sinθ| < τ_c/k_g = 0.42，即 |θ| < 24.8° 的范围内，'
          '重力本身无法推动摆杆——系统存在一个约 ±25° 的“重力死区”，摆杆要靠电机出力才能移动。'
          '摩擦项在仿真中按“速度接近零且驱动力矩小于静摩擦时锁死”的粘滑（stick-slip）模型处理，'
          '以真实反映死区现象。')

h2(doc, '2.2 平衡控制器设计')
body(doc, '在直立点附近线性化（忽略摩擦）：θ̈ = (k_g·θ − K_m·duty/100)/I。'
          '采用 PD 控制律 u = kp·e + kd·ω（e = θ − θ0，符号由实物实测确定），'
          '闭环稳定条件为 K_m·kp/100 > k_g，即 kp > 100·k_g/K_m ≈ 14.7；'
          '本项目取 kp = 60、kd = 8，对应闭环自然频率约 13 rad/s、阻尼比约 1.15。')
body(doc, '死区分析：稳态（ω=0）时电机力矩需满足 |K_m·u/100| > τ_c 才能推动摆杆。'
          '对纯 PD，u ≈ kp·θ，故只有当 |θ| > 100·τ_c/(K_m·kp) ≈ 0.104 rad ≈ 6° 时才能出力移动摆杆；'
          '再计入重力矩的抵消作用，PD 的最终停位误差可达约 ±8°。'
          '因此必须引入积分项：u = kp·e + kd·ω + ki·∫e·dt，本项目取 ki = 100，'
          '积分限幅 ±0.5 并带抗饱和（输出接近饱和且积分仍在同向加深时冻结积分）。'
          '控制器参数如表 5 所示。')
table(doc, [
    ['控制器', '参数', '取值', '作用'],
    ['PD', 'kp / kd', '60 / 8', '快速回中与阻尼（符号由实测确定）'],
    ['PID', 'ki / 积分限幅', '100 / ±0.5', '累积出力跨过静摩擦死区，消除稳态误差'],
    ['LQR（对照）', 'Q / R', 'diag(40, 1) / 0.02', '系统性设计对照（结构等价于 PD）'],
    ['起摆', 'k_sw / 捕获窗口', '4.5×10⁴ %/J / 45°、25 rad·s⁻¹', '能量泵摆与捕获切换（占空比限幅 ±26%）'],
], widths=[2.6, 3.0, 3.4, 6.0], cap='表 5　控制器参数')

h2(doc, '2.3 角度与角速度处理链')
body(doc, 'AS5600 输出 0~4095 的循环量（对应 0~360°），转满一圈后回绕。核心结论：'
          '不能直接对循环量做滤波或差分——角度从 4090 跳变到 10 时直接相减会得到 −4080'
          '（真实只差 +16），回绕点会产生假的巨大差值。因此处理顺序固定为：'
          '① 回绕修正（差值超半圈则加减整圈）→ ② 展开成连续角度 → ③ 一阶低通（α=0.35）→ '
          '④ 按实测 dt 差分求角速度 → ⑤ 限幅 ±1500°/s。')
body(doc, '同时对单拍跳变设置毛刺剔除阈值（>13.2° 判为毛刺、保持旧值），连续失败计数用于安全判据。'
          '仿真中角度链的峰值估计误差 1.50°、RMS 误差 0.092°（含 12bit 量化与噪声），满足控制需求。')

h2(doc, '2.4 起摆控制（能量法）')
body(doc, '定义摆杆机械能 E = 0.5·I·ω² + k_g·(cosθ − 1)：直立静止时 E* = 0，下垂静止时 E = −2k_g。'
          '对转轴力矩直驱的对象有 dE/dt = τ_m·ω，因此只要让电机力矩与角速度同相（τ_m ∝ ω），'
          '即可使 dE/dt ≥ 0，能量单调增加——这正是“荡秋千”式泵能量的原理。'
          '仿真取 duty = −k_sw·(E* − E)·tanh(ω/ε)（注意力矩与占空比的符号关系），起摆阶段占空比限幅 ±26%；'
          '当能量达到捕获阈值（E ≥ −0.25 J）且 |θ| < 45°、|ω| < 25 rad/s 时判定捕获成功，切换到 PID 平衡，'
          '并在 0.5s 内把限幅从 25% 线性放松到 100% 以防切换冲击。针对停滞（|ω| 很小）另设“唤醒踢”打破静摩擦死点。')

h2(doc, '2.5 采样周期选择')
body(doc, '摆杆失稳时间尺度由其动力学决定（本项目重力矩小、摩擦大，失稳较慢）。'
          '仿真对采样周期 1~44ms 扫描：30ms 以内均能稳定，36ms 起失稳，'
          '说明 2ms（500Hz）设计点相对稳定边界有约 15 倍裕量，并为 I2C 读取与计算留足时间。')

h2(doc, '2.6 安全监控设计')
body(doc, '安全监控遵循“监测与执行分离、故障锁存、人工复位”原则：监测模块只产生事件与故障码，'
          '由状态机响应；硬故障一经触发直接断电并拉低 STBY，且必须人工复位，杜绝自动复归造成反复冲击。'
          '安全阈值与动作如表 6 所示。')
table(doc, [
    ['监控项', '阈值/判据', '动作'],
    ['平衡中摆角超限', '|θ| > 35° 降级回起摆；> 60° 硬故障', '降级重捕 / 断电抱闸'],
    ['传感器断连/冻结', '连续 20 拍（40ms）无效', '断电刹车'],
    ['占空比/电流异常', '|duty| ≥ 95% 连续 30 拍（60ms）', '断电'],
    ['程序失控（看门狗）', '20ms 未喂狗', '复位并停机'],
], widths=[4.2, 6.0, 3.0], cap='表 6　安全监控阈值与动作')

# ---------------- 三、电路与程序设计 ----------------
h1(doc, '三、电路与程序设计')

h2(doc, '3.1 硬件电路设计')
body(doc, '电源：12V≥2A 适配器经 3A 保险丝与自锁按钮（按下断开，作急停）为 TB6612 VM 供电，'
          'AMS1117 输出 3.3V 为逻辑电路供电，动力地与逻辑地共地。')
body(doc, '电机驱动：STM32 PB0（TIM3_CH3，20kHz PWM）接 PWMA，PA0/PA1 接 AIN1/AIN2 控制方向，'
          'PA2 接 STBY（上电默认禁能，程序初始化后才放行）。角度采集：AS5600 经 I2C（SCL=PB6，SDA=PB7）'
          '以 3.3V 供电，读 0x36 寄存器得到 12bit RAW。调试串口：PA9/PA10 接 USB-TTL，115200 8N1。'
          '接线与装配如图 2、图 3 所示。')
add_fig(doc, os.path.join(PHYS, 'S1_接线图.png'), 12.5, '图 2　实物接线图（电源/电机/编码器/串口）')
add_fig(doc, os.path.join(PHYS, 'S1_装配示意_3D.png'), 10.5, '图 3　整机装配示意（3D）')
body(doc, '调试中解决的关键硬件问题（真实踩坑，作为工程经验沉淀）：'
          '① CubeMX 中 TIM3 默认 Period=65535，而旧固件把 ARR 写死为 3599，'
          '导致“40%”档实际只输出 2.2% 占空比、电机只响不转——改为按 htim3.Init.Period 实时计算占空比，'
          '并将 Period 设为 3599（20kHz）；'
          '② CubeMX 未勾选 USART1 全局中断，导致能打印却收不到命令——补中断服务函数并打开 NVIC；'
          '③ AS5600 读得 |B|=0、AGC 停在默认 128，是磁铁未装到位——正式安装到法兰中心、'
          '间隙 1~2mm 后 |B| 达 1000+、MAG=OK；'
          '④ 整份覆盖 CubeMX 生成的 main.c 导致 6 个 L6218E Undefined symbol——'
          '自定义逻辑全部放在独立模块，main.c 仅在 USER CODE 区挂调用。')

h2(doc, '3.2 程序设计')
body(doc, '2ms 硬节拍：采用累加推进（g_tick_next += SAMP_US）而非取当前时间，偶尔晚一拍会自动追回，'
          '长期平均周期精确；时间源用 TIM2 硬件计数器（PSC=71→1MHz，软件扩展到 32 位）'
          '替代分辨率不足的 HAL_GetTick()；并加开机自检。实测 dt 平均 2000µs、最大 2002µs、最小 1998µs、'
          '零漏拍（500ms 窗口 251 拍）。')
body(doc, '角度链按 2.3 节顺序实现（回绕修正 → 展开 → 低通 → 差分 → 限幅），单拍跳变 >13.2° 判毛刺丢弃。'
          '数据记录：环形缓冲 1200 样本（2.4s @500Hz），命令 d 一次性 dump 成 CSV（i, th_deg, dps, duty），'
          '采用非阻塞发送（HAL_UART_Transmit_IT + 双缓冲 + 丢帧计数），dump 1200 行期间节拍不受影响——'
          '宁可丢日志，不能让日志拖垮控制节拍。实物数据记录效果如图 4。')
add_fig(doc, os.path.join(PHYS, 'S2_dump_v9.png'), 13.0,
        '图 4　实物数据记录效果（角度连续；速度曲线仍有零星毛刺尖刺，由限幅兜底）')
body(doc, '控制程序结构：模式状态机在 BALANCE（PID）/ PUMP（能量起摆）/ FAULT（锁存断电）之间切换；'
          '闭环中包含 1 拍计算延迟（本拍采样、下一拍指令执行）以贴近真实时序；'
          '安全监控独立成层，每拍检查摆角、传感器有效性与占空比饱和情况。')

# ---------------- 四、测试方案与测试结果 ----------------
h1(doc, '四、测试方案与测试结果')

h2(doc, '4.1 实物测试（S1~S2）')
body(doc, '实物测试分两阶段：S1 全链路通电（电机驱动 + 角度采集 + 串口双向 + 整机联跑），'
          'S2 固定采样节拍与数据记录。测试记录如表 7 所示。')
table(doc, [
    ['序号', '测试项目', '测试方法与判据', '结果'],
    ['1', '电机驱动', '20kHz PWM 按档位（0/40/70/100%）转动；r 换向；x 急停', '通过'],
    ['2', '角度采集', '手转一圈 deg 从 0° 平滑扫至 360°（含回绕）；|B|≈1000、MAG=OK', '通过'],
    ['3', '串口双向', '命令 0~100/r/s/x/e 全部生效；打印正常（补 USART1 中断后）', '通过'],
    ['4', '采样节拍', '2ms 硬节拍 500ms 窗口实测 dt avg=2000µs max=2002µs min=1998µs，251 拍，over=0', '通过'],
    ['5', '角度链与速度', '循环量展开后角度连续；速度限幅 ±1500°/s 兜底（未展开时存在回绕假差值）', '通过'],
    ['6', '数据记录', 'd 命令 dump 1200 样本 CSV，上位机出三曲线；dump 期间节拍不受影响', '通过'],
    ['7', '机械装配', '磁铁偏心/松动会直接毁掉读数；转整圈 |B| 波动 <10%、bad=0 判合格', '通过'],
], widths=[1.2, 2.6, 7.0, 1.6], cap='表 7　实物测试记录')
body(doc, '需要如实说明：实物的平衡闭环（S3）尚未完成。调试中已确认一条关键事实——'
          '由于摆杆过轻（重力矩与减速箱静摩擦同量级），摆杆“松手不倒”，'
          '这正是仿真中建模并重点解决的摩擦死区问题；因此先在仿真平台上完成控制算法验证，'
          '再移植到实物。')

h2(doc, '4.2 仿真测试（与实物同结构的 2 状态模型）')
body(doc, '仿真平台（Python/numpy/scipy）采用与实物相同的结构、参数与 2ms 采样节拍，'
          '含 12bit 量化与噪声、粘滑摩擦、执行器一阶滞后与 1 拍计算延迟，完成 9 组验证场景，'
          '指标汇总如表 8 所示，代表性曲线见图 5~图 12。')
table(doc, [
    ['场景', '测试内容', '关键指标'],
    ['S1 初始偏差', 'θ0=10°，PID 平衡', '0.52s 进 ±3° 带；随后 ±2° 极限环（峰峰 4.34°）'],
    ['S2 脉冲扰动', '2s 时给 2 rad/s 角速度冲击', '1.19s 恢复；峰值 2.67°'],
    ['S3 参数失配', '杆质量+50%、长+20%、摩擦×2', '0.90s 收敛；末值 −1.80°'],
    ['S4 角度链', '12bit 量化 + 噪声 + 毛刺', '峰值估计误差 1.50°，RMS 0.092°'],
    ['S5 能量起摆', '从下垂位泵摆到直立', '17.98s 稳定；稳态残差约 −0.05°'],
    ['S6a 强扰动', '2s 时给 60 rad/s 强冲击', '40.3° 触发降级回起摆；摆物理上回到倒立（−12.7°、ω≈0），'
                                     '但原判据用连展角比较致日志无重捕获；改用折回角后 0.29s 重捕获'],
    ['S6b 传感器断连', '80ms 无有效采样', '38ms 检测 FAULT_SENSOR 并急停'],
    ['S6c 占空比饱和', '强制 100% 占空比 30 拍', '58ms 检测并急停'],
    ['S6d 看门狗', '控制任务卡死 30ms', '20ms 超时 FAULT_WATCHDOG 停机'],
    ['S7 采样扫描', 'T_s = 1~44ms', '≤30ms 稳定，36ms 发散（2ms 裕量约 15 倍）'],
    ['S8 PD vs LQR', '同 10° 偏差、无积分', '两者都停在 ±6.5°（6.55° / 6.51°，压不过静摩擦）'],
    ['S9 PD vs PID', '同 2° 偏差（死区内起步）', 'PD 卡在 2.03°；PID 1.20s 收敛到 −0.51°'],
], widths=[2.2, 4.4, 5.8], font_size=10, cap='表 8　仿真场景测试指标汇总')
add_fig(doc, os.path.join(SIM, 'D2_S1阶跃响应.png'), 12.5, '图 5　S1 初始偏差 10° 的 PID 闭环响应')
add_fig(doc, os.path.join(SIM, 'D3_死区PDvsPID.png'), 12.5,
        '图 6　摩擦死区对比：纯 PD 卡在 2.03°，PID 收敛到 −0.51°（核心图）')
add_fig(doc, os.path.join(SIM, 'D4_纯PD与LQR卡死区.png'), 12.5,
        '图 7　纯 PD 与 2 状态 LQR 在 10° 起步时都停在 ±6.5°')
add_fig(doc, os.path.join(SIM, 'D5_能量起摆.png'), 12.5, '图 8　S5 能量起摆（摆角/机械能/占空比）')
add_fig(doc, os.path.join(SIM, 'D6_参数失配.png'), 12.5, '图 9　S3 参数失配下的鲁棒性')
add_fig(doc, os.path.join(SIM, 'D7_采样扫描.png'), 12.5, '图 10　S7 采样周期扫描（稳定到 30ms）')
add_fig(doc, os.path.join(SIM, 'D8_传感器断连.png'), 12.5, '图 11　S6b 传感器断连 38ms 内检测并急停')
add_fig(doc, os.path.join(SIM, 'D9_角度链估计.png'), 12.5, '图 12　S4 角度链输出与真实角度对比')

h2(doc, '4.3 测试结论')
body(doc, '（1）实物全链路已打通：电机驱动、角度采集、2ms 硬节拍、角度链与数据记录均实机验收通过，'
          '采样质量（dt=2000±2µs、零漏拍）满足 500Hz 需求；')
body(doc, '（2）仿真揭示并解决了本系统的核心矛盾——摩擦死区：纯 PD 与 LQR 因力矩压不过静摩擦而'
          '停在 2.03°/6.55° 的停位误差上；引入积分后，2° 小角度起步可收敛到 −0.51°，'
          '10° 起步则在直立附近形成 ±2° 量级极限环（受摩擦限制无法严格收敛到 0°）；')
body(doc, '（3）能量起摆、安全监控在仿真中验证有效：起摆 17.98s 稳定，三类故障分别在 38ms/58ms/20ms 内急停，'
          '强扰动可降级回起摆；重捕获判据修复角度口径后 0.29s 内完成重捕获；')
body(doc, '（4）如实说明：实物平衡闭环（S3）尚未跑通，上述控制算法为仿真验证结果，'
          '是移植到实物的设计依据。')

# ---------------- 五、结论 ----------------
h1(doc, '五、结论')
body(doc, '本设计完成了电机直驱倒立摆的实物链路（S1~S2）与同结构仿真平台上的控制算法设计验证。'
          '实物部分验证了“数字→力”与“角度→数”两条链路的正确性，并建立了 2ms 硬节拍下的'
          '角度处理与数据记录体系；仿真部分针对“摆杆重力矩与减速箱静摩擦同量级”这一真实约束，'
          '完成了摩擦死区建模、PID 控制器设计、能量起摆与安全监控验证。')
body(doc, '设计过程中的核心收获：负反馈符号是第一课（出力方向反了系统会发散，需先用固定占空比'
          '实测“力→倒向”的符号关系）；循环量必须先展开再滤波/差分；摩擦死区会让纯 PD/LQR 留下稳态误差，'
          '必须用积分或前馈补偿跨过；安全监控与执行分离、故障锁存人工复位；'
          '以及“真实代码、诚实边界”的工程态度。')
body(doc, '下一步工作：按实测修正摆杆与摩擦参数，把 PID 平衡、能量起摆与安全逻辑移植到实物固件，'
          '完成 S3“让摆杆站住”与 S4“起摆-捕获-站立”的实机验证。')

# ---------------- 六、参考文献 ----------------
h1(doc, '六、参考文献')
for r in [
    '[1] 胡寿松. 自动控制原理[M]. 6版. 北京: 科学出版社, 2013.',
    '[2] 刘豹, 唐万生. 现代控制理论[M]. 3版. 北京: 机械工业出版社, 2006.',
    '[3] 张兴华. STM32嵌入式系统开发实战指南[M]. 北京: 机械工业出版社, 2013.',
    '[4] AMS. AS5600 12-bit Programmable Magnetic Rotary Position Sensor Datasheet[EB/OL].',
    '[5] Toshiba. TB6612FNG Dual Motor Driver Datasheet[EB/OL].',
    '[6] STMicroelectronics. STM32F103x8 Datasheet & Reference Manual[EB/OL].',
    '[7] 郑大钟. 线性系统理论[M]. 2版. 北京: 清华大学出版社, 2002.',
]:
    para(doc, r, size=12, space_after=4, line=1.4)

# ---------------- 附录 ----------------
doc.add_page_break()
h1(doc, '附　录')
h2(doc, '附录 A　学习记录摘要')
body_noindent(doc, '· S1 全链路通电：电机按档位转动 + 角度平滑扫 0~360° + 串口命令双向 + 整机联跑；'
                   '复盘含 4 处真实踩坑（ARR 配置、串口中断、磁铁安装、main.c 覆盖）。')
body_noindent(doc, '· S1.5 读透代码：六块代码逐段精读，动手验收（新增命令、档位表 4→5 档、用 sizeof 去掉魔数）。')
body_noindent(doc, '· S2 固定采样节拍：2ms 硬节拍 + 循环量展开与滤波 + 速度估计 + 环形缓冲记录；'
                   '过程中发现“循环量直接处理 → 回绕假差值”的原理问题并改为先展开再处理；'
                   '剩余毛刺尖刺由 ±1500°/s 限幅兜底。')
body_noindent(doc, '· S3（进行中）：辨识出“摆杆重力矩与减速箱静摩擦同量级”的死区问题，'
                   '该问题已在仿真中建模，并成为选择 PID（而非纯 PD/LQR）的直接依据。')
h2(doc, '附录 B　工具与 AI 使用说明')
body(doc, '开发工具：STM32CubeMX（外设初始化）、Keil MDK-ARM（编译下载）、ST-Link（SWD 调试）、'
          'USB-TTL 串口助手（命令与数据曲线）、Python（numpy/scipy/matplotlib，仿真平台）、Git。')
body(doc, 'AI 使用说明：本项目的建模推导、控制器设计与仿真代码在开发过程中使用 AI 工具辅助编写与校验；'
          '所有写入本报告的关键结论（采样节拍实测、角度链效果、仿真指标）均由本人运行/实测复核，'
          '不引用未经本人验证的结论；设计方案与工程决策由本人完成。'
          '报告中原“小车倒立摆”仿真与实物结构不一致，已核对实物装配后整体重做为转轴直驱摆模型。')

doc.save(OUT)
print('saved:', OUT)
