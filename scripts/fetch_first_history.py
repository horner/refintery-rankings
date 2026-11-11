#!/usr/bin/env python3
"""Capture factual FIRST season-history evidence without republishing full pages.

Python 3.10+, standard library only. Network access is required.
Existing evidence files are never overwritten.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def capture(team: int, through_year: int) -> dict:
    url = f"https://frc-events.firstinspires.org/team/{team}"
    request = urllib.request.Request(url, headers={"User-Agent": "Fort-Wayne-FRC-research/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read()
        headers = {k.lower(): v for k, v in response.headers.items()}
        resolved_url = response.url
    document = raw.decode("utf-8")
    rookie = re.search(r'Rookie Year</label>\s*<div[^>]*>\s*(\d{4})', document)
    headline = re.search(r'Seasons Competed</label>\s*<div[^>]*>\s*(\d+)', document)
    years = sorted({int(y) for y in re.findall(r'id="heading(\d{4})"', document)})
    link_years = sorted({int(y) for y in re.findall(r'href="/(\d{4})/team/' + str(team) + r'"', document)})
    if not rookie or not years or years != link_years:
        raise ValueError(f"Unexpected FIRST history structure for team {team}: {years=} {link_years=}")
    eligible = [y for y in years if y <= through_year]
    no_competition = []
    for year in eligible:
        start = document.index(f'id="heading{year}"')
        next_heading = re.search(r'id="heading\d{4}"', document[start + 1:])
        end = start + 1 + next_heading.start() if next_heading else len(document)
        text = html.unescape(re.sub(r'<[^>]+>', ' ', document[start:end]))
        text = re.sub(r'\s+', ' ', text)
        if re.search(r'registered.{0,150}did not compete', text, re.IGNORECASE):
            no_competition.append(year)
    return {
        "team_number": team,
        "source_url": url,
        "resolved_url": resolved_url,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "response_sha256": hashlib.sha256(raw).hexdigest(),
        "response_bytes": len(raw),
        "response_last_modified": headers.get("last-modified"),
        "official_rookie_year": int(rookie.group(1)),
        "source_headline_seasons_competed": int(headline.group(1)) if headline else None,
        "all_listed_seasons": years,
        "recorded_seasons_through_cutoff": eligible,
        "recorded_season_count": len(eligible),
        "first_recorded_season": min(eligible) if eligible else None,
        "excluded_future_seasons": [y for y in years if y > through_year],
        "seasons_explicitly_registered_without_competition": no_competition,
        "count_definition": "Season entries in FIRST history through the cutoff, including registered seasons without competition; not a count of seasons with matches.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--through", type=int, default=2026)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--roster", type=Path, default=ROOT / "data/roster.json")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; choose a new evidence filename.")
    teams = [row["team_number"] for row in json.loads(args.roster.read_text(encoding="utf-8"))["teams"]]
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(lambda team: capture(team, args.through), teams))
    result = {
        "schema_version": "1.0",
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "through_year": args.through,
        "source": "FIRST Robotics Competition Events team history",
        "extraction_method": "Cross-check season accordion heading years against season-specific team links; parse rookie year separately; exclude future years.",
        "teams": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)
        file.write("\n")
    print(f"Captured {len(records)} team histories through {args.through}: {args.output}")
    for row in records:
        print(f"{row['team_number']}: rookie {row['official_rookie_year']}; {row['recorded_season_count']} recorded seasons; future excluded {row['excluded_future_seasons']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
