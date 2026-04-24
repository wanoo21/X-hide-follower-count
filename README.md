# X: hide follower count

Chrome extension (Manifest V3) that shows **∞** instead of follower and following **numbers** on [x.com](https://x.com) wherever the usual `…/followers` and `…/following` stat links appear — including the **main profile** and **hover profile cards** in the feed.

## Load unpacked

1. Open Chrome and go to `chrome://extensions`.
2. Turn on **Developer mode** (top right).
3. Click **Load unpacked**.
4. Choose this folder: `hide-x-followers` (the directory that contains `manifest.json`).

Reload the extension after you change any file.

## Icons

Toolbar / store icons: **black** base (like the official tile), a **ghost** X from that asset, and a large **∞** on top. Rebuild: `pip install -t .vendor pillow` and `python3 scripts/render-icon.py`.

## Manual checks

- On a profile (`https://x.com/someone`) confirm followers / following show **∞**.
- Hover a profile in the timeline and confirm the hover card stats do too.
- Click to another profile without a full page reload; the count should still be replaced.
- Try accounts with `K` / `M` shorthand counts.

X’s HTML can change; if the count appears again, the content script’s selectors or replacement logic may need a small update.

## Limitations

This only changes what you see in the page UI. It does not affect X’s data or other clients.

## Publishing to the Chrome Web Store

1. Fill in the **Contact** line in `[privacy-policy.html](privacy-policy.html)` and host that file on **HTTPS** (GitHub Pages, your site, etc.). You will paste that URL into the store listing.
2. Read the checklist in `[docs/chrome-web-store.md](docs/chrome-web-store.md)` (screenshots, fees, permission justification, listing text).
3. Build the upload zip:
   ```bash
   npm run deploy
   ```
   (Equivalent to `bash ./scripts/package-for-store.sh`.) Upload **`dist/hide-x-followers-<version>.zip`** in the [Developer Dashboard](https://chrome.google.com/webstore/devconsole). The zip includes only `manifest.json`, `content.js`, and `icons/`.

## License

[MIT](LICENSE) (adjust copyright year or holder if you publish under your name).