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
| `DATA LAYER` | `SPECIES` catalogue and `API_RESPONSE` — all sample data |
| `FISH SILHOUETTES` | Hand-drawn generic SVG paths, one per body shape |
| `DATE + SEASON LOGIC` | `evaluate()`, `statusLine()` — the actual brains |
| `GEOMETRY` | Ray-casting point-in-polygon, zone and sub-area resolution |
| `APP STATE` | The single `state` object; all state is in memory |
| `MAP` | Leaflet init, zone layers, pin, `setPin()` |
| `BOTTOM SHEET` | Drag/snap behaviour for the sliding sheet |
| `RENDER` | Sheet header + species list rendering |
| `SPECIES DETAIL` | The full-screen slide-over, season timeline, size-limit bar |
| `SAVED SPOTS` | In-memory saved locations |
| `UI WIRING` | All event listeners |
| `INIT` | `boot()` |

### The part that matters most

`evaluate(reg, date)` in `DATE + SEASON LOGIC` is the core of the product. Every
status label, count, filter and timeline derives from it. It handles:

- multiple open windows per species per zone
- windows that **wrap the new year** (`from` > `to`, e.g. `12-01` → `04-30`)
- finding the next opening date when a species is currently closed

If you change season handling, re-check all four cases: year-round, single
window, multiple windows, and a wrapping window.

## Hard constraints — do not break these

1. **All regulation data is fictional.** The `PROTOTYPE — SAMPLE DATA ONLY`
   banner must stay visible on every screen, and the disclaimer must remain in
   the species detail footer. This app tells people what is legal; shipping
   something that *looks* authoritative while carrying invented numbers is the
   main risk in the whole project.
2. **No real conservation authority names, logos or wordmarks.** The publisher
   is the invented "Provincial Fisheries Data Service".
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
   warn when the accuracy circle crosses a zone or sub-area boundary.

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

## Data shape

`API_RESPONSE` mirrors the payload the real service will return, so the fetch
layer can be swapped in without touching the UI. The commented-out `fetch()`
call at the top of the `DATA LAYER` section marks the seam.

Full field-by-field specification, including what the authority portal must
collect and validate: **`docs/data-model.md`**. Read it before changing the
shape of a zone or species record.

## Known limitations

- **Sample dates are tuned to September 2026.** Three species were authored as
  teaching cases: one closing within a week, one opening within two weeks, one
  wrapping the new year. Viewed months later those read as ordinary entries.
  Retune the dates in `API_RESPONSE`, don't change the logic.
- **Zone polygons are approximate blocks**, not real GIS boundaries. They exist
  to prove zone resolution works, not to be accurate.
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
