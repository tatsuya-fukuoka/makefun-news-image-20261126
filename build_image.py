#!/usr/bin/env python3
"""Build entry.png: a newspaper front-page infographic for 26 November 2026.

Deterministic: fixed fonts, no randomness, no timestamps. All text is rendered
with PIL TrueType fonts; pictograms are flat PIL shapes. Drawn at 2x and
downsampled for smooth edges.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
S = 2  # supersampling factor
PAPER = (245, 240, 227)
TINT = (231, 224, 205)
INK = (18, 18, 18)
RED = (200, 30, 36)
GREY = (120, 116, 106)
WHITE = (250, 247, 240)

FONT_DIR = "/usr/share/fonts/truetype/noto/"
F_BLACK = FONT_DIR + "NotoSans-Black.ttf"
F_BOLD = FONT_DIR + "NotoSans-Bold.ttf"
F_REG = FONT_DIR + "NotoSans-Regular.ttf"

_fc = {}


def font(path, size):
    key = (path, size)
    if key not in _fc:
        _fc[key] = ImageFont.truetype(path, int(round(size * S)))
    return _fc[key]


img = Image.new("RGB", (W * S, H * S), PAPER)
d = ImageDraw.Draw(img)


def sc(pts):
    return [v * S for v in pts]


def rect(x0, y0, x1, y1, fill=None, outline=None, width=1):
    d.rectangle(sc([x0, y0, x1, y1]), fill=fill, outline=outline, width=width * S)


def rrect(x0, y0, x1, y1, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(sc([x0, y0, x1, y1]), radius=r * S, fill=fill,
                        outline=outline, width=width * S)


def ell(x0, y0, x1, y1, fill=None, outline=None, width=1):
    d.ellipse(sc([x0, y0, x1, y1]), fill=fill, outline=outline, width=width * S)


def poly(pts, fill=None):
    d.polygon([(x * S, y * S) for x, y in pts], fill=fill)


def line(pts, fill=INK, width=1):
    d.line([(x * S, y * S) for x, y in pts], fill=fill, width=int(width * S), joint="curve")


def rot_ellipse(cx, cy, rx, ry, ang_deg, n=72):
    a = math.radians(ang_deg)
    out = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append((cx + x * math.cos(a) - y * math.sin(a),
                    cy + x * math.sin(a) + y * math.cos(a)))
    return out


def text_w(s, f):
    return d.textlength(s, font=f) / S


def text(x, y, s, f, fill=INK):
    """Draw with (x, y) = top-left of the line box (ascender-based)."""
    d.text((x * S, y * S), s, font=f, fill=fill)


def spaced(x, y, s, f, fill, track):
    for ch in s:
        text(x, y, ch, f, fill)
        x += text_w(ch, f) + track
    return x


def spaced_w(s, f, track):
    return sum(text_w(c, f) + track for c in s) - track


# ----------------------------------------------------------------- pictograms
def pic_containers(ox, oy):
    def box(x, y, w, h, col):
        rect(ox + x, oy + y, ox + x + w, oy + y + h, fill=col)
        for i in range(1, 6):
            xx = x + i * w / 6
            line([(ox + xx, oy + y + 3), (ox + xx, oy + y + h - 3)], fill=WHITE, width=1.5)
    box(10, 96, 62, 36, INK)
    box(76, 96, 62, 36, GREY)
    box(10, 58, 62, 36, GREY)
    box(76, 58, 62, 36, INK)
    box(43, 20, 62, 36, RED)
    rect(ox + 4, oy + 134, ox + 146, oy + 140, fill=INK)
    # large % tag
    cx, cy = ox + 112, oy + 26
    ell(cx - 26, cy - 26, cx + 26, cy + 26, fill=INK, outline=WHITE, width=3)
    f = font(F_BLACK, 36)
    w = text_w("%", f)
    text(cx - w / 2, cy - 27, "%", f, WHITE)


def pic_tanker(ox, oy):
    # flames
    for fx, fh, col in ((38, 46, RED), (68, 58, RED), (98, 40, RED)):
        poly([(ox + fx - 12, oy + 76), (ox + fx - 8, oy + 76 - fh * 0.5),
              (ox + fx - 2, oy + 76 - fh * 0.45), (ox + fx + 2, oy + 76 - fh),
              (ox + fx + 8, oy + 76 - fh * 0.4), (ox + fx + 14, oy + 76 - fh * 0.55),
              (ox + fx + 12, oy + 76)], fill=col)
    for fx, fh in ((38, 22), (68, 30), (98, 20)):
        poly([(ox + fx - 5, oy + 76), (ox + fx, oy + 76 - fh), (ox + fx + 5, oy + 76)], fill=INK)
    # tank
    rrect(ox + 8, oy + 76, ox + 108, oy + 116, 20, fill=INK)
    line([(ox + 40, oy + 80), (ox + 40, oy + 112)], fill=WHITE, width=2)
    line([(ox + 74, oy + 80), (ox + 74, oy + 112)], fill=WHITE, width=2)
    # cab
    poly([(ox + 110, oy + 82), (ox + 130, oy + 82), (ox + 144, oy + 100),
          (ox + 144, oy + 120), (ox + 110, oy + 120)], fill=GREY)
    poly([(ox + 116, oy + 88), (ox + 128, oy + 88), (ox + 137, oy + 100), (ox + 116, oy + 100)], fill=PAPER)
    rect(ox + 4, oy + 116, ox + 146, oy + 124, fill=INK)
    for wx in (28, 56, 124):
        ell(ox + wx - 11, oy + 114, ox + wx + 11, oy + 136, fill=INK, outline=PAPER, width=2)
        ell(ox + wx - 4, oy + 121, ox + wx + 4, oy + 129, fill=PAPER)


def pic_balloon(ox, oy):
    # wind streaks (left)
    for yy, x0, x1 in ((40, 0, 34), (58, 4, 40), (76, 0, 28)):
        line([(ox + x0, oy + yy), (ox + x1, oy + yy)], fill=GREY, width=3)
    # string
    line([(ox + 82, oy + 100), (ox + 70, oy + 128), (ox + 78, oy + 146)], fill=INK, width=2)
    # tilted balloon
    poly(rot_ellipse(ox + 86, oy + 62, 34, 44, 28), fill=RED)
    poly(rot_ellipse(ox + 76, oy + 48, 8, 14, 28), fill=(228, 96, 98))
    poly([(ox + 76, oy + 100), (ox + 90, oy + 104), (ox + 84, oy + 112), (ox + 78, oy + 110)], fill=INK)
    # rain lines
    for x0, y0 in ((18, 98), (44, 112), (108, 92), (126, 112), (96, 124), (136, 76), (22, 126)):
        line([(ox + x0, oy + y0), (ox + x0 - 8, oy + y0 + 16)], fill=INK, width=2)


def pic_boat(ox, oy):
    # island
    poly([(ox + 98, oy + 112), (ox + 108, oy + 72), (ox + 124, oy + 62),
          (ox + 140, oy + 72), (ox + 150, oy + 112)], fill=GREY)
    line([(ox + 126, oy + 64), (ox + 126, oy + 40)], fill=INK, width=3)
    for dx, dy in ((-16, 4), (-10, -6), (12, 4), (10, -6)):
        line([(ox + 126, oy + 40), (ox + 126 + dx, oy + 40 + dy + 6)], fill=INK, width=3)
    # boat
    poly([(ox + 14, oy + 82), (ox + 78, oy + 82), (ox + 68, oy + 102), (ox + 26, oy + 102)], fill=INK)
    rect(ox + 36, oy + 62, ox + 56, oy + 82, fill=RED)
    line([(ox + 66, oy + 82), (ox + 66, oy + 56)], fill=INK, width=2)
    poly([(ox + 66, oy + 56), (ox + 80, oy + 62), (ox + 66, oy + 68)], fill=RED)
    # waves
    for k, (yy, col) in enumerate(((104, INK), (120, GREY), (136, INK))):
        pts = []
        for i in range(0, 151, 3):
            pts.append((ox + i, oy + yy + 5 * math.sin((i + k * 25) / 150 * 6 * math.pi)))
        line(pts, fill=col, width=4)


def pic_door(ox, oy):
    rect(ox + 8, oy + 14, ox + 84, oy + 140, fill=INK)
    rect(ox + 16, oy + 22, ox + 76, oy + 140, fill=TINT)
    # open door leaf, in perspective
    poly([(ox + 16, oy + 22), (ox + 50, oy + 32), (ox + 50, oy + 140), (ox + 16, oy + 140)], fill=GREY)
    rect(ox + 38, oy + 82, ox + 44, oy + 92, fill=PAPER)
    # arrow pointing outward (right)
    poly([(ox + 70, oy + 66), (ox + 112, oy + 66), (ox + 112, oy + 44), (ox + 148, oy + 78),
          (ox + 112, oy + 112), (ox + 112, oy + 90), (ox + 70, oy + 90)], fill=RED)


def pic_guitar(ox, oy):
    ang = 40
    # body
    poly(rot_ellipse(ox + 54, oy + 100, 30, 26, ang), fill=INK)
    poly(rot_ellipse(ox + 34, oy + 120, 34, 30, ang), fill=INK)
    # waist notch
    poly(rot_ellipse(ox + 72, oy + 104, 9, 14, ang), fill=INK)
    # pickguard and sound area
    poly(rot_ellipse(ox + 50, oy + 104, 14, 9, ang), fill=RED)
    ell(ox + 30, oy + 112, ox + 46, oy + 128, fill=PAPER)
    ell(ox + 34, oy + 116, ox + 42, oy + 124, fill=INK)
    # neck
    line([(ox + 66, oy + 88), (ox + 126, oy + 28)], fill=GREY, width=11)
    line([(ox + 66, oy + 88), (ox + 126, oy + 28)], fill=INK, width=2)
    # headstock
    poly([(ox + 120, oy + 16), (ox + 134, oy + 8), (ox + 148, oy + 22),
          (ox + 136, oy + 38), (ox + 124, oy + 32)], fill=INK)
    for px, py in ((130, 18), (138, 25), (126, 27)):
        ell(ox + px - 2, oy + py - 2, ox + px + 2, oy + py + 2, fill=PAPER)
    # bridge + strings glint
    line([(ox + 20, oy + 128), (ox + 40, oy + 142)], fill=PAPER, width=2)


# -------------------------------------------------------------------- stories
STORIES = [
    ("ECONOMY", "US UNVEILS NEW TARIFFS", "India 25%, China up to 40%", pic_containers),
    ("EGYPT", "CAIRO TANKER FIRE KILLS 30+", "Fuel truck overturns on ring road", pic_tanker),
    ("AMERICA", "STORM POSTPONES THANKSGIVING PARADE", "New York braces for a huge storm", pic_balloon),
    ("EUROPE", "2,000 MIGRANTS REACH CANARIES IN A DAY", "A record single-day arrival", pic_boat),
    ("ASIA", "NORTH KOREA EXPELS SWISS ENVOY", "Pyongyang orders the office closed", pic_door),
    ("CULTURE", "ANDY TAYLOR DIES AT 65", "Duran Duran's guitarist, sound of the 80s", pic_guitar),
]
BRIEFS = [
    "SPACEX CLEARED TO DEPLOY 1 MILLION SATELLITES",
    "BANGLADESH GARMENT WORKERS WIN 36% PAY RISE",
    "CHINA PROBES SHANGHAI PARTY CHIEF",
]


def wrap(s, f, maxw):
    lines, cur = [], ""
    for word in s.split():
        t = (cur + " " + word).strip()
        if text_w(t, f) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def fit_headline(s, maxw, hi=26, lo=18):
    for size in range(hi, lo - 1, -1):
        f = font(F_BLACK, size)
        ls = wrap(s, f, maxw)
        if len(ls) <= 2 and all(text_w(l, f) <= maxw for l in ls):
            return size, f, ls
    raise SystemExit("headline does not fit: " + s)


def fit_line(s, path, maxw, hi, lo):
    for size in range(hi, lo - 1, -1):
        f = font(path, size)
        if text_w(s, f) <= maxw:
            return size, f
    raise SystemExit("line does not fit: " + s)


# --------------------------------------------------------------------- header
M = 24
# top rule
rect(M, 14, W - M, 18, fill=INK)
f_small = font(F_BOLD, 15)
label = "THE WORLD IN ONE DAY"
tw = spaced_w(label, f_small, 7)
spaced((W - tw) / 2, 24, label, f_small, RED, 7)
rect(M, 46, W - M, 47.5, fill=INK)
# date
date = "THURSDAY 26 NOVEMBER 2026"
dsize, fdate = fit_line(date, F_BLACK, W - 2 * M, 80, 20)
dw = text_w(date, fdate)
text((W - dw) / 2, 50 + (46 - dsize) * 0.15 - 2, date, fdate, INK)
HEAD_END = 119
rect(M, HEAD_END, W - M, HEAD_END + 4, fill=INK)
rect(M, HEAD_END + 7, W - M, HEAD_END + 8.5, fill=INK)

# ----------------------------------------------------------------------- grid
GRID_TOP = HEAD_END + 16
FOOT_TOP = 936
GAP = 12
PW = (W - 2 * M - GAP) // 2
PH = (FOOT_TOP - 10 - GRID_TOP - 2 * GAP) // 3
PIC = 150

for i, (tag, head, sub, pic) in enumerate(STORIES):
    col, row = i % 2, i // 2
    px = M + col * (PW + GAP)
    py = GRID_TOP + row * (PH + GAP)
    rect(px, py, px + PW, py + PH, outline=INK, width=2)
    # region tag on red block
    ft = font(F_BOLD, 14)
    tww = spaced_w(tag, ft, 2)
    rect(px, py, px + tww + 24, py + 26, fill=RED)
    spaced(px + 12, py + 3, tag, ft, WHITE, 2)
    # pictogram panel
    bs = 156
    bx, by = px + 12, py + 26 + (PH - 26 - bs) / 2
    rect(bx, by, bx + bs, by + bs, fill=TINT)
    pic(bx + (bs - PIC) / 2, by + (bs - PIC) / 2)
    # text
    tx = bx + bs + 14
    tmax = px + PW - 12 - tx
    hs, hf, hl = fit_headline(head, tmax)
    lh = hs * 1.28
    ss, sf = fit_line(sub, F_REG, tmax, 17, 13)
    block_h = lh * len(hl) + 8 + ss * 1.3
    ty = by + (bs - block_h) / 2
    for k, l in enumerate(hl):
        text(tx, ty + k * lh, l, hf, INK)
    ry = ty + lh * len(hl) + 3
    rect(tx, ry, tx + 36, ry + 3, fill=RED)
    text(tx, ry + 7, sub, sf, (60, 57, 50))

# --------------------------------------------------------------------- footer
rect(0, FOOT_TOP, W, H, fill=INK)
rect(0, FOOT_TOP, W, FOOT_TOP + 4, fill=RED)
fb = font(F_BOLD, 16)
y = FOOT_TOP + 11
for b in BRIEFS:
    assert text_w(b, fb) <= W - 2 * M - 30, b
    cy = y + 11
    ell(M + 2, cy - 5, M + 12, cy + 5, fill=RED)
    text(M + 26, y, b, fb, WHITE)
    y += 25

out = img.resize((W, H), Image.LANCZOS)
dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
out.save(dest, format="PNG", optimize=True)
print("wrote", dest)
