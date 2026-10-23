"""One-time capture of 2026 results from public TBA team pages (no API key available)."""
import sys, re, html, os, json, hashlib, zlib
src, out = sys.argv[1], sys.argv[2]
NAMES = {"2026inmis": ("FIN District Mishawaka Event", "Mishawaka", "district", "2026-03-06", "2026-03-08", 1),
         "2026inlaf": ("FIN District Lafayette Event", "Lafayette", "district", "2026-03-26", "2026-03-28", 4),
         "2026incol": ("FIN District Columbus Event", "Columbus", "district", "2026-03-20", "2026-03-22", 3),
         "2026inwas": ("FIN District Washington Event", "Washington", "district", "2026-04-02", "2026-04-04", 5),
         "2026incmp": ("FIRST Indiana State Championship", "Indiana State Championship", "district_championship", "2026-04-17", "2026-04-19", 7),
         "2026arc": ("FIRST Championship · Archimedes Division", "World Championship (Archimedes)", "championship_division", "2026-04-29", "2026-05-02", None),
         "2026dal": ("FIRST Championship · Daly Division", "World Championship (Daly)", "championship_division", "2026-04-29", "2026-05-02", None),
         "2026kylou": ("RiverBOaT Rumble", "RiverBOaT Rumble", "offseason", "2026-07-10", "2026-07-11", None),
         "2026iri": ("Indiana Robotics Invitational", "Indiana Robotics Invitational", "offseason", "2026-07-16", "2026-07-18", None)}
snap = json.loads(open(sys.argv[3], encoding="utf-8").read())["team_years"]
snap = {r["team"]: r for r in snap}
teams = []
for n in map(int, sys.argv[4:]):
    raw = open(os.path.join(src, f"{n}-2026.html"), "rb").read()
    s = raw.decode("utf-8")
    events = []
    for m in re.finditer(r"(?:was|is)\s*<strong>Rank (\d+)</strong>\s*with a record of\s*<strong>([\d-]+)</strong>(.*?)(?=<table|<h3|<div class=\"col-|$)", s, flags=re.S):
        before = s[:m.start()]
        key = re.findall(r'/event/(2026[a-z0-9]+)', before)[-1]
        seg = m.group(3)
        awards = [html.unescape(re.sub(r"\s+", " ", a)).strip() for a in re.findall(r"<li>(.*?)</li>", seg, flags=re.S)]
        tail = s[m.start() + 20:]
        nxt = re.search(r"<strong>Rank \d+</strong>", tail)
        tail = tail[:nxt.start()] if nxt else tail
        p = re.search(r"They (?:competed in the playoffs as the|are)(.*?)</p>", tail, flags=re.S)
        playoff = None
        if p:
            t = html.unescape(re.sub(r"<[^>]+>|\s+", " ", p.group(0))).replace(" .", ".").strip()
            t = re.sub(r"\s+", " ", t)
            role = re.search(r"as the (Captain|1st Pick|2nd Pick|3rd Pick|Backup) of Alliance (\d+)", t)
            if t.startswith("They are"): result = "Playoffs (final result not recorded on TBA)"
            elif "won the event" in t: result = "Won event"
            elif "eliminated in the Finals" in t: result = "Finalist"
            else:
                r = re.search(r"Round (\d+)", t); result = f"Eliminated in playoff round {r.group(1)}" if r else "Playoffs"
            playoff = {"role": role.group(1) if role else None, "alliance": int(role.group(2)) if role else None, "result": result, "sourceText": t}
        name, short, kind, start, end, week = NAMES[key]
        events.append({"key": key, "name": name, "shortName": short, "type": kind, "startDate": start, "endDate": end, "week": week,
                       "qualRank": int(m.group(1)), "qualRecord": m.group(2), "awards": awards, "playoff": playoff,
                       "tbaUrl": f"https://www.thebluealliance.com/event/{key}"})
    sb = snap[n]
    teams.append({"teamNumber": n, "tbaUrl": f"https://www.thebluealliance.com/team/{n}/2026",
                  "responseSha256": hashlib.sha256(raw).hexdigest(), "responseBytes": len(raw),
                  "officialRecord": {"wins": sb["record"]["wins"], "losses": sb["record"]["losses"], "ties": sb["record"]["ties"]},
                  "district": {"key": "2026fin", "rank": sb.get("district_rank"), "points": sb.get("district_points"), "teamCount": 68},
                  "events": events})
doc = {"schemaVersion": 1, "season": 2026, "source": "The Blue Alliance public team pages",
       "retrievedDate": "2026-10-22",
       "method": "Each team's https://www.thebluealliance.com/team/{n}/2026 page was saved and its event rank, qualification record, awards and playoff sentence extracted. Official record and district rank/points come from the preserved Statbotics snapshot and match TBA's page text. Refresh with scripts/fetch_tba.py and a TBA API key.",
       "teams": teams}
open(out, "w", encoding="utf-8", newline="\n").write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
for t in teams:
    print(t["teamNumber"], t["officialRecord"], t["district"]["rank"], [(e["shortName"], e["qualRank"], e["playoff"]["result"] if e["playoff"] else "-", e["awards"]) for e in t["events"]])
