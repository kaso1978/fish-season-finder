# Lake and river exceptions (trial: FMZ 16 and 17)

The app's species exceptions, waterbody exceptions and fish sanctuaries for
FMZ 16 and 17 come from two hand-made files and the official water layers.

1. **`data16_17.py`**: every exception as printed in the 2026 summary
   (pp. 118–124 and 128–129): the place, its printed description (kept word
   for word), its page and its rules. Edit this when the summary changes.
2. **`ends.py`**: where each stretch starts and ends: a road (`R:`), a rail
   line (`RR:`), a dam (`D:`), a point (`P:lat,lng`), a confluence (`C:`), a
   township line (`T:`) or the mouth. `anchor` + `radius` mark a small area
   around a dam, falls or causeway.
3. **Water layers**: run `py fetch_waters.py` in `boundaries\` on a PC that
   can reach Land Information Ontario (the cloud can't). It saves the Ontario
   Hydro Network lakes and rivers, geographic townships, place names, dams,
   roads and rail lines near the named waters into `boundaries/waters/`
   (not committed: about 15 MB; `fetch_waters.meta.json` records the run).
4. **Build**: `python build_geo.py` (about 5 minutes; needs shapely) matches
   each place to its water and cuts the stretch, writing `geoms.json`. It
   prints one line per place: `CUT` (both ends found: precision `drawn`,
   rules replace the zone-wide ones when the pin is on it), `APPROX` /
   `whole` (shown as "may apply here") or point only (listed as nearby).
   `python build_geo.py ID ...` rebuilds just those places.
5. **Official records**: run `py fetch_regs.py` in `boundaries\` (same PC)
   to download the province's "Recreational fishing regulations data"
   (data.ontario.ca, Open Government Licence – Ontario) into
   `boundaries/regs/`. Then `python official.py` links every place to its
   official record and writes `official.json`. The dataset has no stretch
   shapes, only one point per rule (a sanctuary's centroid, or a waterbody's
   centroid or river mouth) and an OGF ID. We use it to:
   - store the official `ogfId` on each place (the key an authority portal
     would use),
   - place the sanctuaries the hydro layer can't draw, and fix spots we put
     on the wrong stretch (`USE_OFFICIAL_POINT` in `official.py`),
   - check our work: it prints `NO MATCH`, `CHECK` (our shape is over 1 km
     from the official sanctuary centroid) and `NOT IN APP` (an official
     sanctuary we have no place for). Look at each one.
6. `python shrink.py` simplifies it to `geoms_small.json`, and
   `python gen_exc.py ../../index.html` writes the `EXC16_*` / `EXC17_*`
   blocks into the app. (On a file that already has them, delete those
   blocks and the "attach the pilot exceptions" lines first.)

North Creek and Stoney Creek (Walsingham), Fisher's Creek, Indian River
(Sarawak) and Sangs Creek have no named shape in the hydro layer, so they sit
at the official sanctuary point and are listed as nearby
(`pointSource:'official'`).

The official file covers all 20 zones, so it is the starting point for
loading exceptions in other zones: it saves transcribing, but its wording
sometimes differs from the printed summary, and the app quotes the summary.
