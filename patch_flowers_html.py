from __future__ import annotations
from pathlib import Path
import re

def patch_file(fn: str, slot: str) -> None:
    p = Path(fn)
    s = p.read_text(encoding="utf-8")

    if slot == "left":
        en_src = "assets/flower-en-left.png"
        es_src = "assets/flower-es-left.png"
    else:
        en_src = "assets/flower-en-right.png"
        es_src = "assets/flower-es-right.png"

    # Replace any existing floral-strip bilingual tags (or single tag) inside the floral-col.
    # We only touch the first floral-col block to keep changes tight.
    floral_col_pat = re.compile(r'(<div\s+class="floral-col"[\s\S]*?</div>)', re.IGNORECASE)
    m = floral_col_pat.search(s)
    if not m:
        raise SystemExit(f"Could not find floral-col in {fn}")

    col = m.group(1)

    # Remove any existing <img class="floral-strip"...> lines inside that block
    col2 = re.sub(r'^\s*<img\s+class="floral-strip"[^>]*>\s*$', "", col, flags=re.IGNORECASE | re.MULTILINE)
    col2 = re.sub(r'^\s*<img\s+class="floral-strip"[^>]*/>\s*$', "", col2, flags=re.IGNORECASE | re.MULTILINE)

    # Insert bilingual images right after the opening div line
    open_div = re.search(r'<div\s+class="floral-col"[^>]*>', col2, flags=re.IGNORECASE)
    if not open_div:
        raise SystemExit(f"Could not parse floral-col opening tag in {fn}")

    insert = (
        f'\n            <img class="floral-strip" data-lang="en" src="{en_src}" alt="" aria-hidden="true" />\n'
        f'            <img class="floral-strip" data-lang="es" src="{es_src}" alt="" aria-hidden="true" />\n'
    )
    col3 = col2[:open_div.end()] + insert + col2[open_div.end():]

    s2 = s[:m.start()] + col3 + s[m.end():]
    p.write_text(s2, encoding="utf-8")
    print(f"OK: patched {fn} ({slot})")

patch_file("travel.html", "left")
patch_file("index.html", "right")
