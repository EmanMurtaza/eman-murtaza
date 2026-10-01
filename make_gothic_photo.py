import math
from PIL import Image, ImageDraw, ImageOps, ImageEnhance, ImageFilter
import numpy as np

SRC = r"C:\Users\user\Downloads\WhatsApp Image 2026-10-01 at 10.25.51.jpeg"
OUT = "eman_gothic_portrait.png"

im = Image.open(SRC).convert("RGB")
# head-and-shoulders crop (3:4)
box = (385, 835, 865, 1475)
im = im.crop(box)
W, H = im.size

# gothic grade: desaturate, lift contrast, tint shadows plum / highlights bone
g = ImageOps.grayscale(im)
g = ImageOps.autocontrast(g, cutoff=1)
g = ImageEnhance.Contrast(g).enhance(1.25)
a = np.asarray(g, dtype=np.float32) / 255.0
shadow = np.array([14, 6, 12], np.float32)
mid = np.array([120, 40, 55], np.float32)
high = np.array([232, 220, 212], np.float32)
t = a[..., None]
rgb = np.where(t < 0.5, shadow + (mid - shadow) * (t / 0.5), mid + (high - mid) * ((t - 0.5) / 0.5))
im = Image.fromarray(rgb.clip(0, 255).astype(np.uint8))

# vignette
yy, xx = np.mgrid[0:H, 0:W]
d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.42) / (H * 0.62)) ** 2)
v = np.clip(1.05 - d * 1.0, 0.0, 1.0)[..., None]
im = Image.fromarray((np.asarray(im, np.float32) * v).clip(0, 255).astype(np.uint8))

# pointed gothic arch mask (supersampled)
S = 4
m = Image.new("L", (W * S, H * S), 0)
dr = ImageDraw.Draw(m)
w, h = W * S, H * S
r = w * 0.75              # arch radius > half-width -> pointed apex
spring = math.sqrt((w*0.75)**2 - (w/2 - w*0.75)**2)  # apex lands exactly on top edge
cx = w / 2
# two circles whose intersection forms the point
c1 = (w - r, spring)      # left arc centre (on right side)
c2 = (r, spring)          # right arc centre (on left side)
poly = []
import math
apex_y = spring - math.sqrt(r * r - (cx - c2[0]) ** 2) if False else None
# left arc: centre at (r, spring) radius r  -> spans x from 0 .. ; right arc centre (w-r, spring)
left_c = (r, spring); right_c = (w - r, spring)
steps = 120
pts_left = []
for i in range(steps + 1):
    x = i / steps * cx
    y = spring - math.sqrt(max(r * r - (x - left_c[0]) ** 2, 0))
    pts_left.append((x, y))
pts_right = [(w - x, y) for x, y in reversed(pts_left)]
poly = [(0, h)] + [(0, spring)] + pts_left + pts_right[1:] + [(w, spring), (w, h)]
dr.polygon(poly, fill=255)
m = m.resize((W, H), Image.LANCZOS)
out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
out.paste(im, (0, 0), m)
out.save(OUT)
print(out.size)
