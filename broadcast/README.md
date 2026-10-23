# The REFINERY · NEI Robotics Top 10

A broadcast-style screen and media rundown for introducing regional robotics teams to football and baseball audiences. The hero message leads into a 2026 FRC Top 10, individual team profiles, and separate FTC features. Student and adult names retain their exact published roles and evidence dates.

The 2026–27 season preview teases the upcoming calendar while keeping the ranking screen a rewind of last season. Its [coverage plan](data/season-preview.json) separates confirmed events from proposed show dates and local planning windows. [Source checks](data/season-sources) retain the FIRST, FIRST Indiana, and REFINERY calendar evidence. The Indiana FTC countdown uses the current date in Fort Wayne and targets December 5, 2026 (44 days from the October 22 research date). R.Amp’s profile follows its first official match; the team’s debut assignment is not yet published.

The bottom [DNF invitation](https://horner.github.io/refintery-rankings/#dnf) means **Did Not Field. Yet.** It lists physical high-school campuses within 60 straight-line miles of downtown Fort Wayne where the reviewed sources do not verify a school-affiliated FTC or FRC team. Visitors can search schools, towns, districts, or superintendents, filter by state and school type, and start a school-specific email draft to The REFINERY. The draft requires the visitor to send it; the site does not record interest or contact schools automatically. A separate check-in list preserves former teams and documented community connections. [Methodology and the complete directory](dist/dnf-methodology.md), [frozen source evidence](data/dnf-research), and the [offline join](scripts/build_dnf.py) document campus scope, exact leadership roles, older directory years, and unresolved private-school names.

## Use the screen

[Open the public interactive site](https://horner.github.io/refintery-rankings/). Visitors can select a team in the Top 10, switch to its spotlight, explore FTC features, and open presenter notes and sources. The main URL opens directly on the Top 10 screen. Team links retain the ranking list alongside the selected details; the optional standalone spotlight has its own `#spotlight/<number>` route. Direct team links work, for example [North Side / 9119](https://horner.github.io/refintery-rankings/#team/9119) and [FTC features](https://horner.github.io/refintery-rankings/#ftc).

The [GitHub Pages workflow](../.github/workflows/pages.yml) rebuilds and verifies the research on every push to `main`, then publishes only `broadcast/dist`. The public site uses the same interactive files as the broadcast screen; PNGs remain optional downloads.

Serve the static files from the repository root:

```bash
python3 -m http.server 8765 --directory broadcast/dist
```

Open `http://localhost:8765`. Use the on-screen controls to select a team, switch between FRC and FTC, show presenter notes, enter fullscreen, and export a 1920 × 1080 graphic. Keyboard shortcuts are listed in the interface. Auto-cycle is on by default and advances FRC teams every 12 seconds; uncheck it to stop. It pauses while the page is hidden, on FTC features, during PNG export, and while a visitor hovers or focuses in the film room or on a frame replay link. The controls also link directly to the GitHub source. Presenter notes belong with the announcer; the clean frame is intended for the audience.

The [press kit](dist/press-kit.md) includes an opening script, team rundown, source qualifications, and a draft pitch. It does not send anything to a station.

Ready-to-use 1920 × 1080 graphics: [FRC Top 10](dist/exports/nei-top10-2026.png), [North Side spotlight](dist/exports/team-spotlight-9119.png), and [FTC features](dist/exports/ftc-features.png). The same browser export produces each graphic; dates and role qualifications remain on screen.

School marks appear before the identity text and team marks after it. List thumbnails are compact; team details and spotlights use larger images. Logos are also embedded in PNG exports. All ten FRC teams and both FTC features have verified team marks. PhyXTGears is a community team without a single school logo; R.Amp has no verified published team mark. The [logo manifest](data/logos.json) records source pages, asset URLs, retrieval dates, and checksums; [readable credits](dist/logo-credits.md) travel with the site.

## Close games to watch

Each FRC team has a clickable **video preview thumbnail** in the details panel on the Top 10 screen, alongside its close-match score and official result. The preserved YouTube thumbnail is cached locally so it also appears in PNG exports. All featured teams have a **Watch replay** link on their broadcast profile and a **Down to the wire** card below the screen. The card shows the event, phase, final Red/Blue alliance scores, all playing team numbers, the featured team's result, and an official FIRST scorecard link. Main selections use the closest eligible final-score margin; equally close playoffs take priority. A different closest playoff is available as an alternative. Wins and losses qualify, and scores include penalties. Changing alliance opponents are a matchup rather than a claim of a permanent rivalry.

The [thumbnail manifest](data/video-thumbnails.json) records the exact YouTube metadata source, original dimensions, retrieval time and SHA-256 for each preview.

The [complete match library](dist/match-highlights.md) covers all 17 FRC and 9 FTC research entries, including two pending entries without a prior-season match. All 12 played teams on the interactive screen have verified video links. FRC clips are joined to exact The Blue Alliance match pages; featured FTC replays open at official FIRSTINRobotics match chapters. [Frozen candidates, official scorecard checks, video evidence and source captures](data/match-research) make the selections inspectable. The [offline builder](scripts/build_matches.py) and [independent verifier](scripts/verify_matches.py) preserve the dated season scope and complete-field eligibility.

## What the ranking means

The Top 10 sorts the 13 FRC teams in The REFINERY's 12-county Northeast Indiana region by **2026 Statbotics EPA** in the frozen **June 12, 2026** source. A [fresh official FIRST Indiana district roster/profile screening](data/first-fin-scope-audit.json) supports the regional hometown selection. It does not establish workshop locations or student residences. The list is an independent performance ranking, not a voted poll or a live scoreboard.

FTCs 22331 and 25638 are separate 2025–26 features. Rookie 36124 is a 2026–27 watch item. FTC OPR and FRC EPA remain separate. A school-size division is an analogy only: FIRST does not assign FTC/FRC by enrollment; a school can offer either or both.

## Rebuild

```bash
python3 broadcast/scripts/build.py
python3 broadcast/scripts/verify.py
```

The [editorial inputs](data/editorial.json) preserve source-aware spotlight suggestions. The build reads the canonical FRC and FTC research and writes the shared browser data and press kit. No network access is needed for the build. Static assets are hosted locally with the page.

## Credits

- [The REFINERY](https://refineryrobotics.org/): logo and photograph of robots at its practice field, obtained from its public [website source repository](https://github.com/BioNanomics/REFINERY-site). The photograph is a facility image, not a selected-team portrait.
- [FIRST Global's Robotics Is a Sport campaign](https://first.global/sport/): the hero campaign phrase, presented with attribution and career-skills context.
- [FIRST](https://www.firstinspires.org/), [Statbotics](https://www.statbotics.io/), and [FTCScout](https://ftcscout.org/): program, team, and performance evidence documented in the main research.

The on-screen dates and role qualifications travel with the graphics. Confirm current-season appointments with the team when arranging a new interview.
