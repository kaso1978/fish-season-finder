# CLAUDE.md

Guidance for Claude Code working in this repository.

## What this is

**Fish Season Finder** — a mobile-first prototype that answers one question for a
recreational angler: *what can I legally fish for, right here, right now?*

The user picks a point on a map (or uses their location), and the app resolves
which fisheries management zone that point falls in and lists the species that
are open on the selected date, with the rules that apply.

**This repository currently contains the end-user prototype only.** It is a
front-end demo with hard-coded data (real 2026 rules, transcribed by hand). There is no backend, no
authentication, and no conservation-authority portal. That is deliberate — see
`docs/roadmap.md`.

## Running it

```bash
node serve.js          # then open http://localhost:8000
# or
python -m http.server 8000
```

Open `index.html` directly from disk and most things work, but **geolocation
will not** — browsers only grant it in a secure context. `localhost` counts as
secure; a `file://` path does not. Always use the dev server when testing
"Use my location".

## Architecture

Everything lives in **`index.html`** — one self-contained file, ~1,300 lines, no
build step, no framework, no dependencies beyond Leaflet from a CDN.

Keep it that way unless the user explicitly asks to split it up. The single file
is a feature: it can be emailed, dropped on any static host, or opened straight
from disk, which is what makes it useful as a prototype.

The file is divided by banner comments. In reading order:

| Section | What lives there |
| --- | --- |
| `DATA LAYER` | `GEO` shapes, `SPECIES`/`GROUPS` catalogue, the hand-written `FMZ16` zone document, `ZONE_DOCS_GEN` (the other 19 zones, generated), `ZONE_DOCS` |
| `FISH SILHOUETTES` | Hand-drawn generic SVG paths, one per body shape |
| `DATE + SEASON LOGIC` | `resolveDate()` (date expressions), `intervals()`, `evaluate()`, `statusLine()` |
| `GEOMETRY` | Point in Polygon/MultiPolygon (holes aware), `zonesAt()`, `areasAt()` |
| `WHICH RULE WINS` | `resolveAt(doc, lat, lng, date)`: provisions → species cards |
| `APP STATE` | The single `state` object; all state is in memory |
| `MAP` | Leaflet init, zone layers, pin, `setPin()` |
| `BOTTOM SHEET` | Drag/snap behaviour for the sliding sheet |
| `RENDER` | Sheet header + species list rendering |
| `SPECIES DETAIL` | The full-screen slide-over, season timeline, size-limit bar |
| `SAVED SPOTS` | In-memory saved locations |
| `UI WIRING` | All event listeners |
| `INIT` | `boot()` |

### The part that matters most

`resolveAt()` and `evaluate(season, date)` are the core of the product. Every
status label, count, filter and timeline derives from them.

- A season is a list of windows, each `[start, end]` **date expressions**:
  `fixed` (month/day), `nth_weekday` ("fourth Saturday in April", with optional
  `offset_days` for "Friday before"), or `last_day` of a month. They are
  resolved for the year being viewed, so moving openers are right every year.
- Windows whose end resolves before their start **wrap the new year**.
  Intervals from neighbouring years are merged, so "Jan 1 to Mar 31 and second
  Saturday in May to Dec 31" is stored as one window and reads as one stretch.
- `closedAllYear: true` means closed. A season with no windows that isn't
  marked closed is a data error and shows as "Season not published", never open.
- Seasons and limits have one winner per slot (type + species or group): the
  most specific area wins (waterbody > group of waters > zone), then a rule
  naming the species beats one naming its group. Group (aggregate) limits apply
  alongside species limits ("also counts toward"). Restrictions, closures and
  notices all apply together.
- Species sharing a group season and identical limits show as one card
  ("Walleye and Sauger"), as the summary prints them.

If you change season handling, re-check: year-round, single window, multiple
windows, a wrapping window, an nth-Saturday opener (Apr 24 vs Apr 25, 2026 in
Toronto), and closed all year (Lake Simcoe musky).

## Hard constraints — do not break these

1. **Real data is always labelled as an unofficial transcription.** Every
   zone holds real 2026 zone-wide rules transcribed by hand (FMZ 16 also has
   the Lake Simcoe exception). There is no sample data any more; if invented
   data ever comes back it must be badged `sample`. The `PROTOTYPE ·
   NOT OFFICIAL` banner stays visible on every screen, every zone shows a badge
   saying which kind of data it is (`meta.dataStatus`: `transcribed` or
   `sample`), and the footer and species detail say where the rules came from.
   Never present sample numbers as real, and never present the transcription
   as official. This app tells people what is legal; looking authoritative
   while being wrong is the main risk in the whole project.
2. **No authority logos or wordmarks, and no implied endorsement.** The real
   data cites its source document (the 2026 Ontario Fishing Regulations
   Summary) by name and page; it does not claim the ministry as publisher.
   Portal design files (schema, data-structure notes) stay out of
   this public repo.
3. **No `localStorage` / `sessionStorage`.** Saved spots live in
   `state.spots` for the page session only. This was a brief constraint so the
   file renders correctly in sandboxed preview panes.
4. **Single file, no build step.** The app is still all in `index.html`.
   `manifest.webmanifest`, `sw.js` and `icons/` only make it installable and
   usable offline when hosted; the page works without them (e.g. from disk).
   `boundaries/` is tooling only (download and simplify the official zone
   layer); the app never loads anything from it at runtime.
5. **Colour is never the only signal.** Open/closed status always carries an
   icon and a text label alongside the green/grey treatment.
6. **Never guess the user's location.** Which rules apply depends on where the
   angler is standing. If GPS fails, say why and how to fix it; never drop a
   pin somewhere and present it as theirs. Always show where the pin came from
   (GPS with ±accuracy, a tapped point or a saved spot), and
   warn when the accuracy circle crosses a zone or sub-area boundary. Because
   boundaries are approximate, also warn (for any pin, tapped or GPS) when the
   point is within a geometry's `toleranceM` of a zone or lake edge, and when
   it falls in an `advisory` area. A point out on a Great Lake must resolve to
   that lake's zone, never to FMZ 16. A point outside every zone shows
   "outside Ontario's fishing zones" and a list of zones; a zone picked from
   the list is always labelled "chosen by you, not by GPS", and the pick is
   dropped once the pin moves more than 20 km away (`PICK_KEEP_M`).

## Location (GEOLOCATION section)

`locate()` uses `watchPosition` with high accuracy, keeps the best fix for up
to 10 s (stops early at ±25 m), and gives up after 30 s. Each failure kind
(denied, unavailable, timeout, not HTTPS, unsupported) opens a help dialog with
iPhone/Android-specific steps. `nearBoundary()` samples points around the
accuracy circle to detect a nearby zone or sub-area edge, and flags spots where
published zones overlap. Location only works over HTTPS or `localhost`; the
permission prompt is only ever triggered by the button, except that a returning
user who already granted it is located on load.

## Releasing

The hosted copy is what testers use. To ship a change: bump `APP_VERSION` in
`index.html` and `VERSION` in `sw.js` to the same value, then publish. The
service worker is network-first, so testers get the new version on their next
open with a connection, at the same link. The version shows in the settings
(gear) menu so testers can report which build they're on.
Anyone with the app already open sees a "new version available · Reload"
banner within 5 minutes or when they return to the app, because it compares
its `APP_VERSION` with the one in the live `index.html`.

## Data shape

`ZONE_DOCS` holds one **zone document** per zone, the shape the authority
portal will publish: `meta` (source, edition, effective dates, `dataStatus`),
`zone` (code, name, geometry, `geometryStatus`, `toleranceM`), `areas` (lakes,
groups of waters, `advisory` areas that only warn) and a flat list of
`provisions` (`season` | `limit` | `restriction` | `closure` | `notice`, each
with a stable `key`, an `areaId` and a `target` of `{species}`, `{group}` or
null for all species). Limits carry licence (sport/conservation) and kind
(catch/possession); size rules are length bands with a max count. The
commented-out `fetch()` at the top of `DATA LAYER` marks the seam.

A limit provision can carry `when` (windows, same date expressions as a
season) plus `whenText`: it only exists on those dates and, at equal rank,
beats the undated one for the same slot (e.g. "must be less than 35 cm from
January 1 to June 30"). `residentNote` holds the non-Canadian-resident limits
the summary prints for FMZ 5. Size bands may carry `licence` when they apply
to one licence only; the detail page then draws one bar per licence.

FMZ 16 is hand-written. Zones 1–15 and 17–20 are generated from the
summary's zone-wide tables by a one-off script and checked by hand; edit them in `index.html` directly, and keep the
`text` field exactly as printed. `docs/data-model.md` is the old 0.3 shape and
is superseded.

## Known limitations

- **Exceptions are only loaded for FMZ 16 and 17 (trial).** Every zone has
  its zone-wide seasons and limits and general rules. In FMZ 16 and 17 the
  species exceptions, waterbody exceptions and fish sanctuaries are loaded too
  (153 places, `EXC16_*` / `EXC17_*`, built by `boundaries/exceptions/`). Each
  is an area with `exc:true` and a `precision`: `drawn` (official hydro shape
  cut at both printed ends: its rules replace the zone-wide ones when the pin
  is on it), `approx` (shown as "may apply here") or `point` (only listed as
  nearby). Anything within 2 km (`EXC_NEAR_M`) is listed; an active sanctuary
  under the pin shows a red "No fishing here now" block. Each place also
  carries the province's `ogfId` from the "Recreational fishing regulations
  data" open dataset (`boundaries/fetch_regs.py` + `exceptions/official.py`),
  and places with no hydro shape sit at the official sanctuary point
  (`pointSource:'official'`). The other 18 zones still list the affected
  waters and warn.
- **The rules run to Dec 31, 2026** (`meta.effectiveTo`). After that the app
  still resolves dates but shows a banner that the 2027 summary may differ.
- **Zone boundaries are simplified.** All 20 zones come from the official
  Land Information Ontario "Fisheries Management Zone" layer (edition
  2026-10-22, Open Government Licence – Ontario; the footer carries the
  required attribution). `boundaries/simplify_fmz.py` simplifies it with
  shared borders kept aligned, every point within ~170 m of the official
  line, so each zone has `toleranceM: 200`. Simplification leaves a few tiny
  overlaps and self-crossings along borders; `nearBoundary` reports a spot
  in an overlap as "right on a zone line". `boundaries/HOW-TO-UPDATE-ZONES.md`
  covers downloading a new edition (`fetch_fmz.py`, run on Andrew's PC: the
  LIO servers are blocked from the cloud) and loading it. Lake Simcoe and
  its watershed advisory are still Natural Earth plus hand drawing.
- **Leaflet loads from cdnjs.** If it fails, the app degrades to a "Map
  unavailable" notice and still renders species data — preserve that fallback if
  you touch the `MAP` section.

## Conventions

- Vanilla JS, no framework. No dependencies added without asking.
- Two-space indent, single quotes in JS, double quotes in HTML attributes.
- CSS custom properties for all colours, defined once on `:root` and redefined
  under `prefers-color-scheme: dark`. Never hard-code a hex outside `:root`.
- All user-facing strings pass through `esc()` before reaching `innerHTML`.

## What not to build yet

Do not add the conservation-authority portal, user accounts, licence purchasing,
catch logging, or analytics. The prototype's value is that it stays small enough
to change your mind about. `docs/roadmap.md` has the intended order of work.
