#!/usr/bin/env python3
"""Check FTC source fidelity, joins, geometry, history, roles, and CSV exports offline."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.parse import unquote

from normalize_ftcscout import normalize

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {22331, 25638, 5501, 14174, 12802, 19778, 30782, 32552}


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def keyed(rows):
    result = {r["team_number"]: r for r in rows}
    require(len(result) == len(rows), "Duplicate team number")
    return result


def distance(origin, point, radius):
    a, b, c, d = map(math.radians, [origin["latitude"], origin["longitude"], point["latitude"], point["longitude"]])
    h = math.sin((c-a)/2)**2 + math.cos(a)*math.cos(c)*math.sin((d-b)/2)**2
    return 2 * radius * math.asin(math.sqrt(h))


def main():
    config = load("data/publication.json")
    output = load("data/teams.json")
    records = keyed(output["teams"])
    roster = keyed(load("data/roster.json")["teams"])
    geography = load("data/geography.json")
    locations = keyed(geography["teams"])
    leadership = load("data/leadership.json")
    leaders = keyed(leadership["records"])
    rankings = load("data/rankings.json")
    ratings = keyed(rankings["teams"])
    histories = keyed(load("artifacts/first/season-history-through-2025.json")["teams"])
    require(set(records) == set(roster) == set(ratings) == EXPECTED, "Completed-season roster changed")
    require({n for n, r in ratings.items() if r["value"] is None} == {32552}, "Ranked/unranked population changed")
    require(sum(r["state"] == "IN" for r in records.values()) == 2, "Indiana roster mismatch")
    require(sum(r["state"] == "OH" for r in records.values()) == 6, "Ohio roster mismatch")
    require(config["season_start_year"] == config["season_history_cutoff_start_year"] == 2025, "FTC starting-year cutoff changed")
    require(output["publication"] == config and output["ranking_method"] == rankings["method"], "Publication metadata changed in export")

    root_geography = json.loads((ROOT.parent / "data/geography.json").read_text(encoding="utf-8"))
    require(geography["origin"]["latitude"] == root_geography["origin"]["coordinates"]["latitude"] and
            geography["origin"]["longitude"] == root_geography["origin"]["coordinates"]["longitude"], "FTC/FRC origins differ")
    require(geography["earth_radius_miles"] == root_geography["scope"]["earth_radius_miles"], "FTC/FRC distance conventions differ")
    for point in geography["teams"] + geography["boundary_exclusions"] + geography["historical_candidates"]:
        miles = distance(geography["origin"], point, geography["earth_radius_miles"])
        require(abs(miles - point["distance_miles"]) < 1e-8, f"Distance mismatch: {point['team_number']}")
        require((miles <= 60) == point["within_60_reference_point"], f"Radius decision mismatch: {point['team_number']}")
        require(point["qualification"] and point["source_urls"], "Missing geographic qualifications")
    require(all(locations[n]["within_60_reference_point"] for n in EXPECTED), "Included reference outside radius")
    require({n for n in EXPECTED if locations[n]["point_type"] == "town_screening_only"} == {19778, 32552}, "Town-only screening qualification lost")

    snapshot = ROOT / config["ranking_snapshot_directory"]
    fresh = keyed(normalize(snapshot))
    saved_extract = keyed(json.loads((snapshot / "local-ranking-extract.json").read_text(encoding="utf-8")))
    require(fresh == saved_extract, "Frozen ranking extract does not reproduce from raw captures")
    # Validate every captured body, including the five best-event metadata responses.
    capture_count = 0
    for manifest_file in snapshot.rglob("manifest.json"):
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        for capture in manifest["captures"]:
            raw = (manifest_file.parent / capture["raw_file"]).read_bytes()
            require(len(raw) == capture["byte_count"] and hashlib.sha256(raw).hexdigest() == capture["sha256"], "Raw response integrity failure")
            capture_count += 1
    for number in EXPECTED:
        r, k = records[number], ratings[number]
        require(all(r[key] == value for key, value in roster[number].items() if key != "source_urls"), f"Roster qualification lost: {number}")
        require(r["rankings"] == k and r["geography"] == locations[number] and r["leadership"] == leaders[number], f"Joined evidence differs: {number}")
        require(all(k[key] == value for key, value in fresh[number].items()), f"Ranking source value differs: {number}")
        if k["value"] is not None:
            require(k["world_team_count"] == 8368, "World ranking denominator changed")
            expected_count = 71 if k["regional_code"] == "USIN" else 113
            require(k["regional_team_count"] == expected_count, "Event-region denominator changed")
            for code in k["world_best_event_codes"] + k["regional_best_event_codes"]:
                event = json.loads((snapshot / "event-metadata" / f"event-2025-{code}.json").read_text(encoding="utf-8"))
                require(event["season"] == 2025 and not event["remote"] and not event["modifiedRules"], "Best event fails eligibility")
                if code in k["regional_best_event_codes"]:
                    require(event["regionCode"] == k["regional_code"], "Regional best assigned to wrong event region")
        h = r["season_history"]
        require(h == histories[number], f"History extract changed: {number}")
        require(h["recorded_season_count"] == len(h["recorded_seasons_through_cutoff"]), "Season count mismatch")
        require(h["recorded_seasons_through_cutoff"] == [s for s in h["all_listed_seasons"] if s <= 2025], "Future or invented season counted")
        require(h["history_coverage_note"] and h["source_url"], "History coverage qualification lost")
    require(records[22331]["rankings"]["value"] != records[22331]["rankings"]["regional_value"], "World and regional maxima incorrectly conflated")
    require(records[32552]["rankings"]["value"] is None and records[32552]["rankings"]["world_rank"] is None, "Unranked team assigned a value")
    current = output["current_season_only_teams"]
    require(len(current) == 1 and current[0]["team_number"] == 36124, "New-season watch list mismatch")
    require(current[0]["season_history"]["recorded_season_count"] == 0 and "rankings" not in current[0], "Current-season registration leaked into completed cohort")

    source_urls = {s["url"] for s in load("data/sources.json")["sources"]}
    source_ids = {s["source_id"] for s in load("data/sources.json")["sources"]}
    require(len(source_urls) == len(source_ids) == load("data/sources.json")["source_count"], "Duplicate source ID or URL")
    leader_source_ids = {s["id"] for s in leadership["sources"]}
    person_count = 0
    for number, l in leaders.items():
        require(l["captain"] is None and l["gap"], "Student captain or leadership gap incorrectly inferred")
        for category in ("adult_leadership", "student_leadership", "public_student_representatives"):
            for p in l.get(category, []):
                require(p["name"] and p["role"] and p["season"] and p["notes"] and p["evidence_status"], "Incomplete person-role evidence")
                require("evidence_date" in p and p["evidence_date_basis"], "Evidence date or undated qualification lost")
                require(set(p["source_ids"]) <= leader_source_ids and set(p["source_urls"]) <= source_urls, "Broken leadership-source join")
                person_count += 1
    for r in records.values():
        require(set(r["source_ids"]) <= source_ids and set(r["source_urls"]) <= source_urls, "Broken team-source join")

    for table in load("artifacts/export-tables.json")["tables"]:
        with (ROOT / table["output"]).open(encoding="utf-8", newline="") as file:
            actual = list(csv.reader(file))
        expected = [["" if v is None else str(v) for v in row] for row in [table["headers"], *table["rows"]]]
        require(actual == expected, f"CSV values or qualifications changed: {table['output']}")
        require(all(not isinstance(v, str) or not re.match(r"^[=+@\t\r]", v) for row in table["rows"] for v in row), "Unexpected spreadsheet formula prefix")
    for file in ROOT.rglob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
            if target.startswith(("https://", "http://", "#", "mailto:")):
                continue
            relative = unquote(target.split("#", 1)[0])
            require(not relative or (file.parent / relative).exists(), f"Broken local documentation link: {file.name}: {relative}")
    print(f"Verified FTC: {len(records)} rostered teams; 7 ranked; 1 current-season addition; {person_count} person-role rows; {capture_count} raw source responses.")
    print("Raw rankings and denominators, distinct world/regional metrics, geometry, season cutoff, roles, source joins, CSV fidelity, and local links passed.")


if __name__ == "__main__":
    main()
