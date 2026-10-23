#!/usr/bin/env python3
"""Verify the published data and local links offline, independently of the build."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import unquote
import zlib

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def haversine(a, b, radius):
    lat1, lon1, lat2, lon2 = map(math.radians, [a["latitude"], a["longitude"], b["latitude"], b["longitude"]])
    h = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return radius * 2 * math.asin(math.sqrt(h))


def eligible_files():
    return sorted(p for p in ROOT.rglob("*") if p.is_file() and not any(part in {".git", "node_modules", "__pycache__", "verification-runs"} for part in p.relative_to(ROOT).parts) and p.name not in {"SHA256SUMS", "tba.env"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-checksums", action="store_true")
    args = parser.parse_args()
    config = load("data/publication.json")
    records = load("data/teams.json")["teams"]
    baseline = {r["team_number"]: r for r in load("data/research-baseline.json")["teams"]}
    ids = {r["team_number"] for r in records}
    require(len(records) == len(ids) == 17 and ids == set(baseline), "17 unique baseline teams required")
    require(sum(r["state"] == "IN" for r in records) == 13, "Expected 13 Indiana teams")
    snap = ROOT / config["statbotics_snapshot_directory"]
    meta = json.loads((snap / "metadata.json").read_text())
    raw = (snap / "team-years-2026.json.zlib").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == meta["raw_sha256"], "Raw Statbotics checksum mismatch")
    full = json.loads(zlib.decompress(raw))
    original = {r["team"]: r for r in full["team_years"]}
    subset = json.loads((snap / "team-years-2026-subset.json").read_text())["team_years"]
    require({r["team"] for r in subset} == ids, "Statbotics subset coverage mismatch")
    require(all(r == original[r["team"]] for r in subset), "Statbotics subset changed source rows")
    require(len(full["team_years"]) == 3724, "World denominator changed")
    for r in records:
        number = r["team_number"]
        b, k, h = baseline[number], r["rankings"], r["season_history"]
        require(r["state"] == original[number]["state"], f"State join mismatch: {number}")
        require((k["epa_mean"], k["state_rank"], k["world_rank"]) == (b["epa_mean"], b["state_rank"], b["world_rank"]), f"Rating/rank mismatch: {number}")
        require((k["state_team_count"], k["world_team_count"]) == (b["state_total"], b["world_total"]), f"Rank denominator mismatch: {number}")
        require(k["snapshot_last_modified_utc"] == config["rankings_last_modified_utc"] == "2026-06-12T02:51:19Z", "Ranking date changed")
        require(h["recorded_seasons_through_cutoff"] == b["recorded_seasons"], f"Season mismatch: {number}")
        require(h["recorded_season_count"] == len(b["recorded_seasons"]), f"Season count mismatch: {number}")
        require(all(y <= 2026 for y in h["recorded_seasons_through_cutoff"]), "Future season counted")
        require(h["official_rookie_year"] == b["official_rookie_year"], f"Rookie year mismatch: {number}")
        require(r["leadership"]["team_number"] == number, "Leadership join mismatch")
        for category in ("adults", "students", "other_representatives"):
            for person in r["leadership"][category]:
                require(person["name"] and person["role"] and person["notes"] and person["evidence_status"], "Incomplete person-role evidence")
                require(person["source_urls"] and all(u.startswith("https://") for u in person["source_urls"]), "Missing person source")
    by_id = {r["team_number"]: r for r in records}
    for n in (8431, 8432):
        require(not by_id[n]["leadership"]["adults"], "East Noble team-specific coach inferred without evidence")
    require(any(p["name"] == "Ava Stanley" for p in by_id[8742]["leadership"]["other_representatives"]), "Ava Stanley role qualification lost")
    require(not any(p["name"] == "Ava Stanley" for p in by_id[8742]["leadership"]["students"]), "Ava Stanley incorrectly classified as student")
    krystina = [p for p in by_id[11407]["leadership"]["students"] if "Johnson" in p["name"]]
    require(krystina and all("drive" in p["role"].lower() for p in krystina), "Drive-team captain distinction lost")

    geography = load("data/geography.json")
    locations = {p["location_id"]: p for p in geography["locations"]}
    for r in geography["teams"] + geography["exclusions"]:
        if r["location_id"] is None: continue
        miles = haversine(geography["origin"]["coordinates"], locations[r["location_id"]]["coordinates"], geography["scope"]["earth_radius_miles"])
        require(abs(miles - r["distance_miles"]) < 1e-5, f"Distance mismatch: {r['team_number']}")
        require((miles <= 60) == r["within_radius"], f"Radius classification mismatch: {r['team_number']}")

    matrices = load("artifacts/export-tables.json")["tables"]
    for table in matrices:
        with (ROOT / table["output"]).open(newline="", encoding="utf-8") as file:
            rows = list(csv.reader(file))
        expected = [["" if value is None else str(value) for value in row] for row in [table["headers"], *table["rows"]]]
        require(len(rows) == len(expected) and rows[0] == expected[0], f"CSV shape mismatch: {table['output']}")
        for actual, source in zip(rows[1:], [*table["rows"]]):
            require(len(actual) == len(source), "CSV column count mismatch")
            for x, y in zip(actual, source):
                if isinstance(y, (int, float)):
                    require(float(x) == float(y), "Numeric CSV value changed")
                else:
                    require(x == ("" if y is None else y), "Text qualification or source lost in CSV")

    sources = load("data/sources.json")["sources"]
    source_ids = {s["source_id"] for s in sources}
    require(len(source_ids) == len(sources) == len({s["url"] for s in sources}), "Duplicate source ID/URL")
    require(all(set(r["source_ids"]) <= source_ids for r in records), "Broken source join")
    broken = []
    checksum_path = ROOT / "SHA256SUMS"
    text_file_count = 0
    for file in eligible_files():
        if file.suffix not in {".md", ".json", ".csv", ".py", ".mjs", ".tsx"}: continue
        text = file.read_text(encoding="utf-8")
        text_file_count += 1
        forbidden_runtime_strings = ("\ue200" + "genui", "sandbox" + ":/", "/workspace/" + "scratch/")
        require(not any(value in text for value in forbidden_runtime_strings), f"Private/runtime citation leaked: {file.name}")
        require(not re.search(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}", text), f"Credential-like value found: {file.name}")
        if file.suffix == ".md":
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if target.startswith(("https://", "http://", "#", "mailto:")): continue
                relative = unquote(target.split("#", 1)[0])
                target = (file.parent / relative).resolve()
                planned_checksum = args.write_checksums and target == checksum_path
                if relative and not target.exists() and not planned_checksum:
                    broken.append((str(file.relative_to(ROOT)), relative))
    require(not broken, f"Broken local documentation links: {broken}")
    if args.write_checksums:
        checksum_path.write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}\n" for p in eligible_files()))
    if checksum_path.exists():
        for line in checksum_path.read_text().splitlines():
            digest, relative = line.split("  ", 1)
            require(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest, f"File checksum mismatch: {relative}")
    print(f"Verified: {len(records)} teams; {len(matrices[1]['rows'])} person-role rows; {len(sources)} sources; {text_file_count} text files.")
    print("Ranks, denominators, source snapshot, season cutoff, leadership qualifiers, geography, CSV fidelity, source joins, and local links passed.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, AssertionError, KeyError) as error:
        print(f"Verification failed: {error}", file=sys.stderr)
        sys.exit(1)
