# The Blue Alliance API: keeping results and the calendar current

The site's FRC records, event finishes, awards and district standings come from [The Blue Alliance](https://www.thebluealliance.com/) (TBA). The calendar combines TBA (FRC events), [FTCScout](https://ftcscout.org/) (FTC events, no key needed) and hand-checked entries.

**Status:** the scripts and the refresh workflow are ready, but **no API key is set yet**. Until one is added:

- FRC results stay at the October 22, 2026 capture in [`broadcast/data/tba/results-2026.json`](../broadcast/data/tba/results-2026.json), taken from TBA's public team pages.
- FRC calendar entries come from [`broadcast/data/calendar-manual.json`](../broadcast/data/calendar-manual.json).
- FTC calendar entries still refresh from FTCScout.

## 1. Get a key

1. Sign in at <https://www.thebluealliance.com/account>.
2. Under **Read API Keys**, add a key. A description like "refintery-rankings site" is fine.
3. Copy the key. It's read-only, but treat it like a password and don't commit it.

## 2. Add the key

**On your computer** (for running the scripts yourself):

```bash
cp tba.env.example tba.env
```

Open `tba.env` and paste the key after `TBA_AUTH_KEY=`. `tba.env` is ignored by git and skipped by the checksum check. Or set it for one shell session instead:

```bash
export TBA_AUTH_KEY=your-key-here
```

On Windows PowerShell: `$env:TBA_AUTH_KEY = "your-key-here"`.

**On GitHub** (for the automatic refresh): go to the repository **Settings → Secrets and variables → Actions → New repository secret**, name it `TBA_AUTH_KEY`, and paste the key. Also turn on **Settings → Actions → General → Allow GitHub Actions to create and approve pull requests**, so the refresh can open its pull request.

## 3. What uses the key

| Script | Without a key | With a key |
|---|---|---|
| [`scripts/fetch_calendar.py`](../scripts/fetch_calendar.py) | Refreshes FTC events from FTCScout; FRC events from `calendar-manual.json` | Also pulls every Indiana FRC district, state and offseason event from TBA |
| [`scripts/fetch_tba.py`](../scripts/fetch_tba.py) | Stops with a message | Pulls each Northeast Indiana team's events, qualifying rank and record, playoff result, awards, district rank and points, website and social accounts |

Both read the key from `TBA_AUTH_KEY`, or from `tba.env` if that variable isn't set (see [`scripts/tba_key.py`](../scripts/tba_key.py)).

TBA endpoints used, all read-only:

- `/team/frc{n}`
- `/team/frc{n}/social_media`
- `/team/frc{n}/events/{year}/simple`
- `/team/frc{n}/events/{year}/statuses`
- `/team/frc{n}/awards/{year}`
- `/district/{year}fin/rankings`
- `/events/{year}/simple`

## 4. Refresh by hand

```bash
python scripts/fetch_calendar.py
python scripts/fetch_tba.py --season 2026 --output broadcast/data/tba/results-2026.json
python scripts/build.py && python ftc/scripts/build.py && python broadcast/scripts/build.py
python broadcast/scripts/build_share_images.py && python broadcast/scripts/build.py   # redraw team share cards (needs Pillow)
python scripts/verify.py --write-checksums
python scripts/verify.py && python ftc/scripts/verify.py && python broadcast/scripts/verify.py
```

Review the diff before committing. A refresh should only change dates, results and counts you expect.

## 5. Automatic refresh

[`.github/workflows/refresh-data.yml`](../.github/workflows/refresh-data.yml) runs every Monday at 9 a.m. ET (after competition weekends). You can also start it from the **Actions** tab with **Run workflow**. It:

1. Refreshes the calendar, and the FRC results if the `TBA_AUTH_KEY` secret exists.
2. Rebuilds the site, rewrites the checksums and runs every verify step.
3. Opens a pull request named "Refresh results and calendar (date)" if anything changed.

Nothing goes live until someone reviews and merges that pull request. The publish workflow then deploys it as usual. If nothing changed, no pull request is opened.

## 6. Season rollover (each January)

When the 2027 FRC season starts:

1. Run `fetch_tba.py --season 2027 --output broadcast/data/tba/results-2027.json`.
2. Point `broadcast/scripts/build.py` and `broadcast/scripts/verify.py` at `results-2027.json`.
3. Change `--season 2026` to `2027` in the refresh workflow.
4. Update the season constants at the top of `scripts/fetch_calendar.py` (`FTC_SEASON`, `FRC_YEAR`, `FRC_OFFSEASON_YEAR`) and rename the calendar file for the new season.

Keep the 2026 file as the final record of that season.
