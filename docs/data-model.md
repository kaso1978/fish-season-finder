> **Superseded (Nov 2026).** The app now reads *zone documents*: a zone, its
> areas, and a flat list of provisions with date expressions such as "fourth
> Saturday in April". See the `DATA LAYER` banner in `index.html`. This file
> describes the original 0.3 payload. Nothing in the app uses it any more.

# Data model

The shape of the payload the prototype consumes, and — more importantly — the
shape of what a conservation authority has to supply for a zone to appear in the
app at all.

The prototype hard-codes this as `API_RESPONSE` inside `index.html`. The real
service will return the same structure over HTTP. Nothing in the UI reads
anything that isn't described here.

---

## Top level

```jsonc
{
  "meta": {
    "publisher":        "Provincial Fisheries Data Service",
    "dataCurrentAsOf":  "2026-08-15",   // ISO date; surfaced to the angler
    "schemaVersion":    "0.3-prototype",
    "disclaimer":       "…"
  },
  "zones": [ /* Zone objects */ ]
}
```

`dataCurrentAsOf` is displayed in the app. It is the honesty mechanism: an
angler standing on a dock needs to know whether they're looking at something
published last week or last season.

---

## Zone

```jsonc
{
  "id":          "FMZ-17",                 // stable, unique, never reused
  "name":        "FMZ 17",                 // short label, drawn on the map
  "subtitle":    "South-central Ontario — Kawartha Lakes",
  "publishedOn": "2026-08-11",             // when this authority last published
  "geometry":    { "type": "Polygon", "coordinates": [ [ [lng, lat], … ] ] },
  "subAreas":    [ /* SubArea objects, may be empty */ ],
  "species":     [ /* SpeciesRegulation objects */ ]
}
```

**Geometry** is GeoJSON, coordinates in `[longitude, latitude]` order (note: the
reverse of how Leaflet takes latlngs — the app converts at the boundary). The
prototype supports a single `Polygon`; real zones will need `MultiPolygon`,
because almost every real management zone has islands and detached water bodies.
That is the first schema change production will force.

Rings must be closed (first coordinate repeated as the last).

---

## SubArea

A named water body inside a zone that carries different rules — the case that
breaks naive "one zone, one answer" designs.

```jsonc
{
  "id":        "SA-17-WP",
  "name":      "Whitepine Lake",
  "appliesTo": ["walleye", "musky"],   // species keys the exception touches
  "geometry":  { "type": "Polygon", "coordinates": [ … ] },
  "rule":      "Whitepine Lake is a rehabilitation water. Walleye is …"
}
```

In the prototype `rule` is free text, displayed to the angler. **In production it
must become structured overrides** — a partial `SpeciesRegulation` that replaces
named fields of the parent zone's record. Free text can't be filtered, counted,
or checked for contradictions, and an angler inside a sub-area should see the
corrected limits in the tables, not a paragraph telling them the tables are
wrong.

---

## SpeciesRegulation

One record per species per zone. This is what an authority actually authors.

```jsonc
{
  "sp": "walleye",                          // key into the species catalogue

  "seasons": [                              // one or more open windows
    { "from": "01-01", "to": "03-15" },
    { "from": "05-16", "to": "12-31" }
  ],

  "limits": {
    "sport":        4,                      // daily catch/possession
    "conservation": 2                       // 0 means "not permitted"
  },

  "size": {
    "type":  "slot",                        // "none" | "min" | "max" | "slot"
    "under": 40,                            // slot only
    "over":  50,                            // slot only
    "min":   null,                          // min only
    "max":   null,                          // max only
    "text":  "Must be less than 40 cm or greater than 50 cm. …"
  },

  "gear": [ "No live baitfish above the Burleigh locks" ],
  "note": "The protected slot shelters the main spawning year-classes."
}
```

### Seasons

`MM-DD` strings, no year — regulations recur annually.

- A window where `from` ≤ `to` is an ordinary within-year window.
- A window where `from` > `to` **wraps the new year**: `12-01` → `04-30` means
  open from December through April.
- Year-round is `01-01` → `12-31`.

Two adjacent windows (`… → 12-31` and `01-01 → …`) are *not* automatically
merged, and the app will honestly report "Open until Dec 31". If a season is
genuinely continuous across the new year, author it as one wrapping window
instead. This is a real authoring trap — the portal should detect it and prompt.

### Size

`text` is what the angler reads; the typed fields drive the visual keep/release
bar. Both must be present and must agree. The portal should generate `text` from
the typed fields rather than letting an author write them independently, because
a mismatch here is a legal problem, not a display bug.

`type: "max"` in the sample data means "not more than one greater than N cm",
which is the common Ontario phrasing. Production needs to distinguish that from
a true hard maximum — they are different rules that currently share a type.

### Limits

`conservation: 0` renders as "Not permitted", which is not the same as "no
limit". A missing or null limit and a zero limit must never be conflated.

---

## Species catalogue

Reference data shared across all zones, keyed by the `sp` field above.

```jsonc
"walleye": {
  "common": "Walleye",
  "sci":    "Sander vitreus",
  "group":  "Other",          // Bass | Trout & Salmon | Pike & Musky | Panfish | Other
  "shape":  "perch"           // which silhouette to draw
}
```

Owned centrally, not by individual authorities — otherwise the same fish appears
under six spellings and search stops working. Authorities pick species from this
list; they do not create entries in it.

`group` drives the app's filter chips. It is a coarse angler-facing grouping, not
taxonomy — walleye sits in "Other" despite being a perch relative, because
that's where an angler looks for it.

---

## What the portal must enforce

The app trusts this data completely, so validation has to happen upstream:

1. **Geometry** — closed rings, valid winding, no self-intersection, and no
   overlap with a neighbouring zone from the same authority. Overlaps make
   "which zone am I in" ambiguous, and the app resolves first-match-wins.
2. **Season coverage** — flag adjacent windows that should be one wrapping
   window; flag windows that overlap each other.
3. **Size text vs typed fields** — generate one from the other; never accept both
   as free input.
4. **Species keys** — must exist in the central catalogue.
5. **`appliesTo` on sub-areas** — must reference species present in the parent
   zone.
6. **Publication** — `dataCurrentAsOf` and `publishedOn` set by the system at
   publish time, never typed by a person.

## Open questions

- **Versioning and effective dates.** Regulations change on a date. The current
  model has no way to say "this rule applies from April 1". An angler planning a
  trip needs the rules that will be in force *then*, not now.
- **Licence tiers beyond sport/conservation.** Youth, senior, non-resident and
  Indigenous harvest rights all exist and none are modelled.
- **Bait, ice-hut and motor restrictions** are zone-level, not species-level, and
  have nowhere to live in the current shape.
- **Bilingual content.** Every angler-facing string needs a language dimension.
