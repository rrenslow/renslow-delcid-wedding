from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageOps

EN_SRC = Path("English.png")
ES_SRC = Path("Spanish.png")
OUTDIR = Path("assets")
OUTDIR.mkdir(parents=True, exist_ok=True)

# Target size: subtle on the page (tweak if you want)
TARGET_H = 560

# How aggressively to remove white background (higher = removes more)
WHITE_CUTOFF = 247

def white_to_transparent(im: Image.Image, cutoff: int = WHITE_CUTOFF) -> Image.Image:
    im = im.convert("RGBA")
    px = im.getdata()
    out = []
    for r, g, b, a in px:
        if r >= cutoff and g >= cutoff and b >= cutoff:
            out.append((r, g, b, 0))
        else:
            # soften very light pixels for watercolor edges
            lum = (r + g + b) // 3
            if lum > 230:
                alpha = max(0, min(255, 255 - (lum - 230) * 6))
                out.append((r, g, b, alpha))
            else:
                out.append((r, g, b, 255))
    out_im = Image.new("RGBA", im.size)
    out_im.putdata(out)
    return out_im

def trim(im: Image.Image) -> Image.Image:
    bbox = im.getbbox()
    return im.crop(bbox) if bbox else im

def resize_to_height(im: Image.Image, h: int) -> Image.Image:
    w0, h0 = im.size
    if h0 == 0:
        return im
    w = max(1, round(w0 * (h / h0)))
    return im.resize((w, h), Image.Resampling.LANCZOS)

def process(src: Path) -> Image.Image:
    if not src.exists():
        raise SystemExit(f"Missing {src} (expected in repo root).")
    im = Image.open(src)
    im = white_to_transparent(im)
    im = trim(im)
    im = resize_to_height(im, TARGET_H)
    return im

en = process(EN_SRC)
es = process(ES_SRC)

# Left/right variants (right = mirrored)
en_left  = en
en_right = ImageOps.mirror(en)
es_left  = es
es_right = ImageOps.mirror(es)

(en_left).save(OUTDIR / "flower-en-left.png",  optimize=True)
(en_right).save(OUTDIR / "flower-en-right.png", optimize=True)
(es_left).save(OUTDIR / "flower-es-left.png",  optimize=True)
(es_right).save(OUTDIR / "flower-es-right.png", optimize=True)

print("OK: wrote assets/flower-en-left.png, assets/flower-en-right.png, assets/flower-es-left.png, assets/flower-es-right.png")
print("Sizes:",
      "en_left", en_left.size,
      "en_right", en_right.size,
      "es_left", es_left.size,
      "es_right", es_right.size)
