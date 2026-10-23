#!/usr/bin/env python3
"""Add a photo to the site: resize it to WebP, record its source and credit, and tag teams.

    python broadcast/scripts/add_photo.py path/to/photo.jpg --id robot-1501 \
        --caption "THRUST (1501) climbs the tower at Mishawaka." --credit "The REFINERY" \
        --source "https://..." --teams 1501

Then run broadcast/scripts/build.py and broadcast/scripts/build_share_images.py. Needs Pillow.
Only add photos you have permission to use; see docs/photo-plan.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

from PIL import Image, ImageOps

HERE = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image")
    parser.add_argument("--id", required=True, help="short name, e.g. robot-1501 or match-2027inftw")
    parser.add_argument("--caption", required=True, help="one sentence saying what is in the photo")
    parser.add_argument("--credit", required=True, help="photographer or organization, as it should appear")
    parser.add_argument("--source", required=True, help="where the original lives (URL or 'Sent by <team>, <date>')")
    parser.add_argument("--teams", type=int, nargs="*", default=[], help="team numbers shown in the photo")
    parser.add_argument("--width", type=int, default=1400)
    args = parser.parse_args()
    original = Path(args.image)
    image = ImageOps.exif_transpose(Image.open(original)).convert("RGB")
    if image.width > args.width:
        image = image.resize((args.width, round(image.height * args.width / image.width)), Image.LANCZOS)
    target = HERE / f"dist/assets/photos/{args.id}.webp"
    image.save(target, "WEBP", quality=74, method=6)
    manifest_path = HERE / "data/photos.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    row = {"id": args.id, "file": f"assets/photos/{args.id}.webp", "width": image.width, "height": image.height,
           "caption": args.caption, "teams": args.teams, "credit": args.credit, "sourceUrl": args.source, "pageUrl": args.source,
           "sourceSha256": hashlib.sha256(original.read_bytes()).hexdigest(), "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
           "retrievedDate": date.today().isoformat()}
    manifest["photos"] = [p for p in manifest["photos"] if p["id"] != args.id] + [row]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Added {target.name} ({image.width}×{image.height}, {target.stat().st_size // 1024} KB) for teams {args.teams or 'none'}.")


if __name__ == "__main__":
    main()
