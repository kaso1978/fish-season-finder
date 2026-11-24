# How to update the fishing zone boundaries

The app needs to know where each of Ontario's 20 Fisheries Management Zones
(FMZs) begins and ends. Those lines come from an official government map
layer. This folder holds a copy of that layer and a small script that
downloads it again whenever you want.

## Where the data comes from

- **Dataset:** "Fisheries Management Zone", published by Land Information
  Ontario (LIO)
- **Page:** https://geohub.lio.gov.on.ca/datasets/eafadbf2d09448beb483da1e7dfba86d
- **Item ID:** `eafadbf2d09448beb483da1e7dfba86d`
- **Licence:** Open Government Licence – Ontario
  (https://www.ontario.ca/page/open-government-licence-ontario). We may use
  and share it, and we credit the source.

## How to run the script

You need Python, which is already installed on this computer.

1. Open the `boundaries` folder in File Explorer.
2. Click the address bar, type `powershell`, and press Enter. A blue window
   opens in this folder.
3. Type this and press Enter:

   ```powershell
   py fetch_fmz.py
   ```

4. Wait. The file is large (about 110 MB) and arrives a few zones at a
   time, so it can take a few minutes. If the government server is busy you
   may see "request failed … retrying"; that is normal, the script tries
   again on its own.

When it finishes it prints `Saved …` and the list of zones (1 to 20).

The new files land in `boundaries\official`, named after the date the
government last changed the data, for example:

- `fmz_official_2026-10-22.geojson`: the boundaries
- `fmz_official_2026-10-22.meta.json`: where they came from, when they were
  downloaded, the zone list and a fingerprint (SHA-256) of the file

Older downloads are **never** overwritten. Each edition is kept side by side.

## How to tell whether a newer edition exists

To just check, without downloading, run:

```powershell
py fetch_fmz.py --check
```

It prints one of:

- **"NEWER EDITION AVAILABLE"**: the government has changed the data since
  your latest download. Run `py fetch_fmz.py` to get it.
- **"matches your latest file - no newer edition"**: nothing to do.

A changed date does not always mean the lines moved. The government
sometimes only updates the record's details. Claude can compare the two
editions for you.

## Make the phone copy

After downloading a new edition, run `py simplify_fmz.py` to make the phone
copy (`fmz_app_<date>.geojson`), then tell Claude.

```powershell
py simplify_fmz.py
```

## What to tell Claude afterwards

After a new download, say:

> New FMZ boundaries are in boundaries\official, please load them into the app.

## Which copy counts

The file in `boundaries\official` is the **authoritative copy**. Leave it
exactly as downloaded. The app can't use it directly because it is far too
detailed for a phone. Claude makes a **simplified copy** from it for the app,
and the app warns people near zone edges because of that simplification. If
there is ever a doubt about which side of a line a spot is on, the original
file decides.

## For whoever loads it into the app (usually Claude)

1. Replace the `fmz1` … `fmz20` entries in the `GEO` block of `index.html`
   with the geometry of each feature in the new `fmz_app_<date>.geojson`
   (property `zone` gives the number).
2. Clip `GEO.simcoe` and `GEO.shed` to the new `fmz16` so they stay inside it.
3. Update `FMZ_BOUNDARY` (edition date, and `simplifiedM` from `maxShiftM` in
   the `.meta.json`). Keep each zone's `toleranceM` a little above that.
4. Commit the new `fmz_app_<date>.geojson`, its `.meta.json` and
   `official/fmz_official_<date>.meta.json`. Never commit the large official
   `.geojson`: `.gitignore` keeps it out.
5. Bump `APP_VERSION` in `index.html` and `VERSION` in `sw.js`, test, publish.
