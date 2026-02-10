from __future__ import annotations

from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image

FRONT = Path("front_final.pdf")  # English
BACK  = Path("back_final.pdf")   # Spanish

OUT = Path("assets")
OUT.mkdir(parents=True, exist_ok=True)

TARGET_H = 900       # final height of the flower strips
ZOOM = 3.0           # render scale from PDF
WHITE_CUTOFF = 248   # >= this is considered "paper white" and made transparent
ALPHA_SOFTEN = 2     # higher -> softer watercolor edge (1-4 reasonable)

def render_pdf_page(pdf_path: Path, page_index: int = 0, zoom: float = ZOOM) -> Image.Image:
    if not pdf_path.exists():
        raise SystemExit(f"Missing {pdf_path} (expected in repo root).")
    doc = fitz.open(str(pdf_path))
    page = doc.load_page(page_index)
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img.convert("RGBA")

def white_to_transparent(im: Image.Image, cutoff: int = WHITE_CUTOFF) -> Image.Image:
    # Near-white -> transparent, keep color pixels opaque, preserve soft watercolor.
    px = im.getdata()
    out = []
    for r, g, b, a in px:
        if r >= cutoff and g >= cutoff and b >= cutoff:
            out.append((r, g, b, 0))
        else:
            # soften edge a bit: make very light pixels partially transparent
            lum = (r + g + b) // 3
            if lum > 220:
                alpha = max(0, min(255, 255 - (lum - 220) * ALPHA_SOFTEN))
                out.append((r, g, b, alpha))
            else:
                out.append((r, g, b, 255))
    im2 = Image.new("RGBA", im.size)
    im2.putdata(out)
    return im2

def trim(im: Image.Image) -> Image.Image:
    bbox = im.getbbox()
    return im.crop(bbox) if bbox else im

def split_left_right(im: Image.Image) -> tuple[Image.Image, Image.Image]:
    w, h = im.size
    left  = im.crop((0, 0, w // 2, h))
    right = im.crop((w // 2, 0, w, h))
    return left, right

def resize_to_height(im: Image.Image, target_h: int) -> Image.Image:
    w, h = im.size
    if h <= 0:
        return im
    if h == target_h:
        return im
    new_w = max(1, int(round(w * (target_h / h))))
    return im.resize((new_w, target_h), Image.Resampling.LANCZOS)

def export_pair(src_pdf: Path, prefix: str) -> None:
    page = render_pdf_page(src_pdf, 0)

    # Remove paper background, then split and trim each side separately.
    page_t = white_to_transparent(page)
    left, right = split_left_right(page_t)

    left = trim(left)
    right = trim(right)

    left = resize_to_height(left, TARGET_H)
    right = resize_to_height(right, TARGET_H)

    out_a = OUT / f"floral-strip-{prefix}-a.png"
    out_b = OUT / f"floral-strip-{prefix}-b.png"

    left.save(out_a, optimize=True)
    right.save(out_b, optimize=True)

    print(f"OK: wrote {out_a} {left.size}")
    print(f"OK: wrote {out_b} {right.size}")

export_pair(FRONT, "en")
export_pair(BACK, "es")
