from __future__ import annotations

import re
from pathlib import Path

FILES = ["index.html", "travel.html"]

LANG_BLOCK_NEW = """<div class="lang-switch" role="group" aria-label="Language">
        <button class="lang-btn" type="button" data-lang="en" aria-pressed="true">
          <span class="flag" aria-hidden="true">
            <svg class="flag-svg" viewBox="0 0 64 48" width="18" height="14" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="United States flag">
              <rect width="64" height="48" fill="#ffffff"/>
              <rect y="0"  width="64" height="4" fill="#b22234"/>
              <rect y="8"  width="64" height="4" fill="#b22234"/>
              <rect y="16" width="64" height="4" fill="#b22234"/>
              <rect y="24" width="64" height="4" fill="#b22234"/>
              <rect y="32" width="64" height="4" fill="#b22234"/>
              <rect y="40" width="64" height="4" fill="#b22234"/>
              <rect width="28" height="20" fill="#3c3b6e"/>
              <g fill="#ffffff" opacity="0.95">
                <circle cx="4" cy="3" r="1"/>
                <circle cx="10" cy="3" r="1"/>
                <circle cx="16" cy="3" r="1"/>
                <circle cx="22" cy="3" r="1"/>
                <circle cx="7" cy="7" r="1"/>
                <circle cx="13" cy="7" r="1"/>
                <circle cx="19" cy="7" r="1"/>
                <circle cx="25" cy="7" r="1"/>
                <circle cx="4" cy="11" r="1"/>
                <circle cx="10" cy="11" r="1"/>
                <circle cx="16" cy="11" r="1"/>
                <circle cx="22" cy="11" r="1"/>
                <circle cx="7" cy="15" r="1"/>
                <circle cx="13" cy="15" r="1"/>
                <circle cx="19" cy="15" r="1"/>
                <circle cx="25" cy="15" r="1"/>
              </g>
            </svg>
          </span>
          <span class="lang-label">English</span>
        </button>

        <button class="lang-btn" type="button" data-lang="es" aria-pressed="false">
          <span class="flag" aria-hidden="true">
            <svg class="flag-svg" viewBox="0 0 64 48" width="18" height="14" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="El Salvador flag">
              <rect width="64" height="48" fill="#0f47af"/>
              <rect y="16" width="64" height="16" fill="#ffffff"/>
              <g transform="translate(32 24)">
                <circle r="5.2" fill="#0f47af" opacity="0.9"/>
                <circle r="3.6" fill="#ffffff" opacity="0.95"/>
                <circle r="2.0" fill="#2e8b57" opacity="0.95"/>
              </g>
            </svg>
          </span>
          <span class="lang-label">Español</span>
        </button>
      </div>"""

PAT = re.compile(r'<div\s+class="lang-switch"[\s\S]*?</div>', re.IGNORECASE)

def patch_file(path: Path) -> None:
    s = path.read_text(encoding="utf-8")
    m = PAT.search(s)
    if not m:
        raise SystemExit(f"Could not find lang-switch block in {path.name}")
    out = s[:m.start()] + LANG_BLOCK_NEW + s[m.end():]
    path.write_text(out, encoding="utf-8")
    print(f"OK: patched {path.name}")

for fn in FILES:
    patch_file(Path(fn))
