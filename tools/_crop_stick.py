
from PIL import Image
im = Image.open(r"C:\Users\65630\.dsh\attachments\v1\objects\40\40f6ec1ac60866043ff891bf3df0c8b225f926b96a2c6129096d268f9eadc8d5")
print(im.size)
box = (560, 880, 1420, 1700)
c = im.crop(box)
c = c.resize((int(c.width*1.7), int(c.height*1.7)), Image.LANCZOS)
c.convert("RGB").save(r"D:\harness\学业\yf105招新\25级-倒立摆实物\figs\_crop_stick.jpg", quality=92)
print("saved", c.size)
