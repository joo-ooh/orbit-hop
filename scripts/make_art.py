"""Draws the app icon (1024x1024) and launch image (2732x2732) and copies them into the Xcode project.

Run from the project root:  python3 scripts/make_art.py
"""
import math
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "resources"
IOS_ASSETS = ROOT / "ios/App/App/Assets.xcassets"

VOID = (23, 15, 46)
VOID_2 = (58, 29, 79)
INK = (246, 238, 252)
APRICOT = (255, 179, 107)
ROSE = (255, 111, 145)
PLANET = ((255, 159, 122), (194, 69, 107))
PLANET_2 = ((143, 211, 255), (59, 91, 214))


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vertical_gradient(size, top, bottom):
    img = Image.new("RGB", (size, size))
    d = ImageDraw.Draw(img)
    for y in range(size):
        d.line([(0, y), (size, y)], fill=lerp(top, bottom, y / (size - 1)))
    return img


def sphere(size, light, dark):
    """A planet: radial gradient lit from the upper left."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    r = size / 2
    lx, ly = r * 0.62, r * 0.55
    for y in range(size):
        for x in range(size):
            dx, dy = x + 0.5 - r, y + 0.5 - r
            if dx * dx + dy * dy > r * r:
                continue
            t = min(1, math.hypot(x - lx, y - ly) / (size * 0.95))
            px[x, y] = lerp(light, dark, t) + (255,)
    return img


def glow(canvas, cx, cy, radius, color, strength):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=color + (strength,))
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.45))
    canvas.alpha_composite(layer)


def draw_motif(canvas, cx, cy, s):
    """Planet, orbit ring and the player dot with its trail. s = planet radius in px."""
    orbit = s * 1.75
    glow(canvas, cx, cy, s * 1.6, PLANET[0], 110)

    d = ImageDraw.Draw(canvas)
    w = max(2, round(s * 0.05))
    d.ellipse([cx - orbit, cy - orbit, cx + orbit, cy + orbit], outline=INK + (90,), width=w)

    ball = sphere(round(s * 2), *PLANET)
    canvas.alpha_composite(ball, (round(cx - s), round(cy - s)))

    # surface bands, clipped to the planet
    bands = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(bands)
    for k in (-0.45, 0.0, 0.45):
        bd.ellipse([cx - s * 1.2, cy + k * s - s * 0.1, cx + s * 1.2, cy + k * s + s * 0.1], outline=(255, 255, 255, 40), width=round(s * 0.16))
    mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(mask).ellipse([cx - s, cy - s, cx + s, cy + s], fill=255)
    canvas.paste(Image.alpha_composite(canvas, bands), (0, 0), mask)

    # trail: an arc along the orbit that fades toward its tail, apricot into rose
    trail = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    td = ImageDraw.Draw(trail)
    head = -38  # degrees, upper right
    steps = 60
    for i in range(steps):
        t = i / (steps - 1)
        a0 = math.radians(head - 110 + 110 * t)
        a1 = math.radians(head - 110 + 110 * (t + 1 / steps))
        width = s * (0.06 + 0.22 * t)
        col = lerp(ROSE, APRICOT, t) + (round(40 + 215 * t),)
        p0 = (cx + math.cos(a0) * orbit, cy + math.sin(a0) * orbit)
        p1 = (cx + math.cos(a1) * orbit, cy + math.sin(a1) * orbit)
        td.line([p0, p1], fill=col, width=round(width))
        td.ellipse([p1[0] - width / 2, p1[1] - width / 2, p1[0] + width / 2, p1[1] + width / 2], fill=col)
    canvas.alpha_composite(trail)

    hx = cx + math.cos(math.radians(head)) * orbit
    hy = cy + math.sin(math.radians(head)) * orbit
    glow(canvas, hx, hy, s * 0.42, APRICOT, 200)
    d = ImageDraw.Draw(canvas)
    dot = s * 0.17
    d.ellipse([hx - dot, hy - dot, hx + dot, hy + dot], fill=(255, 255, 255, 255))


def stars(canvas, count, seed, max_r):
    import random
    rnd = random.Random(seed)
    d = ImageDraw.Draw(canvas)
    w, h = canvas.size
    for _ in range(count):
        x, y, r = rnd.random() * w, rnd.random() * h, rnd.random() * max_r + max_r * 0.3
        d.ellipse([x - r, y - r, x + r, y + r], fill=INK + (rnd.randint(60, 170),))


def make_icon(path):
    ss = 4  # supersample for smooth edges
    size = 1024 * ss
    canvas = vertical_gradient(size, VOID_2, VOID).convert("RGBA")
    stars(canvas, 70, 7, 5 * ss)
    # a small next planet, top left
    sx, sy, sr = size * 0.24, size * 0.22, size * 0.075
    glow(canvas, sx, sy, sr * 1.8, PLANET_2[0], 80)
    canvas.alpha_composite(sphere(round(sr * 2), *PLANET_2), (round(sx - sr), round(sy - sr)))
    draw_motif(canvas, size * 0.55, size * 0.6, size * 0.2)
    canvas.convert("RGB").resize((1024, 1024), Image.LANCZOS).save(path)  # App Store icons must have no alpha


def make_splash(path):
    size = 2732
    canvas = vertical_gradient(size, VOID, VOID_2).convert("RGBA")
    stars(canvas, 260, 11, 4)
    draw_motif(canvas, size / 2, size / 2 - 150, 150)
    font = ImageFont.truetype(str(RES / "fonts/BlackHanSans-Regular.ttf"), 150)
    d = ImageDraw.Draw(canvas)
    d.text((size / 2, size / 2 + 260), "궤도점프", font=font, fill=INK, anchor="mm")
    canvas.convert("RGB").save(path)


if __name__ == "__main__":
    RES.mkdir(exist_ok=True)
    make_icon(RES / "icon.png")
    make_splash(RES / "splash.png")
    if IOS_ASSETS.exists():
        shutil.copy(RES / "icon.png", IOS_ASSETS / "AppIcon.appiconset/AppIcon-512@2x.png")
        for name in ("splash-2732x2732.png", "splash-2732x2732-1.png", "splash-2732x2732-2.png"):
            shutil.copy(RES / "splash.png", IOS_ASSETS / "Splash.imageset" / name)
        print("icon and splash copied into the Xcode project")
    print("wrote resources/icon.png and resources/splash.png")
