#!/usr/bin/env python3
"""Write the reporter pages from the same data as the site: press kit, printable standings,
logos and photos, and a standings CSV. Called by build.py; stdlib only."""
from __future__ import annotations

import csv
import io
from datetime import date
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
PRESS = HERE / "dist/press"
CONTACT = "celder@bionanomics.com"
ABOUT = ("The REFINERY is a nonprofit robotics makerspace in Fort Wayne, Indiana, affiliated with BioNanomics. "
         "It helps youth FIRST robotics teams across 12 Northeast Indiana counties with funding, parts, tools, "
         "practice space and training, and helps schools start new teams.")
DISCLOSURE = ("The REFINERY and its affiliate BioNanomics are listed sponsors of FRC teams 4982, 8742, 10172, 10332 and 10434 "
              "and FTC team 22331; Doug Horner of The REFINERY is a listed sponsor of 9431; FTC team 36124 is based at The REFINERY. "
              "Standings, records and ratings come only from The Blue Alliance, Statbotics and FTCScout and are not adjusted by hand.")


def e(value):
    return escape(str(value if value is not None else ""))


def link(url, label):
    return f'<a href="{e(url)}" target="_blank" rel="noopener">{e(label)}</a>'


def nice_date(iso):
    d = date.fromisoformat(iso)
    return f"{d:%b} {d.day}, {d.year}"


def date_range(start, end):
    a, b = date.fromisoformat(start), date.fromisoformat(end)
    if a == b:
        return nice_date(start)
    if (a.year, a.month) == (b.year, b.month):
        return f"{a:%b} {a.day}–{b.day}, {a.year}"
    return f"{a:%b} {a.day} – {b:%b} {b.day}, {b.year}"


def record(r):
    return f"{r['wins']}-{r['losses']}" + (f"-{r['ties']}" if r["ties"] else "")


def handle(url):
    return url.rstrip("/").split("/")[-1].lstrip("@")


def page(title, body, description):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{e(title)} · Northeast Indiana Robotics · The REFINERY</title>
  <meta name="description" content="{e(description)}">
  <link rel="icon" href="../assets/refinery-logo.svg" type="image/svg+xml">
  <link rel="stylesheet" href="press.css">
</head>
<body>
  <header class="bar"><a href="../"><img src="../assets/refinery-logo-reversed.svg" alt="The REFINERY" width="124" height="32"></a>
    <nav><a href="./">Press kit</a><a href="standings.html">Standings</a><a href="media.html">Logos &amp; photos</a><a href="../#schedule">Calendar</a></nav></header>
  <main class="sheet">
{body}
  </main>
  <footer class="sheet small"><p><strong>Media contact:</strong> <a href="mailto:{CONTACT}">{CONTACT}</a></p><p>{e(DISCLOSURE)}</p></footer>
</body>
</html>
"""


def team_block(t):
    honors = [f"Won {', '.join(t['titles'])}" if t["titles"] else "", f"{t['worlds']}" if t["worlds"] else "",
              "Indiana State Championship" if t["stateChampionship"] and not t["worlds"] else ""]
    awards = "; ".join(f"{a['award']} ({a['event']})" for a in t["awards"])
    follow = " · ".join(link(x["url"], f"{x['type']} @{handle(x['url'])}" if x["type"] in ("Instagram", "X", "YouTube", "TikTok") else x["type"]) for x in t["teamLinks"])
    news = "".join(f"<li>{link(s['url'], s['title'])} <span class=\"muted\">{e(s['outlet'])}, {nice_date(s['date'])}</span></li>" for s in t["news"])
    return f"""<section class="team" id="team-{t['number']}">
      <h3>{e(t['name'])} <span class="muted">· FRC {t['number']}</span></h3>
      <p class="muted">{e(t['school'])} · {e(t['city'])}, {e(t['county'])} County · rookie year {t['rookieYear']}</p>
      <dl class="facts"><div><dt>2026 record</dt><dd>{record(t['record'])}</dd></div><div><dt>Indiana district rank</dt><dd>#{t['district']['rank']} of {t['district']['teamCount']}</dd></div><div><dt>District points</dt><dd>{t['district']['points']}</dd></div><div><dt>EPA (Statbotics)</dt><dd>{t['epa']:.1f}</dd></div></dl>
      {f"<p><strong>Honors:</strong> {e('; '.join(h for h in honors if h))}</p>" if any(honors) else ""}
      {f"<p><strong>Awards:</strong> {e(awards)}</p>" if awards else ""}
      {f"<p><strong>Follow the team:</strong> {follow}</p>" if follow else ""}
      {f"<p><strong>Coverage:</strong></p><ul class='news'>{news}</ul>" if news else ""}
      <p class="small">{link(t['links']['tba'], 'The Blue Alliance')} · {link(t['links']['statbotics'], 'Statbotics')} · {link(t['links']['first'], 'FIRST profile')}</p>
    </section>"""


def storylines(result, dnf_count):
    teams, s = result["standings"], result["seasonSummary"]
    lines = []
    for t in sorted((t for t in teams if t["titles"]), key=lambda t: -len(t["titles"])):
        season = 2026 - t["rookieYear"] + 1
        extra = f" and reached the {t['worlds']}" if t["worlds"] else (" in only its second season" if season == 2 else "")
        lines.append(f"<strong>{e(t['name'])} ({t['number']})</strong> won the {e(' and '.join(t['titles']))} district event{'s' if len(t['titles']) > 1 else ''}{e(extra)}.")
    for t in (t for t in teams if t["worlds"] and not t["titles"]):
        lines.append(f"<strong>{e(t['name'])} ({t['number']})</strong> earned a trip to the {e(t['worlds'])} in Houston.")
    lines.append(f"Regional teams won <strong>{s['awards']} judged awards</strong> in 2026, from Innovation in Control to Rising All-Star.")
    ftc = result["ftc"]
    names = [f"{e(t['school'])}'s {e(t['name'])} ({t['number']})" for t in ftc["teams"]]
    if names:
        new = "".join(f", and {e(t['name'])} ({t['number']}) debuts this season" for t in ftc["newTeams"])
        lines.append(f"In FTC, {' and '.join(names)} return{new}.")
    lines.append(f"<strong>Did Not Field. Yet.</strong> {dnf_count} schools within 60 miles of downtown Fort Wayne have no school-affiliated FTC or FRC team. The REFINERY wants them on the leaderboard and lists them, with their superintendents and principals, on the main page.")
    return "".join(f"<li>{line}</li>" for line in lines)


def write_press(result, dnf_count):
    PRESS.mkdir(parents=True, exist_ok=True)
    teams = sorted(result["standings"], key=lambda t: t["standingsRank"])
    s, cal = result["seasonSummary"], result["calendar"]
    upcoming = [x for x in cal["events"] if x["endDate"] >= cal["retrievedDate"]][:8]

    # Standings CSV
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["district_standing", "power_ranking", "team_number", "team_name", "school_or_organization", "city", "county",
                     "wins", "losses", "ties", "indiana_district_rank", "district_points", "epa_2026", "event_titles", "world_championship",
                     "awards", "website", "results_source", "ratings_source"])
    for t in teams:
        site = next((x["url"] for x in t["teamLinks"] if x["type"] == "Website"), "")
        writer.writerow([t["standingsRank"], t["powerRank"], t["number"], t["name"], t["school"], t["city"], t["county"],
                         t["record"]["wins"], t["record"]["losses"], t["record"]["ties"], t["district"]["rank"], t["district"]["points"],
                         f"{t['epa']:.2f}", "; ".join(t["titles"]), t["worlds"] or "", "; ".join(a["award"] for a in t["awards"]), site,
                         s["resultsSource"], s["ratingsSource"]])
    (HERE / "dist/standings-2026.csv").write_text(buffer.getvalue(), encoding="utf-8")

    # Printable standings
    rows = "".join(f"<tr><td>{t['standingsRank']}</td><td><strong>{e(t['name'])}</strong> {t['number']}<br><span class='muted'>{e(t['city'])} · {e(t['school'])}</span></td>"
                   f"<td class='n'>{record(t['record'])}</td><td class='n'>#{t['district']['rank']}</td><td class='n'>{t['district']['points']}</td><td class='n'>{t['epa']:.1f}</td>"
                   f"<td>{e('; '.join(t['badges']))}</td></tr>" for t in teams)
    standings = f"""    <p class="kicker">2026 FRC season · final</p>
    <h1>Northeast Indiana standings</h1>
    <p class="muted">Ordered by 2026 FIRST Indiana district points. Updated {nice_date(s['updated'])}. <a href="../standings-2026.csv" download>Download CSV</a> · <a href="javascript:print()">Print</a></p>
    <table class="standings"><thead><tr><th>#</th><th>Team</th><th class="n">W-L</th><th class="n">IN rank</th><th class="n">Points</th><th class="n">EPA</th><th>2026 honors</th></tr></thead><tbody>{rows}</tbody></table>
    <p class="small">Records count official matches (district events, state and world championship). Indiana district rank is among {teams[0]['district']['teamCount']} teams. Records, events and awards: {e(s['resultsSource'])}. EPA: {e(s['ratingsSource'])}.</p>"""
    (PRESS / "standings.html").write_text(page("2026 standings", standings, "Printable 2026 FRC standings for Northeast Indiana."), encoding="utf-8")

    # Press kit
    stats = [(s["teams"], "FRC teams in the region"), (s["eventTitles"], "district event titles in 2026"), (len(s["worldsTeams"]), "World Championship teams"),
             (s["awards"], "judged awards"), (len(result["ftc"]["teams"]) + len(result["ftc"]["newTeams"]), "FTC teams to follow")]
    dates = "".join(f"<li><strong>{date_range(x['startDate'], x['endDate'])}</strong> · {e(x['name'])} <span class='muted'>· {e(', '.join(v for v in (x['venue'], x['city']) if v))}</span></li>" for x in upcoming)
    kit = f"""    <p class="kicker">Press kit · updated {nice_date(s['updated'])}</p>
    <h1>Northeast Indiana high school robotics</h1>
    <div class="contact"><strong>Media contact</strong><a href="mailto:{CONTACT}?subject=Media%20request%3A%20Northeast%20Indiana%20robotics">{CONTACT}</a><span>Interviews, photos, team introductions and event access.</span></div>
    <h2>At a glance</h2>
    <ul class="glance">{''.join(f'<li><strong>{v}</strong> {e(label)}</li>' for v, label in stats)}</ul>
    <h2>Story ideas</h2>
    <ul class="stories">{storylines(result, dnf_count)}</ul>
    <h2>Coming up</h2>
    <ul class="dates">{dates}</ul>
    <p><a href="../calendar.ics" download>Add every event to your calendar (.ics)</a> · <a href="../#schedule">Full calendar</a></p>
    <h2>Downloads</h2>
    <ul class="downloads"><li><a href="standings.html">Printable standings</a> and <a href="../standings-2026.csv" download>standings CSV</a></li><li><a href="media.html">Team logos and photos</a> with credits</li><li><a href="../calendar.ics" download>Season calendar (.ics)</a></li><li>{link('https://github.com/horner/refintery-rankings', 'Full data, sources and methodology on GitHub')}</li></ul>
    <h2>How the sport works</h2>
    <p><strong>FRC</strong> (<i>FIRST</i> Robotics Competition) is for grades 9–12 and uses industrial-size robots; <strong>FTC</strong> (<i>FIRST</i> Tech Challenge) is for grades 7–12 with smaller robots. Matches pit a red alliance against a blue alliance, three FRC teams per side, and partners change every qualifying match. Top teams pick partners for the playoffs. Indiana FRC teams earn district points at two district events; the leaders advance to the state championship and the <i>FIRST</i> Championship in Houston.</p>
    <p><strong>Rankings on this site:</strong> the standings follow official FIRST Indiana district points. The power ranking uses Statbotics EPA (Expected Points Added), an estimate of the points a robot adds to its alliance each match. FTC ratings (OPR) are separate and not comparable to EPA.</p>
    <h2>About The REFINERY</h2>
    <p>{e(ABOUT)} {link('https://refineryrobotics.org/', 'refineryrobotics.org')}</p>
    <h2>Team by team</h2>
    <p class="muted">In district-standings order. People are named on the main site only with the role and date found in a public source; confirm current captains and coaches with the team.</p>
    {''.join(team_block(t) for t in teams)}"""
    (PRESS / "index.html").write_text(page("Press kit", kit, "Press kit for Northeast Indiana high school robotics: story ideas, standings, dates, team facts and contacts."), encoding="utf-8")

    # Logos and photos
    marks = []
    for t in teams + result["ftc"]["teams"] + result["ftc"]["newTeams"]:
        program = "FRC" if t in teams else "FTC"
        for kind, mark in sorted((t.get("logos") or {}).items()):
            if mark.get("file"):
                shown = result["displayAssets"].get(mark["file"], {}).get("file", mark["file"])
                marks.append(f"<figure class='mark{' dark' if mark.get('background') == 'dark' else ''}'><img src='../{e(shown)}' alt='{e(mark['label'])}' loading='lazy'><figcaption><strong>{e(t['name'])}</strong> · {program} {t['number']} · {e(kind)} mark<br><a href='../{e(mark['file'])}' download>Download original</a> · {link(mark['pageUrl'], 'source')}</figcaption></figure>")
    photos = "".join(f"<figure class='photo'><img src='../{e(p['file'])}' alt='{e(p['caption'])}' loading='lazy' width='{p['width']}' height='{p['height']}'><figcaption>{e(p['caption'])} Photo: {e(p['credit'])}.<br><a href='../{e(p['file'])}' download>Download ({p['width']}×{p['height']})</a> · {link(p['sourceUrl'], 'full-size original')}</figcaption></figure>" for p in result["photos"])
    media = f"""    <p class="kicker">For reporters</p>
    <h1>Logos &amp; photos</h1>
    <p>School and team marks belong to their schools and teams; they're shown here for identification in news coverage. Photos are from The REFINERY; credit "Photo: The REFINERY". For other uses, or for more photos of a team, email <a href="mailto:{CONTACT}">{CONTACT}</a>.</p>
    <div class="contact"><strong>Have photos of your team?</strong><a href="mailto:{CONTACT}?subject=Team%20photos">{CONTACT}</a><span>Send action shots of your robot and team with the photographer's name and an OK to post. We're adding at least one photo for every team.</span></div>
    <h2>Photos</h2>
    <div class="grid photos">{photos}</div>
    <h2>Team and school logos</h2>
    <div class="grid marks">{''.join(marks)}</div>
    <p class="small">Each logo links to the page it came from. Originals are unmodified; checksums are in the {link('https://github.com/horner/refintery-rankings/blob/main/broadcast/data/logos.json', 'logo manifest')}.</p>"""
    (PRESS / "media.html").write_text(page("Logos & photos", media, "Team logos and photos for news coverage of Northeast Indiana robotics."), encoding="utf-8")
