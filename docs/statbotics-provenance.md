# Statbotics snapshot provenance

The rankings in this project come from an **official Statbotics public cache for the 2026 season**, with an HTTP `Last-Modified` timestamp of **June 12, 2026, at 02:51:19 UTC**. The cache was retrieved for preservation on **October 22, 2026, at 04:29:17.883403 UTC**. These are the dates of the cache object and its retrieval, respectively; the ratings should not be described as a live October 2026 ranking. The exact response headers and checksums are preserved in [capture metadata](../artifacts/statbotics/snapshots/2026-10-22T04-29-18-072314Z_0059dfe792a0/metadata.json).

The re-fetch matched the previously recorded June 12 snapshot byte for byte. All 17 selected teams' EPA point estimates, state ranks, world ranks, and denominators match the frozen research baseline. The [comparison report](../artifacts/statbotics/snapshots/2026-10-22T04-29-18-072314Z_0059dfe792a0/rankings-comparison.json) records the result; the separate [baseline file](../artifacts/statbotics/expected-rankings-2026.json) records the expected values.

## Official endpoint and source evidence

The public data URL is:

<https://storage.googleapis.com/site_v1/team_years/2026>

Its provenance is established by the [official Statbotics source repository](https://github.com/avgupta456/statbotics), pinned to commit `169330ecef38a4f614356ac0b0caa156f2180021`:

| Official source | What it establishes |
| --- | --- |
| [frontend/src/constants.tsx](https://github.com/avgupta456/statbotics/blob/169330ecef38a4f614356ac0b0caa156f2180021/frontend/src/constants.tsx#L3-L15) | The production bucket URL is `https://storage.googleapis.com/site_v1`, and the configured season is 2026. |
| [frontend/src/api/teams.tsx](https://github.com/avgupta456/statbotics/blob/169330ecef38a4f614356ac0b0caa156f2180021/frontend/src/api/teams.tsx) | The team-year list path is `/team_years/${year}`. |
| [frontend/src/api/storage.tsx](https://github.com/avgupta456/statbotics/blob/169330ecef38a4f614356ac0b0caa156f2180021/frontend/src/api/storage.tsx) | The cache path is appended to the bucket URL. The response is inflated with `pako.inflate` and parsed as JSON. |
| [LICENSE](https://github.com/avgupta456/statbotics/blob/169330ecef38a4f614356ac0b0caa156f2180021/LICENSE) | Statbotics' source-code MIT license and attribution. |

The pinned `constants.tsx` also sets `DISABLE_GCS = true`. Consequently, these source files establish the **origin and format of the preserved cache**, not a claim that this cache is currently enabled in the live website. The dataset's June timestamp remains the freshness boundary used for this publication.

Copies of the two small API source files, relevant constants excerpts, and the MIT license are retained in [source evidence](../artifacts/statbotics/snapshots/2026-10-22T04-29-18-072314Z_0059dfe792a0/source-evidence/). A [source manifest](../artifacts/statbotics/snapshots/2026-10-22T04-29-18-072314Z_0059dfe792a0/source-evidence/manifest.json) gives each pinned URL, its complete upstream file checksum, saved-file checksum, and excerpt line ranges. The constants excerpt contains only the endpoint, season, and cache configuration required for provenance.

## What is preserved

The capture directory is:

`artifacts/statbotics/snapshots/2026-10-22T04-29-18-072314Z_0059dfe792a0/`

| File | Contents |
| --- | --- |
| [team-years-2026.json.zlib](../artifacts/statbotics/snapshots/2026-10-22T04-29-18-072314Z_0059dfe792a0/team-years-2026.json.zlib) | Exact 714,810 response bytes; one zlib-compressed JSON object containing 3,724 team-year records. |
| [team-years-2026-subset.json](../artifacts/statbotics/snapshots/2026-10-22T04-29-18-072314Z_0059dfe792a0/team-years-2026-subset.json) | All source fields for the fixed 17-team roster, plus the original top-level `year` object. The JSON is indented and its object keys are sorted; source values are preserved. |
| [metadata.json](../artifacts/statbotics/snapshots/2026-10-22T04-29-18-072314Z_0059dfe792a0/metadata.json) | Retrieval timestamp, selected HTTP headers, checksums, row counts, fixed team numbers, and provenance URLs. |
| [rankings-comparison.json](../artifacts/statbotics/snapshots/2026-10-22T04-29-18-072314Z_0059dfe792a0/rankings-comparison.json) | Flattened EPA/rank values, comparisons with the frozen baseline, and explicit change flags. |

The full decompressed response is 4,888,042 bytes and can be reproduced from the compressed file. A second large, globally decoded JSON file is not necessary for this repository. The 17-team decoded subset is 40,435 bytes. File sizes and hashes are recorded in the metadata linked above.

### Integrity values

```text
Exact compressed response SHA-256:
0059dfe792a03f257cf20d94580daab4d669e955e8a08c409d98acf80fd790b3

Full decompressed response SHA-256:
7050d91c815afaabbf58c84ff76559cf5c828c7394d83e3804cc379660e14274

Saved 17-team JSON subset SHA-256:
5fad005ee118f7d66c081af03cc9c22404f5fceccf688b0c5c91fad9cebcff63
```

## Metric fields and denominators

Statbotics describes EPA as **Expected Points Added**, a measure of a team's scoring contribution expressed in game points; see the [official repository introduction](https://github.com/avgupta456/statbotics). This publication copies Statbotics' reported values without calculating a replacement rating.

| Published value | Exact source field in each `team_years` row | Interpretation |
| --- | --- | --- |
| Team number | `team` | Join key for the separately verified school and leadership records. |
| Season | `year` | 2026 for every selected record. |
| EPA points | `epa.total_points.mean` | The point estimate reported in this snapshot. It is not computed here from the team's match scores. |
| State rank | `epa.ranks.state.rank` | Statbotics' EPA rank within the row's state. |
| State denominator | `epa.ranks.state.team_count` | The number of teams in that Statbotics ranking population. |
| World rank | `epa.ranks.total.rank` | Statbotics' overall EPA rank. |
| World denominator | `epa.ranks.total.team_count` | The number of teams in the overall ranking population. |

The snapshot reports **68 Indiana teams**, **530 Michigan teams**, **60 Ohio teams**, and **3,724 teams overall** in the corresponding rank objects. The selected Michigan and Ohio teams' state ranks therefore use their own state denominators. They are not Indiana ranks. These denominators are read from the source data; they should not be equated with a FIRST registration census or with the number of teams in this local study.

The full source also contains `district_points` and `district_rank`. Those fields describe FIRST district-points standings and are **not the EPA rankings used in this project**. The `competing` fields were not used to filter records. Source team names and `rookie_year` fields remain visible for audit purposes; school identities and participating-season counts are established separately by the project's school and FIRST-history research.

## Fixed study roster

The extraction selects these 17 team numbers, in the project's fixed research order:

```text
1501, 1720, 9119, 9431, 4982, 10434, 8103, 10332, 8742,
10172, 8431, 10411, 8432, 5559, 3777, 6556, 11407
```

The first 13 are the Indiana research roster. The final four are the separately reported Michigan/Ohio border cases. Geographic eligibility is decided in the main research data, not inferred by the Statbotics downloader. Extraction does not add new teams automatically or silently remove a team that becomes missing upstream.

This frozen snapshot still contains 1720 because it was captured before the roster changed. Team 1720 PhyXTGears is not part of The REFINERY and is not included. The research build reads only rostered teams from the snapshot.

## Reproduce and check the data

The [download and verification script](../scripts/fetch_statbotics.py) uses only the Python standard library. Run commands from the repository root.

Verify the committed compressed bytes and all 17 ranking records **without network access or file writes**:

```sh
python scripts/fetch_statbotics.py --input artifacts/statbotics/snapshots/2026-10-22T04-29-18-072314Z_0059dfe792a0/team-years-2026.json.zlib --check-only
```

Retrieve a fresh candidate capture and the pinned provenance source files:

```sh
python scripts/fetch_statbotics.py --download --include-source-evidence
```

Each saved capture receives a new UTC timestamp and checksum suffix under `artifacts/statbotics/snapshots/`. Existing files are opened exclusively and will not be overwritten. The script checks zlib completeness, duplicate team numbers, season consistency, fixed-roster coverage, finite EPA values, valid ranks/denominators, and differences from the frozen baseline.

Exit status `0` means the checked data matches the baseline. Exit status `1` means the data could not be retrieved or validated. Exit status `2` means the bytes, selected rankings, global row count, or available `Last-Modified` header differ and require review. A valid changed download is retained as a new candidate capture; the baseline, existing captures, and project roster remain unchanged. When validating a local file, HTTP headers are unavailable and the header comparison is reported as `null` rather than inferred.

The extraction and comparison JSON are deterministic for the same input bytes and baseline. Network capture metadata necessarily records the actual time and headers of each retrieval. Updating the published research after a changed capture requires an explicit review of the new data and its freshness.

## Attribution

The EPA model, source ratings, team-year data, and copied frontend excerpts are attributable to Statbotics and its contributors. The included source license retains **Copyright (c) 2020 Abhijit Gupta** and the MIT notice. School associations, geographic scope, leadership findings, and the local comparison are this project's research and should be assessed using their separate cited evidence. Hosting an official cache capture here does not imply endorsement by Statbotics or FIRST.
