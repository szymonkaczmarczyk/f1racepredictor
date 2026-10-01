from __future__ import annotations

import base64
import io
import shutil
import sys
from pathlib import Path

import numpy as np
from fontTools import subset
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "branding"
OUT = ROOT / "src" / "app" / "static" / "brand"
FONT_SOURCE = SOURCE / "fonts"
FONT_OUT = ROOT / "src" / "app" / "static" / "fonts"
FONT_WEIGHTS = ("Regular", "SemiBold", "Bold", "Black", "BoldItalic")
LATIN = "U+0000-024F,U+0259,U+02C6-02DD,U+1E00-1EFF,U+2000-206F,U+20AC,U+2122,U+2190-2193,U+2212"
OG_SIZE = (1200, 630)
OG_TITLE = "RACE PREDICTOR"
OG_TAGLINE = ("Formula 1 podium predictions", "from 30 years of race data")
OG_FOOT = "Win · podium · points odds from 20,000 simulated races"
OG_DOMAIN = "f1racepredictor.com"

BACKGROUND_FROM = 150
BACKGROUND_TO = 228
GREY_SPREAD = 40
LIGHT_GREY = (232, 234, 238)
TILE = (21, 21, 30)
WORDMARK_SHARE = 0.78


def knock_out(path: Path) -> Image.Image:
    rgb = np.asarray(Image.open(path).convert("RGB")).astype(float)
    floor = rgb.min(axis=2)
    alpha = np.clip((BACKGROUND_TO - floor) / (BACKGROUND_TO - BACKGROUND_FROM), 0.0, 1.0)
    paper = np.median(rgb[:40, :40].reshape(-1, 3), axis=0)
    safe = np.where(alpha > 0.01, alpha, 1.0)[..., None]
    colour = np.clip((rgb - (1.0 - alpha[..., None]) * paper) / safe, 0, 255)
    rgba = np.dstack([colour, alpha * 255]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def for_dark(image: Image.Image) -> Image.Image:
    data = np.asarray(image).copy()
    rgb = data[..., :3].astype(int)
    grey = (rgb.max(axis=2) - rgb.min(axis=2)) < GREY_SPREAD
    data[grey, 0], data[grey, 1], data[grey, 2] = LIGHT_GREY
    return Image.fromarray(data, "RGBA")


def trim(image: Image.Image, pad: int = 8, top_share: float = 1.0) -> Image.Image:
    alpha = np.asarray(image)[..., 3]
    limit = int(alpha.shape[0] * top_share)
    rows = np.where((alpha[:limit] > 20).any(axis=1))[0]
    cols = np.where((alpha[:limit] > 20).any(axis=0))[0]
    box = (max(cols[0] - pad, 0), max(rows[0] - pad, 0),
           min(cols[-1] + pad + 1, alpha.shape[1]), min(rows[-1] + pad + 1, limit))
    return image.crop(box)


def fit_height(image: Image.Image, height: int) -> Image.Image:
    width = round(image.width * height / image.height)
    return image.resize((width, height), Image.LANCZOS)


def tile(mark: Image.Image, size: int, radius_share: float = 0.22, inset_share: float = 0.14) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(canvas).rounded_rectangle(
        (0, 0, size - 1, size - 1), radius=round(size * radius_share), fill=TILE + (255,)
    )
    room = round(size * (1 - 2 * inset_share))
    scale = min(room / mark.width, room / mark.height)
    inner = mark.resize((max(1, round(mark.width * scale)), max(1, round(mark.height * scale))), Image.LANCZOS)
    canvas.alpha_composite(inner, ((size - inner.width) // 2, (size - inner.height) // 2))
    return canvas


def square(mark: Image.Image, size: int, inset_share: float = 0.04) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    room = round(size * (1 - 2 * inset_share))
    scale = min(room / mark.width, room / mark.height)
    inner = mark.resize((max(1, round(mark.width * scale)), max(1, round(mark.height * scale))), Image.LANCZOS)
    canvas.alpha_composite(inner, ((size - inner.width) // 2, (size - inner.height) // 2))
    return canvas


def png_data(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return base64.b64encode(buffer.getvalue()).decode()


def adaptive_svg(light: Image.Image, dark: Image.Image) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">'
        "<style>.d{display:none}@media (prefers-color-scheme:dark){.l{display:none}.d{display:inline}}</style>"
        f'<image class="l" width="128" height="128" href="data:image/png;base64,{png_data(light)}"/>'
        f'<image class="d" width="128" height="128" href="data:image/png;base64,{png_data(dark)}"/>'
        "</svg>"
    )


def web_fonts() -> None:
    FONT_OUT.mkdir(parents=True, exist_ok=True)
    for weight in FONT_WEIGHTS:
        options = subset.Options()
        options.flavor = "woff"
        options.layout_features = ["*"]
        options.name_IDs = ["*"]
        font = subset.load_font(str(FONT_SOURCE / f"TitilliumWeb-{weight}.ttf"), options)
        subsetter = subset.Subsetter(options)
        subsetter.populate(unicodes=subset.parse_unicodes(LATIN))
        subsetter.subset(font)
        subset.save_font(font, str(FONT_OUT / f"titillium-web-{weight.lower()}.woff"), options)
    shutil.copyfile(FONT_SOURCE / "OFL.txt", FONT_OUT / "OFL.txt")


def og_image(mark: Image.Image) -> Image.Image:
    width, height = OG_SIZE
    font = lambda weight, size: ImageFont.truetype(str(FONT_SOURCE / f"TitilliumWeb-{weight}.ttf"), size)
    canvas = Image.new("RGBA", OG_SIZE, TILE + (255,))
    draw = ImageDraw.Draw(canvas)
    for x in range(0, width, 6):
        shade = int(30 * (1 - x / width))
        draw.line([(x, 0), (x, height)], fill=(21 + shade, 21, 30 + shade // 3, 255), width=6)
    draw.rectangle((0, 0, width, 10), fill=(225, 6, 0, 255))
    logo = fit_height(mark, 250)
    canvas.alpha_composite(logo, (width - logo.width - 56, (height - logo.height) // 2 - 20))
    draw.polygon([(80, 150), (150, 150), (140, 166), (70, 166)], fill=(225, 6, 0, 255))
    draw.text((78, 178), OG_TITLE, font=font("Black", 80), fill=(245, 245, 247, 255))
    for i, line in enumerate(OG_TAGLINE):
        draw.text((80, 300 + i * 52), line, font=font("Regular", 42), fill=(205, 205, 214, 255))
    draw.text((80, 460), OG_FOOT, font=font("SemiBold", 28), fill=(154, 154, 171, 255))
    draw.text((80, 520), OG_DOMAIN, font=font("Bold", 34), fill=(255, 30, 16, 255))
    return canvas.convert("RGB")


def main() -> None:
    logo = SOURCE / "f1racepredictor-logo.jpg"
    mark = SOURCE / "f1racepredictor-logo2.jpg"
    if not logo.exists() or not mark.exists():
        sys.exit("expected branding/f1racepredictor-logo.jpg and branding/f1racepredictor-logo2.jpg")
    OUT.mkdir(parents=True, exist_ok=True)

    full = knock_out(logo)
    car = trim(full, top_share=WORDMARK_SHARE)
    fit_height(car, 160).save(OUT / "logo-mark-light.png", optimize=True)
    fit_height(for_dark(car), 160).save(OUT / "logo-mark-dark.png", optimize=True)
    whole = trim(full)
    fit_height(whole, 600).save(OUT / "logo-light.png", optimize=True)
    fit_height(for_dark(whole), 600).save(OUT / "logo-dark.png", optimize=True)

    plain = trim(knock_out(mark))
    symbol = for_dark(plain)
    tile(symbol, 512).save(OUT / "icon-512.png", optimize=True)
    tile(symbol, 192).save(OUT / "icon-192.png", optimize=True)
    tile(symbol, 512, radius_share=0.0, inset_share=0.22).save(OUT / "icon-maskable-512.png", optimize=True)
    tile(symbol, 180, radius_share=0.0).save(OUT / "apple-touch-icon.png", optimize=True)
    square(plain, 256).save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    (OUT / "favicon.svg").write_text(adaptive_svg(square(plain, 128), square(symbol, 128)), encoding="utf-8")
    og_image(for_dark(car)).save(OUT / "og-image.png", optimize=True)
    web_fonts()
    print("written:", ", ".join(sorted(p.name for p in OUT.iterdir())))
    print("fonts:", ", ".join(f"{p.name} {p.stat().st_size // 1024} KB" for p in sorted(FONT_OUT.iterdir())))


if __name__ == "__main__":
    main()
