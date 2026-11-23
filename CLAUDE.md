# CLAUDE.md

Guidance for Claude Code working in this repository.

## What this is

**Fish Season Finder** — a mobile-first prototype that answers one question for a
recreational angler: *what can I legally fish for, right here, right now?*

The user picks a point on a map (or uses their location), and the app resolves
which fisheries management zone that point falls in and lists the species that
are open on the selected date, with the rules that apply.

**This repository currently contains the end-user prototype only.** It is a
front-end demo with hard-coded sample data. There is no backend, no
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
| `DATA LAYER` | `GEO` shapes, `SPECIES`/`GROUPS` catalogue, the real `FMZ16` zone document, `SAMPLE_ZONES` (invented) and `fromLegacy()`, `ZONE_DOCS` |
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

1. **Real and invented data are always labelled.** FMZ 16 holds real 2026
   rules transcribed by hand; every other zone is invented. The `PROTOTYPE ·
   NOT OFFICIAL` banner stays visible on every screen, every zone shows a badge
   saying which kind of data it is (`meta.dataStatus`: `transcribed` or
   `sample`), and the footer and species detail say where the rules came from.
   Never present sample numbers as real, and never present the transcription
   as official. This app tells people what is legal; looking authoritative
   while being wrong is the main risk in the whole project.
2. **No authority logos or wordmarks, and no implied endorsement.** The real
   data cites its source document (the 2026 Ontario Fishing Regulations
   Summary) by name and page; it does not claim the ministry as publisher.
   Sample zones are credited to the invented "Provincial Fisheries Data
   Service". Portal design files (schema, data-structure notes) stay out of
   this public repo.
3. **No `localStorage` / `sessionStorage`.** Saved spots live in
   `state.spots` for the page session only. This was a brief constraint so the
   file renders correctly in sandboxed preview panes.
4. **Single file, no build step.** The app is still all in `index.html`.
   `manifest.webmanifest`, `sw.js` and `icons/` only make it installable and
   usable offline when hosted; the page works without them (e.g. from disk).
5. **Colour is never the only signal.** Open/closed status always carries an
   icon and a text label alongside the green/grey treatment.
6. **Never guess the user's location.** Which rules apply depends on where the
   angler is standing. If GPS fails, say why and how to fix it; never drop a
   pin somewhere and present it as theirs. Always show where the pin came from
   (GPS with ±accuracy, a tapped point, a saved spot, or the sample spot), and
   warn when the accuracy circle crosses a zone or sub-area boundary. Because
   boundaries are approximate, also warn (for any pin, tapped or GPS) when the
   point is within a geometry's `toleranceM` of a zone or lake edge, and when
   it falls in an `advisory` area. A point out on a Great Lake must resolve to
   that lake's zone (shown as "no data"), never to FMZ 16.

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

The invented sample zones are still written in the old 0.3 shape
(`docs/data-model.md`) and converted by `fromLegacy()`. Add new real data as
zone documents, not in the old shape.

## Known limitations

- **FMZ 16 is partial.** Zone-wide seasons and limits (pp. 117–118) and the
  Lake Simcoe exception (p. 121) are loaded. Species exceptions, additional
  fishing opportunities, other waterbody exceptions and fish sanctuaries
  (pp. 118–124) are not; the app lists the affected waters and warns. The
  logic already supports closures (sanctuaries) and night-only rules in the
  data shape, so loading them is data entry plus drawing the areas.
- **FMZ 16 runs to Dec 31, 2026** (`meta.effectiveTo`). After that the app
  still resolves dates but shows a banner that the 2027 summary may differ.
- **Boundaries are approximate.** The official FMZ layer (Ontario GeoHub / LIO)
  was blocked from the build environment. `GEO.fmz16` is Natural Earth 1:10m
  shorelines and the Ontario border, minus the Great Lakes, with a hand-drawn
  eastern/northern edge (`ADV-FMZ16-EDGE` warns along it). Lake Simcoe is
  Natural Earth plus a hand-drawn Kempenfelt Bay. Replace them with the
  official layer when it can be downloaded; keep the `toleranceM` warnings
  until then.
- **Sample zones (5, 15, 17, 20) are invented** and their dates were tuned to
  September 2026. Their shapes were trimmed so they don't overlap FMZ 16.
- **Leaflet loads from cdnjs.** If it fails, the app degrades to a "Map
  unavailable" notice and still renders species data — preserve that fallback if
  you touch the `MAP` section.
- **Sub-area exceptions are rendered but shallow.** One sub-area (Whitepine
  Lake, in FMZ 17) exists to prove the pattern; it does not override the parent
  zone's limits, it only displays a rule.

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
