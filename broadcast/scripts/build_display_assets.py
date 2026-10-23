#!/usr/bin/env python3
"""Write small WebP display copies of the logos and hero photo for the web page.

The verified originals stay untouched (their checksums are part of the evidence).
The browser shows these copies instead: the largest logo slot is 8cqw of a
1920-pixel frame (about 154 px), so 320 px covers it at 2x. Run this after a logo
or hero image changes; it needs Pillow, which the offline build and CI do not.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import re
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parents[1]
DIST = HERE / "dist"
LOGO_EDGE = 320
HERO_WIDTHS = (640, 1200)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fit(image, edge):
    image = image.copy()
    image.thumbnail((edge, edge), Image.LANCZOS)
    return image


def masked_raster_svg(path):
    """Render the one SVG logo that is a luminance-masked raster, not vector art."""
    text = path.read_text(encoding="utf-8")
    view = [float(v) for v in re.search(r'viewBox="([^"]+)"', text).group(1).split()]
    scale = float(re.search(r"matrix\(([\d.]+),", text).group(1))
    mask, art = (Image.open(io.BytesIO(base64.b64decode(m))) for m in re.findall(r"base64,([A-Za-z0-9+/=]+)", text))
    image = art.convert("RGBA")
    image.putalpha(mask.convert("L"))
    size = (round(image.width * scale), round(image.height * scale))
    image = image.resize(size, Image.LANCZOS)
    x, y, w, h = view
    return image.crop((round(x), round(y), round(x + w), round(y + h)))


def encode(image, photo):
    """Smallest WebP that keeps marks crisp: logos try lossless and lossy."""
    options = [{"quality": 62}] if photo else [{"lossless": True}, {"quality": 88}]
    out = []
    for option in options:
        buffer = io.BytesIO()
        image.save(buffer, "WEBP", method=6, **option)
        out.append(buffer.getvalue())
    return min(out, key=len)


def save(image, source, name, rows, photo=False):
    data = encode(image, photo)
    if len(data) > source.stat().st_size * 0.8:
        return  # Not worth a second file; the page keeps the original.
    target = DIST / "assets/display" / name
    target.write_bytes(data)
    rows.append({"source": source.relative_to(DIST).as_posix(), "sourceSha256": sha256(source),
                 "file": target.relative_to(DIST).as_posix(), "sha256": sha256(target),
                 "width": image.width, "height": image.height})


def main():
    rows = []
    for source in sorted((DIST / "assets/logos").iterdir()):
        if source.suffix == ".png":
            image = Image.open(source)
            image = fit(image.convert("RGBA") if image.mode in ("P", "LA", "L") else image, LOGO_EDGE)
        elif source.suffix == ".svg" and "base64," in source.read_text(encoding="utf-8"):
            image = fit(masked_raster_svg(source), LOGO_EDGE)
        else:
            continue  # Vector logos are already small; the page uses them directly.
        save(image, source, f"{source.stem}.webp", rows)
    hero = DIST / "assets/refinery-shop.jpeg"
    for width in HERO_WIDTHS:
        image = Image.open(hero)
        image = image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
        save(image, hero, f"refinery-shop-{width}.webp", rows, photo=True)
    manifest = {"generator": "broadcast/scripts/build_display_assets.py",
                "note": "Resized WebP copies for on-screen display only. Originals, sources and checksums remain in logos.json and asset-manifest.json.",
                "assets": rows}
    (HERE / "data/display-assets.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    before = sum((DIST / r["source"]).stat().st_size for r in rows if "refinery-shop" not in r["file"])
    after = sum((DIST / r["file"]).stat().st_size for r in rows if "refinery-shop" not in r["file"])
    print(f"Wrote {len(rows)} display assets; logos {before // 1024} KB -> {after // 1024} KB.")


if __name__ == "__main__":
    main()
