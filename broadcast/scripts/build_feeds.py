#!/usr/bin/env python3
"""Write data feeds for graphics operators: flat JSON, CSV and ticker text.

vMix Data Sources, Ross XPression DataLinq, NewBlue Captivate, Singular and OBS/CasparCG browser
sources all read a JSON array of flat objects (one object per row) or a CSV with the same columns.
Every row here uses short, paste-ready fields; nothing is nested. Called by build.py; stdlib only.
"""
from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
FEEDS = HERE / "dist/feeds"
SITE = "https://horner.github.io/refintery-rankings/"


def school_short(school):
    name = school.split(" / ")[0]
    name = re.sub(r"\s*\(community team\)$", "", name)
    for long, short in ((" Junior/Senior High School", " HS"), (" Jr./Sr. High School", " HS"), (" High School", " HS"), ("R. Nelson Snider", "Snider")):
        name = name.replace(long, short)
    return name


def record(r):
    return f"{r['wins']}-{r['losses']}" + (f"-{r['ties']}" if r["ties"] else "")


def honors_line(t):
    parts = []
    if t["titles"]:
        parts.append(f"Won {', '.join(t['titles'])}")
    if t["worlds"]:
        parts.append("World Championship")
    elif t["stateChampionship"]:
        parts.append("State qualifier")
    if t["awards"]:
        parts.append(f"{len(t['awards'])} judged award{'s' if len(t['awards']) != 1 else ''}")
    return " · ".join(parts)


def logo_url(t, kind):
    file = t["logos"].get(kind, {}).get("file")
    return SITE + file if file else ""


def standings_rows(result):
    updated = result["seasonSummary"]["updated"]
    rows = []
    for t in sorted(result["standings"], key=lambda t: t["standingsRank"]):
        rows.append({
            "rank": t["standingsRank"],
            "team_number": t["number"],
            "team_name": t["name"],
            "short_name": t["name"] if len(t["name"]) <= 20 else t["name"].removesuffix(" Robotics")[:20],
            "school": t["school"],
            "school_short": school_short(t["school"]),
            "city": t["city"],
            "county": t["county"],
            "wins": t["record"]["wins"],
            "losses": t["record"]["losses"],
            "ties": t["record"]["ties"],
            "record": record(t["record"]),
            "district_points": t["district"]["points"],
            "indiana_rank": t["district"]["rank"],
            "indiana_teams": t["district"]["teamCount"],
            "event_titles": len(t["titles"]),
            "honors": honors_line(t),
            "epa": round(t["epa"], 1),
            "team_logo": logo_url(t, "team"),
            "school_logo": logo_url(t, "school"),
            "team_page": f"{SITE}team/{t['number']}/",
            "updated": updated,
            "source": "FIRST Indiana district points and records via The Blue Alliance; EPA via Statbotics",
        })
    return rows


def schedule_rows(result):
    # Finished FRC events have no entry list any more; list who actually played from the results.
    played = {}
    for t in result["standings"]:
        for ev in t["events"]:
            played.setdefault(ev["key"], []).append(t["number"])
    rows = []
    for e in result["calendar"]["events"]:
        entrants = e.get("entrants") or {}
        key = e["id"].split("-", 1)[1] if e["id"].startswith("frc-") else None
        if not entrants.get("posted") and key in played:
            entrants = {"posted": True, "local": sorted(played[key])}
        rows.append({
            "start_date": e["startDate"], "end_date": e["endDate"], "program": e["program"], "type": e.get("type", ""),
            "event": e["name"], "venue": e.get("venue", ""), "city": e.get("city", ""), "state": e.get("state", ""),
            "local_teams": ", ".join(str(n) for n in entrants.get("local", [])) if entrants.get("posted") else "",
            "url": e["url"],
        })
    return rows


def ticker_lines(rows):
    lines = []
    for r in rows:
        line = f"#{r['rank']} {r['team_name']} ({r['team_number']}, {r['school_short']}) · {r['record']} · {r['district_points']} pts"
        if r["honors"]:
            line += f" · {r['honors']}"
        lines.append(line)
    return lines


def write_csv(path, rows):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    path.write_text(buffer.getvalue(), encoding="utf-8", newline="\n")


def write_feeds(result):
    FEEDS.mkdir(parents=True, exist_ok=True)
    standings = standings_rows(result)
    schedule = schedule_rows(result)
    dump = lambda rows: json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    (FEEDS / "standings.json").write_text(dump(standings), encoding="utf-8", newline="\n")
    write_csv(FEEDS / "standings.csv", standings)
    (FEEDS / "top10.json").write_text(dump(standings[:10]), encoding="utf-8", newline="\n")
    write_csv(FEEDS / "top10.csv", standings[:10])
    (FEEDS / "schedule.json").write_text(dump(schedule), encoding="utf-8", newline="\n")
    write_csv(FEEDS / "schedule.csv", schedule)
    (FEEDS / "ticker.txt").write_text("\n".join(ticker_lines(standings)) + "\n", encoding="utf-8", newline="\n")
    return standings
