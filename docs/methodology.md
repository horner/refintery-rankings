# Methodology and field definitions

## Scope

This compilation follows the original 17-team research roster: 13 Indiana FIRST Robotics Competition (FRC) teams and four nearby Michigan/Ohio teams in the Fort Wayne study area. The radius is 60 straight-line miles, not 60 driving miles. The [geographic verification](geographic-scope.md) documents the origin, official school or host addresses, geocoding, calculations, and boundary limitations.

The original request concerned Statbotics rankings, so this dataset covers FRC. It does not claim a census of FIRST Tech Challenge, FIRST LEGO League, other robotics programs, or historically inactive teams. Community teams are identified as community programs rather than assigned an exclusive high-school affiliation.

## Ranking metric and time

Statbotics Expected Points Added (EPA) estimates a robot's scoring contribution. The reported value is `epa.total_points.mean` in the preserved 2026 team-year records. Higher EPA indicates higher estimated scoring performance. State and world ranks come directly from `epa.ranks.state` and `epa.ranks.total`; lower rank numbers are better. Denominators are copied from those same objects.

The official cache response has HTTP `Last-Modified: Fri, 12 Jun 2026 02:51:19 GMT`. It was retrieved again on October 22, 2026 and matched the values used in the original research. These are dated snapshot rankings, not a claim about a live October leaderboard. The cache may contain other stale fields such as a next-event indicator; this report uses only the explicit rating and ranking fields. Full provenance, field paths, source code, response headers, and checksums are in [Statbotics provenance](statbotics-provenance.md).

The study's local order is a sort of the selected teams by EPA. It is not another official Statbotics ranking. Keep `district_rank` separate: that field represents a different ranking system and is not used as an EPA rank.

## Years active

The auditable measure is **recorded FIRST seasons through 2026**. The season history extractor cross-checks the year headings against the season-specific team-page links. It counts every recorded year through 2026, includes registered pandemic seasons without matches, and excludes 2027 entries already present on many pages.

This is not a guarantee that a team played matches in every counted year. For example, the captured FIRST records explicitly flag Homestead 4982 in 2020 and 2021, and Waldron 6556 in 2021, as registered without competition. Those facts are retained in the history artifact and combined JSON.

The official rookie year is stored separately. East Noble 8431 and 8432 both have rookie year 2020, but their recorded histories begin in 2025 and 2026 respectively. The directory therefore shows two and one recorded seasons, not seven. Inclusive season counts can also differ from an anniversary expressed in elapsed calendar years; 2006 through 2026 contains 21 season labels.

## School affiliation

The display name prioritizes the high school. FIRST season pages and school/team sources provide the team-number link. Huntington 1501 has a Huntington North connection and a county 4-H community program. PhyXTGears 1720 and Lima 3777 are community programs; their records do not imply exclusive enrollment from a single high school. The three East Noble teams share a school but retain distinct team numbers, season histories, rankings, and leadership gaps.

## Adult and student leadership

Each person is stored with an exact documented role, evidence date or an explicit undated status, source URLs, evidence status, and qualifying notes. A source's publication date is not automatically the start or end date of an appointment. A name checked in October 2026 does not by itself establish a 2026–27 appointment.

An overall captain, assistant captain, drive-team captain, student representative, outreach officer, mentor, coach, and organization president remain distinct roles. Quoted students and former captains are not promoted to current captains. Partial names remain partial. Contradictory spelling is retained as a source conflict. An empty people list means no qualifying identification was verified, not that the team has no leader.

Current-season confirmation gaps are explicit. Snider's Nick Sims and Carroll's Nieng Mang have evidence tied to the completed 2026 season or 2025–26 school year. Homestead's 2026–27 captain (Jake) and its coaches, and Carroll's coaching history, were confirmed directly by a team mentor on November 10, 2026 (status `confirmed_by_team_mentor` or `confirmed_by_person`). FWCS's February board slides designate representatives, not captains. Ava Stanley's public team-spokesperson role does not establish whether she was an adult or student.

## Evidence and preservation

The initial work was an inline research answer; no standalone report or spreadsheet existed then. This repository assembles that research into durable files and records fresh capture times. The June ranking timestamp is kept separate from the October preservation date. It does not reconstruct an unavailable original browser session or imply that newly captured files were saved earlier.

The repository preserves the exact compressed official Statbotics response, its decoded 17-team subset, pinned source-code evidence, factual FIRST history extracts with page hashes, geographic evidence, structured leadership findings, and a catalog of source links. Linked third-party PDFs are identified by URL and checksum. News articles, profiles, social posts, podcasts, and school presentations remain at their source URLs rather than being copied in full.

## Updates

The curated roster and leadership records are inputs. Generated reports and exports are rebuilt from those records and the explicitly selected frozen captures. A new download writes a new capture directory. Changing the reporting season, roster, geographic rule, or leadership evidence requires an explicit data change and review of the corresponding documentation. Do not silently replace the June snapshot while keeping its date label.
