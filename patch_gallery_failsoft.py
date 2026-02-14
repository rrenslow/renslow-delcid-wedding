from pathlib import Path
import re

def ensure_script_order(html_path: str):
    p = Path(html_path)
    s = p.read_text(encoding="utf-8")

    # Ensure photos.js appears before script.js (and both exist)
    has_photos = re.search(r'<script\s+src="photos\.js"', s)
    has_script = re.search(r'<script\s+src="script\.js"', s)
    if not has_script:
        raise SystemExit(f"{html_path}: missing script.js include")

    if not has_photos:
        # Insert photos.js immediately before script.js
        s = re.sub(
            r'(\s*<script\s+src="script\.js"\s*></script>\s*)',
            r'\n  <script src="photos.js"></script>\n\1',
            s,
            count=1
        )
        print(f"OK: inserted photos.js before script.js in {html_path}")
    else:
        # If both present, reorder if needed
        # Remove both then reinsert in correct order near the end before </body>
        if s.find('src="photos.js"') > s.find('src="script.js"'):
            s = re.sub(r'\s*<script\s+src="photos\.js"\s*></script>\s*', "\n", s, count=1)
            s = re.sub(r'\s*<script\s+src="script\.js"\s*></script>\s*', "\n", s, count=1)
            s = re.sub(
                r'(</body>)',
                r'  <script src="photos.js"></script>\n  <script src="script.js"></script>\n\1',
                s,
                count=1
            )
            print(f"OK: reordered photos.js before script.js in {html_path}")
        else:
            print(f"OK: script order already correct in {html_path}")

    p.write_text(s, encoding="utf-8")

# Apply to index.html (gallery lives there)
ensure_script_order("index.html")

# travel.html might not need photos.js; leave it alone unless you want it there too.
# If you DO want it there, uncomment:
# ensure_script_order("travel.html")

# Patch script.js to fail softly if PHOTO_GALLERY missing
p = Path("script.js")
js = p.read_text(encoding="utf-8")

marker = "/* GALLERY FAILSOFT */"
if marker not in js:
    # Find the line where photos are read
    # You showed: const photos = Array.isArray(window.PHOTO_GALLERY) ? window.PHOTO_GALLERY : null;
    # Replace with: [] and keep fallback content if empty
    js2 = js

    js2, n = re.subn(
        r'const\s+photos\s*=\s*Array\.isArray\(window\.PHOTO_GALLERY\)\s*\?\s*window\.PHOTO_GALLERY\s*:\s*null\s*;',
        marker + '\nconst photos = Array.isArray(window.PHOTO_GALLERY) ? window.PHOTO_GALLERY : [];',
        js2,
        count=1
    )

    if n == 0:
        print("WARN: did not find expected PHOTO_GALLERY line; skipping failsoft patch")
    else:
        # If photos is empty, do not wipe the existing HTML inside #photoGallery
        # Look for a pattern where it clears galleryEl.innerHTML = "" and guard it
        js2 = re.sub(
            r'(galleryEl\.innerHTML\s*=\s*""\s*;)',
            r'if (photos.length) { \1 }',
            js2,
            count=1
        )
        p.write_text(js2, encoding="utf-8")
        print("OK: patched script.js gallery to fail softly when PHOTO_GALLERY missing")
else:
    print("OK: script.js already has failsoft marker")

