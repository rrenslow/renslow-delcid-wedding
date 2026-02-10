from __future__ import annotations
import re
from pathlib import Path

FILES = ["index.html", "travel.html"]

def patch_file(fn: str) -> None:
    p = Path(fn)
    s = p.read_text(encoding="utf-8")

    # Replace the first <img ... class="floral-strip" ...> inside the floral-col with EN+ES stacked tags.
    # We preserve whether the page was using a.png or b.png by reading the existing src.
    floral_col = re.search(r'(<div\s+class="floral-col"[\s\S]*?>)([\s\S]*?)(</div>)', s, flags=re.IGNORECASE)
    if not floral_col:
        raise SystemExit(f"Could not find floral-col block in {fn}")

    block = floral_col.group(0)

    m = re.search(r'<img[^>]*class="floral-strip"[^>]*src="assets/floral-strip-([ab])\.png"[^>]*>', block, flags=re.IGNORECASE)
    if not m:
        # fallback: if already patched or different src, we still patch the first floral-strip img
        m2 = re.search(r'<img[^>]*class="floral-strip"[^>]*src="([^"]+)"[^>]*>', block, flags=re.IGNORECASE)
        if not m2:
            raise SystemExit(f"Could not find floral-strip <img> in floral-col block in {fn}")
        # If we can't infer a/b, default to b (right side) since that is what index commonly used.
        ab = "b"
        old_img = m2.group(0)
    else:
        ab = m.group(1)
        old_img = m.group(0)

    indent = "            "  # match your existing indentation

    new_imgs = (
        f'{indent}<img class="floral-strip" data-lang="en" src="assets/floral-strip-en-{ab}.png" alt="" aria-hidden="true" />\n'
        f'{indent}<img class="floral-strip" data-lang="es" src="assets/floral-strip-es-{ab}.png" alt="" aria-hidden="true" />'
    )

    new_block = block.replace(old_img, new_imgs, 1)
    s2 = s.replace(block, new_block, 1)

    p.write_text(s2, encoding="utf-8")
    print(f"OK: patched {fn} (uses {ab})")

for fn in FILES:
    patch_file(fn)
