"""Draws the app icon, launch images and store graphics, and copies them into the Xcode and Android projects.

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
    d.ellipse([cx - orbit, cy - orbit, cx + orbit, cy + orbit], outline=INK + (255,), width=w)

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
    canvas = icon_background(size)
    canvas.alpha_composite(icon_foreground(size))
    canvas.convert("RGB").resize((1024, 1024), Image.LANCZOS).save(path)  # App Store icons must have no alpha


def icon_background(size):
    canvas = vertical_gradient(size, VOID_2, VOID).convert("RGBA")
    stars(canvas, 70, 7, size * 5 / 1024)
    return canvas


def icon_foreground(size):
    """The small next planet and the orbit motif on a transparent layer."""
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sx, sy, sr = size * 0.24, size * 0.22, size * 0.075
    glow(canvas, sx, sy, sr * 1.8, PLANET_2[0], 80)
    canvas.alpha_composite(sphere(round(sr * 2), *PLANET_2), (round(sx - sr), round(sy - sr)))
    draw_motif(canvas, size * 0.55, size * 0.6, size * 0.2)
    return canvas


ANDROID_RES = ROOT / "android/app/src/main/res"
DENSITIES = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}


def make_android(res):
    """Launcher icons (legacy, round, adaptive layers) and pre-Android-12 launch images."""
    big = 2048
    bg = icon_background(big)
    fg = icon_foreground(big)
    full = bg.copy()
    full.alpha_composite(fg)
    # adaptive foreground: the artwork shrunk into the 66dp safe circle of the 108dp layer
    safe = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    inner = round(big * 0.62)
    safe.alpha_composite(fg.resize((inner, inner), Image.LANCZOS), ((big - inner) // 2, (big - inner) // 2))
    for name, scale in DENSITIES.items():
        folder = res / f"mipmap-{name}"
        folder.mkdir(exist_ok=True)
        icon, layer = round(48 * scale), round(108 * scale)
        full.convert("RGB").resize((icon, icon), Image.LANCZOS).save(folder / "ic_launcher.png")
        round_icon = full.resize((icon, icon), Image.LANCZOS)
        mask = Image.new("L", (icon * 4, icon * 4), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, icon * 4 - 1, icon * 4 - 1], fill=255)
        round_icon.putalpha(mask.resize((icon, icon), Image.LANCZOS))
        round_icon.save(folder / "ic_launcher_round.png")
        bg.convert("RGB").resize((layer, layer), Image.LANCZOS).save(folder / "ic_launcher_background.png")
        safe.resize((layer, layer), Image.LANCZOS).save(folder / "ic_launcher_foreground.png")
    # launch images for Android 11 and older: crop the square splash to each screen shape
    splash = Image.open(RES / "splash.png")
    for path in res.glob("drawable*/splash.png"):
        w, h = Image.open(path).size
        side = max(w, h)
        img = splash.resize((side, side), Image.LANCZOS)
        img.crop(((side - w) // 2, (side - h) // 2, (side - w) // 2 + w, (side - h) // 2 + h)).save(path)


def make_play_assets(folder):
    """Google Play listing graphics: 512x512 icon and 1024x500 feature graphic."""
    folder.mkdir(parents=True, exist_ok=True)
    Image.open(RES / "icon.png").resize((512, 512), Image.LANCZOS).save(folder / "play-icon-512.png")

    ss = 2
    w, h = 1024 * ss, 500 * ss
    canvas = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(canvas)
    for x in range(w):
        d.line([(x, 0), (x, h)], fill=lerp(VOID, VOID_2, x / (w - 1)))
    canvas = canvas.convert("RGBA")
    stars(canvas, 120, 5, 3 * ss)
    draw_motif(canvas, w * 0.76, h * 0.52, h * 0.2)
    d = ImageDraw.Draw(canvas)
    title = ImageFont.truetype(str(RES / "fonts/BlackHanSans-Regular.ttf"), 128 * ss)
    sub = ImageFont.truetype(str(RES / "fonts/GothicA1-Bold.ttf"), 34 * ss)
    d.text((80 * ss, 215 * ss), "궤도점프", font=title, fill=INK, anchor="ls")
    d.text((84 * ss, 290 * ss), "탭 한 번으로 우주를 건너요", font=sub, fill=APRICOT, anchor="ls")
    canvas.convert("RGB").resize((1024, 500), Image.LANCZOS).save(folder / "feature-graphic-1024x500.png")


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
    if ANDROID_RES.exists():
        make_android(ANDROID_RES)
        print("launcher icons and launch images written into the Android project")
    make_play_assets(ROOT / "store/play")
    print("wrote resources/icon.png, resources/splash.png and store/play/ graphics")
