from __future__ import annotations

from pathlib import Path
import re

HTML_FILES = ["index.html", "travel.html"]
CSS_FILE = "styles.css"

# These should already exist in assets/ from your previous work.
# If your filenames differ, edit them here (only here).
ASSETS = {
    "en_left": "assets/flower-en-left.png",
    "en_right": "assets/flower-en-right.png",
    "es_left": "assets/flower-es-left.png",
    "es_right": "assets/flower-es-right.png",
}

for k, v in ASSETS.items():
    if not Path(v).exists():
        raise SystemExit(f"Missing required asset: {v}")

def patch_html(fn: str) -> None:
    p = Path(fn)
    s = p.read_text(encoding="utf-8")

    # Detect which side this page currently uses (a vs b, left vs right).
    # We prefer to keep the existing "left column art" placement: floral-col inside hero-card.
    # We'll decide which flower to use by looking for existing floral-col block and if it's on left.
    # index.html typically shows the right-side plant, travel.html often shows left-side plant.
    # We keep that vibe: index -> right plant, travel -> left plant.
    use_side = "right" if fn == "index.html" else "left"

    if use_side == "right":
        en_src = ASSETS["en_right"]
        es_src = ASSETS["es_right"]
    else:
        en_src = ASSETS["en_left"]
        es_src = ASSETS["es_left"]

    new_block = f'''<div class="floral-col" aria-hidden="true">
            <div class="floral-frame" aria-hidden="true">
              <img class="floral-strip" data-lang="en" src="{en_src}" alt="" aria-hidden="true" />
              <img class="floral-strip" data-lang="es" src="{es_src}" alt="" aria-hidden="true" />
            </div>
          </div>'''

    # Replace existing floral-col block (robust multi-line replace)
    pat = re.compile(r'<div\s+class="floral-col"[\s\S]*?</div>\s*</div>', re.IGNORECASE)
    m = pat.search(s)
    if not m:
        # Alternative pattern: floral-col not wrapped with extra </div> in some variants
        pat2 = re.compile(r'<div\s+class="floral-col"[\s\S]*?</div>', re.IGNORECASE)
        m2 = pat2.search(s)
        if not m2:
            raise SystemExit(f"Could not find floral-col block in {fn}")
        s2 = s[:m2.start()] + new_block + s[m2.end():]
        p.write_text(s2, encoding="utf-8")
        print(f"OK: patched {fn} (alt match)")
        return

    s2 = s[:m.start()] + new_block + s[m.end():]
    p.write_text(s2, encoding="utf-8")
    print(f"OK: patched {fn}")

def patch_css() -> None:
    p = Path(CSS_FILE)
    s = p.read_text(encoding="utf-8")

    marker = "/* Floral frame (language-aware) */"
    if marker in s:
        print("OK: styles.css already contains floral frame block")
        return

    css_block = """
/* Floral frame (language-aware) */
.floral-col{
  display:flex;
  align-items:flex-start;
  justify-content:center;
  padding: 14px 10px 0 10px;
}
.floral-frame{
  background: rgba(255,255,255,0.78);
  border: 1px solid rgba(40,40,40,0.10);
  border-radius: 18px;
  box-shadow: 0 14px 34px rgba(0,0,0,0.10);
  padding: 18px 18px 14px 18px;
  backdrop-filter: blur(6px);
}
.floral-strip{
  display:block;
  width: min(320px, 26vw);
  height: auto;
  filter: drop-shadow(0 10px 18px rgba(0,0,0,0.10));
}

/* Keep the flower visually subtle on small screens */
@media (max-width: 860px){
  .floral-strip{
    width: min(260px, 56vw);
  }
  .floral-frame{
    padding: 14px 14px 10px 14px;
    border-radius: 16px;
  }
}
""".strip() + "\n"

    # Append near existing hero-card rules if possible, else append to end.
    insert_after = re.search(r'(?ms)^\.hero-card\s*\{.*?\}\s*', s)
    if insert_after:
        idx = insert_after.end()
        s2 = s[:idx] + "\n\n" + css_block + "\n" + s[idx:]
    else:
        s2 = s.rstrip() + "\n\n" + css_block

    p.write_text(s2, encoding="utf-8")
    print("OK: patched styles.css (added floral frame block)")

for f in HTML_FILES:
    patch_html(f)

patch_css()
print("DONE")
