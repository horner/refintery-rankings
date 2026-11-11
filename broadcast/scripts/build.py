#!/usr/bin/env python3
"""Build the broadcaster data and press kit from the repository's frozen research."""
from __future__ import annotations

import json
import re
from datetime import date, timedelta
from build_dnf import build_dnf
from build_feeds import write_feeds
from build_matches import build_matches
from build_pages import playoff_result, write_pages
from build_press import write_press
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def person(row, ftc=False):
    return {
        "name": row["name"], "role": row["role"],
        "date": row.get("evidence_date"),
        "status": row.get("evidence_status", "").replace("_", " "),
        "note": row["notes"], "sourceUrls": row["source_urls"],
        "season": row.get("season", "Evidence from the published research; see date and notes"),
        "dateBasis": row.get("evidence_date_basis", "Undated source" if not row.get("evidence_date") else "Source publication date; not an appointment date"),
    }


def write_ics(calendar):
    """All-day events for newsroom calendars (RFC 5545: CRLF lines, escaped text, exclusive end date)."""
    def text(value):
        return str(value or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
    def day(iso, plus=0):
        return (date.fromisoformat(iso) + timedelta(days=plus)).strftime("%Y%m%d")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//The REFINERY//NEI Robotics calendar//EN", "CALSCALE:GREGORIAN",
             "X-WR-CALNAME:Northeast Indiana Robotics 2026–27", "X-WR-TIMEZONE:America/Indiana/Indianapolis"]
    for e in calendar["events"]:
        place = ", ".join(x for x in (e["venue"], e["city"], e["state"]) if x)
        lines += ["BEGIN:VEVENT", f"UID:{e['id']}@refintery-rankings", f"DTSTAMP:{day(calendar['retrievedDate'])}T000000Z",
                  f"DTSTART;VALUE=DATE:{day(e['startDate'])}", f"DTEND;VALUE=DATE:{day(e['endDate'], 1)}",
                  f"SUMMARY:{text(e['name'] if e['name'].startswith(('FTC', 'FRC', 'FIN', 'FIRST')) else e['program'] + ' · ' + e['name'])}", f"LOCATION:{text(place)}",
                  f"DESCRIPTION:{text((e['description'] + ' ' if e['description'] else '') + e['url'])}", f"URL:{e['url']}", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    folded = []
    for line in lines:  # Lines over 75 octets continue on the next line after a space.
        raw = line.encode("utf-8")
        while len(raw) > 75:
            cut = 75
            while (raw[cut] & 0xC0) == 0x80:
                cut -= 1
            folded.append(raw[:cut])
            raw = b" " + raw[cut:]
        folded.append(raw)
    (HERE / "dist/calendar.ics").write_bytes(b"\r\n".join(folded) + b"\r\n")


def unique_links(links):
    """Drop repeated accounts (same URL, ignoring case and trailing slash)."""
    seen, out = set(), []
    for link in links:
        key = link["url"].lower().rstrip("/").replace("://www.", "://")
        if key not in seen:
            seen.add(key)
            out.append(link)
    return out


def short_award(name):
    """'Innovation in Control Award sponsored by nVent' -> 'Innovation in Control Award'."""
    name = re.split(r" (?:sponsored by|in honor of|presented by) ", name)[0]
    name = re.sub(r"^District Championship FIRST Leadership Award Semi-Finalist.*", "FIRST Leadership Award semifinalist", name)
    return name


def build_standings(frc, editorial, logos, matches):
    """One row per Northeast Indiana FRC team: 2026 results from TBA, ratings from Statbotics."""
    results = {r["teamNumber"]: r for r in load(HERE / "data/tba/results-2026.json")["teams"]}
    # Kendallville (8431, 8432) and Fort Wayne (10411) sit outside the editorial Top 10 list.
    counties = {8431: "Noble", 8432: "Noble", 10411: "Allen", **{r["team_number"]: r["county"] for r in editorial["top_10"]}}
    photos = load(HERE / "data/photos.json")["photos"]
    news = load(HERE / "data/news.json")["stories"]
    team_links = {t["teamNumber"]: t["links"] for t in load(HERE / "data/team-links.json")["teams"]}
    closest = {r["number"]: r for r in matches["teams"] if r["program"] == "FRC"}
    history = {h["teamNumber"]: h for h in load(HERE / "data/tba/history.json")["teams"]}
    regional = sorted([r for r in frc["teams"] if r["scope_group"] == "northeast_indiana"],
                      key=lambda r: (-r["rankings"]["epa_mean"], r["team_number"]))
    rows = []
    for power_rank, r in enumerate(regional, 1):
        number, k, h, l = r["team_number"], r["rankings"], r["season_history"], r["leadership"]
        t = results[number]
        official = [e for e in t["events"] if e["type"] != "offseason"]
        titles = [e for e in official if e["playoff"] and e["playoff"]["result"] == "Won event"]
        worlds = next((e for e in official if e["type"] == "championship_division"), None)
        state = next((e for e in official if e["type"] == "district_championship"), None)
        badges = []
        if titles:
            badges.append(f"{len(titles)}× event winner" if len(titles) > 1 else "Event winner")
        if any(e["playoff"] and e["playoff"]["result"] == "Finalist" for e in official):
            badges.append("Event finalist")
        if worlds:
            badges.append("World Championship")
        elif state:
            badges.append("State qualifier")
        awards = [{"award": a, "event": e["shortName"], "eventKey": e["key"]} for e in t["events"] for a in e["awards"]
                  if a not in ("District Event Winner", "District Event Finalist")]
        # Name the awards rather than counting them; two fit on a row, the rest become "+N".
        names = [short_award(a["award"]) for a in awards]
        badges.extend(names[:2])
        if len(names) > 2:
            badges.append(f"+{len(names) - 2} more")
        match = closest.get(number)
        rows.append({
            "number": number, "name": r["team_name"], "school": r["school_or_organization"], "city": r["city"],
            "county": counties[number], "affiliationNote": r["affiliation_notes"],
            "logos": logos(number), "rookieYear": h["official_rookie_year"], "seasons": h["recorded_season_count"],
            "powerRank": power_rank, "epa": k["epa_mean"], "epaStandardDeviation": k["epa_standard_deviation"],
            "stateEpaRank": k["state_rank"], "stateEpaCount": k["state_team_count"], "worldEpaRank": k["world_rank"], "worldEpaCount": k["world_team_count"],
            "record": t["officialRecord"], "district": t["district"], "events": t["events"], "awards": awards,
            "titles": [e["shortName"] for e in titles], "worlds": worlds["shortName"] if worlds else None,
            "stateChampionship": bool(state), "badges": badges,
            "closestMatch": match.get("main") if match else None,
            "students": [person(p) for p in l["students"]], "adults": [person(p) for p in l["adults"]],
            "representatives": [person(p) for p in l["other_representatives"]], "gaps": l["gaps"],
            "news": [s for s in news if f"frc{number}" in s["teams"]],
            "photos": [p["id"] for p in photos if number in p["teams"]],
            "links": {"tba": t["tbaUrl"], "statbotics": r["statbotics_url"], "first": r["first_team_url"], "school": r["school_url"]},
            "teamLinks": unique_links(team_links.get(number, [])),
            "history": all_time(history.get(number)),
        })
    by_points = sorted(rows, key=lambda row: (row["district"]["rank"] or 999))
    for i, row in enumerate(by_points, 1):
        row["standingsRank"] = i
    summary = {
        "teams": len(rows),
        "eventTitles": sum(len(row["titles"]) for row in rows),
        "worldsTeams": [row["number"] for row in rows if row["worlds"]],
        "stateTeams": [row["number"] for row in rows if row["stateChampionship"]],
        "awards": sum(len(row["awards"]) for row in rows),
        "wins": sum(row["record"]["wins"] for row in rows),
        "updated": load(HERE / "data/tba/results-2026.json")["retrievedDate"],
        "resultsSource": "The Blue Alliance, captured " + (lambda d: f"{d:%b} {d.day}, {d.year}")(date.fromisoformat(load(HERE / "data/tba/results-2026.json")["retrievedDate"])),
        "ratingsSource": "Statbotics EPA, final 2026 values (June 12, 2026 snapshot), shown as a secondary model rating",
    }
    return rows, summary


def all_time(h):
    """All-time Blue Alliance record for a team: blue banners and awards by season (played seasons only)."""
    if not h:
        return None
    by_year = {}
    for ev in h["events"]:
        if ev["awards"] and ev["year"] <= 2026:
            by_year.setdefault(ev["year"], []).extend({"award": a, "event": ev["event"]} for a in ev["awards"])
    return {"tbaUrl": h["tbaUrl"], "banners": h["banners"], "bannerCount": len(h["banners"]), "awardCount": h["awardCount"],
            "seasonsPlayed": h["seasonsPlayed"], "awardsByYear": [{"year": y, "awards": by_year[y]} for y in sorted(by_year, reverse=True)],
            "registered": [{"year": e["year"], "eventKey": e["eventKey"], "event": e["event"]} for e in h["registered"]]}


def ftc_all_time(h):
    """FTC season-by-season record from FTCScout, trimmed to what the pages show."""
    if not h:
        return None
    role = {"Captain": "Captain", "FirstPick": "1st pick", "SecondPick": "2nd pick"}
    seasons = []
    for season in sorted(h["seasons"], key=lambda x: x["season"], reverse=True):
        played = [ev for ev in season["events"] if ev.get("finished") or ev.get("qualRank")]
        if not played:
            continue
        rows = []
        for ev in sorted(played, key=lambda ev: ev["startDate"]):
            rec = ev.get("qualRecord")
            po = ev.get("playoff")
            rows.append({"name": ev["name"], "startDate": ev["startDate"], "endDate": ev["endDate"], "type": ev["type"], "url": ev["eventUrl"],
                         "qualRank": ev.get("qualRank"), "qualRecord": f"{rec['wins']}-{rec['losses']}-{rec['ties']}" if rec else None,
                         "npOpr": ev.get("npOpr"),
                         "playoff": f"{role.get(po.get('allianceRole'), po.get('allianceRole') or 'Alliance')} · {po['wins']}-{po['losses']}" + (f"-{po['ties']}" if po.get('ties') else "") if po else None,
                         "awards": [a["displayName"] for a in ev.get("awards", [])]})
        tot = season["totals"]
        seasons.append({"season": season["season"], "label": season.get("seasonLabel"), "name": season.get("seasonName"),
                        "record": f"{tot['wins']}-{tot['losses']}-{tot['ties']}", "awards": tot["awards"], "bestNpOpr": tot.get("bestNpOpr"), "events": rows})
    a = h["allTime"]
    return {"url": h["ftcscoutUrl"], "rookieYear": h.get("rookieYear"), "seasonsPlayed": len(seasons), "events": a["totalEvents"],
            "record": f"{a['wins']}-{a['losses']}-{a['ties']}", "awards": a["totalAwards"], "eventWins": a["eventWins"],
            "inspireAwards": a["inspireAwards"], "seasons": seasons, "upcoming": h.get("upcoming", [])}


def latest_results(standings, count=3):
    """The most recent events any regional FRC team played, with each local team's finish, newest first."""
    order = {"Won event": 0, "Finalist": 1}
    events = {}
    for t in standings:
        for ev in t["events"]:
            row = events.setdefault(ev["key"], {"key": ev["key"], "name": ev["name"], "shortName": ev["shortName"], "type": ev["type"],
                                                "startDate": ev["startDate"], "endDate": ev["endDate"], "tbaUrl": ev["tbaUrl"], "teams": []})
            outcome = ev["playoff"]["result"] if ev["playoff"] else "Not picked"
            # Same placement wording as the team pages ("Won the event", "3rd place", ...).
            row["teams"].append({"number": t["number"], "name": t["name"], "school": t["school"], "qualRank": ev["qualRank"],
                                 "outcome": outcome, "result": playoff_result(ev["playoff"]), "awards": [short_award(a) for a in ev["awards"] if a not in ("District Event Winner", "District Event Finalist")]})
    recent = sorted(events.values(), key=lambda e: (e["endDate"], e["key"]), reverse=True)[:count]
    for ev in recent:
        ev["teams"].sort(key=lambda r: (order.get(r["outcome"], 2), r["qualRank"] or 999))
    return recent


def main():
    frc = load(ROOT / "data/teams.json")
    ftc = load(ROOT / "ftc/data/teams.json")
    editorial = load(HERE / "data/editorial.json")
    logo_rows = load(HERE / "data/logos.json")["logos"]
    def logos(number, program="frc"):
        return {r["kind"]: r for r in logo_rows if r["number"] == number and r["program"] == program}
    selected = {r["team_number"]: r for r in editorial["top_10"]}
    results = {r["teamNumber"]: r for r in load(HERE / "data/tba/results-2026.json")["teams"]}
    # One ranking everywhere: official FIRST Indiana district points, as reported by The Blue Alliance.
    # EPA stays on every team as a secondary model rating; it no longer decides the order.
    regional = sorted([r for r in frc["teams"] if r["scope_group"] == "northeast_indiana"],
                      key=lambda r: (results[r["team_number"]]["district"]["rank"] or 999, r["team_number"]))
    counties = {8431: "Noble", 8432: "Noble", 10411: "Allen", **{r["team_number"]: r["county"] for r in editorial["top_10"]}}
    teams = []
    for rank, r in enumerate(regional[:10], 1):
        number = r["team_number"]
        k, h, l = r["rankings"], r["season_history"], r["leadership"]
        t = results[number]
        spotlight = selected[number]["spotlight"] if number in selected else None
        rec = t["officialRecord"]
        points = [
            f"No. {rank} among Northeast Indiana teams; {r['school_or_organization']} in {r['city']}.",
            f"{t['district']['points']} FIRST Indiana district points; #{t['district']['rank']} of {t['district']['teamCount']} in Indiana. 2026 record {rec['wins']}-{rec['losses']}-{rec['ties']} (The Blue Alliance).",
            f"{h['recorded_season_count']} recorded FIRST season entries through 2026; official rookie year {h['official_rookie_year']}.",
        ]
        if spotlight:
            points.append(f"{spotlight['name']} — {spotlight['role']}. {spotlight['qualification']}")
        teams.append({
            "rank": rank, "number": number, "name": r["team_name"],
            "logos": logos(number),
            "school": r["school_or_organization"], "city": r["city"], "county": counties[number],
            "districtPoints": t["district"]["points"], "districtRank": t["district"]["rank"], "districtCount": t["district"]["teamCount"],
            "record": rec,
            "epa": k["epa_mean"], "epaStandardDeviation": k["epa_standard_deviation"],
            "stateRank": k["state_rank"], "stateCount": k["state_team_count"],
            "worldRank": k["world_rank"], "worldCount": k["world_team_count"],
            "seasons": h["recorded_season_count"], "rookieYear": h["official_rookie_year"],
            "students": [person(p) for p in l["students"]],
            "adults": [person(p) for p in l["adults"]],
            "representatives": [person(p) for p in l["other_representatives"]],
            "gaps": l["gaps"], "talkingPoints": points,
            "spotlight": spotlight,
            "sourceUrls": sorted(set([r["first_team_url"], r["statbotics_url"], *r["affiliation_source_urls"],
                                      *[u for c in (l["students"], l["adults"], l["other_representatives"]) for p in c for u in p["source_urls"]]])),
            "profileUrl": r["statbotics_url"],
            "schoolUrl": r["school_url"], "affiliationNote": r["affiliation_notes"],
        })
    ftc_links = {t["teamNumber"]: t["links"] for t in load(HERE / "data/team-links.json")["teams"]}
    # FTC features stay within the same Indiana regional frame; nearby Ohio research remains linked separately.
    features = []
    for r in ftc["teams"]:
        if r["state"] != "IN":
            continue
        l, k = r["leadership"], r["rankings"]
        features.append({
            "number": r["team_number"], "name": r["team_name"], "school": r["school_or_organization"],
            "logos": logos(r["team_number"], "ftc"),
            "city": r["city"], "opr": k["value"], "worldRank": k["world_rank"], "worldCount": k["world_team_count"],
            "regionalOpr": k["regional_value"], "regionalRank": k["regional_rank"],
            "regionalCount": k["regional_team_count"], "regionalCode": k["regional_code"],
            "students": [person(p, True) for p in l["student_leadership"]],
            "adults": [person(p, True) for p in l["adult_leadership"]],
            "gaps": [l["gap"]], "sourceUrls": r["source_urls"],
            "profileUrl": r["first_team_url"], "qualification": k["qualification"],
            "teamLinks": unique_links(ftc_links.get(r["team_number"], [])),
        })
    result = {
        "title": "The REFINERY · NEI Robotics Top 10",
        "seasonPreview": load(HERE / "data/season-preview.json"),
        # The 166-school invitation list is most of the payload; the page loads it on demand.
        "dnf": {"src": "dnf.json"},
        "matchHighlights": build_matches(),
        "videoThumbnails": {r["videoUrl"]: r for r in load(HERE / "data/video-thumbnails.json")["thumbnails"]},
        "hero": {"headline": "THE ONLY SPORT WHERE EVERYONE CAN GO PRO", "subhead": "Friday-night energy. Skills for a lifetime. Meet the students building their future in engineering, software, manufacturing and business.",
                 "attribution": "Career-focused campaign message from FIRST Global", "attributionUrl": "https://first.global/sport/",
                 "image": "assets/refinery-shop.jpeg", "logo": "assets/refinery-logo.svg"},
        "edition": {"season": 2026, "label": "2026 FRC", "researchDate": load(HERE / "data/tba/results-2026.json")["retrievedDate"], "rankingsDate": "2026-06-12",
                    "note": "The 2026 Top 10 is ordered by official FIRST Indiana district points, as reported by The Blue Alliance. Statbotics EPA appears alongside as a model rating; it does not set the order."},
        "scope": {"label": "The REFINERY region · 12 counties", "counties": editorial["counties"],
                  "cohortCount": len(regional), "note": editorial["scope_recommendation"]},
        "formatExplainer": {"headline": "Two formats. The same team spirit.",
                            "analogy": "School football and baseball use enrollment-based classes. FTC and FRC describe different robotics competition formats instead. FIRST programs are chosen by schools and community teams; they are not assigned by school enrollment.",
                            "ftc": "FTC: compact robots; grades 7–12; often smaller teams.",
                            "frc": "FRC: larger robots; grades 9–12; often larger programs.",
                            "note": "A large school can compete in FTC, a small school can compete in FRC, and a school can offer both. Each program has its own championship.",
                            "sources": ["https://www.firstinspires.org/programs/ftc/", "https://www.firstinspires.org/programs/frc/"]},
        "top10": teams,
        "ftc": {"season": "2025–26 DECODE", "note": "Separate FTC features, using peak event non-penalty OPR captured October 22, 2026. USIN is an assigned event-region cohort, not a home-state rank. FTC OPR and FRC EPA are different models and games.",
                "teams": features, "newTeams": [{"number": r["team_number"], "name": r["team_name"], "school": r["school_or_organization"], "note": r["notes"], "logos": logos(r["team_number"], "ftc"), "teamLinks": unique_links(ftc_links.get(r["team_number"], []))} for r in ftc["current_season_only_teams"]]},
        "links": {"refinery": "https://refineryrobotics.org/", "about": "https://refineryrobotics.org/about/", "involved": "https://refineryrobotics.org/get-involved/", "repo": "https://github.com/horner/refintery-rankings", "pressKit": "press/"},
        "producerNotes": ["Use the documented title and evidence date; do not announce an unconfirmed current captain or head coach.",
                          "The Top 10 follows official district points. EPA values are a model estimate; the first two differ by 0.19 points, much less than their uncertainty.",
                          "Recorded season entries can include registrations without matches. They are not a count of winning seasons.",
                          "No movement arrows or voting totals are shown because only one frozen ranking snapshot supports this edition."],
    }
    ftc_history = {t["teamNumber"]: t for t in load(HERE / "data/ftc/history.json")["teams"]}
    for t in result["ftc"]["teams"] + result["ftc"]["newTeams"]:
        t["history"] = ftc_all_time(ftc_history.get(t["number"]))
    result["standings"], result["seasonSummary"] = build_standings(frc, editorial, logos, result["matchHighlights"])
    result["latestResults"] = latest_results(result["standings"])
    result["calendar"] = load(HERE / "data/calendar-2026-27.json")
    write_ics(result["calendar"])
    result["photos"] = load(HERE / "data/photos.json")["photos"]
    result["news"] = load(HERE / "data/news.json")
    result["displayAssets"] = {r["source"]: {"file": r["file"], "width": r["width"], "height": r["height"]}
                               for r in load(HERE / "data/display-assets.json")["assets"]}
    (HERE / "dist/data.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    # The home page needs about two thirds of data.json; ship it a compact copy without the Top 10
    # display, match library and coverage plan. data.json stays the full feed for top10.html and tools.
    home_keys = ("standings", "seasonSummary", "latestResults", "ftc", "calendar", "news", "photos", "displayAssets", "videoThumbnails", "dnf", "hero", "links")
    (HERE / "dist/site.json").write_text(json.dumps({k: result[k] for k in home_keys}, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    dnf = build_dnf()
    (HERE / "dist/dnf.json").write_text(json.dumps(dnf, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    write_press(result, len(dnf["schools"]))
    write_feeds(result)
    write_pages(result, dnf)
    press = ["# The REFINERY — NEI Robotics Top 10", "", "## Segment concept", "",
             "Bring the energy of a college football rankings reveal to local student robotics: reveal the regional FRC Top 10 by official district points, select a team, and introduce the students and adults behind the robot. FTC appears in its own feature segment.", "",
             "Hero line: **The only sport where everyone can go pro.** The career-focused campaign phrase is attributed to [FIRST Global](https://first.global/sport/). Engineering, software, manufacturing, design, and business skills give the line its meaning.", "",
             "## Graphics", "", "Open the [Top 10 display](top10.html) and use Save PNG for a current 1920 × 1080 graphic of any team. Live overlays and data feeds for graphics operators are listed at [feeds/](feeds/).", "",
             "## Suggested opening", "", '“You know the football rankings. Here is another local team sport to follow: robotics. These students build the machine, write its code, scout the opposition, and work with other schools on the field. Our regional FRC Top 10 follows the official Indiana district points. Behind every number is a team and a story.”', "",
             "## Explain the divisions", "", result["formatExplainer"]["analogy"], "", result["formatExplainer"]["ftc"], "", result["formatExplainer"]["frc"], "", result["formatExplainer"]["note"], "",
             "## Ranking and source line", "", "**2026 FRC · FIRST Indiana district points via The Blue Alliance.** Local ranks are computed within the 13 teams in The REFINERY's 12-county region found in the official FIRST Indiana district roster. Hometowns establish the county reference; workshops and student residences were not surveyed. The list is not a voted poll.", "",
             "Statbotics EPA appears as a secondary model rating (June 12, 2026 snapshot). It is a modeled scoring contribution, not a record of wins, and is least reliable early in a season. FTC OPR is separate. Identify historical or undated leadership evidence accurately.", "",
             "## Coming up: the 2026–27 coverage plan", ""]
    preview = result["seasonPreview"]
    # Doug's coverage plan stays as written in season-preview.json (verify.py checks it); the rundown
    # shows only what is still ahead and puts finished offseason results first.
    as_of = result["calendar"]["retrievedDate"]
    as_of_text = (lambda d: f"{d:%B} {d.day}, {d.year}")(date.fromisoformat(as_of))
    recent = [f"- **{ev['name']}** ({ev['endDate']}): " + "; ".join(f"{r['name']} ({r['number']}) {'won' if r['outcome'] == 'Won event' else r['result'].lower()}" for r in ev["teams"][:4]) for ev in result.get("latestResults", []) if ev["type"] == "offseason"]
    press.extend(["### Recent results", "", *recent, ""] if recent else [])
    press.extend(["The FRC Top 10 ranks the region's teams by official 2026 FIRST Indiana district points. Here is the coverage road ahead: BIOBUZZ, the live build, spring competition, and Houston.", "", "Confirmed events retain organizer dates. Show dates and local build/practice windows are planning targets; times and watch links are still to come.", "", "| Date / window | Program | Teaser | Status | Details |", "|---|---|---|---|---|"])
    for item in (m for m in preview["milestones"] if m["endDate"] >= as_of):
        item = {**item, "description": item["description"].replace("This weekend: ", ""), "note": item["note"].replace("checked Oct 22, 2026", f"checked {as_of_text}")}
        press.append(f"| {item['dateLabel']} | {item['program']} | {item['title']} | {item['status']} | {item['description']} {item['note']} [Source / details]({item['linkUrl']}) |")
    press.extend(["", "### Weekly show promise", "", preview["weeklyPromise"], "", "All episode dates below are **planned coverage**, rather than confirmed broadcasts.", "", "| Proposed date | Episode | Focus |", "|---|---|---|"])
    for show in sorted((x for x in preview["shows"]["ftc"] + preview["shows"]["frc"] if x["date"] >= as_of), key=lambda r: (r["date"], r["title"])):
        press.append(f"| {show['date']} | {show['title']} | {show['summary']} |")
    stale = ("not yet published", "frozen 2026 EPA ordering", "Schedule checked")
    notes = [n for n in preview["notes"] if not any(x in n for x in stale)]
    notes += ["Local FTC entries: random() (22331) and R.Amp (36124) at Westfield 2 on Dec 6; see the calendar for every posted entry list.",
              f"Schedule checked {as_of_text}. Local Week 0 and livestream details await organizer announcements."]
    press.extend(["", *["- " + note for note in notes], "", "## Close games to watch", "",
                  "Every Top 10 team has a sourced closest-score match and verified replay; the two returning FTC teams' replays are in the match library. Select its profile to see the score and both alliances. A different closest playoff is linked as an alternative where available. FTC replays open at publisher-authored match chapters.", "",
                  result["matchHighlights"]["scoreNote"], "", "[Complete match library and selection methodology](match-highlights.md)", "", "## Team rundown", ""])
    match_lookup = {(r["program"], r["number"]): r for r in result["matchHighlights"]["teams"]}
    for t in teams:
        press.extend([f"### {t['rank']}. {t['name']} · FRC {t['number']}", "", f"{t['school']} · {t['city']}, {t['county']} County", "",
                      f"{t['districtPoints']} district points; Indiana district rank {t['districtRank']}/{t['districtCount']}. Statbotics EPA {t['epa']:.2f}.", "", *["- " + s for s in t["talkingPoints"]], ""])
        for category in ("students", "adults", "representatives"):
            for p in t[category]:
                press.append(f"- {p['name']} — {p['role']}. Evidence: {p['date'] or 'undated'}; {p['status']}. {p['note']} Sources: " + " ".join(p["sourceUrls"]))
        press.extend(["", "Evidence gaps: " + " ".join(t["gaps"]), ""])
        match = match_lookup[("FRC", t["number"])]["main"]
        if match:
            press.extend([f"- Closest finish: {match['eventName']}, {match['matchLabel']}. Red {match['redScore']}–Blue {match['blueScore']} ({match['margin']}-point margin); {t['number']} on {match['teamAlliance']}, {match['outcome'].lower()}. [Watch replay]({match['videoUrl']}) · [Official result]({match['officialUrl']}).", ""])
    press.extend(["## FTC feature ideas", "", result["ftc"]["note"], ""])
    for t in features:
        press.append(f"- FTC {t['number']} {t['name']} — {t['school']}, {t['city']}. Worldwide peak NP OPR {t['opr']:.2f}; world rank {t['worldRank']}/{t['worldCount']}. USIN value {t['regionalOpr']:.2f}; rank {t['regionalRank']}/{t['regionalCount']}. See the interactive profile for exact public roles and dates.")
    for t in result["ftc"]["newTeams"]:
        press.append(f"- New-season watch: FTC {t['number']} {t['name']}, {t['school']}. {t['note']}")
    press.extend(["", "## Draft pitch", "", "**Subject: A local Top 10 sports segment where students build the game**", "",
                  "The REFINERY's NEI Robotics Top 10 offers a visual way to introduce local robotics teams to sports viewers. The screen pairs a clearly dated FRC performance ranking with sourced student and adult roles, plus separate FTC features and an explanation for families new to robotics. It can support a studio rankings reveal, a school feature, or a conversation about careers and community support. The attached graphics and rundown provide a starting point; arrange interviews and confirm current-season roles directly with the school or team before introducing people as current leaders.", "",
                  "## Source and asset credits", "", "- Research and raw captures: https://github.com/horner/refintery-rankings", "- The REFINERY: https://refineryrobotics.org/", "- About / people / region: https://refineryrobotics.org/about/", "- Get involved: https://refineryrobotics.org/get-involved/", "- Hero campaign: https://first.global/sport/", "- Logo and practice-field photograph: The REFINERY website / BioNanomics REFINERY-site repository. The photo illustrates the shared practice facility, not an individual team profile.", "",
                  "This is a prepared media package. Coaching and captain details for Carroll (10332) and Olympus (4982) were confirmed with a team mentor on November 10, 2026; no station or school was contacted."])
    (HERE / "dist/press-kit.md").write_text("\n".join(press).rstrip() + "\n", encoding="utf-8", newline="\n")
    credits = ["# School and team logo sources", "", "Marks identify the named school or robotics team. Original proportions and colors are preserved. No endorsement or new license is asserted.", ""]
    for r in logo_rows:
        credits.extend([f"- {r['program'].upper()} {r['number']} / {r['kind']}: {r['label']}. {r['status']}. {r['note']} Source page: {r['pageUrl']}" + (f" Asset: {r['sourceUrl']}" if r.get("file") else "")])
    (HERE / "dist/logo-credits.md").write_text("\n".join(credits) + "\n", encoding="utf-8", newline="\n")
    print(f"Built broadcast data: {len(teams)} FRC teams, {len(features)} FTC features, one current-season watch.")


if __name__ == "__main__":
    main()
