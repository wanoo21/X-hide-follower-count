#!/usr/bin/env python3
"""
Fetches the X responsive-web iOS icon, fades the mark using the luminance mask
(so it reads as a ghost, not solid white at full strength), then draws a very
large centered ∞ (sized to the real glyph box, not font pt alone).

  pip install -t .vendor pillow
  python3 scripts/render-icon.py
"""
import os
import sys
import urllib.request

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_VENDOR = os.path.join(_ROOT, ".vendor")
if os.path.isdir(_VENDOR):
    sys.path.insert(0, _VENDOR)

from io import BytesIO  # noqa: E402

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

_URL = "https://abs.twimg.com/responsive-web/client-web/icon-ios.77d25eba.png"

try:
    _LANCZOS = Image.Resampling.LANCZOS
except AttributeError:
    _LANCZOS = Image.LANCZOS


def _ua_open(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; render-icon/1.0)"},
    )
    with urllib.request.urlopen(req) as r:
        return r.read()


def _font_path():
    for c in (
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ):
        if os.path.isfile(c):
            return c
    return None


def _ghost_x_from_luma(data: bytes) -> Image.Image:
    """
    The CDN icon is light X on dark canvas. Pixels in convert(RGBA) are opaque
    white/black — scaling alpha alone still looks "solid" on a gray toolbar.
    Rebuild a layer from the L channel: dim gray where the X is, transparent
    where the background is, with modest alpha so it reads as a watermark.
    """
    base = Image.open(BytesIO(data)).convert("RGBA")
    l = base.convert("L")
    t = 18  # ignore noise / soft edges
    # Soft gray that stays visible but clearly behind the ∞
    R = l.point(lambda p, t=t: int(78 + 55 * p / 255) if p > t else 0)
    G = l.point(lambda p, t=t: int(82 + 50 * p / 255) if p > t else 0)
    B = l.point(lambda p, t=t: int(90 + 45 * p / 255) if p > t else 0)
    # Brighter X strokes = a bit more opacity, but cap so it never reads as "solid"
    A = l.point(lambda p, t=t: int(115 * (p / 255) ** 0.9) if p > t else 0)
    return Image.merge("RGBA", (R, G, B, A))


def _text_extents(draw, ch, font, stroke):
    if hasattr(draw, "textbbox"):
        return draw.textbbox(
            (0, 0), ch, font=font, stroke_width=stroke, anchor="lt"
        )
    tw, th = font.getsize(ch)  # type: ignore[union-attr]
    return (0, 0, tw, th)


def _font_size_fitting_width(
    draw, w, h, ch, font_path, stroke, target_frac: float
) -> ImageFont.ImageFont:
    """
    Font pt is not the drawn width of '∞' — binary-search the largest size so
    the inked bbox (incl. stroke) fits inside the frame.
    """
    if not font_path:
        return ImageFont.load_default()
    margin = int(min(w, h) * 0.04)
    max_w = int(min(w, h) * target_frac) - 2 * margin
    max_h = int(min(w, h) * 0.88) - 2 * margin
    lo, hi = 8, int(min(w, h) * 1.2)
    best_font = None
    while lo <= hi:
        mid = (lo + hi) // 2
        font = ImageFont.truetype(font_path, mid)
        l, t, r, b = _text_extents(draw, ch, font, stroke)
        tw, th = r - l, b - t
        if tw <= max_w and th <= max_h:
            best_font = font
            lo = mid + 1
        else:
            hi = mid - 1
    if best_font is None:
        best_font = ImageFont.truetype(
            font_path, max(16, int(min(w, h) * 0.2))
        )
    return best_font


def _draw_infinity_center(draw, w, h, font, ch, stroke):
    cx, cy = w // 2, h // 2
    # Thin stroke: reads clean when scaled to 16px
    try:
        draw.text(
            (cx, cy),
            ch,
            font=font,
            fill=(255, 255, 255, 255),
            stroke_width=stroke,
            stroke_fill=(25, 30, 35, 255),
            anchor="mm",
        )
    except TypeError:
        l, t, r, b = _text_extents(draw, ch, font, stroke)
        tw, th = r - l, b - t
        x = (w - tw) // 2 - l
        y = (h - th) // 2 - t
        draw.text(
            (x, y),
            ch,
            font=font,
            fill=(255, 255, 255, 255),
            stroke_width=stroke,
            stroke_fill=(25, 30, 35, 255),
        )


def build(data, target_width_frac: float = 0.9) -> Image.Image:
    """
    Stack: solid black (opaque) → ghost X → white ∞. Matches the original
    iOS-tile look so the mark stays visible on the toolbar, not muddied by
    mid-gray show-through.
    """
    ghost = _ghost_x_from_luma(data)
    w, h = ghost.size
    black = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    base = Image.alpha_composite(black, ghost)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    ch = "\u221E"
    fp = _font_path()
    stroke = max(1, int(min(w, h) * 0.0028))
    font = _font_size_fitting_width(
        draw, w, h, ch, fp, stroke, target_width_frac
    )
    _draw_infinity_center(draw, w, h, font, ch, stroke)
    return Image.alpha_composite(base, overlay)


def write_export(img, out_dir):
    for s in (16, 32, 48, 128):
        p = os.path.join(out_dir, f"icon{s}.png")
        img.resize((s, s), _LANCZOS).save(p, "PNG", optimize=True)
        print(p)


def main():
    out = os.path.join(_ROOT, "icons")
    os.makedirs(out, exist_ok=True)
    raw = _ua_open(_URL)
    img = build(raw)
    write_export(img, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
