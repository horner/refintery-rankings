#!/usr/bin/env python3
"""Build the combined dataset, source catalog, report, and CSV input matrices offline."""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def write_json(path, value):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path, value):
    (ROOT / path).write_text(value.rstrip() + "\n", encoding="utf-8")


def by_team(rows):
    result = {r["team_number"]: r for r in rows}
    if len(result) != len(rows):
        raise ValueError("Duplicate team number")
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
    return f"[{md(label)}]({url.replace('(', '%28').replace(')', '%29')})"


def period(years):
    if len(years) == 1:
        return str(years[0])
    if years == list(range(years[0], years[-1] + 1)):
        return f"{years[0]}–{years[-1]}"
    return ", ".join(map(str, years))


def person_text(person):
    date = person["evidence_date"] or "undated"
    status = person["evidence_status"].replace("_", " ")
    return f"{person['name']}: {person['role']} (evidence: {date}; {status}). {person['notes']}"


def short_person(person):
    date = person["evidence_date"] or "undated"
    status = person["evidence_status"].replace("_", " ")
    return f"**{md(person['name'])}**: {md(person['role'])} ({md(date)}; {md(status)}). {link('Source', person['source_urls'][0])}"


TITLES = {
    "https://refineryrobotics.org/about/": "The REFINERY: Our Story, People & Facility",
    "https://www.pfw.edu/news-center/north-side-robotics-team-boosted-pfw-presence": "Purdue Fort Wayne: North Side robotics team boosted by PFW presence",
    "https://phyxtgears.org/2026/05/15/local-robotics-team-celebrates-20th-season-with-world-championship-appearance/": "PhyXTGears: 2026 season and world championship report",
    "https://video.wfwa.org/video/science-centrals-new-planetarium-snider-robotics-and-arena-dinner-theatre-4j2kgy/": "PBS Fort Wayne: The 260, Snider Robotics interview and transcript, October 2, 2026",
    "https://chargeronline.nacs.k12.in.us/12210/sports/from-worst-to-first-how-indianas-football-program-became-the-nations-best/": "Carroll school newspaper: January 27, 2026 article, Nieng Mang contributor biography",
    "https://wilcoxnewspapers.com/shs-robotics-team-receives-recognition-at-district-meet/": "Wilcox Newspapers: SHS robotics team receives recognition, March 27, 2026",
    "https://www.hometownstations.com/news/allen_county/lima-bean-city-bots-ready-robot-for-first-robotics-competition-buckeye-regional/article_e5d3d483-ada8-4a44-91a8-361777fc6b54.html": "WLIO: Lima Bean City Bots prepare for Buckeye Regional, March 17, 2026",
    "https://www.linkedin.com/in/chriselston": "Chris Elston: public professional profile",
    "https://www.linkedin.com/in/matt-elder-24b8b615a": "Matt Elder: public professional profile",
    "https://www.linkedin.com/in/camelder": "Cameron Elder: public professional profile and historical roles",
    "https://www.linkedin.com/in/m4ttbit": "Matt Arnold: public professional profile and historical role",
    "https://www.instagram.com/4982_olympus_robotics/": "Olympus Robotics: official team Instagram; indexed 2025–26 captain announcement",
    "https://www.instagram.com/snider_robotics9431/": "Snider Robotics: official team Instagram",
    "https://www.instagram.com/walnuthillcatering/": "Walnut Hill Catering & Events: indexed Snider coach identification",
    "https://www.facebook.com/NorthropRobotics/": "Northrop Robotics: official team Facebook, indexed Coach Jacobs mention",
    "https://www.firstindianarobotics.org/about-first-indiana-robotics/board-of-directors/": "FIRST Indiana: Board of Directors and mentor biographies",
    "https://www.waldronspartans.org/live-feed?page_no=66": "Waldron official school feed: January 2024 Coach Fuller announcement",
    "https://www.waldronspartans.org/live-feed?page_no=67": "Waldron official school feed: December 2023 Mike Fuller contact announcement",
    "https://www.trine.edu/news/2019/east-noble-robotics.aspx": "Trine University: East Noble robotics program and Shawn Kimmel",
    "https://podcasts.apple.com/ma/podcast/eric-cale-and-robotics/id1773140582?i=1000760060708": "Madison-Grant Live Wire: Eric Cale and Robotics, April 7, 2026",
    "https://resources.finalsite.net/images/v1770749036/fwcsk12inus/v2dggvv52hkh9sfiqsme/2-9-26Presentation_Roboticshighschool.pdf": "FWCS board presentation: FIRST Robotics high schools, February 9, 2026, pages 2 and 7",
    "https://resources.finalsite.net/images/v1685982230/fwcsk12inus/us2rusjsudqci2p1ltxv/03132023.pdf": "FWCS board minutes: March 13, 2023, Dennis Fisher coaching identification",
    "https://static1.squarespace.com/static/5dc440cbaed3360b099cc5e8/t/68e97523a86b466f4093381a/1760130339609/Regular%2BMeeting%2BMinutes%2B09.08.2025.pdf": "Fairmount Town Council minutes: September 8, 2025, Argyll Attack presentation",
    "https://www.21alivenews.com/2024/04/13/snider-robotics-club-prepares-compete-world-championship/": "21Alive: Snider world championship preparation; displayed publication April 12, 2024",
    "https://www.the74million.org/article/building-a-mindset-amp-lab-makes-entrepreneurship-work-skills-its-mission/": "The 74: Amp Lab feature, March 25, 2026, Alfy Krider identification",
    "https://www.kpcnews.com/newssun/article_01fef033-f9cb-525e-82e8-676e717dee03.html": "KPC News Sun: East Noble robotics team demonstrates real-world learning",
    "https://www.euvolution.com/prometheism-transhumanism-posthumanism/robotics/en-robotics-team-demonstrates-real-world-learning-news-sun-kpcnews-com-kpcnews-com/": "Republished KPC News Sun report: East Noble coaches, May 2024",
    "https://huntingtonnhs.ss13.sharpschool.com/get_involved/clubs/robotics": "Huntington North High School: Robotics club page",
    "https://huntingtonrobotics.org/faq/": "Huntington robotics: community participation FAQ",
}


def title(url):
    if url in TITLES:
        return TITLES[url]
    host = urlparse(url).netloc
    path = unquote(urlparse(url).path)
    if "geocoding.geo.census.gov" in host:
        return "U.S. Census Bureau: geocoder result or method documentation"
    if "nces.ed.gov" in host:
        return "NCES: official school coordinate data or school map"
    if "statbotics.io/team/" in url:
        return f"Statbotics 2026 profile: team {path.split('/')[2]}"
    if "frc-events.firstinspires.org" in host and "/team/" in path:
        return f"FIRST {'2026 team page' if path.startswith('/2026/') else 'team history'}: {path.rsplit('/', 1)[-1]}"
    return host + (": " + path.strip("/").replace("-", " ") if path.strip("/") else "")


def main():
    config = read("data/publication.json")
    roster = read("data/roster.json")["teams"]
    baseline = by_team(read("data/research-baseline.json")["teams"])
    people = by_team(read("data/leadership.json"))
    geography = read("data/geography.json")
    places = {r["location_id"]: r for r in geography["locations"]}
    geo = by_team(geography["teams"])
    histories = by_team(read(config["first_history_artifact"])["teams"])
    snap = config["statbotics_snapshot_directory"]
    stats = {r["team"]: r for r in read(snap + "/team-years-2026-subset.json")["team_years"]}
    snapshot_metadata = read(snap + "/metadata.json")
    expected_ids = {r["team_number"] for r in roster}
    for label, items in [("baseline", baseline), ("leadership", people), ("geography", geo), ("FIRST", histories), ("Statbotics", stats)]:
        if set(items) != expected_ids:
            raise ValueError(f"{label} team coverage differs from the curated roster")
    combined = []
    for r in roster:
        number = r["team_number"]
        stat = stats[number]
        ranks = stat["epa"]["ranks"]
        history = histories[number]
        expected = baseline[number]
        actual = (stat["epa"]["total_points"]["mean"], ranks["state"]["rank"], ranks["total"]["rank"])
        if actual != (expected["epa_mean"], expected["state_rank"], expected["world_rank"]):
            raise ValueError(f"Ranking change requires review: {number}")
        if history["recorded_seasons_through_cutoff"] != expected["recorded_seasons"]:
            raise ValueError(f"Season-history change requires review: {number}")
        if history["official_rookie_year"] != expected["official_rookie_year"]:
            raise ValueError(f"Rookie-year change requires review: {number}")
        record = dict(r)
        record["rankings"] = {
            "season": 2026, "source_url": snapshot_metadata["source"]["url"],
            "snapshot_last_modified_utc": config["rankings_last_modified_utc"],
            "epa_mean": actual[0], "epa_standard_deviation": stat["epa"]["total_points"]["sd"],
            "state_rank": actual[1], "state_team_count": ranks["state"]["team_count"],
            "world_rank": actual[2], "world_team_count": ranks["total"]["team_count"],
            "source_artifact": snap + "/team-years-2026-subset.json",
        }
        record["season_history"] = history
        record["leadership"] = people[number]
        record["geography"] = dict(geo[number], location=places[geo[number]["location_id"]])
        combined.append(record)
    combined.sort(key=lambda r: (r["scope_group"] != "northeast_indiana", -r["rankings"]["epa_mean"], r["team_number"]))

    registry = {}
    def register(url, category, team=None):
        if not url.startswith(("https://", "http://")):
            raise ValueError(f"Not a source URL: {url}")
        if url not in registry:
            registry[url] = {"source_id": "S-" + hashlib.sha256(url.encode()).hexdigest()[:10], "title": title(url), "url": url, "publisher_domain": urlparse(url).netloc, "categories": set(), "teams": set()}
        registry[url]["categories"].add(category)
        if team is not None:
            registry[url]["teams"].add(team)
    for r in combined:
        for category, section in [("school and team", {k: r[k] for k in ("school_url", "first_team_url", "first_history_url", "statbotics_url", "affiliation_source_urls")}), ("rankings", r["rankings"]), ("leadership", r["leadership"]), ("geography", r["geography"])]:
            for u in urls(section): register(u, category, r["team_number"])
    for category, section in [("geographic method", geography), ("Statbotics provenance", snapshot_metadata), ("linked documents", read("artifacts/source-manifests/documents.json"))]:
        for u in urls(section): register(u, category)
    sources = []
    for record in sorted(registry.values(), key=lambda r: (r["publisher_domain"], r["url"])):
        sources.append(dict(record, categories=sorted(record["categories"]), teams=sorted(record["teams"])))
    for r in combined:
        r["source_ids"] = sorted({registry[u]["source_id"] for u in urls(r) if u in registry})
    write_json("data/teams.json", {"schema_version": "1.0", "publication": config, "distance_origin": geography["origin"], "distance_method": geography["scope"], "teams": combined})
    write_json("data/sources.json", {"schema_version": "1.0", "research_date": config["research_date"], "source_count": len(sources), "note": "Source links and per-person access limitations are preserved. This catalog does not assert that every linked page is currently accessible or archived locally.", "sources": sources})

    team_headers = ["team_number", "team_name", "school_or_organization", "city", "state", "epa_mean", "state_rank", "state_team_count", "world_rank", "world_team_count", "official_rookie_year", "first_recorded_season", "recorded_season_count", "recorded_seasons", "distance_miles_approx", "location_basis", "adult_leaders", "student_leaders", "other_representatives", "leadership_gaps", "school_url", "statbotics_url", "first_history_url", "source_urls", "ranking_snapshot_utc", "research_date", "registered_without_competition_years", "affiliation_notes"]
    team_rows = []
    person_headers = ["team_number", "category", "name", "documented_role", "evidence_date", "date_precision", "evidence_status", "qualifying_notes", "source_urls"]
    person_rows = []
    for r in combined:
        h, rank, p, g = r["season_history"], r["rankings"], r["leadership"], r["geography"]
        team_rows.append([r["team_number"], r["team_name"], r["school_or_organization"], r["city"], r["state"], rank["epa_mean"], rank["state_rank"], rank["state_team_count"], rank["world_rank"], rank["world_team_count"], h["official_rookie_year"], h["first_recorded_season"], h["recorded_season_count"], ";".join(map(str, h["recorded_seasons_through_cutoff"])), g["display_distance_miles"], g["inclusion_basis"], " | ".join(map(person_text, p["adults"])), " | ".join(map(person_text, p["students"])), " | ".join(map(person_text, p["other_representatives"])), " | ".join(p["gaps"]), r["school_url"], r["statbotics_url"], r["first_history_url"], " | ".join(sorted(set(urls(r)))), config["rankings_last_modified_utc"], config["research_date"], ";".join(map(str, h["seasons_explicitly_registered_without_competition"])), r["affiliation_notes"]])
        for category in ("adults", "students", "other_representatives"):
            for person in p[category]:
                person_rows.append([r["team_number"], category, person["name"], person["role"], person["evidence_date"], person["date_precision"], person["evidence_status"], person["notes"], " | ".join(person["source_urls"])])
    write_json("artifacts/export-tables.json", {"schema_version": "1.0", "tables": [{"name": "Teams", "output": "data/teams.csv", "headers": team_headers, "rows": team_rows}, {"name": "Leadership", "output": "data/leadership.csv", "headers": person_headers, "rows": person_rows}]})

    table_header = "| School / organization | FRC team | Approx. miles | FIRST seasons through 2026 | EPA | State EPA rank | World EPA rank |\n|---|---|---:|---|---:|---:|---:|"
    def rankings_table(group):
        lines = [table_header]
        for r in combined:
            if r["scope_group"] != group: continue
            h, k, g = r["season_history"], r["rankings"], r["geography"]
            count = f"{h['recorded_season_count']} ({period(h['recorded_seasons_through_cutoff'])})"
            lines.append("| " + " | ".join([link(r["school_or_organization"], r["school_url"]), link(str(r["team_number"]) + " " + r["team_name"], r["statbotics_url"]), f"{g['display_distance_miles']:.1f}", link(count, r["first_history_url"]), f"{k['epa_mean']:.2f}", f"{r['state']} {k['state_rank']} / {k['state_team_count']}", f"{k['world_rank']:,} / {k['world_team_count']:,}"]) + " |")
        return "\n".join(lines)
    leadership_lines = ["| School / program (team) | Documented adult roles | Documented student leadership | Other documented representatives |", "|---|---|---|---|"]
    for r in combined:
        p = r["leadership"]
        adults = "<br><br>".join(map(short_person, p["adults"])) or "Individual adult lead not verified."
        students = "<br><br>".join(map(short_person, p["students"])) or "Student captain not verified."
        representatives = "<br><br>".join(map(short_person, p["other_representatives"])) or "No additional representative documented."
        leadership_lines.append(f"| {md(r['school_or_organization'])} ({r['team_number']}) | {adults} | {students} | {representatives} |")
    report = f"""# Team directory and ranking snapshot

Research date: **{config['research_date']}**. Rankings: **2026 season, official cache last modified June 12, 2026 at 02:51:19 UTC**. This is a frozen snapshot; October retrieval does not make the rankings October-current.

The tables cover the original **17 FRC teams: 13 Indiana and 4 nearby Michigan/Ohio teams**. School names link to the school or community program. Team numbers link to Statbotics. Season counts link to FIRST. See [source catalog](sources.md), [methodology](methodology.md), [geography](geographic-scope.md), and [detailed leadership evidence](leadership-findings.md).

## Indiana teams

{rankings_table('northeast_indiana')}

## Nearby Michigan and Ohio teams

{rankings_table('nearby_border')}

## Dates, geography, and season counts

Distances use the documented Citizens Square downtown origin and linked school/host reference points. They are approximate straight-line miles. Team 1720 uses a Matthews town reference because its physical workshop was not confirmed. Lima 3777 and Waldron 6556 are close to the boundary, at 58.8 and 58.6 miles under this convention. The underlying coordinates and assumptions are preserved in [geography.json](../data/geography.json).

Recorded seasons include registered years without matches and exclude 2027. They are not a count of uninterrupted on-field competition years. East Noble 8431 has two recorded seasons (2025–26), and 8432 has one (2026), although both official rookie years are 2020. Community programs retain their community identity rather than being assigned an exclusive school.

## Adult and student leadership

Roles below are the roles documented by the cited sources. Evidence dates are not appointment dates. Historical roles, undated professional profiles, partial names, and indexed announcements retain their evidence status. No row is a blanket confirmation of a current 2026–27 head coach or captain. Representatives, outreach officers, overall captains, assistant captains, and drive-team captains are distinct. The final column includes identified student representatives and people whose adult/student status is unknown; those entries do not establish captain appointments.

{chr(10).join(leadership_lines)}

The [complete leadership findings](leadership-findings.md) include all qualifying notes, source-access limits, historical people, public representatives, and unresolved gaps. [Leadership JSON](../data/leadership.json) and [CSV](../data/leadership.csv) retain every person-role record, including people whose student/adult status is not established, such as Ava Stanley. Homestead's Jasroop/Jake announcement is retained as a first-name-only captain/assistant-captain pair. The publication conservatively leaves the individual title assignment unconfirmed.
"""
    write_text("docs/team-directory.md", report)
    source_lines = ["# Source catalog", "", f"This catalog contains **{len(sources)} unique source URLs** used for team identity, school affiliation, rankings, season history, geography, and leadership. It was assembled from the October 22, 2026 research and preservation work.", "", "The per-person records contain evidence dates, exact roles, and access qualifications. Several social pages and professional profiles were available only through indexed public text. A link is not a claim that a complete local copy exists. The [linked-document manifest](../artifacts/source-manifests/documents.json) records hashes for the two principal PDFs.", "", "| Source ID | Source | Used for | Included teams |", "|---|---|---|---|"]
    for s in sources:
        source_lines.append(f"| {s['source_id']} | {link(s['title'], s['url'])} | {md(', '.join(s['categories']))} | {', '.join(map(str, s['teams'])) or 'Method / scope'} |")
    write_text("docs/sources.md", "\n".join(source_lines))
    readme = f"""# FIRST Robotics teams around Fort Wayne

[Explore the NEI Robotics standings and season preview](https://horner.github.io/refintery-rankings/) — browse all 13 regional FRC teams on desktop or phone, follow the 2026–27 calendar, explore team profiles and the DNF invitation for schools ready to start a team, and open the research sources. The separate [Top 10 display](broadcast/dist/top10.html) provides a large-screen EPA ranking, replay previews, optional cycling, and PNG exports. Public access; no sign-in required.

## New to robotics? A guide for football and baseball fans

If you follow football or baseball, much of competitive robotics will feel familiar: a team has an identity, students and coaches, practices, scouting, a season, and tournaments. Students design, build, program, and drive the robot their team brings to the field. Success takes preparation and contributions from the whole team, including the people organizing events, raising funds, and keeping equipment ready.

**FIRST Tech Challenge (FTC)** and **FIRST Robotics Competition (FRC)** are two robotics sports under the FIRST umbrella. They share engineering and teamwork, while using different robots, fields, and game rules. Both are full competition programs, with overlapping student ages and their own championships.

Football and baseball divide schools into enrollment-based classes. FTC and FRC describe different robotics competition formats, chosen by schools and community teams rather than assigned by school enrollment. A large school can compete in FTC, a small school can compete in FRC, and a school can offer both.

| What to know | FTC | FRC |
|---|---|---|
| Students | Grades 7–12; ages 12–18 | Grades 9–12; ages 14–18 |
| Robots and playing space | Compact robots and a smaller playing field; reusable robot kits | Larger, industrial-sized robots and a larger playing field |
| New game announced | September | January |
| What students do | Build, code, drive, scout, organize, and work with mentors | Build, code, drive, scout, organize, and work with mentors |

Official program guides: [FIRST Tech Challenge](https://www.firstinspires.org/programs/ftc/) and [FIRST Robotics Competition](https://www.firstinspires.org/programs/frc/).

One difference from football or baseball is the **alliance**: several robotics teams join forces for a match. During qualification matches, partners change, so a team you face in one match may be your partner in another. Students prepare strategies with other teams and help one another keep robots running, even while competing for tournament success.

Read the ratings here as you might read **yards per play in football or batting average in baseball**: a useful view of performance alongside the win column and championship results. FRC's EPA and FTC's OPR estimate robot scoring contributions; they do not measure every engineering achievement, student contribution, or community impact. The two programs use different games and models, so an FTC OPR number and an FRC EPA number cannot be compared directly.

## Meet The REFINERY

[The REFINERY](https://refineryrobotics.org/) helps youth robotics teams in Fort Wayne and Northeast Indiana with funding, parts, tools, facilities, and training. Think of the shared support behind a sports program: access to practice space, equipment, and experienced people helps teams develop. Learn [how The REFINERY supports teams](https://refineryrobotics.org/what-we-do/), [meet its teams and people](https://refineryrobotics.org/about/), or [find a team, volunteer, partner, or help start a program](https://refineryrobotics.org/get-involved/).

## Explore the local teams

[Responsive site, Top 10 display, and media package](broadcast/README.md): full regional FRC standings, a separate large-screen Top 10, team profiles, FTC features, and a source-aware press kit. See the same guide for a local preview that leaves the publication unchanged.

Research directories for two FIRST programs within 60 straight-line miles of Citizens Square in downtown Fort Wayne. Each program retains its own season, ranking metric, evidence, and qualifications.

| Program | Season | Directory and downloads | Ranking metric |
|---|---|---|---|
| FIRST Robotics Competition (FRC) | 2026 | [FRC directory](docs/team-directory.md), [JSON](data/teams.json), [CSV](data/teams.csv) | Statbotics EPA; June 12, 2026 snapshot |
| FIRST Tech Challenge (FTC) | 2025–26 DECODE | [FTC research](ftc/README.md), [directory](ftc/docs/team-directory.md), [JSON](ftc/data/teams.json), [CSV](ftc/data/teams.csv) | FTCScout peak event non-penalty OPR; dated capture |

Read each program's methodology for the details behind its ratings. FTC's current-season additions and teams without ranking data are identified separately.

## FRC research

School-linked **2026 Statbotics rankings, recorded FIRST seasons, and public coach/student leadership evidence** for 17 FRC teams in the Fort Wayne study area: 13 Indiana teams and four nearby Michigan/Ohio teams.

**Research date:** October 22, 2026. **Ranking snapshot:** June 12, 2026, 02:51:19 UTC. Rankings are preserved historical values, not a live leaderboard.

## Read and download

| Resource | Contents |
|---|---|
| [Team directory](docs/team-directory.md) | School and team links, EPA/state/world ranks, seasons, distances, adult and student roles |
| [Combined JSON](data/teams.json) | Complete joined dataset, including qualifications, evidence URLs, geographic points, and snapshot metadata |
| [Team CSV](data/teams.csv) | One row per team; 17 rows with explicit source and qualification columns |
| [Leadership CSV](data/leadership.csv) | One row per person-role record; {len(person_rows)} rows with dates, status, notes, and sources |
| [Leadership findings](docs/leadership-findings.md) | Detailed source evidence, historical roles, captain/representative distinctions, and gaps |
| [Source catalog](docs/sources.md) / [JSON](data/sources.json) | {len(sources)} unique source URLs |
| [Methodology](docs/methodology.md) | Metric definitions, scope, dates, affiliations, and inclusion rules |
| [Geographic verification](docs/geographic-scope.md) | Documented origin, source coordinates, distance calculations, and exclusions |
| [Statbotics provenance](docs/statbotics-provenance.md) | Official cache, exact source fields, freshness limit, and reproduction instructions |
| [Artifact inventory](artifacts/README.md) | Preserved raw response, extracted facts, linked PDFs, source code, and checksums |

## Indiana snapshot

{rankings_table('northeast_indiana')}

## Nearby Michigan and Ohio snapshot

{rankings_table('nearby_border')}

## How to interpret the data

- EPA describes estimated robot scoring performance in the 2026 game. State and world ranks are copied directly from the preserved Statbotics response. Denominators are included.
- The 60-mile rule uses straight-line distance from Citizens Square in downtown Fort Wayne to a documented school/host point. Team 1720 remains a town-based screening result. Lima and Waldron are near the boundary; see the geographic qualifications before changing the origin or reference facilities.
- “Years in FIRST” means recorded season entries through 2026, including registered pandemic years with no matches. Future 2027 entries are excluded. East Noble 8431 and 8432 have official rookie year 2020 but recorded histories beginning in 2025 and 2026.
- Leadership records carry exact roles and evidence dates. Most student evidence relates to 2025–26 or the 2026 competition season. Unverified head coaches, partial names, historical captains, indexed sources, and other gaps remain visible.
- PhyXTGears and Lima are community programs. Huntington's record retains its high-school connection and county 4-H identity.

## Rebuild and verify

The research-only analysis build and checks use Python 3.10+ and the standard library. The complete site build, including its HTML page generator, requires **Python 3.12+**. Builds run offline against the committed captures. CSV serialization has a Node standard-library mode; the initial CSV authoring also used the spreadsheet artifact runtime.

```bash
python scripts/build.py
node scripts/export_csv.mjs --stdlib
python ftc/scripts/build.py
python ftc/scripts/verify.py
python broadcast/scripts/build.py
python broadcast/scripts/verify.py
python scripts/verify.py
```

Use a Python 3.12+ interpreter for the sequence above. To review the resulting site locally without publishing, run `python3 -m http.server 8765 --bind 127.0.0.1 --directory broadcast/dist` and open `http://127.0.0.1:8765/`. The [Pages workflow](.github/workflows/pages.yml) deploys pushes to `main`; local builds and previews do not publish. Use this local workflow to review a change before deployment.

To record fresh evidence without overwriting these captures:

```bash
python scripts/fetch_first_history.py --through 2026 --output /tmp/first-history-new.json
python scripts/capture_documents.py --output /tmp/linked-documents-new.json
python scripts/fetch_statbotics.py --help
```

The Statbotics preservation script creates dated capture directories and compares fresh results with the frozen baseline. See its [documented commands](docs/statbotics-provenance.md). A new retrieval does not silently update the published dataset: review the result and explicitly change `data/publication.json` and the baseline when appropriate.

## Keeping results and the calendar current

FRC results and the event calendar refresh from The Blue Alliance and FTCScout with [`scripts/fetch_tba.py`](scripts/fetch_tba.py) and [`scripts/fetch_calendar.py`](scripts/fetch_calendar.py), by hand or every Monday through the [refresh workflow](.github/workflows/refresh-data.yml), which opens a pull request for review. The Blue Alliance key is **not set yet**: copy [`tba.env.example`](tba.env.example) to `tba.env` locally, or add a `TBA_AUTH_KEY` repository secret. Full setup: [docs/tba-api.md](docs/tba-api.md).

## Contributing corrections

For a coach, captain, or representative correction, supply the team number, exact role, applicable season, and a public school/team source. Add the new evidence with its date; retain historical evidence as historical. Update the curated input files, rebuild the exports, and verify them. A student's quote or an award nomination alone does not establish a captain title.

Source documents remain linked to their publishers. The repository preserves factual extracts and the official Statbotics data response; third-party source-code attribution is included. See [third-party notices](THIRD_PARTY_NOTICES.md).
"""
    write_text("README.md", readme)
    print(f"Built {len(combined)} teams, {len(person_rows)} person-role rows, and {len(sources)} unique sources.")


if __name__ == "__main__":
    main()
