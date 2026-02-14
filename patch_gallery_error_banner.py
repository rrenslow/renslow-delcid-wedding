from pathlib import Path
import re

p = Path("script.js")
s = p.read_text(encoding="utf-8")

marker = "/* GALLERY ERROR BANNER */"
if marker in s:
    print("Already patched.")
    raise SystemExit(0)

# Find the start of the photo gallery IIFE by locating the line that grabs photoGallery
m = re.search(r'const\s+galleryEl\s*=\s*document\.getElementById\("photoGallery"\)\s*;', s)
if not m:
    raise SystemExit("Could not find galleryEl init line in script.js")

insert_at = m.start()

banner = r'''
/* GALLERY ERROR BANNER */
function __galleryBanner(msg) {
  try {
    const el = document.getElementById("photoGallery");
    if (!el) return;
    const box = document.createElement("div");
    box.className = "paper card subtle";
    box.style.gridColumn = "1 / -1";
    box.innerHTML = '<strong>Gallery error:</strong><br/><span style="font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \\"Liberation Mono\\", \\"Courier New\\", monospace;">' +
      String(msg).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;") +
      "</span>";
    el.prepend(box);
  } catch (e) {}
}
'''.lstrip("\n")

s2 = s[:insert_at] + banner + s[insert_at:]

# Wrap the gallery render section in try/catch by guarding the first usage of photos
# We do this by inserting try { right after const photos = ...; and a catch before the end of that gallery block.
m2 = re.search(r'const\s+photos\s*=\s*Array\.isArray\(window\.PHOTO_GALLERY\)[^;]*;', s2)
if not m2:
    raise SystemExit("Could not find photos assignment line in script.js")

after_photos = m2.end()

# Insert try { after photos line
s2 = s2[:after_photos] + "\n  try {\n" + s2[after_photos:]

# Insert catch right before the end of the photo gallery IIFE by finding the next occurrence of })(); after galleryEl line.
start_search = s2.find('document.getElementById("photoGallery")')
end_iife = s2.find("})();", start_search)
if end_iife == -1:
    raise SystemExit("Could not find end of gallery IIFE (})();)")

# Put catch just before end_iife
s2 = s2[:end_iife] + '\n  } catch (e) { __galleryBanner(e && (e.stack || e.message) ? (e.stack || e.message) : e); }\n' + s2[end_iife:]

p.write_text(s2, encoding="utf-8")
print("OK: patched script.js to show gallery errors on-page")
