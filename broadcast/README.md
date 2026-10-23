# The REFINERY · Northeast Indiana Robotics

A responsive sports-style site and a separate Top 10 display introduce regional robotics teams to football and baseball audiences. The home page covers all 13 regional FRC teams, with district standings, an EPA power-ranking sort, team pages, match replays, FTC features, a calendar, and a press kit. Student and adult names retain their exact published roles and evidence dates.

The 2026–27 season preview looks ahead while keeping 2026 rankings and results clearly dated. Its [coverage plan](data/season-preview.json) separates confirmed events from proposed show dates and local planning windows. [Source checks](data/season-sources) retain the FIRST, FIRST Indiana, and REFINERY calendar evidence. Event dates, entry lists, and rookie-team assignments retain their published status; a planning date is not a confirmed competition assignment.

## Browse and display

[Open the public site](https://horner.github.io/refintery-rankings/) for desktop and phone browsing. The home page opens on the responsive season overview. Its standings include all 13 regional FRC teams and can be sorted by official FIRST Indiana district rank or frozen Statbotics EPA. Expand a team for details or open its static team page, such as [North Side / 9119](dist/team/9119/). FTC features, the event calendar and downloadable `.ics` file, media resources, and the DNF directory remain on the home page.

The separate [Top 10 · Big screen display](dist/top10.html) uses the same generated data and the original ten highest-EPA teams. Its fluid layout makes room for the ranking and selected-team spotlight on a large desktop screen and adapts to a phone. Select a team for its profile and cached replay preview, enter fullscreen, or export a 1920 × 1080 PNG. Optional cycling advances the selected team every 12 seconds and is **off by default**. Replay interaction and PNG export pause cycling.

Direct `#team/<number>` links continue to open home-page standings details. Legacy `#spotlight/<number>`, `#board`, and `#broadcast` links open the dedicated Top 10 display. A direct display selection uses `top10.html#team/<number>`.

The [press kit](dist/press/) supplies facts, story suggestions, contact information, and downloadable material for media coverage. The [Markdown announcer rundown](dist/press-kit.md) includes an opening script, team introductions, source qualifications, and a draft pitch. Neither sends anything to a station.

School marks and team marks identify the teams. All ten original FRC features and both played FTC features have verified team marks. PhyXTGears is a community team without a single school logo; R.Amp has no verified published team mark. The [logo manifest](data/logos.json) records source pages, asset URLs, retrieval dates, and checksums; [readable credits](dist/logo-credits.md) travel with the site.

## Preview locally without publishing

The complete site build requires **Python 3.12+**. From the repository root, rebuild and verify with:

```bash
python3 broadcast/scripts/build.py
python3 broadcast/scripts/verify.py
```

Then serve the generated files on the loopback interface:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory broadcast/dist
```

Open `http://127.0.0.1:8765/` for the responsive site and `http://127.0.0.1:8765/top10.html` for the display. Local builds and this server do not publish anything. Use this local workflow to review a change before deployment. The [GitHub Pages workflow](../.github/workflows/pages.yml) rebuilds and verifies on every push to `main`, then publishes only `broadcast/dist`.

The home-page source is [`templates/index.html`](templates/index.html). Edit that template and the page generator [`scripts/build_pages.py`](scripts/build_pages.py), then rebuild; `dist/index.html` and `dist/team/*/index.html` are generated files. The display's HTML, JavaScript, and styles live in `dist/top10.html`, `dist/top10.js`, and `dist/top10.css`. The [editorial inputs](data/editorial.json) preserve source-aware spotlight suggestions. The build reads the canonical FRC and FTC research and writes shared browser data, static pages, calendar files, and media material. It needs no network access; the site hosts its static assets locally.

## Close games to watch

The Top 10 display, home-page team details, and static team pages retain clickable **video preview thumbnails** for the original ten FRC features. Each preview pairs the selected close match with its score and official result. Preserved YouTube thumbnails are cached locally and included in the display's PNG export. The [thumbnail manifest](data/video-thumbnails.json) records the exact metadata source, original dimensions, retrieval time, and SHA-256 for each preview.

Replay coverage identifies the event, phase, final Red/Blue alliance scores, all playing team numbers, the featured team's result, and an official FIRST scorecard link. Main selections use the closest eligible final-score margin; equally close playoffs take priority. A different closest playoff is available as an alternative. Wins and losses qualify, and scores include penalties. Changing alliance opponents are a matchup rather than a claim of a permanent rivalry.

The [complete match library](dist/match-highlights.md) covers all 17 FRC and 9 FTC research entries, including two pending entries without a prior-season match. FRC clips are joined to exact The Blue Alliance match pages; featured FTC replays open at official FIRSTINRobotics match chapters. [Frozen candidates, official scorecard checks, video evidence, and source captures](data/match-research) make the selections inspectable. The [offline builder](scripts/build_matches.py) and [independent verifier](scripts/verify_matches.py) preserve dated season scope and complete-field eligibility.

## What the standings and ranking mean

The home page's **district standings** use official FIRST Indiana district points and ranks. Win-loss records, events, and awards come from The Blue Alliance. These are different measures from EPA; district rank and EPA rank must not be described interchangeably.

The **power ranking** and dedicated **Top 10** sort the 13 FRC teams in The REFINERY's 12-county Northeast Indiana region by **2026 Statbotics EPA** from the frozen **June 12, 2026** source. A [FIRST Indiana district roster/profile screening](data/first-fin-scope-audit.json) supports the regional hometown selection. It does not establish workshop locations or student residences. The Top 10 is an independent performance ranking, not a voted poll or a live scoreboard. The broader research directory contains 17 FRC teams within 60 straight-line miles; that geographic study and this 13-team regional cohort have different scopes.

FTCs 22331 and 25638 are separate 2025–26 features. Rookie 36124 is a 2026–27 watch item. FTC OPR and FRC EPA remain separate. A school-size division is an analogy only: FIRST does not assign FTC/FRC by enrollment; a school can offer either or both.

## Schools ready to start a team

The [DNF invitation](dist/index.html#dnf) means **Did Not Field. Yet.** It lists physical high-school campuses within 60 straight-line miles of downtown Fort Wayne where the reviewed sources do not verify a school-affiliated FTC or FRC team. Secure and residential facilities are excluded from invitations. Visitors can search and filter the directory and use its interest links to contact The REFINERY. Contact drafts require the visitor to send them; the site does not record interest or contact schools automatically. A separate check-in list preserves former teams and documented community connections.

[Methodology and the complete directory](dist/dnf-methodology.md), [frozen source evidence](data/dnf-research), and the [offline join](scripts/build_dnf.py) document campus scope, exact leadership roles, older directory years, and unresolved private-school names.

## Credits

- [The REFINERY](https://refineryrobotics.org/): logo and photograph of robots at its practice field, obtained from its public [website source repository](https://github.com/BioNanomics/REFINERY-site). The photograph is a facility image, not a selected-team portrait.
- [FIRST Global's Robotics Is a Sport campaign](https://first.global/sport/): the hero campaign phrase, presented with attribution and career-skills context.
- [FIRST](https://www.firstinspires.org/), [The Blue Alliance](https://www.thebluealliance.com/), [Statbotics](https://www.statbotics.io/), and [FTCScout](https://ftcscout.org/): program, team, results, and performance evidence documented in the main research.

The on-screen dates and role qualifications travel with the graphics. Confirm current-season appointments with the team when arranging a new interview.
