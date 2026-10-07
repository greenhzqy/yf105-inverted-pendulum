
from PIL import Image
im = Image.open(r"C:\Users\65630\.dsh\attachments\v1\objects\bb\bb31a79bbccf2bd1377c8c51379cd8c16c77e1b02aea28a4044f99b7e21a204f")
print(im.size)
box = (120, 620, 1420, 1520)
c = im.crop(box)
c = c.resize((int(c.width*1.25), int(c.height*1.25)), Image.LANCZOS)
c.convert("RGB").save(r"D:\harness\学业\yf105招新\25级-倒立摆实物\figs\_crop_rig3.jpg", quality=92)
print("saved", c.size)
