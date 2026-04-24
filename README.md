# X: hide follower count

**Repository:** [github.com/wanoo21/X-hide-follower-count](https://github.com/wanoo21/X-hide-follower-count)

Open-source Chrome extension (Manifest V3). On [X](https://x.com) it replaces visible **follower** and **following** numbers with **∞** in the browser, so you can focus on posts instead of counts. It runs on profiles, hover cards, and anywhere those stats use the usual site links.

Nothing is uploaded or stored: a content script updates the page locally. Hover a stat after it is hidden to see a short note. Turn the extension off in `chrome://extensions` whenever you want real numbers again.

## Install from source

Clone the repo, open `chrome://extensions`, enable **Developer mode**, **Load unpacked**, and select this directory (the one that contains `manifest.json`).

## Development

- **`npm run deploy`** — build `dist/hide-x-followers-<version>.zip` (store-style package: `manifest.json`, `content.js`, `icons/`).
- **Icons** — `scripts/render-icon.py` (requires [Pillow](https://python-pillow.org/)); use a local venv or `pip install -t .vendor pillow` and point `PYTHONPATH` at `.vendor` if you use the script as written.

X’s front end changes; if a count slips through, the logic in `content.js` may need a small update.

## License

[MIT](LICENSE)