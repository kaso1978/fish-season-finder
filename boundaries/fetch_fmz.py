"""
Download Ontario's official Fisheries Management Zone (FMZ) boundaries.

Source: Land Information Ontario (LIO) layer "Fisheries Management Zone",
published on Ontario GeoHub under the Open Government Licence - Ontario.

What it does:
  1. Looks up the ArcGIS item by ID (falls back to a title search owned by
     LandInformationOntario if the ID ever stops working).
  2. Downloads every feature from the layer as GeoJSON in WGS84 (EPSG:4326)
     with all attributes, paging until no features are left.
  3. Saves it as  official/fmz_official_<modifiedDate>.geojson  plus a
     .meta.json describing the source, download time, fields, zones and SHA-256.

It never overwrites an earlier download. Every edition is kept side by side.
Standard library only. Run:   py fetch_fmz.py   (or: python fetch_fmz.py)
Add --check to only report whether a newer edition exists, without downloading.
"""

import datetime as dt
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ITEM_ID = "eafadbf2d09448beb483da1e7dfba86d"
ITEM_TITLE = "Fisheries Management Zone"
ITEM_OWNER = "LandInformationOntario"
ARCGIS = "https://www.arcgis.com/sharing/rest"
HUB_PAGE = "https://geohub.lio.gov.on.ca/datasets/{id}"
LICENCE_URL = "https://www.ontario.ca/page/open-government-licence-ontario"
PAGE_SIZE = 4  # zone polygons are huge; LIO fails on big responses
EXPECTED_ZONES = 20

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "official"
HEADERS = {"User-Agent": "fmz-boundary-fetch/1.0 (python urllib)"}


def get(url, params=None, timeout=120):
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def get_json(url, params=None):
    data = json.loads(get(url, params))
    if isinstance(data, dict) and "error" in data:
        raise RuntimeError(f"{url}: {data['error']}")
    return data


def find_item():
    """Return item JSON, by ID first, then by title search."""
    try:
        item = get_json(f"{ARCGIS}/content/items/{ITEM_ID}", {"f": "json"})
        if item.get("id") == ITEM_ID and item.get("url"):
            return item, "item ID"
    except Exception as e:
        print(f"Lookup by item ID failed ({e}); trying title search...")
    res = get_json(f"{ARCGIS}/search", {
        "q": f'title:"{ITEM_TITLE}" AND owner:{ITEM_OWNER}',
        "f": "json", "num": 50,
    })
    hits = [r for r in res.get("results", [])
            if r.get("title") == ITEM_TITLE and r.get("owner") == ITEM_OWNER
            and r.get("type") == "Feature Service" and r.get("url")]
    if not hits:
        raise RuntimeError("Could not find the official FMZ item by ID or title.")
    hits.sort(key=lambda r: r["modified"], reverse=True)
    return get_json(f"{ARCGIS}/content/items/{hits[0]['id']}", {"f": "json"}), "title search"


def ms_to_date(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc)


def latest_existing():
    """Newest modified date (YYYY-MM-DD) among files already in official/."""
    dates = []
    for p in OUT_DIR.glob("fmz_official_*.geojson"):
        stem = p.stem.replace("fmz_official_", "")
        dates.append(stem[:10])
    return max(dates) if dates else None


def download_layer(layer_url):
    """Page through the layer. Returns (raw_bytes_or_None, feature_collection)."""
    query = layer_url.rstrip("/") + "/query"
    features, seen, raw_first, offset = [], set(), None, 0
    pages, size = 0, PAGE_SIZE
    while True:
        page, raw, failures = None, None, 0
        while page is None:
            try:
                raw = get(query, {
                    "where": "1=1", "outFields": "*", "outSR": 4326, "f": "geojson",
                    "orderByFields": "OBJECTID", "returnGeometry": "true",
                    "resultOffset": offset, "resultRecordCount": size,
                }, timeout=600)
                page = json.loads(raw)  # LIO returns an HTML error page when overloaded
                if "error" in page:
                    raise RuntimeError(f"Query error: {page['error']}")
            except Exception as e:
                page = None
                failures += 1
                if failures > 6:
                    raise RuntimeError(f"Giving up at offset {offset}: {e}")
                size = max(1, size // 2)
                print(f"  request failed ({str(e)[:80]}); retrying with {size} per page...")
                time.sleep(3 * failures)
        feats = page.get("features", [])
        print(f"  got {len(feats)} feature(s) at offset {offset}")
        if not feats:
            break
        pages += 1
        if raw_first is None:
            raw_first, first_page = raw, page
        new = 0
        for f in feats:
            oid = f.get("id", f.get("properties", {}).get("OBJECTID"))
            if oid in seen:
                continue
            seen.add(oid)
            features.append(f)
            new += 1
        if new == 0:  # server ignored resultOffset; stop rather than loop forever
            break
        offset += len(feats)
    if raw_first is None:
        raise RuntimeError("Layer returned no features.")
    if pages == 1:
        # Everything came in one response: keep the server's bytes untouched.
        return raw_first, first_page, pages
    merged = dict(first_page)
    merged["features"] = features
    merged.pop("exceededTransferLimit", None)
    merged.pop("properties", None)
    return None, merged, pages


def zone_label(props):
    for k in ("FISHERIES_MANAGEMENT_ZONE_ID", "FMZ", "ZONE"):
        if k in props and props[k] is not None:
            return props[k]
    return None


def main():
    check_only = "--check" in sys.argv
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    item, how = find_item()
    modified = ms_to_date(item["modified"])
    mod_date = modified.strftime("%Y-%m-%d")
    print(f"Found item {item['id']} '{item['title']}' (owner {item['owner']}) via {how}")
    print(f"  Layer URL: {item['url']}")
    print(f"  Source modified: {modified.isoformat()}")

    prev = latest_existing()
    if prev is None:
        print("No earlier download in boundaries/official - this will be the first.")
    elif mod_date > prev:
        print(f"NEWER EDITION AVAILABLE: source {mod_date} is newer than your latest file ({prev}).")
    elif mod_date == prev:
        print(f"Source date {mod_date} matches your latest file - no newer edition.")
    else:
        print(f"Source date {mod_date} is older than your latest file ({prev}) - unusual, check manually.")
    if check_only:
        return

    raw, fc, pages = download_layer(item["url"])
    if raw is None:
        raw = json.dumps(fc, ensure_ascii=False).encode("utf-8")
    sha = hashlib.sha256(raw).hexdigest()

    # Never overwrite: same edition + same content = skip; different content = new suffix.
    base = f"fmz_official_{mod_date}"
    target, n = OUT_DIR / f"{base}.geojson", 1
    while target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest() == sha:
            print(f"Identical file already saved: {target.name} - nothing to do.")
            return
        n += 1
        target = OUT_DIR / f"{base}_{n}.geojson"

    feats = fc.get("features", [])
    fields = list(feats[0].get("properties", {}).keys()) if feats else []
    zones = []
    for f in feats:
        p = f.get("properties", {})
        zones.append({"zone": zone_label(p), "description": p.get("LOCATION_DESCR"),
                      "OBJECTID": p.get("OBJECTID")})
    zones.sort(key=lambda z: (z["zone"] is None, str(z["zone"]).zfill(4)))

    meta = {
        "source": {
            "dataset": item["title"],
            "item_id": item["id"],
            "item_url": f"https://www.arcgis.com/home/item.html?id={item['id']}",
            "hub_page": HUB_PAGE.format(id=item["id"]),
            "owner": item["owner"],
            "publisher": item.get("accessInformation"),
            "layer_url": item["url"],
            "licence": "Open Government Licence - Ontario",
            "licence_url": LICENCE_URL,
            "modified_utc": modified.isoformat(),
            "found_via": how,
        },
        "download": {
            "downloaded_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "query": "where=1=1&outFields=*&outSR=4326&f=geojson (paged, orderBy OBJECTID)",
            "pages": pages,
            "file_is_raw_server_response": pages == 1,
            "crs": "EPSG:4326 (WGS84)",
        },
        "file": target.name,
        "sha256": sha,
        "feature_count": len(feats),
        "fields": fields,
        "zones": zones,
        "zone_count": len({z["zone"] for z in zones}),
    }
    target.write_bytes(raw)
    target.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False),
                                                encoding="utf-8")
    print(f"Saved {target}  ({len(raw):,} bytes, {len(feats)} features)")
    print(f"Saved {target.with_suffix('.meta.json')}")
    print("Zones: " + ", ".join(str(z["zone"]) for z in zones))
    if meta["zone_count"] != EXPECTED_ZONES:
        print(f"WARNING: expected {EXPECTED_ZONES} zones, found {meta['zone_count']}.")


if __name__ == "__main__":
    main()
