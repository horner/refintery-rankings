#!/usr/bin/env python3
"""Build the offline close-match library from audited, preserved research.

No network requests run during this build. Research capture scripts and original
responses live in broadcast/data/match-research; this file normalizes their final
selections for the interactive website and creates the public methodology page.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
RESEARCH = HERE / "data/match-research"
REPO = "https://github.com/horner/refintery-rankings/blob/main/"
REPO_TREE = "https://github.com/horner/refintery-rankings/tree/main/"
POLICY = (
    "Select the closest final score; equally close playoffs take priority. "
    "A different closest playoff is linked when available. Wins, losses and "
    "played ties qualify."
)
SCORE_NOTE = (
    "Final scores belong to alliances and include penalties. Partners and "
    "opponents change; a close matchup does not establish a permanent rivalry."
)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def video_index(manifest):
    """Join only exact official result URLs; never construct a replay URL."""
    index = {}
    for row in manifest["records"]:
        url = row["officialResultsUrl"]
        if url in index:
            raise ValueError("Duplicate video association: " + url)
        index[url] = row
    return index


def match_record(raw, program, videos):
    if raw is None:
        return None
    frc = program == "FRC"
    url = raw["matchUrl" if frc else "officialResultUrl"]
    association = videos.get(url)
    choices = association.get("videos", []) if association else []
    video = choices[0] if choices else None
    phase = raw["phase"].capitalize()
    if phase not in ("Playoff", "Qualification"):
        raise ValueError("Unknown match phase: " + phase)
    start, end = raw["eventStartDate"], raw["eventEndDate"]
    # FIRST's FRC team page gives event dates. A missing match timestamp is not
    # silently promoted to the event's closing date, even for a playoff match.
    if frc:
        date_label = f"{start} (event date)" if start == end else f"{start}–{end} (event dates)"
    else:
        date_label = raw.get("date") or (start if start == end else f"{start}–{end} (event dates)")
    alliance = raw["teamAlliance"].capitalize()
    outcome = raw["teamResult" if frc else "outcome"].capitalize()
    result = {
        "id": (association["matchKey"] if association else
               f"{raw['year']}-{raw['eventCode']}-{phase.lower()}-{raw['matchNumber']}") if frc else raw["key"],
        "eventName": raw["eventName"], "eventCode": raw["eventCode"],
        "eventStartDate": start, "eventEndDate": end, "dateLabel": date_label,
        "playedDate": None if frc else raw.get("date"),
        "phase": phase, "matchLabel": raw["matchLabel"], "matchNumber": raw["matchNumber"],
        "redTeams": raw["redTeams"], "blueTeams": raw["blueTeams"],
        "redScore": raw["redScore"], "blueScore": raw["blueScore"], "margin": raw["margin"],
        "teamAlliance": alliance, "outcome": outcome, "officialUrl": url,
        "videoUrl": video["url"] if video else None,
        "videoTitle": video["title"] if video else None,
        "videoPublisher": video["author"] if video else None,
        "videoEvidence": video["evidence"] if video else None,
    }
    if result["margin"] != abs(result["redScore"] - result["blueScore"]):
        raise ValueError("Score margin mismatch: " + url)
    if alliance not in ("Red", "Blue") or outcome not in ("Win", "Loss", "Tie"):
        raise ValueError("Invalid alliance/outcome: " + url)
    return result


def alternate(main, playoff):
    return playoff if playoff and (main is None or main["officialUrl"] != playoff["officialUrl"]) else None


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def match_link(match):
    if not match:
        return "—"
    return f"[{cell(match['eventName'])} · {cell(match['matchLabel'])}]({match['officialUrl']})"


def render_methodology(library, frc, ftc):
    lines = [
        "# Close games to watch", "", f"Research preserved {library['asOf']}.", "",
        library["policy"], "", library["scoreNote"], "",
        "## Season and eligibility", "",
        "- **FRC:** 2026 official season results through the June 12, 2026 ranking snapshot. Later offseason events are excluded. Full team schedules were preserved from FIRST Event Web; every published main match and playoff alternative was independently checked against its official match scorecard, including six-robot lineups, final scores and disqualification penalties. Event ranges remain labeled as event dates when an individual match date was not published in the preserved schedule.",
        "- **FTC:** the 2025 season token means **2025–26 DECODE**, including official Premier play in June 2026. The audited FTCScout event/match responses retain individual participant status. Only played, scored matches with complete on-field lineups, no no-shows or disqualifications, and no modified game rules qualify. Registered backup teams do not count as playing in a match when marked off-field.",
        "- Both wins and losses are valid close games. A genuine played tie can qualify; an unplayed or missing-score schedule row cannot. Equal minimum margins prefer a playoff. The preserved FTC selection then uses later played date and match number; a verified replay can resolve an otherwise exact tie. No FRC team's published minimum required a tie-break.",
        "- An absent replay does not invalidate a scored match: the official result remains available. The main selection stays the closest eligible score, and a different closest playoff appears as a separate alternative.",
        "- Pending means no eligible match exists in this dated research scope. It does not mean a team has never played. New FTC 36124 R.Amp Robotics belongs to 2026–27 BIOBUZZ; its first-match profile is still to come.", "",
        "## Replay verification", "",
        "FRC replay links come from the exact matching The Blue Alliance result-page embed, with title and publisher confirmed by YouTube metadata. FTC replay links use publisher-authored match chapters in official FIRSTINRobotics event recordings. Their timestamps are published chapter starts, not estimates from match wall-clock times. The official result link independently identifies the teams and final score. No guessed video IDs, event-search links or unrelated highlight reels are used as match replays.", "",
        "## Team library", "",
        "The score columns below always read **Red–Blue**. Margin is the absolute difference. Shared matches can appear for multiple teams, with each team's own alliance and result retained in the data.", "",
        "| Program / team | Season | Closest eligible match | Date / event dates | Red–Blue | Margin | Replay | Different closest playoff |",
        "|---|---|---|---|---:|---:|---|---|",
    ]
    for team in library["teams"]:
        main, playoff = team["main"], team["playoff"]
        if main:
            score = f"{main['redScore']}–{main['blueScore']}"
            replay = f"[Watch]({main['videoUrl']})" if main["videoUrl"] else "Official result available"
            alt = match_link(playoff)
            if playoff:
                alt += f" · {playoff['redScore']}–{playoff['blueScore']} ({playoff['margin']} pt)"
                if playoff["videoUrl"]:
                    alt += f" · [Watch]({playoff['videoUrl']})"
            values = [f"{team['program']} {team['number']} {team['teamName']}", team["seasonLabel"], match_link(main), main["dateLabel"], score, main["margin"], replay, alt]
        else:
            values = [f"{team['program']} {team['number']} {team['teamName']}", team["seasonLabel"], f"[Pending]({team['sourceUrl']}) — {team['note']}", "—", "—", "—", "—", "—"]
        # Match links are already escaped; scalar values have no structural pipes
        # except names, which are escaped here without double-escaping link text.
        values[0] = cell(values[0])
        lines.append("| " + " | ".join(map(str, values)) + " |")
    lines.extend(["", "## Source trail", "",
        f"- [Normalized library]({REPO}broadcast/data/match-highlights.json)",
        f"- [FRC complete candidates and verification]({REPO}broadcast/data/match-research/frc-verified.json)",
        f"- [FRC selected match scorecards]({REPO}broadcast/data/match-research/frc-match-scorecards.json)",
        f"- [FRC original schedule captures and research scripts]({REPO_TREE}broadcast/data/match-research/frc-sources/)",
        f"- [FTC candidates, participant flags and exclusions]({REPO}broadcast/data/match-research/ftc-candidates.json)",
        f"- [FTC original event and match responses]({REPO_TREE}broadcast/data/match-research/ftc-sources/)",
        f"- [FRC video associations and metadata references]({REPO}broadcast/data/match-research/video-links.json)",
        f"- [FTC timestamp associations and chapter references]({REPO}broadcast/data/match-research/video-ftc-links.json)",
        "", "The website build reads these preserved files offline. Rebuilding does not silently fetch a newer season, replace a selected match or change the historical rankings.", "",
    ])
    return "\n".join(lines)


def build_matches():
    """Write both generated artifacts and return the normalized library."""
    frc = load(RESEARCH / "frc-verified.json")
    ftc = load(RESEARCH / "ftc-candidates.json")
    frc_manifest = load(RESEARCH / "video-links.json")
    ftc_manifest = load(RESEARCH / "video-ftc-links.json")
    frc_videos, ftc_videos = video_index(frc_manifest), video_index(ftc_manifest)
    frc_roster = load(ROOT / "data/teams.json")["teams"]
    ftc_source = load(ROOT / "ftc/data/teams.json")
    ftc_roster = ftc_source["teams"] + ftc_source["current_season_only_teams"]
    frc_by_number = {r["team"]: r for r in frc["records"]}
    ftc_by_number = {r["teamNumber"]: r for r in ftc["teams"]}
    if set(frc_by_number) != {r["team_number"] for r in frc_roster}:
        raise ValueError("FRC research and published roster differ")
    if set(ftc_by_number) != {r["team_number"] for r in ftc_roster}:
        raise ValueError("FTC research and published roster differ")
    teams = []
    for row in frc_roster:
        number = row["team_number"]
        research = frc_by_number[number]
        main = match_record(research["absoluteClosest"], "FRC", frc_videos)
        playoff_raw = research["selected"]
        playoff = match_record(playoff_raw, "FRC", frc_videos) if playoff_raw and playoff_raw["phase"] == "playoff" else None
        note = "Closest final-score match in the preserved 2026 official season."
        if main and main["phase"] == "Qualification" and playoff:
            note += " A different closest playoff is linked separately."
        if not research["eligibilityCounts"]["playoff"]:
            note += " No played playoff match is listed in this season scope."
        teams.append({
            "program": "FRC", "number": number, "teamName": row["team_name"],
            "season": 2026, "seasonLabel": "2026 REBUILT", "status": "played" if main else "pending",
            "note": note, "counts": {"eligible": research["eligibilityCounts"]["eligible"], "playoff": research["eligibilityCounts"]["playoff"]},
            "sourceUrl": research["sourceUrl"], "main": main, "playoff": alternate(main, playoff),
        })
    for row in ftc_roster:
        number = row["team_number"]
        research = ftc_by_number[number]
        main = match_record(research["selected"], "FTC", ftc_videos)
        playoff = match_record(research["closestPlayoff"], "FTC", ftc_videos)
        new = row in ftc_source["current_season_only_teams"]
        note = research["selectionReason"]
        if not main:
            note = ("New 2026–27 team; no 2025–26 match is attributed to it. Profile to follow its first match." if new else
                    "No eligible played 2025–26 match was returned in the preserved research; a representative match is pending.")
        teams.append({
            "program": "FTC", "number": number, "teamName": row["team_name"],
            "season": 2026 if new else 2025,
            "seasonLabel": "2026–27 BIOBUZZ" if new else "2025–26 DECODE",
            "status": "played" if main else "pending", "note": note,
            "counts": {"eligible": research["eligibleMatchCount"], "playoff": research["eligiblePlayoffCount"]},
            "sourceUrl": row["first_team_url"], "main": main, "playoff": alternate(main, playoff),
        })
    if len(teams) != 26:
        raise ValueError("Expected all 17 FRC and 9 FTC teams")
    library = {
        "asOf": max(source["asOf"][:10] for source in (frc, ftc, frc_manifest, ftc_manifest)),
        "methodologyUrl": "match-highlights.md", "policy": POLICY,
        "scoreNote": SCORE_NOTE, "teams": teams,
    }
    (HERE / "data/match-highlights.json").write_text(json.dumps(library, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (HERE / "dist/match-highlights.md").write_text(render_methodology(library, frc, ftc), encoding="utf-8", newline="\n")
    return library


if __name__ == "__main__":
    result = build_matches()
    played = sum(team["status"] == "played" for team in result["teams"])
    print(f"Built {len(result['teams'])} match profiles: {played} played, {len(result['teams']) - played} pending")
