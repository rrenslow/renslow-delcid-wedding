from __future__ import annotations
from pathlib import Path
import re

p = Path("styles.css")
s = p.read_text(encoding="utf-8")

# Ensure floral strip looks like subtle side art (no huge block)
css_add = r"""
/* Invitation flower art: subtle, watercolor-like side element */
.floral-col {
  display: flex;
  align-items: flex-start;
  justify-content: center;
}

.floral-strip {
  display: block;
  width: auto;
  max-width: 340px;
  height: auto;
  max-height: 560px;
  opacity: 0.9;
  filter: drop-shadow(0 10px 18px rgba(0,0,0,0.10));
  transform: translateY(6px);
}

@media (max-width: 820px) {
  .floral-strip {
    max-width: 220px;
    max-height: 420px;
    opacity: 0.92;
  }
}

@media (max-width: 560px) {
  .floral-col {
    display: none;
  }
}
""".strip() + "\n"

# If there's already a .floral-strip block, remove it (avoid conflicting rules)
s2 = re.sub(r'(?ms)^\s*\.floral-strip\s*\{.*?\}\s*', '', s)
s2 = re.sub(r'(?ms)^\s*\.floral-col\s*\{.*?\}\s*', '', s2)

# Append our canonical block near the end
if "Invitation flower art: subtle" not in s2:
    s2 = s2.rstrip() + "\n\n" + css_add

p.write_text(s2, encoding="utf-8")
print("OK: patched styles.css for floral-strip subtle rendering")
