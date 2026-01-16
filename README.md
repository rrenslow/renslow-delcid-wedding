# Renslow & Del Cid Wedding Website (GitHub Pages)

## Quick publish
1. Create a new GitHub repo (public).
2. Upload all files in this folder (including `assets/`).
3. In GitHub: Settings -> Pages -> Build and deployment -> Source: Deploy from a branch.
4. Select Branch: `main` and Folder: `/ (root)`.

Your site will be available at:
`https://<your-username>.github.io/<repo-name>/`

## Customize
- Edit text in `index.html` and `travel.html`.
- Replace photos in `assets/` and keep the same filenames, or update references in `index.html`.
- Update phone number and date in `script.js`.


## Adding photos

Fastest method (no terminal):
1) In your GitHub repo, open the `assets/` folder.
2) Click **Add file -> Upload files**.
3) Drag in your photos (JPG/PNG).
4) Commit the changes.

Recommended naming:
- `photo6.jpg` (full size)
- `photo6_sm.jpg` (small, optional but faster loading)

To show a new photo on the site, copy/paste one of the existing `<figure class="polaroid">` blocks in `index.html` and update:
- `data-full="assets/<filename>"`
- `<img src="assets/<filename>" alt="...">`
- The English + Spanish captions (`<figcaption data-lang=...>`)

If you send me the photo filenames plus the caption text you want, I can drop them in for you.
