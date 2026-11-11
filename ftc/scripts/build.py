#!/usr/bin/env python3
"""Rebuild FTC JSON, CSV, and Markdown offline from curated inputs and captures."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save_json(path, value):
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def save_text(path, value):
    (ROOT / path).write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def index(rows):
    result = {r["team_number"]: r for r in rows}
    if len(result) != len(rows):
        raise ValueError("Duplicate team number in input")
    return result


def urls(value):
    if isinstance(value, str) and value.startswith(("https://", "http://")):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from urls(child)
    elif isinstance(value, list):
        for child in value:
            yield from urls(child)


def md(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def link(label, url):
    return f"[{md(label)}]({url.replace('(', '%28').replace(')', '%29')})" if url else md(label)


def people(record):
    for category in ("adult_leadership", "student_leadership", "public_student_representatives"):
        for person in record.get(category, []):
            yield category, person


def csv_file(path, headers, rows):
    with (ROOT / path).open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(headers)
        writer.writerows(rows)


def main():
    config = load("data/publication.json")
    roster = load("data/roster.json")
    geography = load("data/geography.json")
    leadership = load("data/leadership.json")
    rankings = load("data/rankings.json")
    locations = index(geography["teams"])
    leaders = index(leadership["records"])
    ratings = index(rankings["teams"])
    histories = index(load("artifacts/first/season-history-through-2025.json")["teams"])
    current_histories = index(load("artifacts/first/current-season-new-teams.json")["teams"])
    combined = []
    for team in roster["teams"]:
        number = team["team_number"]
        record = dict(team)
        record.update({"rankings": ratings[number], "geography": locations[number],
                       "season_history": histories[number], "leadership": leaders[number]})
        record["source_urls"] = sorted(set(urls(record)))
        record["source_ids"] = ["FTC-" + hashlib.sha256(u.encode()).hexdigest()[:12] for u in record["source_urls"]]
        combined.append(record)
    combined.sort(key=lambda r: (r["rankings"].get("value") is None,
                                -(r["rankings"].get("value") or 0), r["team_number"]))
    current = []
    for team in roster.get("current_season_only_teams", []):
        number = team["team_number"]
        record = dict(team)
        record.update({"geography": locations[number], "season_history": current_histories[number],
                       "leadership": leaders[number], "ranking_status": "Outside 2025–26 comparison; current-season registration"})
        current.append(record)
    save_json("data/teams.json", {"schema_version": "1.0", "publication": config,
                                 "ranking_method": rankings["method"], "teams": combined,
                                 "current_season_only_teams": current})

    catalog = {}
    for r in combined + current:
        for url in set(urls(r)):
            catalog.setdefault(url, set()).add(r["team_number"])
    for document in (config, geography, leadership, rankings, roster):
        for url in urls(document):
            catalog.setdefault(url, set())
    sources = [{"source_id": "FTC-" + hashlib.sha256(u.encode()).hexdigest()[:12],
                "url": u, "teams": sorted(teams)} for u, teams in sorted(catalog.items())]
    save_json("data/sources.json", {"source_count": len(sources), "sources": sources})

    headers = ["team_number", "team_name", "school_or_organization", "affiliation_type", "city", "state",
               "reference_point", "distance_miles", "geographic_qualification", "season", "ranking_source",
               "ranking_metric", "ranking_value", "world_rank", "world_team_count", "regional_metric_value", "regional_rank",
               "regional_team_count", "regional_population", "ranking_status", "ranking_qualification",
               "official_rookie_year", "recorded_season_count", "recorded_season_start_years",
               "history_qualification", "adult_roles", "student_roles", "other_student_roles",
               "leadership_gaps", "source_urls"]
    rows = []
    role_rows = []
    for r in combined:
        k, g, h, l = (r[key] for key in ("rankings", "geography", "season_history", "leadership"))
        roles = {category: " ; ".join(f"{p['name']}: {p['role']} ({p['season']})" for p in l.get(category, []))
                 for category in ("adult_leadership", "student_leadership", "public_student_representatives")}
        rows.append([r["team_number"], r["team_name"], r["school_or_organization"], r["affiliation_type"],
                     r["city"], r["state"], g["reference"], g["distance_miles"], g["qualification"],
                     config["season_label"], k["source"], k["metric"], k.get("value"), k.get("world_rank"),
                     k.get("world_team_count"), k.get("regional_value"), k.get("regional_rank"), k.get("regional_team_count"),
                     k.get("regional_population"), k["status"], k["qualification"], h["official_rookie_year"],
                     h["recorded_season_count"], ";".join(map(str, h["recorded_seasons_through_cutoff"])),
                     h["history_coverage_note"], roles["adult_leadership"], roles["student_leadership"],
                     roles["public_student_representatives"], l["gap"], " ; ".join(r["source_urls"])])
    for r in combined + current:
        for category, person in people(r["leadership"]):
            role_rows.append([r["team_number"], category, person["name"], person["role"], person["season"],
                              person["evidence_date"], person["evidence_date_basis"],
                              person["evidence_status"], person["notes"], " ; ".join(person["source_urls"])])
    role_headers = ["team_number", "category", "name", "role", "applicable_season", "evidence_date", "evidence_date_basis", "evidence_status", "notes", "source_urls"]
    csv_file("data/teams.csv", headers, rows)
    csv_file("data/leadership.csv", role_headers, role_rows)
    save_json("artifacts/export-tables.json", {"tables": [{"output": "data/teams.csv", "headers": headers, "rows": rows},
                                                           {"output": "data/leadership.csv", "headers": role_headers, "rows": role_rows}]})

    def rank_text(r, prefix):
        value, count = r.get(prefix + "_rank"), r.get(prefix + "_team_count")
        return (f"{value} / {count:,}" if count else str(value)) if value is not None else "Unavailable"

    table = ["| Team | School / community program | Approx. miles | World Best NP OPR | World rank | Region Best NP OPR | Event-region rank | Recorded seasons |",
             "|---|---|---:|---:|---|---:|---|---|"]
    directory = ["# FTC team directory", "", f"**{config['season_label']} · researched {config['research_date']}**", "",
                 rankings["method"]["display_note"], "", "Regional ranks use the population named below. Read the [methodology](methodology.md) and [geographic qualifications](geographic-scope.md).", ""]
    for r in combined:
        k, g, h = r["rankings"], r["geography"], r["season_history"]
        value = f"{k['value']:.2f}" if k.get("value") is not None else "Unavailable"
        regional_value = f"{k['regional_value']:.2f}" if k.get("regional_value") is not None else "Unavailable"
        region_rank = (k.get("regional_code", "") + " " + rank_text(k, "regional")).strip()
        distance_label = f"{g['distance_miles']:.1f}" + (" †" if g['point_type'] == 'town_screening_only' else "")
        table.append(f"| {link(str(r['team_number']) + ' ' + r['team_name'], r['first_team_url'])} | {link(r['school_or_organization'], r.get('school_url'))} | {distance_label} | {value} | {rank_text(k, 'world')} | {regional_value} | {region_rank} | {h['recorded_season_count']} ({', '.join(map(str, h['recorded_seasons_through_cutoff']))}) |")
    directory.extend(table)
    directory.extend(["", "† Town screening point; physical meeting/workshop address remains unconfirmed."])
    for r in combined:
        k, g, h, l = (r[key] for key in ("rankings", "geography", "season_history", "leadership"))
        directory.extend(["", f"## {r['team_number']} · {r['team_name']}", "",
                          f"**{r['school_or_organization']} — {r['city']}, {r['state']}** ({r['affiliation_type']}). {r['notes']}", "",
                          f"**Ranking:** {k['metric']} — {k['status']}. {k['qualification']} " + (link("Ranking source", k.get("source_url")) if k.get("source_url") else ""), "",
                          f"**Geography:** {g['reference']}, {g['distance_miles']:.1f} miles. {g['qualification']}", "",
                          f"**History:** rookie {h['official_rookie_year']}; {h['recorded_season_count']} recorded season entries through 2025. {h['history_coverage_note']}", ""])
        for category, p in people(l):
            directory.append(f"- **{md(p['name'])}:** {md(p['role'])} ({md(p['season'])}). {md(p['notes'])} " + " · ".join(link("Source", u) for u in p["source_urls"]))
        directory.extend(["", f"**Leadership gaps:** {l['gap']}"])
    directory.extend(["", "## Current-season additions", "", "These teams are outside the 2025–26 ranking comparison.", ""])
    for r in current:
        directory.append(f"- {link(str(r['team_number']) + ' ' + r['team_name'], r['first_team_url'])}: {r['school_or_organization']}; rookie {r['season_history']['official_rookie_year']}; {r['geography']['distance_miles']:.1f} miles. {r['notes']} {r['leadership']['gap']}")
    save_text("docs/team-directory.md", "\n".join(directory))
    leader_lines = ["# FTC public leadership evidence", "", "Exact roles and applicable seasons are retained. Partial names and undated self-reports remain qualified. No student captain is inferred from alliance-selection results. See the [structured evidence and dated source catalog](../data/leadership.json).", ""]
    for r in combined + current:
        leader_lines.extend([f"## {r['team_number']} · {r['team_name']}", ""])
        for category, p in people(r["leadership"]):
            leader_lines.append(f"- **{md(p['name'])}** — {md(p['role'])}; {md(p['season'])}; {md(p['evidence_status'])}. {md(p['notes'])} " + " · ".join(link("Source", u) for u in p["source_urls"]))
        leader_lines.extend(["", "**Gaps:** " + r["leadership"]["gap"], ""])
    leader_lines.extend(["## Source evidence dates and qualifications", ""])
    for s in leadership["sources"]:
        leader_lines.append(f"- **{s['id']} — {link(s['title'], s['url'])}**; evidence date: {s['date'] or 'undated'}. {s['notes']}")
    save_text("docs/leadership-findings.md", "\n".join(leader_lines))
    source_lines = ["# FTC source catalog", "", "Source URLs are preserved for inspection; inclusion does not assert that every publisher page is archived locally. Factual captures and response hashes are described in the [artifact inventory](../artifacts/README.md).", "", "| Source ID | URL | Related teams |", "|---|---|---|"]
    source_lines.extend(f"| {s['source_id']} | {link(s['url'], s['url'])} | {', '.join(map(str, s['teams'])) or 'Method / scope'} |" for s in sources)
    save_text("docs/sources.md", "\n".join(source_lines))
    readme = ["# FIRST Tech Challenge around Fort Wayne", "", f"**{config['season_label']} · research date {config['research_date']}**", "",
              "New to robotics? Our [introduction for football and baseball fans](../README.md#new-to-robotics-a-guide-for-football-and-baseball-fans) explains FTC, FRC, alliances, and how to read the ratings. [The REFINERY](https://refineryrobotics.org/) supports local teams; learn how to [find a team or get involved](https://refineryrobotics.org/get-involved/).", "",
              f"{len(combined)} season-rostered teams in the study area, with school/community affiliations, geographic qualifications, recorded FIRST seasons, and public leadership evidence. Current-season additions are listed separately.", "",
              rankings["method"]["display_note"], "", "| Resource | Contents |", "|---|---|",
              "| [Team directory](docs/team-directory.md) | Rankings, schools/programs, distances, seasons, and leadership |",
              "| [Combined JSON](data/teams.json) / [team CSV](data/teams.csv) | Joined facts, sources, and qualifications |",
              "| [Leadership evidence](docs/leadership-findings.md) / [CSV](data/leadership.csv) | Exact adult/student roles, dates, uncertainty, and gaps |",
              "| [Methodology](docs/methodology.md) | Metric, population, season labels, and evidence policy |",
              "| [Geographic scope](docs/geographic-scope.md) | Origin, reference points, boundary exclusions, and census limits |",
              "| [Sources](docs/sources.md) / [artifacts](artifacts/README.md) | URLs, preserved facts, metadata, and reproduction |", "", *table, "",
              "† Town screening point; physical meeting/workshop address remains unconfirmed. Other distances use school/host reference points. FIRST season-entry counts can omit pre-2019 history and do not count only seasons with played matches. A missing ranking or leader is left unavailable rather than inferred.", "",
              "## 2026–27 registrations", "", *[f"- {link(str(r['team_number']) + ' ' + r['team_name'], r['first_team_url'])} — {r['school_or_organization']}; current-season rookie, outside the 2025–26 rankings." for r in current], "",
              "## Rebuild and verify", "", "From the repository root, using Python's standard library:", "", "```bash", "python ftc/scripts/build.py", "python ftc/scripts/verify.py", "python scripts/verify.py", "```", "",
              "A fresh source capture must use a new output filename or directory. Review its metric, season, population, and qualifications before changing the selected publication. See the [artifact inventory](artifacts/README.md).", "", "[Return to both FIRST programs](../README.md)."]
    save_text("README.md", "\n".join(readme))
    print(f"Built FTC: {len(combined)} rostered teams; {len(current)} current-season additions; {len(role_rows)} person-role rows; {len(sources)} source URLs.")


if __name__ == "__main__":
    main()
