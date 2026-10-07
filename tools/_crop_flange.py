
from PIL import Image
im = Image.open(r"C:\Users\65630\.dsh\attachments\v1\objects\b4\b49120d232ad65c0a5d64dc942be8d912948c85c5ea6a4edd2ebe6487260170d")
print("size", im.size)
box = (620, 780, 1330, 1420)
c = im.crop(box).resize(((box[2]-box[0])*2, (box[3]-box[1])*2), Image.LANCZOS)
c.convert("RGB").save(r"D:\harness\学业\yf105招新\25级-倒立摆实物\figs\_crop_flange.jpg", quality=92)
print("saved", c.size)
