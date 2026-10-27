"""Puts each raw capture into captioned store frames: App Store (1320x2868) and Google Play (1080x1920).

Run from the project root: `npm run store-shots` (captures, then frames)
Edit CAPTIONS to change the copy.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "store/screenshots/raw"
OUT = ROOT / "store/screenshots"
FONT = ROOT / "resources/fonts/BlackHanSans-Regular.ttf"

# output sets: App Store (iPhone 6.9") and Google Play (phone, at most 2:1)
SIZES = {"app-store": (1320, 2868, OUT), "google-play": (1080, 1920, ROOT / "store/play/screenshots")}
TOP, BOTTOM = (58, 29, 79), (23, 15, 46)
INK, APRICOT = (246, 238, 252), (255, 179, 107)

CAPTIONS = {
    "1-menu.png": ("탭 한 번으로", "궤도를 건너뛰세요"),
    "2-play.png": ("가장자리를 스치면", "PERFECT 콤보"),
    "3-climb.png": ("올라갈수록", "작아지고 빨라져요"),
    "4-howto.png": ("규칙은 하나", "링이 사라지기 전에 점프"),
}


def frame(raw_path, lines, W, H):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(round(TOP[i] + (BOTTOM[i] - TOP[i]) * t) for i in range(3)))

    k = W / 1320  # layout was designed at 1320 wide
    font = ImageFont.truetype(str(FONT), round(112 * k))
    d.text((W / 2, H * 250 / 2868), lines[0], font=font, fill=INK, anchor="mm")
    d.text((W / 2, H * 390 / 2868), lines[1], font=font, fill=APRICOT, anchor="mm")

    shot = Image.open(raw_path).convert("RGB")
    y = round(H * 540 / 2868)
    sw = min(round(1040 * k), round((H - y - H * 0.016) * shot.width / shot.height))
    sh = round(shot.height * sw / shot.width)
    shot = shot.resize((sw, sh), Image.LANCZOS)
    x = (W - sw) // 2
    radius = round(64 * sw / 1040)
    border = max(3, round(6 * k))
    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, sw - 1, sh - 1], radius=radius, fill=255)
    d.rounded_rectangle([x - border, y - border, x + sw + border - 1, y + sh + border - 1], radius=radius + border, fill=(90, 62, 120))
    img.paste(shot, (x, y), mask)
    return img


if __name__ == "__main__":
    for W, H, folder in SIZES.values():
        folder.mkdir(parents=True, exist_ok=True)
        for name, lines in CAPTIONS.items():
            src = RAW / name
            if not src.exists():
                print("missing", src)
                continue
            frame(src, lines, W, H).save(folder / name)
            print("wrote", folder / name)
