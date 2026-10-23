#!/usr/bin/env python3
"""Verify the broadcast ordering, source joins, leadership roles, and static files."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path
import re
import struct
from datetime import date, timedelta
import math
from verify_matches import verify_matches

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    data = load(HERE / "dist/data.json")
    verify_matches(data)
    thumbnails = load(HERE / "data/video-thumbnails.json")["thumbnails"]
    require(data["videoThumbnails"] == {r["videoUrl"]: r for r in thumbnails}, "Video thumbnail join changed")
    require(len({r["videoUrl"] for r in thumbnails}) == len(thumbnails), "Duplicate video thumbnail")
    for thumbnail in thumbnails:
        raw = (HERE / "dist" / thumbnail["file"]).read_bytes()
        metadata = load(HERE / thumbnail["sourceMetadataFile"])
        require(raw.startswith(b"\xff\xd8") and hashlib.sha256(raw).hexdigest() == thumbnail["sha256"], "Video thumbnail bytes changed")
        require(thumbnail["sourceUrl"] == metadata["thumbnail_url"] and thumbnail["width"] == metadata["thumbnail_width"] and thumbnail["height"] == metadata["thumbnail_height"], "Video thumbnail source differs from the verified replay metadata")
        require(thumbnail["videoUrl"] == "https://www.youtube.com/watch?v=" + thumbnail["videoId"] and thumbnail["videoId"] in metadata["html"], "Video preview belongs to a different replay")
    match_library = {(r["program"], r["number"]): r for r in data["matchHighlights"]["teams"]}
    require(all(match_library[("FRC", t["number"])]["main"]["videoUrl"] in data["videoThumbnails"] for t in data["top10"]), "Ranked team is missing its match preview")
    frc = load(ROOT / "data/teams.json")
    ftc = load(ROOT / "ftc/data/teams.json")
    regional = sorted([r for r in frc["teams"] if r["scope_group"] == "northeast_indiana"],
                      key=lambda r: (-r["rankings"]["epa_mean"], r["team_number"]))
    require(len(regional) == 13 and len(data["top10"]) == 10, "Unexpected Top 10 population")
    require([r["number"] for r in data["top10"]] == [r["team_number"] for r in regional[:10]], "Top 10 does not match source EPA ordering")
    scope = load(HERE / "data/first-fin-scope-audit.json")
    require(len(scope["teams"]) == 69 and scope["capture_failure_count"] == 0, "Official roster screening is incomplete")
    require(set(scope["included_team_numbers"]) == {r["team_number"] for r in regional}, "Official district and research regional selections differ")
    require(data["edition"]["rankingsDate"] == "2026-06-12" and data["edition"]["season"] == 2026, "Historical snapshot date lost")
    people_count = 0
    for t, r in zip(data["top10"], regional[:10]):
        k, h, l = r["rankings"], r["season_history"], r["leadership"]
        require(t["epa"] == k["epa_mean"] and t["stateRank"] == k["state_rank"] and t["worldRank"] == k["world_rank"], "Source performance value changed")
        require(t["stateCount"] == k["state_team_count"] and t["worldCount"] == k["world_team_count"], "Source ranking denominator changed")
        require(t["seasons"] == h["recorded_season_count"] and t["rookieYear"] == h["official_rookie_year"], "Source history changed")
        require(t["gaps"] == l["gaps"] and t["affiliationNote"] == r["affiliation_notes"], "Qualification lost")
        for to_key, from_key in (("students", "students"), ("adults", "adults"), ("representatives", "other_representatives")):
            require(len(t[to_key]) == len(l[from_key]), "People dropped from evidence")
            for p, original in zip(t[to_key], l[from_key]):
                require((p["name"], p["role"], p["date"], p["note"], p["sourceUrls"]) ==
                        (original["name"], original["role"], original["evidence_date"], original["notes"], original["source_urls"]), "Published role or date changed")
                people_count += 1
    source_ftc = {r["team_number"]: r for r in ftc["teams"]}
    require({r["number"] for r in data["ftc"]["teams"]} == {22331, 25638}, "FTC features escaped regional scope")
    for t in data["ftc"]["teams"]:
        r = source_ftc[t["number"]]
        require(t["opr"] == r["rankings"]["value"] and t["regionalOpr"] == r["rankings"]["regional_value"], "FTC world/regional values conflated")
    require([r["number"] for r in data["ftc"]["newTeams"]] == [36124], "New-season watch changed")
    require(data["hero"]["attributionUrl"] == "https://first.global/sport/", "Hero attribution lost")
    require("not assigned by school enrollment" in data["formatExplainer"]["analogy"], "Enrollment distinction lost")
    preview = load(HERE / "data/season-preview.json")
    require(data["seasonPreview"] == preview, "Season preview did not reach the browser data")
    local = load(HERE / "data/season-sources/refinery.json")
    future_frc = load(HERE / "data/season-sources/frc.json")
    future_ftc = load(HERE / "data/season-sources/ftc.json")
    opening = future_ftc["openingWeekend"]
    require(preview["countdown"]["targetDate"] == opening["startDate"] and preview["countdown"]["endDate"] == opening["endDate"], "Countdown is not the official Indiana opening weekend")
    require((date.fromisoformat(opening["startDate"]) - date.fromisoformat(preview["asOf"])).days == 44, "Opening countdown baseline is incorrect")
    require({r["number"] for r in preview["localFtcTeams"]} == {r["number"] for r in future_ftc["localTeams"]} == {22331, 25638, 36124}, "Current three-team FTC teaser changed")
    milestones = {r["id"]: r for r in preview["milestones"]}
    require(len(milestones) == len(preview["milestones"]), "Duplicate season milestone")
    require([r["startDate"] for r in preview["milestones"]] == sorted(r["startDate"] for r in preview["milestones"]), "Season milestones are out of order")
    expected_events = {
        "boiler-bot-battle": (local["events"][0]["start_date"], local["events"][0]["end_date"]),
        "monster-match": (local["events"][1]["start_date"], local["events"][1]["end_date"]),
        "ftc-opening": (opening["startDate"], opening["endDate"]),
        "frc-week-one": (future_frc["confirmed"]["competitionWeeks"][0]["start"], future_frc["confirmed"]["competitionWeeks"][0]["end"]),
        "ftc-state": (future_ftc["state"]["date"], future_ftc["state"]["date"]),
        "fort-wayne": (future_frc["confirmed"]["indianaEvents"][3]["start"], future_frc["confirmed"]["indianaEvents"][3]["end"]),
        "frc-state": (future_frc["confirmed"]["indianaState"]["start"], future_frc["confirmed"]["indianaState"]["end"]),
        "worlds": (future_ftc["world"]["startDate"], future_ftc["world"]["endDate"]),
    }
    for key, expected in expected_events.items():
        item = milestones[key]
        require((item["startDate"], item["endDate"]) == expected and item["status"] == "Confirmed event", f"Official date/status changed: {key}")
    for item in preview["milestones"]:
        require(date.fromisoformat(item["startDate"]) <= date.fromisoformat(item["endDate"]), "Milestone dates reversed")
        require(item["status"] in {"Confirmed event", "Planned coverage", "Target window"} and item["linkUrl"].startswith("https://"), "Milestone missing status or source")
    require(milestones["ramp-profile"]["status"] == "Planned coverage" and "only if" in milestones["ramp-profile"]["note"], "R.Amp debut incorrectly presented as assigned")
    require(milestones["frc-week-zero"]["status"] == "Target window" and "not yet announced" in milestones["frc-week-zero"]["note"], "Local Week 0 presented as confirmed")
    require(milestones["ri3d"]["status"] == "Planned coverage" and date.fromisoformat(milestones["ri3d"]["endDate"]) - date.fromisoformat(milestones["ri3d"]["startDate"]) == timedelta(days=3), "RI3D planning window changed")
    for show in preview["shows"]["ftc"]:
        require(date.fromisoformat(show["date"]).weekday() == 1, "FTC editorial target is not Tuesday")
    for show, week in zip(preview["shows"]["frc"], future_frc["confirmed"]["competitionWeeks"]):
        require(date.fromisoformat(show["date"]) == date.fromisoformat(week["end"]) + timedelta(days=1), "FRC recap is not after its competition week")
    require(all(date.fromisoformat(s["date"]).weekday() == 0 for s in preview["shows"]["frc"]), "FRC editorial target is not Monday")
    dnf = load(HERE / "data/dnf.json")
    universe = load(HERE / "data/dnf-research/school-universe.json")
    require(data["dnf"] == dnf, "DNF directory did not reach the browser data")
    groups = (dnf["schools"], dnf["excludedSchools"], dnf["reviewSchools"])
    all_schools = [school for group in groups for school in group]
    require(len({school["id"] for school in all_schools}) == len(all_schools) == len(universe["schools"]), "DNF join duplicated or dropped a campus")
    require({school["id"] for school in all_schools} == {school["id"] for school in universe["schools"]}, "DNF universe join lost school identities")
    require(dnf["origin"] == load(ROOT / "data/geography.json")["origin"] and dnf["radiusMiles"] == 60, "DNF origin or radius changed")
    origin = dnf["origin"]["coordinates"]
    for school in all_schools:
        lat1, lon1, lat2, lon2 = map(math.radians, (origin["latitude"], origin["longitude"], school["latitude"], school["longitude"]))
        hav = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
        miles = 3958.7613 * 2 * math.asin(math.sqrt(hav))
        require(miles <= 60 and abs(miles-school["distanceMiles"]) < .00001, f"DNF radius or distance is wrong: {school['name']}")
        require(str(school["gradesHigh"]).isdigit() and int(school["gradesHigh"]) >= 9, "DNF school does not offer high-school grades")
        require(school["schoolUrl"].startswith(("http://", "https://")) and school["sourceUrls"], "DNF school has no source")
        leader = school["leader"]
        require(school["sector"] == "Private" or bool(leader), f"Public superintendent/school leader missing: {school['name']}")
        if leader:
            require(leader["name"] and leader["role"] and leader["sourceUrl"].startswith("https://"), "DNF leader has no documented role/source")
    invited_ids = {school["id"] for school in dnf["schools"]}
    team_screen = load(HERE / "data/dnf-research/team-screen.json")
    for positive in team_screen["positiveSchoolAffiliations"]:
        require(not invited_ids.intersection(positive.get("ncesIds", [])), f"Known team school incorrectly invited as DNF: {positive['schoolName']}")
    require(all(school["teamClassification"] == "no-school-affiliation-verified-in-roster-screen" for school in dnf["schools"]), "DNF treats a known affiliation as absence")
    require(all(school["teamClassification"] == "exclude-active/recent" for school in dnf["excludedSchools"]), "DNF existing-team classification changed")
    require(dnf["counts"]["invited"] == len(dnf["schools"]) and dnf["counts"]["leadersNamed"] == sum(bool(school["leader"]) for school in dnf["schools"]), "DNF visible counts are incorrect")
    require("no school-affiliated FTC or FRC team verified" in dnf["qualification"] and "another robotics program" in dnf["qualification"], "DNF team-absence qualification lost")
    require(dnf["contactEmail"] == "info@refineryrobotics.org" and (HERE / "dist/dnf-methodology.md").is_file(), "DNF interest destination or evidence missing")
    for name in ("index.html", "styles.css", "app.js", "press-kit.md", "assets/refinery-logo.svg", "assets/refinery-shop.jpeg"):
        require((HERE / "dist" / name).is_file(), f"Missing static asset: {name}")
    for asset in load(HERE / "data/asset-manifest.json")["assets"]:
        require(hashlib.sha256((HERE / asset["file"]).read_bytes()).hexdigest() == asset["sha256"], "Official asset checksum changed")
    marks = load(HERE / "data/logos.json")["logos"]
    require(len({(r["program"], r["number"], r["kind"]) for r in marks}) == len(marks), "Duplicate logo identity")
    for mark in marks:
        if mark.get("file"):
            require(mark["status"] == "verified" and mark["sourceUrl"].startswith("https://"), "Logo source is unverified")
            require(hashlib.sha256((HERE / "dist" / mark["file"]).read_bytes()).hexdigest() == mark["sha256"], "Logo checksum changed")
    for program, teams in (("frc", data["top10"]), ("ftc", data["ftc"]["teams"] + data["ftc"]["newTeams"])):
        for team in teams:
            expected = {r["kind"]: r for r in marks if r["program"] == program and r["number"] == team["number"]}
            require(team["logos"] == expected, "Logo joined to the wrong team or program")
    require(not data["top10"][1]["logos"]["school"].get("file"), "Community team incorrectly assigned a school mark")
    for name in ("nei-top10-2026.png", "team-spotlight-9119.png", "ftc-features.png"):
        raw = (HERE / "dist/exports" / name).read_bytes()
        require(raw[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", raw[16:24]) == (1920, 1080), f"Broadcast graphic has incorrect dimensions: {name}")
    for file in (HERE / "dist").rglob("*"):
        if file.suffix not in {".html", ".css", ".js", ".md", ".json", ".svg"}:
            continue
        value = file.read_text(encoding="utf-8")
        require("/tmp/" not in value and "/Users/" not in value, f"Machine path leaked: {file.name}")
        require(not re.search(r"github_pat_[A-Za-z0-9_]{30,}|gh[pousr]_[A-Za-z0-9]{30,}", value), "Credential-like value in static output")
    print(f"Verified broadcast: Top 10 of {len(regional)} regional FRC teams; {people_count} sourced person-role rows; two separate FTC features and one rookie watch.")


if __name__ == "__main__":
    main()
