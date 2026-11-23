# Prompt: "Fish Season Finder" HTML prototype

Copy everything below the line into a fresh Claude conversation (or Claude Code / any code-gen tool). Adjust the bracketed bits if you want a different region or feel.

---

Build a **single-file, self-contained HTML prototype** of a mobile app called **Fish Season Finder**.

## What the app does

A recreational angler opens the app, either taps a spot on a map or uses their current location, and immediately sees **which fish species are open to fishing at that spot on a given date**, along with the rules that apply (season dates, size limits, catch limits, licence tier).

In the real product, the data comes from a central database that provincial/state conservation authorities populate through their own admin portal — they upload GIS boundaries for their management zones and attach species + season + limit records to each zone. **The prototype is end-user experience only.** Do not build the authority portal, a login, or a backend. Hard-code the sample data in a JavaScript object shaped the way the real API response would be shaped, so the fetch layer can later be swapped in with no UI changes.

## Technical constraints

- One `.html` file. All CSS and JS inline. No build step.
- **Leaflet** (from cdnjs) with **OpenStreetMap** tiles for the map. Zone boundaries as **GeoJSON polygons** layered on top.
- Mobile-first: design for a ~390×844 viewport, touch targets ≥44px, thumb-reachable primary controls. It should still be usable if opened on a desktop browser — center the app in a phone-shaped frame on wide screens.
- No frameworks required. Vanilla JS is fine and preferred.
- **Do not use localStorage or sessionStorage** — hold all state in memory. (Fake the "saved spots" persistence with an in-memory array.)
- Everything must work from a single file opened straight in a browser, aside from the CDN map tiles.

## Sample data — Ontario, Canada

Model the data on Ontario's **Fisheries Management Zones (FMZs)**. Include **4–6 zones** as rough GeoJSON polygons (they do not need to be geographically accurate — approximate blocks covering recognizable areas are fine), for example:

- **FMZ 20** — Lake Ontario and tributaries
- **FMZ 17** — south-central Ontario / Kawartha Lakes area
- **FMZ 16** — Lake Simcoe area
- **FMZ 15** — eastern Ontario / Ottawa Valley
- **FMZ 5** — northern Ontario / Lake Nipigon area

Give each zone **6–10 species** drawn from a realistic Ontario list: walleye, northern pike, muskellunge, smallmouth bass, largemouth bass, lake trout, brook trout, rainbow trout, yellow perch, black crappie, sunfish, channel catfish, lake whitefish, splake, Atlantic salmon, Chinook salmon.

Each species record should carry:

- Common name, scientific name, and a simple inline **SVG silhouette** (draw simple, generic fish shapes yourself — do not fetch or copy external artwork or logos)
- One or more **open season windows** as month/day ranges, including at least one that wraps the new year (e.g. Jan 1 – Mar 15 plus May 16 – Dec 31) and at least one **year-round** species
- **Sport vs. Conservation licence** catch limits (Ontario has both tiers)
- Size limits, including at least one **protected slot size** (e.g. "must be less than 40cm or greater than 50cm")
- Gear or method restrictions (e.g. artificial lures only, no live bait, single barbless hook)
- A short free-text note field
- Vary the data meaningfully between zones so the map selection visibly changes the answer.

Deliberately include a couple of instructive edge cases: a species **closed today but opening within 14 days**, a species that **closes within 7 days**, and one zone with a **sub-area exception** (a named lake inside the zone with a different rule).

## Screens and behaviour

**1. Map screen (home)**
- Full-bleed Leaflet map, zone polygons lightly tinted and labelled.
- A prominent **"Use my location"** button using the Geolocation API, with a graceful fallback if it's denied or unavailable (fall back to a default pin and say so).
- Tapping anywhere drops a pin, runs point-in-polygon against the zone GeoJSON, and resolves the zone. If the tap lands outside every zone, show a clear "No regulation data for this location" state.
- A **bottom sheet** that starts as a peek — zone name, date, and a count like "12 of 18 species open today" — and drags/taps up to the full species list.
- A **date control** in the header defaulting to today, with quick chips for Today / +1 week / +1 month plus a full date picker. Changing the date re-evaluates every season window and updates the counts live.

**2. Species list (in the bottom sheet)**
- Cards grouped into **Open now** and **Closed**, with a clear green/grey status treatment plus a text label and icon (never colour alone — must be readable for colour-blind users).
- Each card: silhouette, common name, status, and the single most useful line ("Open until Nov 30" / "Opens May 16 — in 12 days").
- **Search box** filtering by common or scientific name, and filter controls for: open only, species group (bass / trout & salmon / panfish / pike & musky / other), and sort by name or by season opening date.

**3. Species detail**
- Full-screen slide-over with: hero silhouette, name, live status banner, a **12-month horizontal season timeline** showing open/closed bands with a marker at the selected date, a limits table (sport vs conservation), size/slot rules rendered so a slot limit is actually understandable, gear restrictions, any sub-area exceptions, and the notes field.
- A "Report a problem with this listing" button that opens a stub confirmation — this signals the feedback path back to the conservation authority without building it.

**4. Saved spots**
- Save the current pin with a user-supplied nickname; a list view showing each spot's zone and how many species are open there today; tap to jump back to it on the map.

**5. Data freshness / offline**
- A persistent, subtle **"Data current as of [date] · Zone published by [Authority name]"** line, sourced from the data object.
- Simulate an offline state (a toggle in a small dev/demo menu is fine): show a warning banner that data may be stale, while keeping the cached results readable.

## Visual design

Clean, outdoorsy, and legible in bright sunlight on the water: high contrast, generous type sizes, a restrained palette built around deep water blues and a natural green, with a single warm accent for calls to action. Support both light and dark colour schemes via `prefers-color-scheme`. Smooth but quick transitions (150–250ms). It should look like a shipped consumer app, not a wireframe — but keep the styling hand-written, not a copy of any real app's branding.

## Legal and accuracy guardrails

- All regulation data is **fictional placeholder data**. Show a persistent, unmissable **"PROTOTYPE — sample data only. Do not use for actual fishing. Consult the official regulations."** banner or footer on every screen.
- Do not use any real conservation authority's name, logo, or wordmark. Invent a neutral one (e.g. "Provincial Fisheries Data Service").

## Out of scope

No authority-facing portal, no authentication, no real API, no licence purchasing, no catch logging, no analytics.

## Acceptance criteria

The prototype is finished when I can: pick a point on the map, see the correct zone resolve, read which species are open today, change the date and watch the list change, open a species and understand its season and limits from the timeline and tables, search and filter the list, save the spot and return to it — all in one HTML file on a phone-sized screen.

Write the whole thing out as one complete file. Where a real implementation would call the backend, leave a clearly marked comment showing the API call that would replace the hard-coded data.
