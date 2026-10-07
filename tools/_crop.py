
from PIL import Image
im = Image.open(r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs\S1_接线图.png')
w, h = im.size
im.crop((0, int(0.30*h), int(0.45*w), int(0.85*h))).save(r'D:\harness\学业\yf105招新\25级-倒立摆实物\figs\_crop_left.png')
print('cropped')
