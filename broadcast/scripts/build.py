#!/usr/bin/env python3
"""Build the broadcaster data and press kit from the repository's frozen research."""
from __future__ import annotations

import json
from build_dnf import build_dnf
from build_matches import build_matches
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


def main():
    frc = load(ROOT / "data/teams.json")
    ftc = load(ROOT / "ftc/data/teams.json")
    editorial = load(HERE / "data/editorial.json")
    logo_rows = load(HERE / "data/logos.json")["logos"]
    def logos(number, program="frc"):
        return {r["kind"]: r for r in logo_rows if r["number"] == number and r["program"] == program}
    selected = {r["team_number"]: r for r in editorial["top_10"]}
    regional = sorted([r for r in frc["teams"] if r["scope_group"] == "northeast_indiana"],
                      key=lambda r: (-r["rankings"]["epa_mean"], r["team_number"]))
    if [r["team_number"] for r in regional[:10]] != [r["team_number"] for r in editorial["top_10"]]:
        raise ValueError("Editorial Top 10 no longer matches frozen EPA ordering")
    teams = []
    for rank, r in enumerate(regional[:10], 1):
        number = r["team_number"]
        e, k, h, l = selected[number], r["rankings"], r["season_history"], r["leadership"]
        spotlight = e["spotlight"]
        points = [
            f"No. {rank} in this regional list; {r['school_or_organization']} in {r['city']}.",
            f"2026 Statbotics EPA {k['epa_mean']:.2f}; Indiana rank {k['state_rank']} of {k['state_team_count']}. Snapshot June 12, 2026.",
            f"{h['recorded_season_count']} recorded FIRST season entries through 2026; official rookie year {h['official_rookie_year']}.",
            f"{spotlight['name']} — {spotlight['role']}. {spotlight['qualification']}",
        ]
        teams.append({
            "rank": rank, "number": number, "name": r["team_name"],
            "logos": logos(number),
            "school": r["school_or_organization"], "city": r["city"], "county": e["county"],
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
        })
    result = {
        "title": "The REFINERY · NEI Robotics Top 10",
        "seasonPreview": load(HERE / "data/season-preview.json"),
        "dnf": build_dnf(),
        "matchHighlights": build_matches(),
        "videoThumbnails": {r["videoUrl"]: r for r in load(HERE / "data/video-thumbnails.json")["thumbnails"]},
        "hero": {"headline": "THE ONLY SPORT WHERE EVERYONE CAN GO PRO", "subhead": "Friday-night energy. Skills for a lifetime. Meet the students building their future in engineering, software, manufacturing and business.",
                 "attribution": "Career-focused campaign message from FIRST Global", "attributionUrl": "https://first.global/sport/",
                 "image": "assets/refinery-shop.jpeg", "logo": "assets/refinery-logo.svg"},
        "edition": {"season": 2026, "label": "2026 FRC", "researchDate": "2026-10-22", "rankingsDate": "2026-06-12",
                    "note": "2027 preseason baseline: a rewind of 2026 FRC performance, independently ordered by Statbotics EPA. Frozen June 12, 2026 values; research preserved October 22. This is not a voted poll or a live scoreboard."},
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
                "teams": features, "newTeams": [{"number": r["team_number"], "name": r["team_name"], "school": r["school_or_organization"], "note": r["notes"], "logos": logos(r["team_number"], "ftc")} for r in ftc["current_season_only_teams"]]},
        "links": {"refinery": "https://refineryrobotics.org/", "about": "https://refineryrobotics.org/about/", "involved": "https://refineryrobotics.org/get-involved/", "repo": "https://github.com/horner/refintery-rankings", "pressKit": "press-kit.md"},
        "producerNotes": ["Use the documented title and evidence date; do not announce an unconfirmed current captain or head coach.",
                          "The first two EPA values differ by 0.19 points, much less than their model uncertainty. A numbered ordering is not evidence of a meaningful performance gap.",
                          "Recorded season entries can include registrations without matches. They are not a count of winning seasons.",
                          "No movement arrows or voting totals are shown because only one frozen ranking snapshot supports this edition."],
    }
    (HERE / "dist/data.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    press = ["# The REFINERY — NEI Robotics Top 10", "", "## Segment concept", "",
             "Bring the energy of a college football rankings reveal to local student robotics: reveal the regional FRC Top 10, select a team, and introduce the students and adults behind the robot. FTC appears in its own feature segment.", "",
             "Hero line: **The only sport where everyone can go pro.** The career-focused campaign phrase is attributed to [FIRST Global](https://first.global/sport/). Engineering, software, manufacturing, design, and business skills give the line its meaning.", "",
             "## Graphics", "", "- [Regional FRC Top 10](exports/nei-top10-2026.png) — 1920 × 1080 PNG", "- [North Side team spotlight](exports/team-spotlight-9119.png) — 1920 × 1080 PNG", "- [Separate FTC features](exports/ftc-features.png) — 1920 × 1080 PNG", "", "Use the interactive screen to select another team and export its graphic. Presenter notes are excluded from exports.", "",
             "## Suggested opening", "", '“You know the football rankings. Here is another local team sport to follow: robotics. These students build the machine, write its code, scout the opposition, and work with other schools on the field. Our regional FRC Top 10 uses a dated Statbotics performance snapshot. Behind every number is a team and a story.”', "",
             "## Explain the divisions", "", result["formatExplainer"]["analogy"], "", result["formatExplainer"]["ftc"], "", result["formatExplainer"]["frc"], "", result["formatExplainer"]["note"], "",
             "## Ranking and source line", "", "**2026 FRC · Statbotics EPA · Snapshot June 12, 2026.** Local ranks are computed within the 13 teams in The REFINERY's 12-county region found in the official FIRST Indiana district roster. Hometowns establish the county reference; workshops and student residences were not surveyed. The list is independent of FIRST and is not a voted poll or a live October scoreboard.", "",
             "EPA is modeled scoring contribution, not a record of wins or an educational-quality score. The top two values are almost tied relative to their uncertainty. FTC OPR is separate. Retain dates on broadcast graphics and identify historical or undated leadership evidence accurately.", "",
             "## Coming up: the 2026–27 coverage plan", ""]
    preview = result["seasonPreview"]
    press.extend([preview["intro"], "", "Confirmed events retain organizer dates. Show dates and local build/practice windows are planning targets; times and watch links are still to come.", "", "| Date / window | Program | Teaser | Status | Details |", "|---|---|---|---|---|"])
    for item in preview["milestones"]:
        press.append(f"| {item['dateLabel']} | {item['program']} | {item['title']} | {item['status']} | {item['description']} {item['note']} [Source / details]({item['linkUrl']}) |")
    press.extend(["", "### Weekly show promise", "", preview["weeklyPromise"], "", "All episode dates below are **planned coverage**, rather than confirmed broadcasts.", "", "| Proposed date | Episode | Focus |", "|---|---|---|"])
    for show in sorted(preview["shows"]["ftc"] + preview["shows"]["frc"], key=lambda r: (r["date"], r["title"])):
        press.append(f"| {show['date']} | {show['title']} | {show['summary']} |")
    press.extend(["", *["- " + note for note in preview["notes"]], "", "## Close games to watch", "",
                  "All ten FRC Top 10 teams and both returning FTC features have a sourced closest-score match and verified replay. Select its profile to see the score and both alliances. A different closest playoff is linked as an alternative where available. FTC replays open at publisher-authored match chapters.", "",
                  result["matchHighlights"]["scoreNote"], "", "[Complete match library and selection methodology](match-highlights.md)", "", "## Team rundown", ""])
    match_lookup = {(r["program"], r["number"]): r for r in result["matchHighlights"]["teams"]}
    for t in teams:
        press.extend([f"### {t['rank']}. {t['name']} · FRC {t['number']}", "", f"{t['school']} · {t['city']}, {t['county']} County", "",
                      f"EPA {t['epa']:.2f}; Indiana {t['stateRank']}/{t['stateCount']}; world {t['worldRank']}/{t['worldCount']}.", "", *["- " + s for s in t["talkingPoints"]], ""])
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
                  "This is a prepared media package; no station, school, student, or coach was contacted as part of its creation."])
    (HERE / "dist/press-kit.md").write_text("\n".join(press).rstrip() + "\n")
    credits = ["# School and team logo sources", "", "Marks identify the named school or robotics team. Original proportions and colors are preserved. No endorsement or new license is asserted.", ""]
    for r in logo_rows:
        credits.extend([f"- {r['program'].upper()} {r['number']} / {r['kind']}: {r['label']}. {r['status']}. {r['note']} Source page: {r['pageUrl']}" + (f" Asset: {r['sourceUrl']}" if r.get("file") else "")])
    (HERE / "dist/logo-credits.md").write_text("\n".join(credits) + "\n")
    print(f"Built broadcast data: {len(teams)} FRC teams, {len(features)} FTC features, one current-season watch.")


if __name__ == "__main__":
    main()
