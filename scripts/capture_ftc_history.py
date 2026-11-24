#!/usr/bin/env python3
"""Capture FTC team history from the public FTCScout GraphQL API.

Writes broadcast/data/ftc/history.json with per-season events, qualification
records, playoff results, awards, and upcoming 2026 events for the tracked
FTC teams. Stdlib only (Python 3.12).

Usage: python scripts/capture_ftc_history.py [--today YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import socket
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.ftcscout.org/graphql"
USER_AGENT = "scoreboard-broadcast-history/1.0 (+stdlib urllib)"
TEAMS = [22331, 25638, 36124]
CURRENT_SEASON = 2026
OUT = Path(__file__).resolve().parent.parent / "broadcast" / "data" / "ftc" / "history.json"

# FTC game names keyed by FTCScout season (season start year). Unknown -> None.
SEASON_NAMES = {
    2019: "SKYSTONE",
    2020: "ULTIMATE GOAL",
    2021: "FREIGHT FRENZY",
    2022: "POWERPLAY",
    2023: "CENTERSTAGE",
    2024: "INTO THE DEEP",
    2025: "DECODE",
}

# Human-readable award names for FTCScout AwardType enum values.
AWARD_NAMES = {
    "Inspire": "Inspire Award",
    "Think": "Think Award",
    "Connect": "Connect Award",
    "Innovate": "Innovate Award",
    "Design": "Design Award",
    "Motivate": "Motivate Award",
    "Control": "Control Award",
    "Promote": "Promote Award",
    "Compass": "Compass Award",
    "Reach": "Reach Award",
    "Sustain": "Sustain Award",
    "JudgesChoice": "Judges' Choice Award",
    "Winner": "Winning Alliance",
    "Finalist": "Finalist Alliance",
    "DivisionWinner": "Division Winning Alliance",
    "DivisionFinalist": "Division Finalist Alliance",
    "ConferenceFinalist": "Conference Finalist",
    "TopRanked": "Top Ranked Team",
    "DeansListWinner": "Dean's List Winner",
    "DeansListFinalist": "Dean's List Finalist",
    "DeansListSemiFinalist": "Dean's List Semi-Finalist",
}
ALLIANCE_AWARDS = {"Winner", "Finalist", "DivisionWinner", "DivisionFinalist"}
ALLIANCE_PLACEMENT = {1: "Captain", 2: "First Pick", 3: "Second Pick"}

STAT_SEASONS = [2019, 2022, 2023, 2024, 2025, 2026]
SCORE_SEASONS = [2019, 2022, 2023, 2024, 2025, 2026]


def stats_fragments() -> str:
    parts = []
    for s in STAT_SEASONS:
        parts.append(
            f"... on TeamEventStats{s} {{ rank rp wins losses ties dqs qualMatchesPlayed "
            f"opr {{ totalPoints totalPointsNp }} }}"
        )
    return " ".join(parts)


def score_fragments() -> str:
    return " ".join(
        f"... on MatchScores{s} {{ red {{ totalPoints }} blue {{ totalPoints }} }}" for s in SCORE_SEASONS
    )


TEAM_QUERY = """
query($n: Int!) {
  teamByNumber(number: $n) {
    number name schoolName rookieYear activeSeasons website
    location { city state country }
  }
}
"""

SEASON_QUERY = (
    """
query($n: Int!, $s: Int!) {
  teamByNumber(number: $n) {
    events(season: $s) {
      season eventCode
      event { code divisionCode name type start end started finished remote
              location { venue city state country } }
      stats { %s }
      awards { type placement divisionName personName }
    }
    matches(season: $s) {
      eventCode alliance allianceRole surrogate noShow dq
      match { id hasBeenPlayed tournamentLevel series matchNum description
              scores { %s } }
    }
    quickStats(season: $s) { tot { value rank } count }
  }
}
"""
    % (stats_fragments(), score_fragments())
)


def gql(query: str, variables: dict) -> dict:
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    last_err: Exception | None = None
    for attempt in range(1, 4):
        req = urllib.request.Request(
            API,
            data=body,
            headers={"Content-Type": "application/json", "User-Agent": USER_AGENT, "Accept": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            if payload.get("errors"):
                raise RuntimeError(f"GraphQL errors: {payload['errors']}")
            return payload["data"]
        except (TimeoutError, socket.timeout, urllib.error.URLError) as exc:
            last_err = exc
            time.sleep(2 * attempt)
    raise RuntimeError(f"FTCScout request failed after 3 attempts: {last_err}")


def award_entry(a: dict) -> dict:
    t = a["type"]
    name = AWARD_NAMES.get(t, t)
    placement = a.get("placement")
    if t in ALLIANCE_AWARDS:
        role = ALLIANCE_PLACEMENT.get(placement)
        display = f"{name} ({role})" if role else name
    else:
        display = f"{name} – {ordinal(placement)} Place" if placement else name
    return {
        "type": t,
        "name": name,
        "placement": placement,
        "displayName": display,
        "divisionName": a.get("divisionName"),
        "personName": a.get("personName"),
    }


def ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suf = "th"
    else:
        suf = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


def playoff_summary(matches: list[dict], team: int) -> dict | None:
    """Summarise playoff (non-Quals) matches for one event from the team's view."""
    po = [m for m in matches if m["match"]["tournamentLevel"] != "Quals"]
    if not po:
        return None
    w = l = t = 0
    role = None
    alliance = None
    for m in po:
        role = role or m.get("allianceRole")
        alliance = alliance or m.get("alliance")
        sc = m["match"].get("scores")
        if not m["match"].get("hasBeenPlayed") or not sc or "red" not in sc:
            continue
        mine = sc[m["alliance"].lower()]["totalPoints"]
        opp = sc["blue" if m["alliance"] == "Red" else "red"]["totalPoints"]
        if mine > opp:
            w += 1
        elif mine < opp:
            l += 1
        else:
            t += 1
    levels = sorted({m["match"]["tournamentLevel"] for m in po})
    return {
        "allianceRole": role,
        "allianceColorLastMatch": alliance,
        "levels": levels,
        "matchesPlayed": w + l + t,
        "wins": w,
        "losses": l,
        "ties": t,
    }


def build_team(n: int, today: dt.date) -> dict:
    info = gql(TEAM_QUERY, {"n": n})["teamByNumber"]
    if not info:
        raise RuntimeError(f"Team {n} not found on FTCScout")
    seasons_out = []
    upcoming = []
    all_awards = []
    total_events = 0
    for season in sorted(set(info["activeSeasons"]) | {CURRENT_SEASON}):
        data = gql(SEASON_QUERY, {"n": n, "s": season})["teamByNumber"]
        teps = data["events"]
        if not teps:
            continue
        matches_by_event: dict[str, list] = {}
        for m in data["matches"]:
            matches_by_event.setdefault(m["eventCode"], []).append(m)
        events = []
        sw = sl = st = 0
        best_opr = best_np = None
        for tep in sorted(teps, key=lambda x: (x["event"]["start"], x["eventCode"])):
            ev = tep["event"]
            stats = tep.get("stats") or {}
            opr = (stats.get("opr") or {}) if stats else {}
            awards = [award_entry(a) for a in tep.get("awards") or []]
            record = None
            if stats and stats.get("wins") is not None:
                record = {"wins": stats["wins"], "losses": stats["losses"], "ties": stats["ties"]}
                sw += stats["wins"]
                sl += stats["losses"]
                st += stats["ties"]
            o, onp = opr.get("totalPoints"), opr.get("totalPointsNp")
            if o is not None and (best_opr is None or o > best_opr):
                best_opr = o
            if onp is not None and (best_np is None or onp > best_np):
                best_np = onp
            start = dt.date.fromisoformat(ev["start"])
            loc = ev.get("location") or {}
            entry = {
                "eventCode": ev["code"],
                "name": ev["name"],
                "startDate": ev["start"],
                "endDate": ev["end"],
                "type": ev["type"],
                "divisionOf": ev.get("divisionCode"),
                "remote": ev.get("remote"),
                "venue": loc.get("venue"),
                "city": loc.get("city"),
                "state": loc.get("state"),
                "country": loc.get("country"),
                "started": ev.get("started"),
                "finished": ev.get("finished"),
                "qualRank": stats.get("rank") if stats else None,
                "qualMatchesPlayed": stats.get("qualMatchesPlayed") if stats else None,
                "qualRecord": record,
                "opr": round(o, 2) if o is not None else None,
                "npOpr": round(onp, 2) if onp is not None else None,
                "playoff": playoff_summary(matches_by_event.get(ev["code"], []), n),
                "awards": awards,
                "eventUrl": f"https://ftcscout.org/events/{season}/{ev['code']}",
            }
            events.append(entry)
            for a in awards:
                all_awards.append(
                    {
                        "season": season,
                        "eventCode": ev["code"],
                        "eventName": ev["name"],
                        "divisionOf": ev.get("divisionCode"),
                        **a,
                    }
                )
            if season == CURRENT_SEASON and start > today:
                upcoming.append(
                    {k: entry[k] for k in ("eventCode", "name", "startDate", "endDate", "type", "city", "state", "eventUrl")}
                )
        # Division events and their parent finals event count as one competition. Only events that
        # have been played count; registrations for future events are listed under "upcoming".
        played = [e for e in events if e.get("finished") or e.get("qualRank")]
        competitions = len({e["divisionOf"] or e["eventCode"] for e in played})
        total_events += competitions
        qs = data.get("quickStats") or {}
        tot = qs.get("tot") or {}
        seasons_out.append(
            {
                "season": season,
                "seasonLabel": f"{season}-{str(season + 1)[-2:]}",
                "seasonName": SEASON_NAMES.get(season),
                "events": events,
                "totals": {
                    "events": competitions,
                    "eventEntries": len(played),
                    "wins": sw,
                    "losses": sl,
                    "ties": st,
                    "playoffWins": sum((e["playoff"] or {}).get("wins", 0) for e in events),
                    "playoffLosses": sum((e["playoff"] or {}).get("losses", 0) for e in events),
                    "playoffTies": sum((e["playoff"] or {}).get("ties", 0) for e in events),
                    "awards": sum(len(e["awards"]) for e in events),
                    "bestOpr": round(best_opr, 2) if best_opr is not None else None,
                    "bestNpOpr": round(best_np, 2) if best_np is not None else None,
                    "quickStatsNpOpr": round(tot["value"], 2) if tot.get("value") is not None else None,
                    "quickStatsNpOprRank": tot.get("rank"),
                    "quickStatsTeamCount": qs.get("count"),
                },
            }
        )
    loc = info.get("location") or {}
    return {
        "teamNumber": info["number"],
        "name": info["name"],
        "schoolName": info["schoolName"],
        "city": loc.get("city"),
        "state": loc.get("state"),
        "country": loc.get("country"),
        "rookieYear": info["rookieYear"],
        "website": info.get("website"),
        "activeSeasons": info["activeSeasons"],
        "ftcscoutUrl": f"https://ftcscout.org/teams/{n}",
        "seasons": seasons_out,
        "allTime": {
            "seasonsWithEvents": sum(1 for s in seasons_out if s["totals"]["events"]),
            "totalEvents": total_events,
            "totalEventEntries": sum(s["totals"]["eventEntries"] for s in seasons_out),
            "wins": sum(s["totals"]["wins"] for s in seasons_out),
            "losses": sum(s["totals"]["losses"] for s in seasons_out),
            "ties": sum(s["totals"]["ties"] for s in seasons_out),
            "totalAwards": len(all_awards),
            "eventWins": sum(1 for a in all_awards if a["type"] == "Winner" and not a["divisionOf"]),
            "divisionWins": len(
                {
                    (a["season"], a["divisionOf"] or a["eventCode"])
                    for a in all_awards
                    if a["type"] == "DivisionWinner" or (a["type"] == "Winner" and a["divisionOf"])
                }
            ),
            "inspireAwards": sum(1 for a in all_awards if a["type"] == "Inspire" and a["placement"] == 1),
            "awards": all_awards,
        },
        "upcoming": upcoming,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--today", default=dt.date.today().isoformat())
    args = ap.parse_args()
    today = dt.date.fromisoformat(args.today)
    doc = {
        "schemaVersion": 1,
        "source": "FTCScout public GraphQL API",
        "sourceUrl": API,
        "retrievedDate": today.isoformat(),
        "method": (
            "Queried FTCScout teamByNumber for each team and, per active season, its event participations "
            "(event info, qualification stats, awards) and matches (to derive playoff records); "
            "eventWins counts 'Winning Alliance' awards (captain/first/second pick) at top-level events, "
            "divisionWins counts division-level winning alliances, and inspireAwards counts 1st-place Inspire."
        ),
        "teams": [build_team(n, today) for n in TEAMS],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    for t in doc["teams"]:
        a = t["allTime"]
        print(
            f"{t['teamNumber']} {t['name']}: seasons={a['seasonsWithEvents']} events={a['totalEvents']} "
            f"W-L-T={a['wins']}-{a['losses']}-{a['ties']} awards={a['totalAwards']} "
            f"eventWins={a['eventWins']} inspire={a['inspireAwards']} upcoming={len(t['upcoming'])}"
        )
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
