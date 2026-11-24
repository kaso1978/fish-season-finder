"""
Download official shapes for the named waters used by the fishing-regulation
exceptions in FMZ 16 and 17, plus geographic townships and dams in that area.

Source: Land Information Ontario (LIO) open-data ArcGIS REST service
(Open Government Licence - Ontario). Layer URLs are listed below.

Output (in boundaries/waters/, overwritten each run):
  waterbody.geojson    OHN Waterbody polygons whose official name is in NAMES
  watercourse.geojson  OHN Watercourse lines whose official name is in NAMES
  townships.geojson    every Geographic Township (improved) polygon in the bbox
  names.geojson        Geographic Names Ontario features whose name is in NAMES
  dams.geojson         every Ontario Dam Inventory point in the bbox
  roads.geojson        ORN road segments within 300 m of a saved water (names,
                       route names/numbers and bridge structures from ORN tables)
  rail.geojson         ORWN track segments within 300 m of a saved water
  fetch_waters.meta.json  URLs, date, counts, unmatched names

roads/rail are built from waterbody.geojson + watercourse.geojson, so run them
after (or together with) those layers.

All queries are limited to the FMZ 16 + 17 bounding box, returned in WGS84
(outSR=4326), lightly generalised by the server (maxAllowableOffset ~10 m) and
rounded to 5 decimals. Standard library only.

Run:   py fetch_waters.py
       py fetch_waters.py waterbody dams     (only some layers)
       py fetch_waters.py roads rail
"""

import datetime as dt
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

LIO = "https://ws.lioservices.lrc.gov.on.ca/arcgis2/rest/services/LIO_OPEN_DATA"
LAYERS = {
    # key: (layer URL, name field, extra fields to keep, filter by NAMES?)
    "waterbody":   (f"{LIO}/LIO_Open01/MapServer/25", "OFFICIAL_NAME_LABEL", ["WATERBODY_TYPE"], True),
    "watercourse": (f"{LIO}/LIO_Open01/MapServer/26", "OFFICIAL_NAME_LABEL", ["WATERCOURSE_TYPE"], True),
    "townships":   (f"{LIO}/LIO_Open06/MapServer/1",  "OFFICIAL_NAME", [], False),
    "names":       (f"{LIO}/LIO_Open09/MapServer/36", "OFFICIAL_NAME",
                    ["ENTITY_TYPE", "LATITUDE_DECIMAL_DEGREES", "LONGITUDE_DECIMAL_DEGREES"], True),
    "dams":        (f"{LIO}/LIO_Open04/MapServer/0",  "DAM_NAME", ["DAM_ID"], False),
}
# Layer titles on the server: OHN Waterbody, OHN Watercourse, Geographic Township
# Improved, Geographic Names Ontario (polygons, not points), Ontario Dam Inventory.

BBOX = (-83.3, 41.6, -76.8, 45.8)  # xmin, ymin, xmax, ymax  (FMZ 16 + 17)
MAX_OFFSET = 0.0001                # degrees; ~8-11 m generalisation done by the server
DECIMALS = 5
PAGE_SIZE = 1000
NAME_BATCH = 8

NAMES = """Bells Lake; Big Creek; North Thames River; Thames River; Black Creek; Lynn River;
Bronte Creek; Credit River; Don River; Fifteen Mile Creek; Forty Mile Creek; Grindstone Creek;
Highland Creek; Humber River; Nottawasaga River; Boyne River; Rouge River; Sixteen Mile Creek;
Spencer Creek; Waterford Ponds; Twelve Mile Creek; Twenty Mile Creek; Youngs Creek; Ryerse Creek;
Bayfield River; Beaver River; Big Otter Creek; Bighead River; Grand River; Hog Creek;
Little Otter Creek; Little Sauble River; Maitland River; Nine Mile River; Lucknow River;
North Creek; Sauble River; Saugeen River; Sturgeon River; Chenail Ecarte; Sydenham River;
Levis Creek; Fletchers Creek; Pine River; Pretty River; Whitemans Creek; Horner Creek;
Lake Simcoe; Lake Couchiching; Green River; Severn River; Black River; Colpoys Creek;
Gleason Brook; Bradleys Creek; Catfish Creek; Lafontaine Creek; Stoney Creek; Limestone Creek;
Fishers Creek; Galt Creek; Mill Creek; Aberfoyle Creek; Gully Creek; Naftels Creek;
Normandale Creek; Potters Creek; Silver Creek; Pefferlaw River; Talbot River;
Beatty Saugeen River; Indian Brook; Indian River; Judges Creek; Keefers Creek; Meux Creek;
South Saugeen River; Orchard Creek; Centreville Creek; Park Head Creek; Sangs Creek;
Telfer Creek; Bothwells Creek; Willow Creek; Pottawatomi River; Maxwell Creek; Oakville Creek;
Cobourg Brook; Cobourg Creek; Gages Creek; Ganaraska River; Crowe Lake; Crowe River; Crowe Bay;
Balsam Lake; Gull River; Rosedale River; Mitchell Lake; Lake Scugog; Scugog River;
Blackstock Creek; Nonquon River; Mariposa Brook; East Cross Creek; Trent River; Chemong Lake;
Gannons Narrows; Bobcaygeon River; Pigeon Lake; Stony Lake; Perrys Creek; Fenelon River;
Fishog River; Head Lake; Katchewanooka Lake; Lovesick Lake; Lower Buckhorn Lake; Otonabee River;
Pigeon River; Cameron Lake; Sturgeon Lake; Hamilton Harbour; Gordon Pittock Reservoir"""
NAMES = [n.strip() for n in NAMES.replace("\n", " ").split(";") if n.strip()]

# Known official spellings that differ by more than accents/apostrophes/brackets.
ALIASES = {
    "Gannons Narrows": ["Gannon Narrows"],
    "Gages Creek": ["Gage Creek"],
    "Keefers Creek": ["Keefer Creek"],
    "Potters Creek": ["Potter Creek"],
    "Hog Creek": ["Hogg Creek"],
    "Fishog River": ["Fishog Lake"],
    "Gordon Pittock Reservoir": ["Pittock Lake", "Pittock Conservation Area"],
    "Cobourg Creek": ["Cobourg Brook"],
    "Ryerse Creek": ["Youngs Creek", "Young Creek"],
    "Sangs Creek": ["Sang Creek"],
    "Orchard Creek": ["Orchard Park Creek"],
    "Galt Creek": ["Mill Creek"],
}
# Aliases that only apply in some layers (default: every name-matched layer).
ALIAS_LAYERS = {
    "Fishog Lake": ["names"],
}

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "waters"
HEADERS = {"User-Agent": "fmz-waters-fetch/1.0 (python urllib)"}


# ---------------------------------------------------------------- helpers
def norm(s):
    """Upper-case, strip accents, apostrophes and bracketed notes, collapse spaces."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"['’`]", "", s)
    s = re.sub(r"[^A-Za-z0-9 ]", " ", s)
    return " ".join(s.upper().split())


def like_pattern(name):
    """LIKE pattern that tolerates accents (E/A -> _), apostrophes before a
    trailing s (Youngs ~ Young's) and a trailing bracketed note."""
    words = []
    for w in norm(name).split():
        w = re.sub(r"[EA]", "_", w)
        if len(w) > 2 and w.endswith("S"):
            w = w[:-1] + "%S"
        words.append(w)
    return " ".join(words) + "%"


def build_targets(layer):
    """Map normalised official spelling -> list of list names it stands for."""
    t = {}
    for n in NAMES:
        t.setdefault(norm(n), [])
        if n not in t[norm(n)]:
            t[norm(n)].append(n)
        for a in ALIASES.get(n, []):
            if layer in ALIAS_LAYERS.get(a, [layer]):
                t.setdefault(norm(a), [])
                if n not in t[norm(a)]:
                    t[norm(a)].append(n)
    return t


def get(url, params, timeout=300):
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, headers=HEADERS)  # POST: long WHERE clauses
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def query_all(layer_url, where, out_fields, point=False, bbox=BBOX, quiet=False):
    """Page through a query, halving the page size when LIO chokes."""
    url = layer_url + "/query"
    feats, seen, offset, size = [], set(), 0, PAGE_SIZE
    while True:
        params = {
            "where": where, "outFields": ",".join(out_fields), "f": "geojson",
            "geometry": ",".join(map(str, bbox)), "geometryType": "esriGeometryEnvelope",
            "inSR": 4326, "spatialRel": "esriSpatialRelIntersects", "outSR": 4326,
            "returnGeometry": "true", "orderByFields": "OBJECTID",
            "resultOffset": offset, "resultRecordCount": size,
            "geometryPrecision": DECIMALS,
        }
        if not point:
            params["maxAllowableOffset"] = MAX_OFFSET
        page, failures = None, 0
        while page is None:
            try:
                page = json.loads(get(url, params))
                if "error" in page:
                    raise RuntimeError(page["error"])
            except Exception as e:
                page = None
                failures += 1
                if failures > 6:
                    raise RuntimeError(f"giving up at offset {offset}: {str(e)[:200]}")
                size = max(1, size // 2)
                params["resultRecordCount"] = size
                print(f"    request failed ({str(e)[:80]}); retrying with {size} per page")
                time.sleep(3 * failures)
        got = page.get("features", [])
        new = 0
        for f in got:
            oid = f.get("id", (f.get("properties") or {}).get("OBJECTID"))
            if oid in seen:
                continue
            seen.add(oid)
            feats.append(f)
            new += 1
        if not got or new == 0:   # new == 0: server ignored the offset; don't loop
            break
        # LIO pages are positional windows that come back short (~900 of 1000) with no
        # exceededTransferLimit flag, so advance by the requested size and stop only on
        # an empty page. (Stopping on a short page lost most features in dense tiles.)
        offset += size
    # Safety net: compare with the server's count and fetch anything still missing by id.
    base = {"where": where, "geometry": ",".join(map(str, bbox)),
            "geometryType": "esriGeometryEnvelope", "inSR": 4326,
            "spatialRel": "esriSpatialRelIntersects", "f": "json"}
    count = json.loads(get(url, {**base, "returnCountOnly": "true"})).get("count", 0)
    if count > len(seen):
        ids = json.loads(get(url, {**base, "returnIdsOnly": "true"})).get("objectIds") or []
        missing = sorted(set(ids) - seen)
        if not quiet:
            print(f"    paging short by {len(missing)}; fetching them by id")
        for i in range(0, len(missing), 500):
            params = {"objectIds": ",".join(map(str, missing[i:i + 500])),
                      "outFields": ",".join(out_fields), "f": "geojson", "outSR": 4326,
                      "returnGeometry": "true", "geometryPrecision": DECIMALS}
            if not point:
                params["maxAllowableOffset"] = MAX_OFFSET
            for f in json.loads(get(url, params)).get("features", []):
                oid = f.get("id", (f.get("properties") or {}).get("OBJECTID"))
                if oid not in seen:
                    seen.add(oid)
                    feats.append(f)
    return feats


def round_coords(c):
    if isinstance(c, (int, float)):
        return round(c, DECIMALS)
    out = [round_coords(x) for x in c]
    # drop consecutive duplicate vertices created by rounding
    if out and isinstance(out[0], list) and out[0] and isinstance(out[0][0], float):
        ded = [out[0]]
        for p in out[1:]:
            if p != ded[-1]:
                ded.append(p)
        out = ded
    return out


def clean(f, name_field, extra, matched=None):
    p = f.get("properties") or {}
    props = {"id": p.get("OBJECTID", f.get("id")), "name": p.get(name_field)}
    for k in extra:
        props[k.lower()] = p.get(k)
    if matched:
        props["matched_name"] = matched[0]      # first list name (kept for compatibility)
        props["matched_names"] = list(matched)  # every list name this feature stands for
    g = f.get("geometry")
    if g:
        g = {"type": g["type"], "coordinates": round_coords(g["coordinates"])}
    return {"type": "Feature", "id": props["id"], "properties": props, "geometry": g}


def write_fc(path, feats):
    fc = {"type": "FeatureCollection", "features": feats}
    path.write_text(json.dumps(fc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return path.stat().st_size


# ---------------------------------------------------------------- roads + rail near waters
# Used to find where river reaches start and end (bridges, rail crossings).
ORN = f"{LIO}/LIO_Open09/MapServer"
NEAR_LAYERS = {
    "roads": {"url": f"{ORN}/0",                         # ORN Road Net Element (no names on it)
              "fields": ["OBJECTID", "OGF_ID"]},
    "rail":  {"url": f"{LIO}/LIO_Open04/MapServer/18",   # ORWN Track
              "fields": ["OBJECTID", "TRACKNAME", "OPERATOENA", "SUBDI1NAME", "SUBDI2NAME"]},
}
# ORN name tables, joined on ORN_ROAD_NET_ELEMENT_ID = road OGF_ID.
ORN_TABLES = {
    "official_names": (f"{ORN}/7",  ["FULL_STREET_NAME"]),
    "alternate_names": (f"{ORN}/2", ["FULL_STREET_NAME"]),
    "route_names":    (f"{ORN}/11", ["ROUTE_NAME_ENGLISH"]),
    "route_numbers":  (f"{ORN}/12", ["ROUTE_NUMBER"]),
    "structures":     (f"{ORN}/15", ["STRUCTURE_TYPE", "STRUCTURE_NAME_ENGLISH"]),
}
NEAR_M = 300          # keep segments with any point this close to a saved water
DENSIFY_M = 100       # densify water and road lines to this spacing before testing
TILE_DEG = 0.1        # envelope tiles used to query roads/rail
ID_BATCH = 250
M_PER_DEG = 111320.0
COS_LAT = 0.723       # cos(43.7 deg), middle of the bbox; fine for a 300 m test


def iter_lines(geom):
    """Yield coordinate lists (lines and polygon rings) from a GeoJSON geometry."""
    if not geom:
        return
    t, c = geom["type"], geom["coordinates"]
    if t == "LineString":
        yield c
    elif t in ("MultiLineString", "Polygon"):
        yield from c
    elif t == "MultiPolygon":
        for poly in c:
            yield from poly
    elif t == "Point":
        yield [c]


def densify(line, step_m=DENSIFY_M):
    out = []
    for (x1, y1), (x2, y2) in zip(line, line[1:]):
        d = ((x2 - x1) * COS_LAT * M_PER_DEG) ** 2 + ((y2 - y1) * M_PER_DEG) ** 2
        n = max(1, int(d ** 0.5 // step_m) + 1)
        for k in range(n):
            out.append((x1 + (x2 - x1) * k / n, y1 + (y2 - y1) * k / n))
    if line:
        out.append(tuple(line[-1][:2]))
    return out


class WaterIndex:
    """Grid of densified vertices from the saved waterbody + watercourse files."""

    def __init__(self):
        self.cy = NEAR_M / M_PER_DEG
        self.cx = NEAR_M / (M_PER_DEG * COS_LAT)
        self.grid = {}
        n = 0
        for key in ("waterbody", "watercourse"):
            fc = json.loads((OUT_DIR / f"{key}.geojson").read_text(encoding="utf-8"))
            for f in fc["features"]:
                for line in iter_lines(f["geometry"]):
                    for x, y in densify(line):
                        self.grid.setdefault(self.cell(x, y), []).append((x, y))
                        n += 1
        print(f"  water index: {n:,} points in {len(self.grid):,} cells")

    def cell(self, x, y):
        return (int((x + 180) // self.cx), int((y + 90) // self.cy))

    def near(self, x, y):
        cx, cy = self.cell(x, y)
        lim = (NEAR_M / M_PER_DEG) ** 2
        for i in (cx - 1, cx, cx + 1):
            for j in (cy - 1, cy, cy + 1):
                for wx, wy in self.grid.get((i, j), ()):
                    if ((wx - x) * COS_LAT) ** 2 + (wy - y) ** 2 <= lim:
                        return True
        return False

    def tiles(self):
        """Query tiles (TILE_DEG squares) that have a water point within NEAR_M."""
        pad_x, pad_y = self.cx, self.cy
        t = set()
        for pts in self.grid.values():
            x, y = pts[0]
            for dx in (-pad_x, 0, pad_x):
                for dy in (-pad_y, 0, pad_y):
                    t.add((int((x + dx - BBOX[0]) // TILE_DEG), int((y + dy - BBOX[1]) // TILE_DEG)))
        out = []
        for i, j in sorted(t):
            x0, y0 = BBOX[0] + i * TILE_DEG, BBOX[1] + j * TILE_DEG
            box = (max(x0, BBOX[0]), max(y0, BBOX[1]),
                   min(x0 + TILE_DEG, BBOX[2]), min(y0 + TILE_DEG, BBOX[3]))
            if box[0] < box[2] and box[1] < box[3]:
                out.append(tuple(round(v, 6) for v in box))
        return out

    def feature_near(self, geom):
        for line in iter_lines(geom):
            for x, y in densify(line):
                if self.near(x, y):
                    return True
        return False


def query_table(url, ids, fields):
    """Rows of an ORN event table for the given road element ids."""
    rows = []
    for i in range(0, len(ids), ID_BATCH):
        where = "ORN_ROAD_NET_ELEMENT_ID IN (" + ",".join(str(x) for x in ids[i:i + ID_BATCH]) + ")"
        offset = 0
        while True:
            params = {"where": where, "outFields": ",".join(["ORN_ROAD_NET_ELEMENT_ID"] + fields),
                      "returnGeometry": "false", "f": "json",
                      "resultOffset": offset, "resultRecordCount": 2000}
            for attempt in range(6):
                try:
                    page = json.loads(get(url + "/query", params))
                    if "error" in page:
                        raise RuntimeError(page["error"])
                    break
                except Exception as e:
                    if attempt == 5:
                        raise
                    print(f"    table query failed ({str(e)[:80]}); retrying")
                    time.sleep(3 * (attempt + 1))
            got = page.get("features", [])
            rows += [g["attributes"] for g in got]
            if not page.get("exceededTransferLimit") or not got:
                break
            offset += len(got)
    return rows


def uniq(seq):
    out = []
    for s in seq:
        if s and s not in out:
            out.append(s)
    return out


def fetch_near(key, index):
    spec = NEAR_LAYERS[key]
    tiles = index.tiles()
    print(f"  {len(tiles)} tiles of {TILE_DEG} deg to query")
    kept, seen, fetched = {}, set(), 0
    for n, tile in enumerate(tiles, 1):
        for f in query_all(spec["url"], "1=1", spec["fields"], bbox=tile):
            p = f.get("properties") or {}
            oid = p.get("OBJECTID", f.get("id"))
            if oid in seen:
                continue
            seen.add(oid)
            fetched += 1
            if index.feature_near(f.get("geometry")):
                kept[oid] = f
        if n % 50 == 0 or n == len(tiles):
            print(f"    tile {n}/{len(tiles)}: {fetched:,} fetched, {len(kept):,} kept")
    feats = []
    if key == "roads":
        ids = sorted({int(f["properties"]["OGF_ID"]) for f in kept.values()
                      if f["properties"].get("OGF_ID") is not None})
        info = {}
        for tkey, (turl, tfields) in ORN_TABLES.items():
            rows = query_table(turl, ids, tfields)
            print(f"    {tkey}: {len(rows):,} rows")
            for r in rows:
                rid = int(r["ORN_ROAD_NET_ELEMENT_ID"])
                if tkey == "structures":
                    v = r.get("STRUCTURE_TYPE")
                    if r.get("STRUCTURE_NAME_ENGLISH"):
                        v = f"{v}: {r['STRUCTURE_NAME_ENGLISH']}"
                else:
                    v = r.get(tfields[0])
                info.setdefault(rid, {}).setdefault(tkey, []).append(v)
        for f in kept.values():
            rid = int(f["properties"]["OGF_ID"])
            d = info.get(rid, {})
            props = {"id": rid, "name": "; ".join(uniq(d.get("official_names", []))) or None}
            for tkey in ("alternate_names", "route_names", "route_numbers", "structures"):
                v = uniq(d.get(tkey, []))
                if v:
                    props[tkey] = v
            feats.append({"type": "Feature", "id": rid, "properties": props,
                          "geometry": {"type": f["geometry"]["type"],
                                       "coordinates": round_coords(f["geometry"]["coordinates"])}})
    else:
        def tidy(v):  # ORWN stores missing values as the text "None"; fix a broken dash
            if v is None or str(v).strip() in ("", "None"):
                return None
            return str(v).replace("�", "-")
        for f in kept.values():
            p = {k: tidy(v) if isinstance(v, str) else v for k, v in f["properties"].items()}
            props = {"id": p.get("OBJECTID"), "name": p.get("TRACKNAME"),
                     "operator": p.get("OPERATOENA"), "subdivision": p.get("SUBDI1NAME")}
            if p.get("SUBDI2NAME"):
                props["subdivision_2"] = p.get("SUBDI2NAME")
            feats.append({"type": "Feature", "id": props["id"], "properties": props,
                          "geometry": {"type": f["geometry"]["type"],
                                       "coordinates": round_coords(f["geometry"]["coordinates"])}})
    feats.sort(key=lambda f: f["id"])
    size = write_fc(OUT_DIR / f"{key}.geojson", feats)
    return {"url": spec["url"], "file": f"{key}.geojson", "features": len(feats), "bytes": size,
            "fetched_in_tiles": fetched, "tiles": len(tiles),
            "filter": f"any point (lines densified to {DENSIFY_M} m) within {NEAR_M} m of a "
                      "waterbody/watercourse feature in this folder",
            "name_tables": {k: v[0] for k, v in ORN_TABLES.items()} if key == "roads" else None}


# ---------------------------------------------------------------- main
def fetch_layer(key):
    url, name_field, extra, by_name = LAYERS[key]
    targets = build_targets(key)
    fields = ["OBJECTID", name_field] + extra
    point = key == "dams"
    out, matched = [], set()
    if by_name:
        patterns = sorted({like_pattern(n) for n in NAMES} |
                          {like_pattern(a) for als in ALIASES.values() for a in als
                           if key in ALIAS_LAYERS.get(a, [key])})
        for i in range(0, len(patterns), NAME_BATCH):
            batch = patterns[i:i + NAME_BATCH]
            where = " OR ".join(f"UPPER({name_field}) LIKE '{p}'" for p in batch)
            feats = query_all(url, where, fields, point)
            kept = 0
            for f in feats:
                label = (f.get("properties") or {}).get(name_field)
                ns = targets.get(norm(label))
                if ns:
                    out.append(clean(f, name_field, extra, ns))
                    matched.update(ns)
                    kept += 1
            print(f"  [{key}] batch {i // NAME_BATCH + 1}: {len(feats)} returned, {kept} kept")
    else:
        feats = query_all(url, "1=1", fields, point)
        out = [clean(f, name_field, extra) for f in feats]
        print(f"  [{key}] {len(out)} features")
    # de-duplicate (a feature can match two patterns)
    uniq = {}
    for f in out:
        uniq.setdefault(f["id"], f)
    return list(uniq.values()), matched


def main():
    args = sys.argv[1:]
    wanted = [a for a in args if a in LAYERS]
    near = [a for a in args if a in NEAR_LAYERS]
    if not args:
        wanted, near = list(LAYERS), list(NEAR_LAYERS)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    meta_path = OUT_DIR / "fetch_waters.meta.json"
    meta = {}
    if meta_path.exists() and (wanted != list(LAYERS) or near != list(NEAR_LAYERS)):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta.update({
        "source": "Land Information Ontario (LIO) open data, Open Government Licence - Ontario",
        "licence_url": "https://www.ontario.ca/page/open-government-licence-ontario",
        "downloaded_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "bbox_wgs84": {"xmin": BBOX[0], "ymin": BBOX[1], "xmax": BBOX[2], "ymax": BBOX[3]},
        "crs": "EPSG:4326",
        "generalisation": f"server maxAllowableOffset={MAX_OFFSET} deg (~10 m), "
                          f"coordinates rounded to {DECIMALS} decimals",
        "name_matching": "case-insensitive; accents, apostrophes and bracketed notes ignored; "
                         "aliases: " + json.dumps(ALIASES),
        "names_requested": NAMES,
        "aliases_layer_limits": ALIAS_LAYERS,
    })
    meta.setdefault("layers", {})
    matched_any = {}
    for key in wanted:
        print(f"Fetching {key} ...")
        feats, matched = fetch_layer(key)
        size = write_fc(OUT_DIR / f"{key}.geojson", feats)
        url, name_field, extra, by_name = LAYERS[key]
        info = {"url": url, "name_field": name_field, "fields_kept": ["id", "name"] +
                [k.lower() for k in extra] + (["matched_name"] if by_name else []),
                "features": len(feats), "bytes": size, "file": f"{key}.geojson"}
        if by_name:
            info["names_matched"] = sorted(matched)
            info["names_unmatched"] = [n for n in NAMES if n not in matched]
            matched_any[key] = matched
        meta["layers"][key] = info
        print(f"  saved {key}.geojson: {len(feats)} features, {size / 1e6:.2f} MB")
    by_name_layers = [k for k, v in LAYERS.items() if v[3] and k in meta["layers"]]
    all_matched = set()
    for k in by_name_layers:
        all_matched |= set(meta["layers"][k].get("names_matched", []))
    meta["names_unmatched_everywhere"] = [n for n in NAMES if n not in all_matched]
    shape_matched = set()
    for k in ("waterbody", "watercourse"):
        shape_matched |= set(meta["layers"].get(k, {}).get("names_matched", []))
    meta["names_without_ohn_shape"] = [n for n in NAMES if n not in shape_matched]
    if near:
        index = WaterIndex()
        for key in near:
            print(f"Fetching {key} near saved waters ...")
            info = fetch_near(key, index)
            meta["layers"][key] = info
            print(f"  saved {key}.geojson: {info['features']} features, {info['bytes'] / 1e6:.2f} MB")
    meta["total_bytes"] = sum(v["bytes"] for v in meta["layers"].values())
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Total {meta['total_bytes'] / 1e6:.2f} MB")
    print("No OHN shape for: " + ", ".join(meta["names_without_ohn_shape"]))
    print("Matched nowhere: " + ", ".join(meta["names_unmatched_everywhere"]))


if __name__ == "__main__":
    main()
