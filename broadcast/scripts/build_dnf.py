#!/usr/bin/env python3
"""Build the invitation directory from frozen school, team, and leader evidence.

One row represents a physical school/campus, not a district or a FIRST team.
This module does not turn a missing roster match into proof of team absence.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parents[1]
RESEARCH = HERE / "data/dnf-research"


def load(name):
    return json.loads((RESEARCH / name).read_text())


def normalized(value):
    value = str(value or "").casefold().replace("saint", "st")
    value = re.sub(r"\b(?:schools?|district)\b", "", value)
    return re.sub(r"[^a-z0-9]", "", value)


def web_url(value):
    value = str(value or "").strip()
    if value.startswith(("http://", "https://")):
        return value
    if value and "." in value and " " not in value:
        return "https://" + value
    return None


def school_label(value):
    return value.title() if value == value.upper() else value


def build_dnf():
    universe = load("school-universe.json")
    team_screen = load("team-screen.json")
    school_states = {school["id"]: school["state"] for school in universe["schools"]}
    leader_records = []
    for name in ("leaders.json", "leaders-private-directory-root.json", "leaders-private-root.json", "leaders-private-border.json", "leaders-private-universe.json", "leaders-private-border-supplements.json"):
        if (RESEARCH / name).exists():
            evidence = load(name)
            leader_records.extend(evidence["records"])
            leader_records.extend(evidence.get("schoolRecords", []))
    operating_checks = {}
    normalized_leaders = []
    for record in leader_records:
        if "leaderName" in record:
            operating_checks[record["id"]] = record
            published = {"name": record["leaderName"], "role": record["leaderRole"], "sourceUrl": record["leaderSourceUrl"]}
            if not published["name"] and record.get("otherLeader"):
                published = record["otherLeader"]
            record = {**record, **published, "schoolId": record["id"], "state": school_states.get(record["id"], "IN"), "website": record.get("schoolUrl"), "verifiedCurrent": bool(published["name"] and record.get("currentSchoolSiteLocated")), "evidence": record.get("note", ""), "schoolYear": "Current published source"}
        normalized_leaders.append(record)
    leader_records = normalized_leaders

    def leader_for(school):
        matches, sites = [], []
        identifiers = {str(x) for x in [school["id"], school.get("ncesId"), *school.get("aliasesNcesIds", [])] if x}
        for record in leader_records:
            if record.get("state") != school["state"]:
                continue
            priority = 0
            if str(record.get("schoolId")) in identifiers or str(record.get("ncesId")) in identifiers:
                priority = 100
            elif record.get("stateSchoolId") and record["stateSchoolId"] == school.get("stateSchoolId"):
                priority = 95
            elif normalized(school["name"]) in {normalized(s) for s in [record.get("schoolName"), *record.get("schoolNames", [])] if s}:
                priority = 90
            elif school.get("leaId") and record.get("leaId") == school["leaId"]:
                priority = 85
            elif school.get("district") and normalized(record.get("districtName")) == normalized(school["district"]):
                priority = 80
            if priority:
                if web_url(record.get("website")):
                    sites.append((priority, record))
                if record.get("name"):
                    matches.append((bool(record.get("verifiedCurrent")), priority, record))
        if not matches:
            return None, max(sites, key=lambda row: row[0])[1] if sites else None
        record = max(matches, key=lambda row: row[:2])[2]
        return {"name": record["name"], "role": record["role"], "sourceUrl": record["sourceUrl"], "evidenceLabel": "Current published source" if record.get("verifiedCurrent") else record.get("schoolYear", "Dated directory"), "verifiedCurrent": bool(record.get("verifiedCurrent")), "evidence": record.get("evidence", "")}, record

    def team_match(school):
        identifiers = {str(x) for x in [school["id"], school.get("ncesId"), *school.get("aliasesNcesIds", [])] if x}
        for record in team_screen["positiveSchoolAffiliations"]:
            if record["state"] != school["state"]:
                continue
            if identifiers.intersection(str(x) for x in record.get("ncesIds", [])) or normalized(school["name"]) in {normalized(x) for x in [record["schoolName"], *record.get("aliases", [])]}:
                return record
        return None

    facility_reasons = {row["id"]: row["reason"] for row in load("facility-exclusions.json")["schools"]}
    schools, excluded, review, facilities = [], [], [], []
    for school in universe["schools"]:
        leader, leader_source = leader_for(school)
        primary = next((web_url(x) for x in school["sourceUrls"] if web_url(x)), "https://nces.ed.gov/programs/edge/Geographic/SchoolLocations")
        row = {"id": school["id"], "ncesId": school.get("ncesId"), "name": school_label(school["name"]), "state": school["state"], "city": school["city"].title(), "county": school["county"], "district": (leader_source or {}).get("districtName") or school.get("district") or "Independent school", "sector": "Private" if school["sector"] == "private" else "Charter" if school.get("charter") else "Public", "latitude": school["latitude"], "longitude": school["longitude"], "distanceMiles": school["distanceMiles"], "gradesLow": school["gradesLow"], "gradesHigh": school["gradesHigh"], "schoolType": school["schoolType"], "schoolUrl": web_url(school.get("schoolUrl")) or web_url((leader_source or {}).get("website")) or primary, "leader": leader, "sourceUrls": school["sourceUrls"], "schoolDirectoryYear": school["characteristicsYear"]}
        if operating_checks.get(school["id"], {}).get("currentSchoolSiteLocated") is False:
            row["schoolStatusNote"] = "2023–24 directory record; current campus status to confirm."
        match = team_match(school)
        if school["id"] in facility_reasons:
            row["teamClassification"] = "exclude-secure-or-residential-facility"
            row["teamNote"] = facility_reasons[school["id"]]
            facilities.append(row)
        elif match:
            row["teamClassification"] = match["classification"]
            row["teamNote"] = match["note"]
            row["teamEvidence"] = match.get("teamEvidence", [])
            row["additionalSources"] = match.get("additionalSources", [])
            (excluded if match["classification"] == "exclude-active/recent" else review).append(row)
        else:
            row["teamClassification"] = "no-school-affiliation-verified-in-roster-screen"
            schools.append(row)
    for rows in (schools, excluded, review, facilities):
        rows.sort(key=lambda row: (row["name"].casefold(), row["state"], row["id"]))
    result = {"asOf": "2026-10-22", "title": "DNF — Did Not Field. Yet.", "contactEmail": "info@refineryrobotics.org", "interestPage": "https://refineryrobotics.org/get-involved/#start-or-host-a-team", "resourceUrl": "https://refineryrobotics.org/what-we-do/", "methodologyUrl": "dnf-methodology.md", "origin": universe["origin"], "radiusMiles": 60, "qualification": "The schools below have no school-affiliated FTC or FRC team verified in our dated public-source review. DNF is an invitation to join the lineup. A new team, an unlisted affiliation, or participation in another robotics program may already exist.", "scopeNote": "Physical public, charter, and private campuses offering any of grades 9–12 within 60 straight-line miles of Citizens Square, downtown Fort Wayne, including Ohio and Michigan. School locations come from NCES and documented state/site supplements; directory years vary. Distance is tested before rounding. Older private-school records needing current campus confirmation are marked. Statewide virtual-school offices and adult-only diploma centers are excluded. Former teams and documented community-team connections are listed separately for follow-up.", "schools": schools, "reviewSchools": review, "excludedSchools": excluded, "facilitySchools": facilities, "universeCount": len(universe["schools"]), "scopeReviewCount": len(universe.get("reviewSchools", [])), "counts": {"invited": len(schools), "existingTeams": len(excluded), "affiliationsToConfirm": len(review), "facilitiesNotInvited": len(facilities), "leadersNamed": sum(bool(row["leader"]) for row in schools), "byState": dict(Counter(row["state"] for row in schools))}}
    (HERE / "data/dnf.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    write_methodology(result, universe, team_screen)
    return result


def write_methodology(data, universe, team_screen):
    lines = ["# DNF — Did Not Field. Yet.", "", "A school invitation list, checked October 22, 2026. No school or superintendent was contacted, and no interest response is inferred.", "", "## What this list means", "", data["qualification"], "", data["scopeNote"], "", "The list describes school affiliations in FIRST Tech Challenge and FIRST Robotics Competition. It does not say a school has no STEM activities, no robotics of any kind, or no students on independent community teams. No inference is made about a superintendent’s support for robotics.", "", f"The campus universe contains {data['universeCount']} schools: {len(data['schools'])} invitations, {len(data['excludedSchools'])} with current/recent team affiliations, and {len(data['reviewSchools'])} with former-team or community connections to confirm. {data['counts']['leadersNamed']} invitation rows have a named superintendent or school leader; the others retain an explicit unverified field.", "", "## Geography and school coverage", "", universe["method"], "", *["- " + note for note in universe["scopeNotes"]], "", "## Team screening", "", *["- " + note for note in team_screen["method"]], "", "Current/recent team-affiliated schools are omitted from the invitation table even when a registration has no match statistics. The screening includes newer registrations and cross-border teams, and preserves named community participants and former teams below.", "", "## Leadership", "", "Names retain their published roles. A private-school principal or head is not relabeled superintendent. Current official district/school pages take precedence over older directories. Rows using the Indiana 2025–26 directory retain that year rather than claiming a verified 2026–27 appointment. The raw research files and offline join code are [in the repository](https://github.com/horner/refintery-rankings/tree/main/broadcast/data/dnf-research).", "", "## The first step", "", "Say you’re interested. [The REFINERY’s team-starting inquiry](https://refineryrobotics.org/get-involved/#start-or-host-a-team) and email drafts from the directory start a conversation; they do not enroll a school or commit it to a budget. [Published support](https://refineryrobotics.org/what-we-do/) includes program selection, organizational planning, mentor development, technical training, parts, tools and practice access. Launch support focuses on the 12-county Northeast Indiana region; border schools can ask about shared resources and connections."]
    for title, rows in [("Invitation directory", data["schools"]), ("Former teams and community connections to confirm", data["reviewSchools"]), ("Current/recent affiliations — held out of DNF", data["excludedSchools"]), ("Secure or residential facilities — not invited", data["facilitySchools"])]:
        lines.extend(["", "## " + title, "", "| School | District / leader | Miles | Evidence |", "|---|---|---:|---|"])
        for row in rows:
            leader = row["leader"]
            person = f"{leader['name']} — {leader['role']} ({leader['evidenceLabel']}). [Leader source]({leader['sourceUrl']})" if leader else "Leader name not verified."
            evidence = f"[School/location]({row['sourceUrls'][0]}). " + row.get("teamNote", "No school-affiliated FTC/FRC team verified in the source screen.") + " " + row.get("schoolStatusNote", "")
            for team in row.get("teamEvidence", []):
                evidence += f" [{team['program']} {team['teamNumber']} / {team['season']}]({team['sourceUrl']})"
            for source in row.get("additionalSources", []):
                evidence += f" [Affiliation source]({source['sourceUrl']})"
            lines.append(f"| {row['name']} · {row['city']}, {row['state']} | {row['district']}. {person} | {row['distanceMiles']:.1f} | {evidence} |")
    lines.extend(["", "## Other scope decisions", "", "These records were reviewed separately rather than silently counted as physical high-school campuses:", ""])
    for row in universe.get("reviewSchools", []):
        lines.append(f"- {row['name']} ({row['state']}): {row['scopeClass']}. {row.get('scopeNote', '')} [Source]({row['sourceUrls'][0]})")
    (HERE / "dist/dnf-methodology.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    print(build_dnf()["counts"])
