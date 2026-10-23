#!/usr/bin/env python3
"""Refresh broadcast/data/tba/results-<season>.json from The Blue Alliance API v3.

Needs a free read key from https://www.thebluealliance.com/account in TBA_AUTH_KEY or tba.env (docs/tba-api.md).
Writes to --output (default: a new file) so a refresh never silently replaces the
published capture; review the diff, then copy it over.

    TBA_AUTH_KEY=... python scripts/fetch_tba.py --season 2026 --output /tmp/results-2026.json
"""
from __future__ import annotations

import argparse
import json
import urllib.request
from datetime import date
from pathlib import Path

from tba_key import tba_key

ROOT = Path(__file__).resolve().parents[1]
API = "https://www.thebluealliance.com/api/v3"
EVENT_TYPES = {1: "district", 2: "district_championship", 3: "championship_division", 4: "championship_finals",
               5: "district_championship_division", 0: "regional", 99: "offseason", 100: "preseason"}


def get(path, key):
    request = urllib.request.Request(API + path, headers={"X-TBA-Auth-Key": key, "User-Agent": "refintery-rankings"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def playoff(status):
    alliance, playoff = (status or {}).get("alliance"), (status or {}).get("playoff")
    if not playoff:
        return None
    role = {0: "Captain", 1: "1st Pick", 2: "2nd Pick", 3: "3rd Pick"}.get((alliance or {}).get("pick"), "Backup")
    if playoff.get("status") == "won":
        result = "Won event"
    elif playoff.get("level") == "f":
        result = "Finalist"
    elif playoff.get("double_elim_round"):
        result = f"Eliminated in playoff round {playoff['double_elim_round'].split()[-1]}"
    else:
        result = "Playoffs"
    number = (alliance or {}).get("number")
    return {"role": role, "alliance": number, "result": result, "sourceText": (status or {}).get("overall_status_str", "")}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--season", type=int, default=2026)
    parser.add_argument("--district", default="fin")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    key = tba_key()
    if not key:
        raise SystemExit("No TBA key yet: set TBA_AUTH_KEY or fill in tba.env (see docs/tba-api.md).")
    teams = json.loads((ROOT / "data/teams.json").read_text(encoding="utf-8"))["teams"]
    numbers = [t["team_number"] for t in teams if t["scope_group"] == "northeast_indiana"]
    district = {r["team_key"]: r for r in get(f"/district/{args.season}{args.district}/rankings", key) or []}
    out = []
    for number in numbers:
        team_key = f"frc{number}"
        events = sorted(get(f"/team/{team_key}/events/{args.season}/simple", key), key=lambda e: e["start_date"])
        statuses = get(f"/team/{team_key}/events/{args.season}/statuses", key)
        awards = get(f"/team/{team_key}/awards/{args.season}", key)
        wins = losses = ties = 0
        rows = []
        for event in events:
            status = statuses.get(event["key"]) or {}
            qual = (status.get("qual") or {}).get("ranking") or {}
            record = qual.get("record") or {}
            if event["event_type"] in (0, 1, 2, 3, 4, 5):
                for part in (record, ((status.get("playoff") or {}).get("record") or {})):
                    wins += part.get("wins", 0); losses += part.get("losses", 0); ties += part.get("ties", 0)
            rows.append({"key": event["key"], "name": event["name"], "shortName": event.get("short_name") or event["name"],
                         "type": EVENT_TYPES.get(event["event_type"], "other"), "startDate": event["start_date"], "endDate": event["end_date"],
                         "week": event["week"] + 1 if event.get("week") is not None else None,
                         "qualRank": qual.get("rank"), "qualRecord": f"{record.get('wins', 0)}-{record.get('losses', 0)}-{record.get('ties', 0)}" if record else None,
                         "awards": [a["name"] for a in awards if a["event_key"] == event["key"]], "playoff": playoff(status),
                         "tbaUrl": f"https://www.thebluealliance.com/event/{event['key']}"})
        ranking = district.get(team_key, {})
        profile = get(f"/team/{team_key}", key)
        social = [{"type": m["type"], "handle": m["foreign_key"]} for m in get(f"/team/{team_key}/social_media", key)]
        out.append({"teamNumber": number, "tbaUrl": f"https://www.thebluealliance.com/team/{number}/{args.season}",
                    "website": profile.get("website"), "social": social,
                    "officialRecord": {"wins": wins, "losses": losses, "ties": ties},
                    "district": {"key": f"{args.season}{args.district}", "rank": ranking.get("rank"), "points": ranking.get("point_total"), "teamCount": len(district)},
                    "events": rows})
    doc = {"schemaVersion": 1, "season": args.season, "source": "The Blue Alliance API v3", "retrievedDate": date.today().isoformat(),
           "method": "TBA API v3 team profile and social media, events, event statuses, awards and district rankings.", "teams": out}
    Path(args.output).write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(out)} teams to {args.output}. Review the diff before replacing broadcast/data/tba/results-{args.season}.json.")


if __name__ == "__main__":
    main()
