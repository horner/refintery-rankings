#!/usr/bin/env python3
"""Offline checks of close-match selections against preserved FIRST/API evidence.

This verifier reads the raw schedule/FTCScout captures rather than trusting the
builder's selected/absoluteClosest fields. Network access is never required.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
RESEARCH = HERE / "data/match-research"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError("Match highlights: " + message)


def digest(path, expected):
    require(path.is_file(), f"missing preserved source {path.name}")
    require(hashlib.sha256(path.read_bytes()).hexdigest() == expected,
            f"source SHA-256 differs: {path.name}")


class Node:
    def __init__(self, tag="", attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    def all(self, tag=None):
        for child in self.children:
            if isinstance(child, Node):
                if tag is None or child.tag == tag:
                    yield child
                yield from child.all(tag)

    def text(self):
        return " ".join(" ".join(c.text() if isinstance(c, Node) else c
                                 for c in self.children).split())


class SourceHTML(HTMLParser):
    """Small read-only tree sufficient for the preserved FIRST result tables."""
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
            "meta", "param", "source", "track", "wbr"}

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(Node(tag, attrs))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, text):
        self.stack[-1].children.append(text)


def event_dates(text):
    match = re.fullmatch(r"([A-Za-z]+) (\d+)(?: to (?:([A-Za-z]+) )?(\d+))?, (\d{4})", text)
    require(match is not None, f"unrecognized FIRST event date {text!r}")
    month, start, end_month, end, year = match.groups()
    def iso(m, d):
        return datetime.strptime(f"{m} {d} {year}", "%B %d %Y").date().isoformat()
    return iso(month, start), iso(end_month or month, end or start)


def frc_population(record, cutoff):
    number = record["team"]
    path = RESEARCH / "frc-sources" / f"team-{number}.html"
    meta = load(path.with_suffix(".metadata.json"))
    require(meta["status"] == 200, f"FRC {number} schedule capture failed")
    digest(path, meta["sha256"])
    tree = SourceHTML(path.read_text(encoding="utf-8")).root
    found = {}
    for event in tree.all("div"):
        if "tab-pane" not in event.attrs.get("class", "").split():
            continue
        headings = [n for n in event.all("h1") if "panel-title" in n.attrs.get("class", "").split()]
        if not headings:
            continue
        dates = next((n.text() for n in event.all("i") if re.match(r"^[A-Z][a-z]+ \d", n.text())), "")
        start, end = event_dates(dates)
        for table in event.all("table"):
            if table.attrs.get("id") != "matches":
                continue
            rows = list(table.all("tr"))
            for index, row in enumerate(rows):
                links = [a for a in row.all("a") if re.fullmatch(
                    r"/2026/[^/]+/(?:qualifications|playoffs)/\d+", a.attrs.get("href", ""))]
                if not links:
                    continue
                href = links[0].attrs["href"]
                phase = "Playoff" if "/playoffs/" in href else "Qualification"
                cells = [n for n in row.children if isinstance(n, Node) and n.tag == "td"]
                score_text = [n.text() for n in cells[-2:]]
                played = len(score_text) == 2 and all(re.fullmatch(r"\d+", s) for s in score_text)
                lineup = rows[index + 1] if phase == "Playoff" else row
                team_cells = [n for n in lineup.children if isinstance(n, Node) and n.tag == "td"
                              and n.attrs.get("id", "").startswith("team")]
                assigned = [int(next(n.all("a")).text()) for n in team_cells]
                require(len(assigned) == 6 and len(set(assigned)) == 6,
                        f"incomplete FRC lineup: {href}")
                markers = " ".join(str(n.attrs) + " " + " ".join(str(c.attrs) for c in n.all())
                                   for n in team_cells).lower()
                dq = bool(re.search(r"disqual|red.?card", markers))
                absent = bool(re.search(r"no.?show|not.?on.?field|did.?not.?play", markers))
                url = "https://frc-events.firstinspires.org" + href
                require(url not in found, f"duplicate FIRST schedule row: {number} {url}")
                found[url] = {"officialUrl": url, "eventName": headings[0].text(),
                    "eventCode": event.attrs["id"], "eventStartDate": start, "eventEndDate": end,
                    "phase": phase, "matchNumber": int(href.rsplit("/", 1)[1]),
                    "redTeams": assigned[:3], "blueTeams": assigned[3:],
                    "redScore": int(score_text[0]) if played else None,
                    "blueScore": int(score_text[1]) if played else None,
                    "eligible": bool(played and not dq and not absent and end <= cutoff)}
    candidates = {m["matchUrl"]: m for m in record["allCandidates"]}
    require(set(candidates) == set(found), f"FRC {number} candidate population differs from raw schedule")
    for url, source in found.items():
        row = candidates[url]
        for key in ("eventCode", "eventStartDate", "eventEndDate", "matchNumber", "redTeams",
                    "blueTeams", "redScore", "blueScore", "eligible"):
            require(row[key] == source[key], f"FRC {number} candidate {key} differs from raw FIRST row {url}")
        require(row["phase"].title() == source["phase"], f"FRC {number} phase differs from raw schedule")
    eligible = {u: m for u, m in found.items() if m["eligible"]}
    require(record["eligibilityCounts"]["eligible"] == len(eligible), f"FRC {number} eligible count differs")
    return eligible


def ftc_populations():
    sources = RESEARCH / "ftc-sources"
    for path in sources.glob("*.metadata.json"):
        meta = load(path)
        require(meta["httpStatus"] == 200, f"FTC capture failed: {path.name}")
        digest(sources / path.name.removesuffix(".metadata.json"), meta["sha256"])
    result = {}
    for record in load(RESEARCH / "ftc-candidates.json")["teams"]:
        number = record["teamNumber"]
        events_file = sources / f"team-{number}-events-2025.json"
        events = load(events_file) if events_file.exists() else []
        if not events_file.exists():
            require(load(sources / f"team-{number}-matches-2025.json") == [],
                    f"FTC {number} missing prior-season participation proof")
        expected_codes = {e["eventCode"] for e in events}
        eligible, excluded, population_count = {}, set(), 0
        for code in expected_codes:
            event = load(sources / f"event-2025-{code}.json")
            for match in load(sources / f"event-2025-{code}-matches.json"):
                participants = match["teams"]
                if not any(t["teamNumber"] == number for t in participants):
                    continue
                population_count += 1
                key = f"2025-{code}-{match['id']}"
                complete = len(participants) == 4 and len({t["teamNumber"] for t in participants}) == 4
                valid = bool(match["hasBeenPlayed"] and match.get("scores") and complete
                             and all(t["onField"] and not t["noShow"] and not t["dq"] for t in participants)
                             and not event["modifiedRules"])
                if not valid:
                    excluded.add(key)
                    continue
                phase = "Qualification" if match["tournamentLevel"] == "Quals" else "Playoff"
                num = match["id"] if phase == "Qualification" else match["series"]
                suffix = f"qualifications/{num}" if phase == "Qualification" else f"playoff/{num}/1"
                url = f"https://ftc-events.firstinspires.org/2025/{code}/{suffix}"
                scores = match["scores"]
                require(url not in eligible, f"duplicate FTC match key {url}")
                eligible[url] = {"officialUrl": url, "eventCode": code, "eventName": event["name"],
                    "eventStartDate": event["start"], "eventEndDate": event["end"], "phase": phase,
                    "matchNumber": num, "redTeams": [t["teamNumber"] for t in participants if t["alliance"] == "Red"],
                    "blueTeams": [t["teamNumber"] for t in participants if t["alliance"] == "Blue"],
                    "redScore": scores["red"]["totalPoints"], "blueScore": scores["blue"]["totalPoints"],
                    "sourceKey": key, "eligible": True}
        derived = {m["officialResultUrl"]: m for m in record["candidates"]}
        require(set(derived) == set(eligible), f"FTC {number} eligible population differs from raw capture")
        for url, match in eligible.items():
            for field in ("eventCode", "eventName", "eventStartDate", "eventEndDate", "phase", "matchNumber",
                          "redTeams", "blueTeams", "redScore", "blueScore"):
                require(derived[url][field] == match[field], f"FTC {number} {field} differs from raw payload")
        actual_excluded = {f"2025-{m['eventCode']}-{m['sourceMatchId']}" for m in record["excluded"]}
        require(actual_excluded == excluded, f"FTC {number} exclusions differ from raw capture")
        require(record["populationCount"] == population_count and record["eligibleMatchCount"] == len(eligible),
                f"FTC {number} population count differs")
        result[number] = eligible
    return result


def verified_scorecards():
    result = {}
    for source in load(RESEARCH / "frc-match-scorecards.json")["sources"]:
        card = source["scorecard"]
        require(all(v == "None" for v in card["Penalties"].values()),
                f"selected FRC scorecard carries a penalty exclusion: {source['url']}")
        result[source["url"]] = {"redTeams": card["Teams"]["red"], "blueTeams": card["Teams"]["blue"],
            "redScore": int(card["Final Score"]["red"]), "blueScore": int(card["Final Score"]["blue"])}
    for source in load(RESEARCH / "ftc-first-verification.json")["records"]:
        require(source["httpStatus"] == 200 and source["matchesFtcScoutPayload"], "FTC official scorecard verification failed")
        teams = source["teams"]
        result[source["sourceUrl"]] = {"redTeams": [teams["red1"], teams["red2"]],
            "blueTeams": [teams["blue1"], teams["blue2"]], "redScore": source["redScore"], "blueScore": source["blueScore"]}
    return result


def verified_videos():
    result = {}
    for filename in ("video-links.json", "video-ftc-links.json"):
        for record in load(RESEARCH / filename)["records"]:
            if "sourceFile" in record:
                digest(RESEARCH / record["sourceFile"], record["sha256"])
            if "officialSourceFile" in record:
                digest(RESEARCH / record["officialSourceFile"], record["officialSourceSha256"])
            for video in record["videos"]:
                if not video.get("metadataFile"):
                    continue
                metadata = load(RESEARCH / video["metadataFile"])
                require(metadata["title"] == video["title"] and metadata["author_name"] == video["author"],
                        f"video title/publisher differs from YouTube metadata: {video['id']}")
                require(video["id"] in metadata["html"], "video ID differs from YouTube metadata")
                if "chapterSourceFile" in video:
                    chapter = load(RESEARCH / video["chapterSourceFile"])
                    require(chapter["videoId"] == video["id"] and chapter["playabilityStatus"] == "OK",
                            "FTC recording identity/playability differs")
                    marker = video["timestamp"] + " " + video["chapterLabel"]
                    require(marker in chapter["description"].splitlines(), "FTC match chapter absent from publisher description")
                    seconds = sum(int(v) * 60 ** i for i, v in enumerate(reversed(video["timestamp"].split(":"))))
                    query = parse_qs(urlparse(video["url"]).query)
                    require(seconds == video["startSeconds"] and query["t"] == [f"{seconds}s"] and query["v"] == [video["id"]],
                            "FTC replay timestamp differs from publisher chapter")
                    expected_label = ("Q" + str(record["matchNumber"]) if record["phase"] == "qualification"
                                      else "P" + str(record["series"]))
                    require(video["chapterLabel"] == expected_label, "FTC chapter belongs to a different match")
                else:
                    page = (RESEARCH / record["sourceFile"]).read_text(encoding="utf-8")
                    require(video["id"] in page and video["oembedStatus"] == 200,
                            "FRC video absent from exact match page or inaccessible")
                result.setdefault(record["officialResultsUrl"], []).append(video)
    return result


def verify_matches(data):
    """Raise ValueError for a broken evidence join; return a compact audit count."""
    library = data["matchHighlights"]
    require(all(library.get(k) for k in ("asOf", "policy", "scoreNote", "methodologyUrl")), "missing public selection/score context")
    frc_roster = load(ROOT / "data/teams.json")["teams"]
    ftc_roster = load(ROOT / "ftc/data/teams.json")
    roster = {(program, t["team_number"]): t for program, rows in (
        ("FRC", frc_roster), ("FTC", ftc_roster["teams"] + ftc_roster["current_season_only_teams"])) for t in rows}
    entries = {(t["program"], t["number"]): t for t in library["teams"]}
    require(len(entries) == len(library["teams"]) and set(entries) == set(roster), "team library does not cover the complete research roster exactly once")
    frc = load(RESEARCH / "frc-candidates.json")
    populations = {("FRC", r["team"]): frc_population(r, frc["rankingSnapshotCutoff"]) for r in frc["records"]}
    populations.update({("FTC", n): rows for n, rows in ftc_populations().items()})
    require(set(populations) == set(roster), "raw research population does not match the team roster")
    scorecards, videos = verified_scorecards(), verified_videos()
    required_video = {("FRC", t["number"]) for t in data["top10"]} | {("FTC", t["number"]) for t in data["ftc"]["teams"]}
    seen_ids, played_count, video_count = {}, 0, 0
    for key, entry in entries.items():
        program, number = key
        require(entry["teamName"] == roster[key]["team_name"], f"{key} name differs from roster")
        current_ftc = {t["team_number"] for t in ftc_roster["current_season_only_teams"]}
        expected_season = 2026 if program == "FRC" or number in current_ftc else 2025
        require(entry["season"] == expected_season, f"{key} has the wrong performance season")
        require(entry.get("seasonLabel") and entry.get("sourceUrl"), f"{key} missing season/source context")
        population = populations[key]
        playoffs = {u: m for u, m in population.items() if m["phase"] == "Playoff"}
        require(entry["counts"] == {"eligible": len(population), "playoff": len(playoffs)}, f"{key} public match counts differ")
        main, alternate = entry["main"], entry["playoff"]
        if not population:
            require(entry["status"] == "pending" and main is None and alternate is None,
                    f"{key} invents a match without prior-season participation")
            continue
        played_count += 1
        require(entry["status"] == "played" and main, f"{key} lost its representative match")
        min_margin = min(abs(m["redScore"] - m["blueScore"]) for m in population.values())
        ties = [m for m in population.values() if abs(m["redScore"] - m["blueScore"]) == min_margin]
        require(main["margin"] == min_margin, f"{key} primary match is not the minimum eligible score margin")
        if any(m["phase"] == "Playoff" for m in ties):
            require(main["phase"] == "Playoff", f"{key} omitted playoff preference on equal minimum margins")
        if playoffs and main["phase"] != "Playoff":
            require(alternate and alternate["phase"] == "Playoff", f"{key} lost its playoff alternative")
            require(alternate["margin"] == min(abs(m["redScore"] - m["blueScore"]) for m in playoffs.values()),
                    f"{key} playoff alternative is not the closest eligible playoff")
        else:
            require(alternate is None, f"{key} duplicates its main match as a playoff alternative")
        for slot, match in (("main", main), ("playoff", alternate)):
            if match is None:
                continue
            url = match["officialUrl"]
            require(url in population, f"{key} {slot} has no eligible source match")
            source = population[url]
            for field in ("eventCode", "eventName", "eventStartDate", "eventEndDate", "phase", "matchNumber", "redScore", "blueScore"):
                require(match[field] == source[field], f"{key} {slot} {field} differs from raw source")
            for field in ("redTeams", "blueTeams"):
                require(sorted(match[field]) == sorted(source[field]), f"{key} {slot} alliance lineup differs")
            require(url in scorecards, f"{key} {slot} lacks an independent FIRST scorecard check")
            for field in ("redScore", "blueScore", "redTeams", "blueTeams"):
                public, official = match[field], scorecards[url][field]
                require((sorted(public) == sorted(official)) if isinstance(public, list) else public == official,
                        f"{key} {slot} differs from the official scorecard")
            red, blue = match["redScore"], match["blueScore"]
            alliance = "Red" if number in match["redTeams"] else "Blue" if number in match["blueTeams"] else None
            winner = "Tie" if red == blue else "Red" if red > blue else "Blue"
            outcome = "Tie" if winner == "Tie" else "Win" if alliance == winner else "Loss"
            require(alliance and match["teamAlliance"] == alliance and match["outcome"] == outcome
                    and match["margin"] == abs(red - blue), f"{key} {slot} score/alliance/outcome is inconsistent")
            require(match.get("dateLabel") and match.get("matchLabel") and match.get("id"), f"{key} missing match label/date/id")
            facts = (program, url, red, blue, tuple(sorted(match["redTeams"])), tuple(sorted(match["blueTeams"])))
            require(match["id"] not in seen_ids or seen_ids[match["id"]] == facts, "one public match ID identifies different matches")
            seen_ids[match["id"]] = facts
            if match.get("videoUrl"):
                evidence = next((v for v in videos.get(url, []) if v["url"] == match["videoUrl"]), None)
                require(evidence is not None, f"{key} {slot} replay URL has no exact verified match association")
                require(match["videoTitle"] == evidence["title"] and match["videoPublisher"] == evidence["author"]
                        and match["videoEvidence"] == evidence["evidence"], f"{key} {slot} replay evidence differs")
                video_count += 1
            elif key in required_video and (slot == "main" or program == "FTC"):
                require(False, f"{key} {slot} lost a required verified replay")
            else:
                require(not any(match.get(k) for k in ("videoTitle", "videoPublisher", "videoEvidence")),
                        f"{key} {slot} has video claims without a replay")
    return {"teams": len(entries), "playedTeams": played_count, "eligibleTeamMatches": sum(map(len, populations.values())),
            "uniqueSelectedMatches": len(seen_ids), "verifiedVideoLinks": video_count}


if __name__ == "__main__":
    print("Verified match highlights:", verify_matches(load(HERE / "dist/data.json")))
