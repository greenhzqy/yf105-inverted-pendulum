
from PIL import Image, ImageDraw, ImageFont
im = Image.open(r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs\_user_photo_raw.jpg').convert('RGB')
d = ImageDraw.Draw(im)
F  = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 40)
Fb = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 44)

def ring(xy, r, color, w=6):
    d.ellipse([xy[0]-r, xy[1]-r, xy[0]+r, xy[1]+r], outline=color, width=w)

def arrow(p1, p2, color, w=6):
    d.line([p1, p2], fill=color, width=w)
    d.polygon([p2, (p2[0]-20, p2[1]-11), (p2[0]-20, p2[1]+11)], fill=color)

BLUE, ORANGE, MAG, GREEN, RED = (0,120,255), (235,120,0), (190,0,190), (0,150,60), (205,0,0)

# 高亮圈
ring((1030, 1190), 185, BLUE)      # 法兰盘
ring((950, 1160), 78, ORANGE)      # 银色套筒
ring((1063, 1213), 40, MAG)        # 中心端头
ring((1060, 1063), 48, GREEN)      # 安装孔

# 文字标签（统一放在下方空白桌面区）
x0 = 110
d.text((x0, 1500), '① 白色圆盘 = 法兰（已有安装孔）→ 就用它，不要再装第二个联轴器', font=F, fill=BLUE)
d.text((x0, 1585), '② 银色套筒 = 联轴器/轴套，它已在干"夹住轴"的活', font=F, fill=ORANGE)
d.text((x0, 1670), '③ 磁铁贴在这个中心端面（轴线上）；AS5600 从外侧对准它，间隙 1~2mm', font=F, fill=MAG)
d.text((x0, 1755), '④ 摆杆用 M4 螺丝拧在这些偏心孔上（离中心 10~15mm），用两个孔防转', font=F, fill=GREEN)
d.text((x0, 1840), '⑤ 关键：套筒侧面的顶丝必须顶在轴的 D 面上并拧死；拧紧后手转白盘，', font=F, fill=RED)
d.text((x0, 1925), '     套筒和白盘必须同步转动、一点不打滑（打滑 = 角度数据直接废掉）', font=F, fill=RED)

# 引线
arrow((1330, 1520), (1150, 1330), BLUE)
arrow((1200, 1605), (995, 1215), ORANGE)
arrow((1380, 1690), (1085, 1235), MAG)
arrow((1270, 1775), (1060, 1085), GREEN)
arrow((1310, 1860), (1010, 1230), RED)

im.save(r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs\S1_实物标注_法兰与磁铁位置.png')
print('saved')
