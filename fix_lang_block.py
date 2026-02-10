from __future__ import annotations
import re
from pathlib import Path

LANG_BLOCK_NEW = """<div class="lang-switch" role="group" aria-label="Language">
        <button class="lang-btn" type="button" data-lang="en" aria-pressed="true">
          <span class="flag" aria-hidden="true">🇺🇸</span>
          <span class="lang-label">English</span>
        </button>
        <button class="lang-btn" type="button" data-lang="es" aria-pressed="false">
          <span class="flag" aria-hidden="true">🇸🇻</span>
          <span class="lang-label">Spanish</span>
        </button>
      </div>"""

pat = re.compile(r'<div\s+class="lang-switch"[\s\S]*?</div>', re.IGNORECASE)

for fn in ["index.html", "travel.html"]:
    p = Path(fn)
    s = p.read_text(encoding="utf-8")
    m = pat.search(s)
    if not m:
        raise SystemExit(f"Could not find lang-switch block in {fn}")
    out = s[:m.start()] + LANG_BLOCK_NEW + s[m.end():]
    p.write_text(out, encoding="utf-8")

print("OK: replaced lang-switch blocks in index.html and travel.html")
