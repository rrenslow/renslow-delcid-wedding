from __future__ import annotations

import re
from pathlib import Path

REPO_FILES = ["index.html", "travel.html", "styles.css", "script.js"]

for f in REPO_FILES:
    if not Path(f).exists():
        raise SystemExit(f"Missing required file: {f}")

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

def replace_lang_block(html: str) -> str:
    # Replace any existing lang-switch div (multi-line)
    pat = re.compile(r'<div\s+class="lang-switch"[\s\S]*?</div>', re.IGNORECASE)
    m = pat.search(html)
    if not m:
        raise SystemExit("Could not find <div class=\"lang-switch\"> block to replace.")
    return html[:m.start()] + LANG_BLOCK_NEW + html[m.end():]

def ensure_css(styles: str) -> str:
    # Remove any previous lang-switch/lang-btn blocks to avoid conflicting rules
    # We remove blocks that start with ".lang-switch" or ".lang-btn" selector and run until the next blank line.
    # Conservative: only remove if we later re-add our canonical block.
    styles2 = re.sub(r'(?ms)^\s*\.lang-switch\s*\{.*?\}\s*\n(?:\s*\n)?', '', styles)
    styles2 = re.sub(r'(?ms)^\s*\.lang-btn\s*\{.*?\}\s*\n(?:\s*\n)?', '', styles2)
    styles2 = re.sub(r'(?ms)^\s*\.lang-btn\s+\.flag\s*\{.*?\}\s*\n(?:\s*\n)?', '', styles2)
    styles2 = re.sub(r'(?ms)^\s*\.lang-btn\s*\[aria-pressed="true"\]\s*\{.*?\}\s*\n(?:\s*\n)?', '', styles2)
    styles2 = re.sub(r'(?ms)^\s*\.lang-btn:focus-visible\s*\{.*?\}\s*\n(?:\s*\n)?', '', styles2)

    css_block = """
/* Language toggle: two visible buttons with flags */
.lang-switch {
  display: flex;
  gap: 10px;
  align-items: center;
}

.lang-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(0,0,0,0.12);
  background: rgba(255,255,255,0.65);
  padding: 8px 10px;
  border-radius: 999px;
  cursor: pointer;
  font: inherit;
  line-height: 1;
  user-select: none;
}

.lang-btn .flag {
  font-size: 16px;
  line-height: 1;
}

.lang-btn[aria-pressed="true"] {
  background: rgba(255,255,255,0.95);
  border-color: rgba(0,0,0,0.22);
}

.lang-btn:focus-visible {
  outline: 2px solid rgba(0,0,0,0.35);
  outline-offset: 2px;
}
""".lstrip("\n")

    # Append at end so it wins in cascade
    if "Language toggle: two visible buttons with flags" in styles2:
        return styles2
    return styles2.rstrip() + "\n\n" + css_block

def ensure_js(script: str) -> str:
    if "initLanguageToggle" in script or "siteLang" in script:
        return script

    js_block = r"""
// Language toggle (English/Spanish), persisted in localStorage
(function initLanguageToggle() {
  const root = document.documentElement;
  const buttons = Array.from(document.querySelectorAll(".lang-btn"));

  if (!buttons.length) return;

  function setLang(lang) {
    root.setAttribute("data-language", lang);
    buttons.forEach((b) => b.setAttribute("aria-pressed", b.dataset.lang === lang ? "true" : "false"));
    try {
      localStorage.setItem("siteLang", lang);
    } catch (e) {}
  }

  let saved = null;
  try {
    saved = localStorage.getItem("siteLang");
  } catch (e) {}

  setLang(saved === "es" ? "es" : "en");

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => setLang(btn.dataset.lang));
  });
})();
""".lstrip("\n")

    # Insert near top (after any "use strict"; or initial comments)
    lines = script.splitlines(True)
    insert_at = 0
    for i, line in enumerate(lines[:50]):
        if line.strip().startswith('"use strict"') or line.strip().startswith("'use strict'"):
            insert_at = i + 1
            break
    return "".join(lines[:insert_at]) + ("\n" if insert_at else "") + js_block + "\n" + "".join(lines[insert_at:])

# Apply HTML changes
for html_file in ["index.html", "travel.html"]:
    p = Path(html_file)
    text = p.read_text(encoding="utf-8")
    updated = replace_lang_block(text)
    if updated != text:
        p.write_text(updated, encoding="utf-8")

# Apply CSS changes
styles_path = Path("styles.css")
styles_text = styles_path.read_text(encoding="utf-8")
styles_updated = ensure_css(styles_text)
if styles_updated != styles_text:
    styles_path.write_text(styles_updated, encoding="utf-8")

# Apply JS changes
script_path = Path("script.js")
script_text = script_path.read_text(encoding="utf-8")
script_updated = ensure_js(script_text)
if script_updated != script_text:
    script_path.write_text(script_updated, encoding="utf-8")

print("OK: updated index.html, travel.html, styles.css, script.js")
