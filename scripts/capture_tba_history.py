#!/usr/bin/env python3
"""Capture every regional FRC team's all-time history from The Blue Alliance's public history pages.

No API key needed. For each team, saves https://www.thebluealliance.com/team/{n}/history and extracts:
- the competition list (year, event, awards at that event), including registered future events;
- the blue banners TBA shows (event wins and banner awards).

    python scripts/capture_tba_history.py [--pages DIR] 1501 1720 ...

Without --pages it downloads the pages. Writes broadcast/data/tba/history.json.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "broadcast/data/tba/history.json"


def text(fragment):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment))).strip()


def last_played_season():
    """The newest season with a results capture. Rows after it are registrations, not results.
    (Using today's year would turn 2027 registrations into "played" seasons on Jan 1.)"""
    seasons = [json.loads(f.read_text(encoding="utf-8"))["season"] for f in (ROOT / "broadcast/data/tba").glob("results-*.json")]
    return max(seasons) if seasons else date.today().year


def parse(raw):
    s = raw.decode("utf-8")
    table = re.search(r'<table[^>]*id="competition-list-table".*?<tbody>(.*?)</tbody>', s, flags=re.S)
    events = []
    for row in re.findall(r"<tr>(.*?)</tr>", table.group(1) if table else "", flags=re.S):
        cells = re.findall(r"<td>(.*?)</td>", row, flags=re.S)
        if len(cells) < 3:
            continue
        key = re.search(r"/event/([0-9a-z]+)", cells[1])
        awards = [text(a) for a in re.split(r"<br\s*/?>", cells[2]) if text(a)]
        events.append({"year": int(text(cells[0])), "eventKey": key.group(1) if key else None, "event": text(cells[1]), "awards": awards})
    banners = []
    for block in re.findall(r'<div class="banner">(.*?)</div>\s*</div>', s, flags=re.S):
        name = re.search(r'class="award-name(?:-long)?">\s*<span>(.*?)</span>', block, flags=re.S)
        event = re.search(r'class="award-event">\s*<span>(.*?)</span>', block, flags=re.S)
        if name and event:
            banners.append({"award": text(name.group(1)), "event": text(event.group(1))})
    rookie = re.search(r"Rookie Year: (\d{4})", s)
    return {"rookieYear": int(rookie.group(1)) if rookie else None, "events": events, "banners": banners}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", help="directory of saved {n}.html history pages")
    parser.add_argument("teams", nargs="+", type=int)
    args = parser.parse_args()
    season = last_played_season()
    teams = []
    for n in args.teams:
        url = f"https://www.thebluealliance.com/team/{n}/history"
        if args.pages:
            raw = (Path(args.pages) / f"{n}.html").read_bytes()
        else:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (refintery-rankings history capture)"})
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
        record = parse(raw)
        played = [e for e in record["events"] if e["year"] <= season]
        record.update({
            "teamNumber": n, "tbaUrl": url, "responseSha256": hashlib.sha256(raw).hexdigest(), "responseBytes": len(raw),
            "eventWins": sum(1 for e in played if any(a in ("District Event Winner", "Regional Winners", "District Championship Winner", "Championship Winner", "Championship Subdivision Winner", "Winner") or a.endswith(" Winner") and "Award" not in a for a in e["awards"])),
            "awardCount": sum(len(e["awards"]) for e in played),
            "seasonsPlayed": len({e["year"] for e in played}),
            "registered": [e for e in record["events"] if e["year"] > season],
        })
        teams.append(record)
        print(n, f"{len(record['banners'])} banners, {record['eventWins']} event wins, {record['awardCount']} awards, {record['seasonsPlayed']} seasons", [e["eventKey"] for e in record["registered"]])
    doc = {"schemaVersion": 1, "source": "The Blue Alliance public team history pages", "retrievedDate": date.today().isoformat(),
           "method": "Each team's https://www.thebluealliance.com/team/{n}/history page was saved; its competition list (year, event, awards) and blue-banner list were extracted as shown. Event wins count District Event Winner, Regional Winners and championship winner awards. Future-year rows are event registrations, not results.",
           "teams": teams}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
