from pathlib import Path
import re

rev = "0899761"
targets = ["index.html", "travel.html"]

def patch_file(fn: str):
    p = Path(fn)
    s = p.read_text(encoding="utf-8")

    # styles.css (with or without existing ?v=)
    s = re.sub(r'href="styles\.css(\?v=[^"]*)?"', f'href="styles.css?v={rev}"', s)

    # script.js (with or without existing ?v=)
    s = re.sub(r'src="script\.js(\?v=[^"]*)?"', f'src="script.js?v={rev}"', s)

    # photos.js only exists on index.html typically, but safe to patch if present
    s = re.sub(r'src="photos\.js(\?v=[^"]*)?"', f'src="photos.js?v={rev}"', s)

    p.write_text(s, encoding="utf-8")
    print(f"OK: patched {fn}")

for fn in targets:
    patch_file(fn)
