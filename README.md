# Fish Season Finder

A mobile-first prototype that answers one question for a recreational angler:
**what can I legally fish for, right here, right now?**

Pick a point on the map or use your location. The app resolves which fisheries
management zone you're in and lists the species open on the selected date, with
the season, size and catch rules that apply.

> **PROTOTYPE — sample data only. Do not use for actual fishing.**
> Every regulation in this repository is invented. The publisher name
> ("Provincial Fisheries Data Service") is fictional. Consult the official
> regulations for your jurisdiction.

## Quick start

```bash
node serve.js
# open http://localhost:8000
```

Or `python -m http.server 8000`. You can open `index.html` straight from disk,
but **geolocation won't work** — browsers only grant it over HTTPS or on
`localhost`. Everything else works either way.

## Testing on phones

Testers open the shared https:// link in Safari (iPhone) or Chrome (Android).
To install it like an app: Safari › Share › Add to Home Screen, or Chrome ›
menu › Add to Home screen / Install app. Updates arrive at the same link
automatically; the gear menu shows the version.

Press **Use my location** and allow location when asked. The sheet then shows
"Your GPS position · ±N m". If location is blocked, off, or too coarse, the app
explains how to fix it on that phone instead of guessing a spot.

## What to look at

The sample data was authored with deliberate teaching cases. Around September
2026 these read as intended:

- **FMZ 5** (far north-west) — lake trout closing within the week, and splake
  with a season that wraps the new year.
- **FMZ 16** (Lake Simcoe) — lake whitefish is the only closed species, opening
  in nine days.
- **FMZ 17** (Kawarthas) — tap inside the dashed box for a sub-area exception,
  and open Walleye for a protected slot limit drawn as a keep/release bar.
- **Change the date to January** and watch the counts and statuses re-evaluate.

## Structure

```
index.html            the entire app — one self-contained file, no build step
serve.js              zero-dependency dev server
sw.js                 service worker: network-first, so no one is stuck on an old version
manifest.webmanifest  makes it installable (Add to Home Screen)
icons/                app icons
CLAUDE.md             orientation for Claude Code: architecture, constraints
docs/
  prototype-brief.md  the original brief this was built from
  data-model.md       payload spec + what authorities must supply and validate
  roadmap.md          staged plan from prototype to production
```

## Scope

This is the **end-user experience only**. There is no backend, no
authentication, and no conservation-authority portal.

In the real product, data comes from a central database that authorities
populate through their own admin portal: they upload GIS boundaries for their
management zones and attach species, season and limit records to each one. The
hard-coded `API_RESPONSE` object in `index.html` is shaped like that service's
response, so the fetch layer can be swapped in without touching the UI. The seam
is marked with a comment.

See `docs/roadmap.md` for what comes next, and why validating the end-user model
comes before building any of it.

## Tech

Vanilla JavaScript, no framework, no build step. Leaflet (from cdnjs) with
OpenStreetMap tiles for the map; if it fails to load, the app degrades to a
notice and still renders the species data. Light and dark themes follow the
system setting.
