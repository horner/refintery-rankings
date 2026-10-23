#!/usr/bin/env python3
"""Pre-render the home page and write one shareable page per team. Called by build.py; stdlib only.

The home page is a template (broadcast/templates/index.html) with <!--@name--> markers. The build
fills them with the same content app.js draws, so the page reads fine without JavaScript and search
engines see the results; app.js then redraws the same containers and adds sorting and drop-downs.
"""
from __future__ import annotations

import json
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parents[1]
DIST = HERE / "dist"
SITE = "https://horner.github.io/refintery-rankings/"
CONTACT = "celder@bionanomics.com"
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
# Double-elimination bracket: the round a team goes out in fixes its finish (8 alliances).
FINISH = {2: "Tied 7th (out in playoff round 2)", 3: "Tied 5th (out in playoff round 3)", 4: "4th place", 5: "3rd place"}


def e(value):
    return escape(str(value if value is not None else ""))


def ext(url, label, cls=""):
    return f'<a{f" class=\"{cls}\"" if cls else ""} href="{e(url)}" target="_blank" rel="noopener">{e(label)}</a>'


def short(iso):
    try:
        d = date.fromisoformat(iso)
    except ValueError:  # Some sources give a season such as "2025-2026" rather than a day.
        return str(iso)
    return f"{d:%b} {d.day}, {d.year}"


def span(start, end):
    a, b = date.fromisoformat(start), date.fromisoformat(end)
    if a == b:
        return short(start)
    if (a.year, a.month) == (b.year, b.month):
        return f"{a:%b} {a.day}–{b.day}, {a.year}"
    return f"{a:%b} {a.day} – {b:%b} {b.day}, {b.year}"


def record(r):
    return f"{r['wins']}-{r['losses']}" + (f"-{r['ties']}" if r["ties"] else "")


def ordinal(n):
    return f"{n}{'th' if 11 <= n % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def playoff_result(p):
    if not p:
        return "Not picked for playoffs"
    if p["result"] == "Won event":
        return "Won the event"
    if p["result"] == "Finalist":
        return "Runner-up (lost in the finals)"
    digits = [int(c) for c in p["result"] if c.isdigit()]
    return FINISH.get(digits[0], "Reached playoffs") if digits else "Reached playoffs"


def playoff_role(p):
    if not p or not p.get("alliance"):
        return ""
    seed = f"#{p['alliance']} alliance"
    role = p["role"] or ""
    return f"Captain of the {seed}" if role == "Captain" else f"Backup robot for the {seed}" if role == "Backup" else f"{role[:1].upper()}{role[1:].lower()} of the {seed}"


def logo(logos, number, display, prefix=""):
    mark = next((logos.get(k) for k in ("team", "school") if (logos or {}).get(k, {}).get("file")), None)
    if not mark:
        return f'<span class="logo placeholder" aria-hidden="true">{e(number)}</span>'
    shown = display.get(mark["file"])
    size = f' width="{shown["width"]}" height="{shown["height"]}"' if shown else ""
    return f'<span class="logo{" dark-logo" if mark.get("background") == "dark" else ""}"><img src="{prefix}{e(shown["file"] if shown else mark["file"])}" alt="" loading="lazy" decoding="async"{size}></span>'


def identity_logos(t, display, prefix="", kind=None):
    marks = []
    for kind in (kind,) if kind else ("school", "team"):
        mark = t.get("logos", {}).get(kind)
        if not mark or not mark.get("file"):
            continue
        shown = display.get(mark["file"], {})
        image = f'<span class="logo{(" dark-logo" if mark.get("background") == "dark" else "")}"><img src="{prefix}{e(shown.get("file", mark["file"]))}" alt="{e(mark["label"])}" loading="lazy" decoding="async"></span>'
        marks.append(f'<figure class="{kind}-identity">{image}<figcaption>{"School / organization" if kind == "school" else "Team"}</figcaption></figure>')
    return '<div class="profile-logos">' + ''.join(marks) + '</div>'


def standings_mark(t, display, kind):
    mark = t.get("logos", {}).get(kind)
    if not mark or not mark.get("file") or mark.get("status") != "verified":
        return ""
    shown = display.get(mark["file"])
    size = f' width="{shown["width"]}" height="{shown["height"]}"' if shown else ""
    label = f'{"School" if kind == "school" else "Team"}: {mark["label"]}'
    return f'<span class="logo {kind}-mark{" dark-logo" if mark.get("background") == "dark" else ""}"><img src="{e(shown["file"] if shown else mark["file"])}" alt="{e(label)}" title="{e(label)}" loading="lazy" decoding="async"{size}></span>'


def person_evidence(p):
    qualifiers = [("historical", "Historical evidence"), ("retrospective", "Retrospective account"), ("indexed", "Indexed evidence"), ("self reported", "Self-reported")]
    parts = ["Source dated " + short(p["date"]) if p.get("date") else "Undated source"]
    if p.get("season"):
        parts.append("Season " + p["season"])
    parts.extend(label for term, label in qualifiers if term in p.get("status", ""))
    if p.get("note"):
        parts.append(p["note"])
    if p.get("dateBasis"):
        parts.append(p["dateBasis"])
    return e(" · ".join(parts))


def people_details(people, gaps=()):
    if not people:
        return ""
    rows = []
    for p in people:
        sources = " · ".join(ext(url, f"source {i + 1}") for i, url in enumerate(p["sourceUrls"]))
        rows.append(f'<li><strong>{e(p["name"])}</strong> · {e(p["role"])}<br><small>{person_evidence(p)} · {sources}</small></li>')
    note = " ".join(gaps) or "Confirm current captains and coaches with the team before publishing."
    return f'<details open><summary>People named in public sources ({len(people)})</summary><ul class="people">{"".join(rows)}</ul><p class="muted small">{e(note)}</p></details>'


def follow_label(link):
    if link["type"] == "Website":
        return "Team website"
    if link["type"] in ("Instagram", "X", "YouTube", "TikTok"):
        return f"{link['type']} @{link['url'].rstrip('/').split('/')[-1].lstrip('@')}"
    return link["type"]


def replay_thumbnail(match, result, team_name, prefix=""):
    thumbnail = result.get("videoThumbnails", {}).get((match or {}).get("videoUrl"))
    if not thumbnail:
        return ""
    label = f"Watch {team_name}: {match['eventName']}, {match['matchLabel']}"
    alt = f"Replay preview: {match.get('videoTitle') or match['matchLabel']}"
    return (f'<a class="replay-thumbnail" href="{e(match["videoUrl"])}" target="_blank" rel="noopener" aria-label="{e(label)}">'
            f'<img src="{prefix}{e(thumbnail["file"])}" width="{thumbnail["width"]}" height="{thumbnail["height"]}" alt="{e(alt)}" loading="lazy" decoding="async">'
            '<span>▶ Watch replay</span></a>')


# ---------------------------------------------------------------- home page pieces

def standings_rows(result):
    display = result["displayAssets"]
    rows = []
    for t in sorted(result["standings"], key=lambda t: t["standingsRank"]):
        honors = "".join(f'<span class="{"trophy" if "winner" in b.lower() else "worlds" if "World" in b else ""}">{e(b)}</span>' for b in t["badges"])
        rows.append(f"""<details class="team" id="team-{t['number']}"><summary class="team-row"><span class="rank">{t['standingsRank']}</span><span class="identity">{standings_mark(t, display, "school")}<span class="identity-copy"><strong class="school-name">{e(t['school'])}</strong><small class="team-secondary"><span class="team-name">{e(t['name'])}</span> <span class="team-number">· FRC {t['number']}</span></small><small class="school-city">{e(t['city'])}</small></span>{standings_mark(t, display, "team")}</span><span class="stat r num">{record(t['record'])}<small>W-L</small></span><span class="stat r district num">#{t['district']['rank']}<small>{t['district']['points']} points</small></span><span class="stat r epa num">{t['epa']:.1f}<small>EPA</small></span><span class="honors">{honors}</span><span class="chev" aria-hidden="true"></span></summary><div class="team-detail" data-team="{t['number']}"><p><a class="text-link" href="team/{t['number']}/">Full team page</a></p></div></details>""")
    head = '<div class="standings-header" aria-hidden="true"><span>#</span><span>School / team</span><span class="r">Record</span><span class="r">District</span><span class="r">EPA</span><span class="h-honors">2026 honors</span><span></span></div>'
    return head + "".join(rows)


def highlights(result):
    teams, s = result["standings"], result["seasonSummary"]
    cards = []
    for t in sorted((t for t in teams if t["titles"]), key=lambda t: -len(t["titles"])):
        season = 2026 - t["rookieYear"] + 1
        extra = f", then reached the {t['worlds']}" if t["worlds"] else (f" in just its {'first' if season == 1 else 'second'} season" if season <= 2 else "")
        cards.append((f"{len(t['titles'])}×", f"{t['name']} ({t['number']})", f"Won the {' and '.join(t['titles'])} district event{'s' if len(t['titles']) > 1 else ''}{extra}.", f"team/{t['number']}/"))
    for t in (t for t in teams if t["worlds"] and not t["titles"]):
        cards.append(("Worlds", f"{t['name']} ({t['number']})", f"Earned a trip to the {t['worlds']} in Houston.", f"team/{t['number']}/"))
    winners = len({t["number"] for t in teams if t["awards"]})
    cards.append((s["awards"], "Judged awards", f"Won by {winners} regional teams, from Innovation in Control to Rising All-Star.", "#standings"))
    return "".join(f'<a class="highlight" href="{e(href)}"><span class="big">{e(big)}</span><h3>{e(title)}</h3><p>{e(text)}</p></a>' for big, title, text, href in cards[:4])


def gallery(result):
    order = ["winner-banners", "team-8742", "robot-9431", "judging", "robot-9119"]
    photos = {p["id"]: p for p in result["photos"]}
    return "".join(f'<figure><img src="{e(p["file"])}" alt="{e(p["caption"])}" loading="lazy" decoding="async" width="{p["width"]}" height="{p["height"]}"><figcaption>{e(p["caption"])} Photo: {e(p["credit"])}</figcaption></figure>' for p in (photos.get(i) for i in order) if p)


def ftc_cards(result):
    display, cards = result["displayAssets"], []
    for t, rookie in [(t, False) for t in result["ftc"]["teams"]] + [(t, True) for t in result["ftc"]["newTeams"]]:
        stats = '<p class="muted">Rookie team for 2026–27. First matches this season.</p>' if rookie else f'<div class="card-stats"><div><strong>{t["opr"]:.1f}</strong><span>Best OPR, 2025–26</span></div><div><strong>{t["regionalRank"]}<small class="muted">/{t["regionalCount"]}</small></strong><span>Rank at Indiana events</span></div></div>'
        cards.append(f'<article class="card"><span class="label {"new" if rookie else "ftc"}">{"New this season" if rookie else "FTC"} · {t["number"]}</span><div class="identity">{logo(t["logos"], t["number"], display)}<span><strong>{e(t["name"])}</strong><small>{e(t["school"])}{" · " + e(t["city"]) if t.get("city") else ""}</small></span></div>{stats}<p><a class="text-link" href="team/{t["number"]}/">Team page</a></p></article>')
    return "".join(cards)


def region_teams(event, result, prefix=""):
    entry = event.get("entrants")
    if not entry:
        return ""
    if not entry["posted"]:
        text = ("Teams qualify during the season. Region qualifiers will be listed here." if event["type"] == "Championship"
                else "Entry list not posted yet. Region teams will be listed here when it is.")
        return f'<div class="region-teams"><span class="rt-label">REFINERY-region teams</span><p class="muted">{text}</p></div>'
    roster = {t["number"]: t for t in result["standings"] + result["ftc"]["teams"] + result["ftc"]["newTeams"]}
    if not entry["local"]:
        body = f'<p class="muted">{entry["count"]} teams entered; none from The REFINERY’s region yet.</p>'
    else:
        items = "".join(f'<li>{logo(roster[n]["logos"], n, result["displayAssets"], prefix) if n in roster else ""}<span><strong><a href="{prefix}team/{n}/">{e(roster[n]["name"]) if n in roster else f"Team {n}"}</a></strong><small>{n}</small></span></li>' for n in entry["local"])
        body = f'<ul class="entered">{items}</ul><p class="muted">{len(entry["local"])} of {entry["count"]} teams entered are from The REFINERY’s region.</p>'
    return f'<div class="region-teams"><span class="rt-label">REFINERY-region teams</span>{body}</div>'


def calendar(result, today):
    months, html = {}, []
    for ev in result["calendar"]["events"]:
        if ev["endDate"] >= today:
            months.setdefault(ev["startDate"][:7], []).append(ev)
    for key, events in months.items():
        year, month = map(int, key.split("-"))
        items = []
        for ev in events:
            d = date.fromisoformat(ev["startDate"])
            place = " · ".join(x for x in (ev["venue"], ", ".join(x for x in (ev["city"], ev["state"]) if x)) if x)
            items.append(f'<li><div class="date-block"><span class="m">{d:%b}</span><span class="d">{d.day}</span></div><div><span class="label{" ftc" if ev["program"] == "FTC" else ""}">{e(ev["program"])} · {e(ev["type"])}{f" · Week {ev["week"]}" if ev.get("week") else ""}</span><h3>{e(ev["name"])}</h3><p>{span(ev["startDate"], ev["endDate"])}{" · " + e(place) if place else ""}</p>{f"<p class=\"desc\">{e(ev['description'])}</p>" if ev["description"] else ""}{region_teams(ev, result)}<ul class="link-list"><li>{ext(ev["url"], "Event details", "text-link")}</li></ul></div></li>')
        html.append(f'<h3 class="month">{MONTHS[month - 1]} {year}</h3><ol class="schedule">{"".join(items)}</ol>')
    return "".join(html)


def school_leader(s, linked=False):
    leader = s.get("leader")
    if not leader or not leader.get("name"):
        return "School leader name not verified in public sources."
    name = ext(leader["sourceUrl"], leader["name"]) if linked else e(leader["name"])
    return f'{e(leader["role"])}: {name} · {e(leader["evidenceLabel"])}'


def dnf_list(dnf):
    rows = sorted(dnf["schools"], key=lambda s: s["distanceMiles"])
    return "".join(f'<li><details class="school"><summary><span><strong>{e(s["name"])}</strong><small>{e(s["city"])}, {e(s["state"])} · {e(s["sector"])}</small><small class="school-leader">{school_leader(s)}</small></span><span class="miles">{s["distanceMiles"]:.1f}<small> mi</small></span></summary><div class="school-body"><p>{e(s["district"])}</p><p>{school_leader(s, True)}</p></div></details></li>' for s in rows)


def news(result):
    stories = sorted(result["news"]["stories"], key=lambda s: s["date"], reverse=True)
    return "".join(f'<li>{ext(s["url"], s["title"])}<small>{e(s["outlet"])} · {short(s["date"])}</small></li>' for s in stories)


def write_index(result, dnf):
    s = result["seasonSummary"]
    ftc_count = len(result["ftc"]["teams"]) + len(result["ftc"]["newTeams"])
    stats = [(s["teams"], "FRC teams"), (s["eventTitles"], "Event titles in 2026"), (len(s["worldsTeams"]), "World Championship teams"), (s["awards"], "Judged awards"), (ftc_count, "FTC teams to follow")]
    today = result["calendar"]["retrievedDate"]
    fill = {
        "stats": "".join(f'<div><dt>{e(label)}</dt><dd data-count="{value}">{value}</dd></div>' for value, label in stats),
        "updated": f"Final 2026 results · updated {short(s['updated'])}",
        "standings": standings_rows(result),
        "standings-source": f"Records, events and awards: {e(s['resultsSource'])}. Ratings: {e(s['ratingsSource'])}. District rank is among {result['standings'][0]['district']['teamCount']} Indiana teams.",
        "highlights": highlights(result), "gallery": gallery(result), "ftc": ftc_cards(result), "calendar": calendar(result, today),
        "dnf-count": f'<strong data-count="{len(dnf["schools"])}">{len(dnf["schools"])}</strong><span>schools without a team</span>',
        "dnf": dnf_list(dnf), "news": news(result),
        "og-description": e(f"{s['teams']} FRC teams, {s['eventTitles']} event titles, {len(s['worldsTeams'])} World Championship teams. Records, results and stories from The REFINERY region."),
    }
    page = (HERE / "templates/index.html").read_text(encoding="utf-8")
    for name, html in fill.items():
        marker = f"<!--@{name}-->"
        if marker not in page:
            raise ValueError(f"Template marker missing: {marker}")
        page = page.replace(marker, html)
    (DIST / "index.html").write_text(page, encoding="utf-8")


# ---------------------------------------------------------------- team pages

def page_shell(title, description, image, url, body, json_ld):
    return f"""<!doctype html>
<html lang="en" class="team-page">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#18181b">
  <title>{e(title)}</title>
  <meta name="description" content="{e(description)}">
  <link rel="canonical" href="{e(url)}">
  <meta property="og:type" content="profile">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:url" content="{e(url)}">
  <meta property="og:image" content="{e(image)}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="../../assets/refinery-logo.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../../styles.css?v=20261023-integrated-2">
  <script type="application/ld+json">{json.dumps(json_ld, ensure_ascii=False)}</script>
</head>
<body>
  <header class="page-bar"><div class="wrap"><a class="brand" href="../../"><img src="../../assets/refinery-logo-reversed.svg" alt="The REFINERY" width="132" height="34"></a><a class="back" href="../../#standings">All standings</a></div></header>
  <main>
{body}
  </main>
  <footer class="site-footer"><div class="wrap footer-inner"><p>Media contact: <a href="mailto:{CONTACT}">{CONTACT}</a> · <a href="../../press/">Press kit</a> · <a href="../../press/media.html">Logos &amp; photos</a></p><p>Built by <a href="https://refineryrobotics.org/" target="_blank" rel="noopener">The REFINERY</a>. Results: The Blue Alliance; ratings: Statbotics and FTCScout. Not affiliated with or endorsed by <i>FIRST</i>.</p></div></footer>
</body>
</html>
"""


def team_hero(t, program, stats, honors, display):
    return f"""    <section class="team-hero"><div class="wrap"><div class="team-hero-grid">{identity_logos(t, display, '../../', 'school')}<div class="team-hero-copy">
      <p class="eyebrow">{program} {t['number']} · {e(t.get('city', ''))}</p>
      <h1>{e(t.get('school') or t['name'])}</h1>
      <p class="team-school">{e(t['name'])} · {program} {t['number']}</p>
      {f'<p class="honors">{honors}</p>' if honors else ''}
    </div>{identity_logos(t, display, '../../', 'team')}</div>
    <dl class="stat-bar">{''.join(f'<div><dt>{e(label)}</dt><dd>{e(value)}</dd></div>' for value, label in stats)}</dl></div></section>"""


def follow(t):
    links = t.get("teamLinks") or []
    return f'<h2>Follow the team</h2><ul class="link-list follow">{"".join(f"<li>{ext(l["url"], follow_label(l), "text-link")}</li>" for l in links)}</ul>' if links else ""


def news_list(stories):
    return f'<h2>In the news</h2><ul class="news-list">{"".join(f"<li>{ext(s["url"], s["title"])}<small>{e(s["outlet"])} · {short(s["date"])}</small></li>" for s in stories)}</ul>' if stories else ""


def upcoming_for(number, result):
    rows = [ev for ev in result["calendar"]["events"] if ev.get("entrants", {}).get("posted") and number in ev["entrants"]["local"]]
    if not rows:
        return '<h2>Coming up</h2><p class="muted">Entry lists for 2026–27 events haven’t posted yet. <a href="../../#schedule">See the full calendar</a>.</p>'
    return "<h2>Coming up</h2><ul class=\"news-list\">" + "".join(f"<li><strong>{span(ev['startDate'], ev['endDate'])}</strong> · {ext(ev['url'], ev['name'])}<small>{e(ev['venue'])} · {e(ev['city'])}</small></li>" for ev in rows) + "</ul>"


def frc_page(t, result):
    display = result["displayAssets"]
    photos = {p["id"]: p for p in result["photos"]}
    honors = "".join(f'<span class="{"trophy" if "winner" in b.lower() else "worlds" if "World" in b else ""}">{e(b)}</span>' for b in t["badges"])
    stats = [(record(t["record"]), "2026 record"), (f"#{t['district']['rank']}", f"Indiana district rank (of {t['district']['teamCount']})"),
             (t["district"]["points"], "District points"), (f"{t['epa']:.1f}", "EPA (Statbotics)"), (t["rookieYear"], "Rookie year")]
    def row(ev):
        role = playoff_role(ev["playoff"])
        won = ev["playoff"] and ev["playoff"]["result"] == "Won event"
        return f'<tr><td>{ext(ev["tbaUrl"], ev["shortName"])}<br><small class="muted">{span(ev["startDate"], ev["endDate"])}</small></td><td>{ordinal(ev["qualRank"])}<br><small class="muted">{e(ev["qualRecord"].removesuffix("-0"))} record</small></td><td class="{"won" if won else ""}">{e(playoff_result(ev["playoff"]))}{f"<br><small class=\"muted\">{e(role)}</small>" if role else ""}</td></tr>'
    head = "<thead><tr><th>Event</th><th>After qualifying</th><th>Playoffs</th></tr></thead>"
    official = [ev for ev in t["events"] if ev["type"] != "offseason"]
    offseason = [ev for ev in t["events"] if ev["type"] == "offseason"]
    events = f'<table class="events">{head}<tbody>{"".join(row(ev) for ev in official)}</tbody></table>'
    if offseason:
        events += f'<details><summary>Offseason events ({len(offseason)})</summary><table class="events">{head}<tbody>{"".join(row(ev) for ev in offseason)}</tbody></table></details>'
    awards = f'<h2>Awards</h2><ul class="award-list">{"".join(f"<li>{e(a["award"])} <span>· {e(a["event"])}</span></li>" for a in t["awards"])}</ul>' if t["awards"] else ""
    m = t["closestMatch"]
    closest = f'<h2>Closest game</h2><div class="close-game">{replay_thumbnail(m, result, t["name"], "../../")}<div>{e(m["eventName"])} · {e(m["matchLabel"])}</div><div class="scoreline"><span class="red">{m["redScore"]}</span><span class="muted">–</span><span class="blue">{m["blueScore"]}</span></div><div class="muted">{m["margin"]}-point {e(m["outcome"].lower())} on the {e(m["teamAlliance"].lower())} alliance</div><ul class="link-list">{f"<li>{ext(m["videoUrl"], "Watch replay", "text-link")}</li>" if m.get("videoUrl") else ""}<li>{ext(m["officialUrl"], "Official result", "text-link")}</li></ul></div>' if m else ""
    pic = next((photos[p] for p in t["photos"] if p in photos), None)
    figure = f'<figure class="team-photo"><img src="../../{e(pic["file"])}" alt="{e(pic["caption"])}" width="{pic["width"]}" height="{pic["height"]}" loading="lazy"><figcaption>{e(pic["caption"])} Photo: {e(pic["credit"])}</figcaption></figure>' if pic else ""
    people = t["students"] + t["representatives"] + t["adults"]
    people_html = people_details(people, t.get("gaps", []))
    body = f"""{team_hero(t, 'FRC', stats, honors, display)}
    <section class="section team-body"><div class="wrap team-columns"><div>
      {people_html}<h2>2026 season</h2>{events}{awards}{upcoming_for(t['number'], result)}{f'<p><a class="text-link" href="../../top10.html#team/{t["number"]}">View in the Top 10 display</a></p>' if t['powerRank'] <= 10 else ''}
      <h2>Team facts</h2><ul class="people"><li>{e(t['school'])} · {e(t['city'])}, {e(t['county'])} County</li><li>{e(t['affiliationNote'])}</li><li>{t['seasons']} FIRST seasons through 2026 · rookie year {t['rookieYear']}</li><li>Indiana EPA rank {t['stateEpaRank']} of {t['stateEpaCount']} · world {t['worldEpaRank']:,} of {t['worldEpaCount']:,}</li></ul>
    </div><aside>{follow(t)}{closest}{figure}{news_list(t['news'])}
      <h2>Stats &amp; profiles</h2><ul class="link-list"><li>{ext(t['links']['tba'], 'The Blue Alliance', 'text-link')}</li><li>{ext(t['links']['statbotics'], 'Statbotics', 'text-link')}</li><li>{ext(t['links']['first'], 'FIRST profile', 'text-link')}</li>{f"<li>{ext(t['links']['school'], 'School site', 'text-link')}</li>" if t['links'].get('school') else ''}</ul>
      <h2>Media</h2><p>Interview requests: <a href="mailto:{CONTACT}?subject={quote(f'Media request: {t["name"]} ({t["number"]})')}">{CONTACT}</a></p>
      <p><a class="text-link" href="../../press/media.html">Logos &amp; photos</a></p>
    </aside></div></section>"""
    titles = f"won {' and '.join(t['titles'])}; " if t["titles"] else ""
    description = f"{t['name']} (FRC {t['number']}), {t['school']}, {t['city']}: {record(t['record'])} in 2026, {titles}#{t['district']['rank']} in Indiana district points."
    return body, description


def ftc_page(t, result, rookie):
    display = result["displayAssets"]
    stats = [("New", "2026–27 rookie team")] if rookie else [(f"{t['opr']:.1f}", "Best OPR, 2025–26"), (f"{t['regionalRank']}/{t['regionalCount']}", "Rank at Indiana events"), (f"{t['worldRank']:,}", f"World OPR rank (of {t['worldCount']:,})")]
    stories = [s for s in result["news"]["stories"] if f"ftc{t['number']}" in s["teams"]]
    people = (t.get("students") or []) + (t.get("adults") or [])
    people_html = people_details(people, t.get("gaps", []))
    note = e(t.get("note") or t.get("qualification") or "")
    body = f"""{team_hero(t, 'FTC', stats, '', display)}
    <section class="section team-body"><div class="wrap team-columns"><div>
      <h2>About</h2><p>{note}</p><p class="muted">FTC (<i>FIRST</i> Tech Challenge) uses smaller robots than FRC and its own game; OPR ratings aren’t comparable to FRC’s EPA.</p>
      {upcoming_for(t['number'], result)}{people_html}
    </div><aside>{follow(t)}{news_list(stories)}
      <h2>Stats &amp; profiles</h2><ul class="link-list"><li>{ext(f"https://ftcscout.org/teams/{t['number']}", 'FTCScout', 'text-link')}</li>{f"<li>{ext(t['profileUrl'], 'FIRST profile', 'text-link')}</li>" if t.get('profileUrl') else ''}</ul>
      <h2>Media</h2><p>Interview requests: <a href="mailto:{CONTACT}">{CONTACT}</a></p>
    </aside></div></section>"""
    description = f"{t['name']} (FTC {t['number']}), {t.get('school', '')}: " + ("new FTC team for 2026–27." if rookie else f"best 2025–26 OPR {t['opr']:.1f}, {t['regionalRank']} of {t['regionalCount']} at Indiana events.")
    return body, description


def write_team_pages(result):
    cards = json.loads((HERE / "data/share-images.json").read_text(encoding="utf-8"))["cards"]
    entries = [(t, "FRC", frc_page(t, result)) for t in result["standings"]]
    entries += [(t, "FTC", ftc_page(t, result, False)) for t in result["ftc"]["teams"]]
    entries += [(t, "FTC", ftc_page(t, result, True)) for t in result["ftc"]["newTeams"]]
    for t, program, (body, description) in entries:
        url = f"{SITE}team/{t['number']}/"
        image = SITE + cards[str(t["number"])]["file"] if str(t["number"]) in cards else SITE + "assets/share/home.jpg"
        json_ld = {"@context": "https://schema.org", "@type": "SportsTeam", "name": t["name"], "sport": "Robotics",
                   "url": url, "memberOf": {"@type": "SportsOrganization", "name": f"FIRST {'Robotics Competition' if program == 'FRC' else 'Tech Challenge'}"},
                   "location": {"@type": "Place", "name": t.get("city", "")}, "sameAs": [l["url"] for l in t.get("teamLinks") or []]}
        folder = DIST / "team" / str(t["number"])
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "index.html").write_text(page_shell(f"{t['name']} · {program} {t['number']} · Northeast Indiana Robotics", description, image, url, body, json_ld), encoding="utf-8")
    return len(entries)


def write_pages(result, dnf):
    write_index(result, dnf)
    return write_team_pages(result)
