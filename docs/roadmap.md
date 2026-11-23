# Roadmap

Intended order of work. The prototype exists to be argued with before any of
this gets built, so stage 0 is the one that matters most right now.

---

## Stage 0 — Validate the end-user experience *(you are here)*

Put `index.html` in front of actual anglers and watch what confuses them.

Questions worth answering before writing a line of backend code:

- Does "tap the map" match how someone thinks about where they're fishing, or do
  they think in lake names? A map pin is precise; "Balsam Lake" is how people
  talk.
- Is the zone the right unit to show, or does an angler only care about the
  water body they're standing on?
- Does the season timeline earn its space, or does the one-line status answer
  everything?
- Is the sport/conservation split legible to someone who doesn't already know
  what those licences are?
- What do people do with a slot limit? That bar was the hardest thing to render;
  find out whether it worked.

**Do not build stages 1+ until this is done.** Everything downstream gets cheaper
if the model of the product is right.

---

## Stage 1 — Real data, still no portal

Replace the hard-coded object with a real API and real boundaries.

- Stand up a read-only API returning the `docs/data-model.md` shape.
- Source genuine GIS boundaries for the zones. This will force `MultiPolygon`
  support and, at real vertex counts, will force you to stop shipping geometry
  in the initial payload — the app will need a `?bbox=` query or vector tiles.
- Move `MultiPolygon` and point-in-polygon into a tested module. The ray-casting
  function is 8 lines and correct for simple polygons; it is not correct for
  polygons with holes.
- Load real regulations for **one** zone only, and mark every other zone as
  unpublished. A partially-real app is honest. A fully-fake one that looks real
  is the failure mode to avoid.
- The `PROTOTYPE` banner comes off only when a zone's data is genuinely official
  and attributed to the authority that published it.

## Stage 2 — Caching and offline

Anglers are on the water without signal. This is a core requirement, not a
polish item.

- Service worker; cache the app shell and the zone documents the user has looked
  at or saved.
- Persist saved spots properly (IndexedDB), replacing the in-memory array.
- Make the "data current as of" line reflect the cached copy's age, and warn
  when it's stale enough to matter.
- Decide what happens when a cached rule has since changed — the app must never
  silently show an outdated legal limit.

## Stage 3 — The authority portal

The half of the product that isn't in this repo, and the half that determines
whether the data is any good.

- Authentication scoped to an authority, with an audit trail on every change.
- Boundary upload (Shapefile / GeoJSON / KML) with the geometry validation listed
  in `docs/data-model.md`.
- A season and limits editor that generates size-limit text from typed fields
  rather than accepting both.
- Draft → review → publish, with an effective date. Publishing must be a
  deliberate act with a second pair of eyes; a typo here is a legal instruction
  to thousands of people.
- Diff view against the currently published version.

## Stage 4 — Distribution

- Progressive web app: manifest, icons, `Add to Home Screen`.
- Native wrappers only if push notifications or background location turn out to
  matter. They probably don't.
- Deep links to a zone or species so an authority can point at a specific rule.

---

## Things worth deciding early

**Liability and framing.** The app tells people what is legal. Either it is
official — published by authorities who own the content and the consequences —
or it is clearly a convenience layer that defers to the official regulations.
The middle ground, where it looks official but disclaims responsibility in
small print, is the worst of both. This decision shapes the portal, the
attribution, and probably the business model.

**Who owns the species catalogue.** Central ownership keeps search and filtering
coherent; authority ownership means faster onboarding and immediate divergence.
Central, with a request process, is the usual answer.

**Effective dates.** Without them the app can only ever answer "today". Anglers
plan trips. Retrofitting a time dimension onto a published-regulations model is
painful; adding it in stage 1 is cheap.
