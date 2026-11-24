#!/usr/bin/env python3
"""Cache YouTube replay thumbnails for every regional FRC team's closest match.

Run after build.py when a team gains a replay without a cached preview. Each new entry keeps the
oEmbed metadata it came from, the image checksum, and the retrieval time, matching the original ten.
Needs network access; the regular build stays offline.
"""
from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
MANIFEST = HERE / "data/video-thumbnails.json"
USER_AGENT = "refintery-rankings thumbnail cache"


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def main():
    data = json.loads((HERE / "dist/data.json").read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cached = {r["videoUrl"] for r in manifest["thumbnails"]}
    regional = {t["number"] for t in data["standings"]}
    added = 0
    for row in data["matchHighlights"]["teams"]:
        match = row.get("main")
        if row["program"] != "FRC" or row["number"] not in regional or not match or match["videoUrl"] in cached:
            continue
        video_url = match["videoUrl"]
        video_id = video_url.split("v=", 1)[1].split("&", 1)[0]
        metadata_file = f"data/match-research/video-sources/{video_id}-oembed.json"
        raw_meta = fetch(f"https://www.youtube.com/oembed?url={video_url}&format=json")
        (HERE / metadata_file).write_bytes(raw_meta)
        meta = json.loads(raw_meta)
        image = fetch(meta["thumbnail_url"])
        if not image.startswith(b"\xff\xd8"):
            raise ValueError(f"Thumbnail for {video_id} is not a JPEG")
        file = f"assets/match-thumbnails/{video_id}.jpg"
        (HERE / "dist" / file).write_bytes(image)
        now = datetime.now(timezone.utc).isoformat()
        manifest["thumbnails"].append({
            "videoUrl": video_url, "videoId": video_id, "file": file,
            "sourceUrl": meta["thumbnail_url"], "sourceMetadataFile": metadata_file,
            "sha256": hashlib.sha256(image).hexdigest(),
            "width": meta["thumbnail_width"], "height": meta["thumbnail_height"],
            "contentType": "image/jpeg", "retrievedAt": now,
        })
        manifest["asOf"] = now
        cached.add(video_url)
        added += 1
        print(f"Cached {video_id} for FRC {row['number']}")
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Added {added} thumbnail(s).")


if __name__ == "__main__":
    main()
