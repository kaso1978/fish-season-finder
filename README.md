# Fish Season Finder

A mobile-first prototype that answers one question for a recreational angler:
**what can I legally fish for, right here, right now?**

Pick a point on the map or use your location. The app resolves which fisheries
management zone you're in and lists the species open on the selected date, with
the season, size and catch rules that apply.

> **PROTOTYPE — not an official source. Do not rely on it for actual fishing.**
> **FMZ 16** carries real rules: the zone-wide seasons and limits and the Lake
> Simcoe exception, transcribed by hand from the 2026 Ontario Fishing
> Regulations Summary. It is not an official copy, its boundary is approximate,
> and its river and stream exceptions are not loaded yet (the app lists them and
> warns). **FMZ 5, 15, 17 and 20 are invented sample data**, labelled as such
> on every screen. Always check the official summary at ontario.ca/fishing.

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

- **FMZ 16 (real 2026 rules).** The app opens on Lake Simcoe, which has its own
  rules for lake trout, whitefish, cisco, musky (closed all year) and perch
  (daily and possession limits). Tap inland (Kitchener, London) for the
  zone-wide rules. Pick **April 24** and then **April 25, 2026** to see the
  "fourth Saturday in April" trout opener resolve. Bass and walleye show their
  shared (combined) limits; trout also count toward the trout-and-salmon total.
- **Out on a Great Lake** (Lake Erie, Lake Huron) the app says which zone that
  is and that its rules aren't loaded, instead of falling back to FMZ 16.
- **Near a boundary** (the Toronto waterfront, the Lake Simcoe shore, the FMZ
  16/17 edge east of Lake Simcoe) the app warns that the boundary is
  approximate.
- **FMZ 17** (sample) still has the Whitepine Lake sub-area and the protected
  slot limit; **FMZ 5** (sample) has a season that wraps the new year.

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
  data-model.md       the first prototype's payload (sample zones still use it)
  roadmap.md          staged plan from prototype to production
```

## Scope

This is the **end-user experience only**. There is no backend, no
authentication, and no conservation-authority portal.

In the real product, data comes from a central database that authorities
populate through their own admin portal: they upload GIS boundaries for their
management zones and attach species, season and limit records to each one. The app
reads zone documents (`ZONE_DOCS` in `index.html`) shaped like what that
service will publish: a zone, the areas inside it, and a flat list of rules
(seasons, limits, restrictions, closures, notices) that the phone resolves for
a point and date. The fetch seam is marked with a comment.

See `docs/roadmap.md` for what comes next, and why validating the end-user model
comes before building any of it.

## Tech

Vanilla JavaScript, no framework, no build step. Leaflet (from cdnjs) with
OpenStreetMap tiles for the map; if it fails to load, the app degrades to a
notice and still renders the species data. Light and dark themes follow the
system setting.
