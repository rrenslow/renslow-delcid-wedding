from pathlib import Path
import re

p = Path("script.js")
s = p.read_text(encoding="utf-8")

marker = "/* GALLERY NORMALIZE */"
if marker in s:
    print("Already normalized.")
    raise SystemExit(0)

pat = r'(const\s+photos\s*=\s*Array\.isArray\(window\.PHOTO_GALLERY\)\s*\?\s*window\.PHOTO_GALLERY\s*:\s*\[\]\s*;\s*)'
m = re.search(pat, s)
if not m:
    raise SystemExit("Could not find canonical photos assignment line to patch")

norm = r'''
/* GALLERY NORMALIZE */
const photosNorm = photos
  .filter((p) => p && typeof p === "object" && typeof p.full === "string" && typeof p.thumb === "string")
  .map((p) => {
    const alt = (p.alt && typeof p.alt === "object") ? p.alt : {};
    const cap = (p.caption && typeof p.caption === "object") ? p.caption : {};
    return {
      full: p.full,
      thumb: p.thumb,
      alt: { en: String(alt.en || "Photo"), es: String(alt.es || "Foto") },
      caption: { en: String(cap.en || ""), es: String(cap.es || "") },
      tilt: typeof p.tilt === "string" ? p.tilt : "tilt2"
    };
  });
/* Use normalized entries for rendering */
const photosToRender = photosNorm;
'''.lstrip("\n")

# Insert immediately after the photos assignment line
s2 = s[:m.end()] + "\n" + norm + s[m.end():]

# Replace later references to photos (in the gallery section) with photosToRender conservatively:
# We only replace photos.length and photos.forEach which are the common operations.
s2 = re.sub(r'\bphotos\.length\b', 'photosToRender.length', s2)
s2 = re.sub(r'\bphotos\.forEach\b', 'photosToRender.forEach', s2)

p.write_text(s2, encoding="utf-8")
print("OK: added PHOTO_GALLERY normalization and switched render to photosToRender")
