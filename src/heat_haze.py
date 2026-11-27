# 陽炎（環流・陽炎の絵）を足すのに使った加工。刀の位置 x0,y0,x1,y1 は絵ごとに測り直す。
# 使い方: python3 src/heat_haze.py <元の絵> <出力>
# 刀のまわりに陽炎（空気のゆらぎ）と、刀身の白い光を足す
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
W, H = im.size
a = np.asarray(im).astype(np.float32)
# 刀身：鍔のあたりから切っ先まで（この絵での位置）
x0, y0, x1, y1 = 702, 320, 985, 305
# ゆらぎの強さ：刀身の線からの距離で弱くなる。刀身より右（切っ先の先）と上下に広がる
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
t = np.clip((xx - x0) / (x1 - x0), 0, 1)
ly = y0 + (y1 - y0) * t
dist = np.abs(yy - ly)
along = np.where(xx < x0 - 40, 0, np.clip((xx - (x0 - 40)) / 120, 0, 1)) * np.where(xx > W, 0, 1)
mask = np.exp(-(dist / 75) ** 2) * along * (1 - np.exp(-(dist / 14) ** 2))
amp = 10.0
dx = amp * mask * np.sin(yy / 7.0 + xx / 23.0)
dy = amp * 0.6 * mask * np.sin(xx / 9.0 + yy / 17.0)
sx = np.clip(xx + dx, 0, W - 1).astype(np.int32)
sy = np.clip(yy + dy, 0, H - 1).astype(np.int32)
warped = a[sy, sx]
out = Image.fromarray(warped.astype(np.uint8))
# 刀身そのものはくっきり残す
blade = Image.new('L', (W, H), 0)
d = ImageDraw.Draw(blade)
d.line([(x0 - 110, y0 + 2), (x0, y0), (x1, y1)], fill=255, width=16)
blade = blade.filter(ImageFilter.GaussianBlur(1.2))
out = Image.composite(im, out, blade)
# 刀身の白い光
glow = Image.new('RGB', (W, H), (0, 0, 0))
g = ImageDraw.Draw(glow)
g.line([(x0, y0), (x1, y1)], fill=(255, 245, 210), width=6)
g1 = glow.filter(ImageFilter.GaussianBlur(8))
g2 = glow.filter(ImageFilter.GaussianBlur(3))
out = ImageChops.screen(out, Image.eval(g1, lambda v: int(v * 0.55)))
out = ImageChops.screen(out, Image.eval(g2, lambda v: int(v * 0.35)))
# 熱でまわりが少し明るく、黄色っぽく
haze = Image.fromarray((np.dstack([mask * 40, mask * 30, mask * 8])).clip(0, 255).astype(np.uint8))
out = ImageChops.screen(out, haze)
out.save(dst, quality=92)
print('ok')
