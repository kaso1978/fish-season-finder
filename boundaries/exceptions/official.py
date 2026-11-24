# Links each exception in data16_17.py to the province's own record in the
# "Recreational fishing regulations data" open dataset (MNR, Open Government
# Licence - Ontario), and writes official.json for gen_exc.py.
#
#   python official.py [path/to/fishingregulationsexceptionopendata_*.xlsx]
#
# The dataset gives no stretch shapes. It gives, per rule, an OGF ID and one
# point: the centroid of a fish sanctuary, or the centroid / river mouth of a
# waterbody. We use it to
#   * record the official OGF ID on every matched place (ogfId),
#   * place sanctuaries the hydro layer can't draw (USE_OFFICIAL_POINT), and
#   * check our drawn shapes: a sanctuary centroid far from our shape is
#     reported, because it usually means we picked the wrong water.
import csv, difflib, glob, io, json, math, os, re, sys, zipfile
D = os.path.dirname(os.path.abspath(__file__)) + '/'
ns = {}
exec(open(D + 'data16_17.py', encoding='utf-8').read(), ns)
PLACES = ns['PLACES']

# Places whose map position comes from the official point instead of our build:
# no hydro shape at all, or our point/approximate shape is on the wrong stretch.
USE_OFFICIAL_POINT = {
    'X16-NORTHCREEK-WALS', 'X16-STONEY', 'X16-FISHERS', 'X16-INDIANRIVER', 'X16-SANGS',
    'X17-TALBOT-KIRKFIELD', 'X16-NINEMILE-TRIBS', 'X16-SYDENHAM-CHANNELS',
}
# Of those, small sites drawn as a circle round the official centroid ("may apply
# here") rather than a bare point, so a closed-all-year sanctuary still warns on the spot.
OFFICIAL_RADIUS_M = {'X16-SYDENHAM-CHANNELS': 300}
# Hand-checked matches where the wording differs too much to match on its own.
OVERRIDES = {
    'X16-NINEMILE-FISHWAY': '107036061',   # "100 m above Port Albert Fishway", same closure dates
}
SHEETS = {'Fish Sanctuaries': 'S', 'Waterbody Exceptions': 'W', 'Additional Fishing Opportunity': 'W',
          'Fish Sanctuary Location': 'SL', 'Waterbody Location': 'WL'}


def read_xlsx(path):
    """Minimal .xlsx reader (no openpyxl needed): {sheet name: [dict rows]}."""
    z = zipfile.ZipFile(path)
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        x = z.read('xl/sharedStrings.xml').decode('utf-8')
        for si in re.findall(r'<si>(.*?)</si>', x, re.S):
            ss.append(unesc(''.join(re.findall(r'<t[^>]*>(.*?)</t>', si, re.S))))
    wb = z.read('xl/workbook.xml').decode('utf-8')
    rels = z.read('xl/_rels/workbook.xml.rels').decode('utf-8')
    target = {m[0]: m[1] for m in re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', rels)}
    target.update({m[1]: m[0] for m in re.findall(r'Target="([^"]+)"[^>]*Id="([^"]+)"', rels)})
    out = {}
    for name, rid in re.findall(r'<sheet [^>]*name="([^"]+)"[^>]*r:id="([^"]+)"', wb):
        name = unesc(name)
        if name not in SHEETS:
            continue
        t = target[rid].lstrip('/')
        x = z.read(t if t.startswith('xl/') else 'xl/' + t).decode('utf-8')
        rows = []
        for row in re.findall(r'<row[^>]*>(.*?)</row>', x, re.S):
            cells = {}
            for ref, attrs, body in re.findall(r'<c r="([A-Z]+)\d+"([^>]*?)(?:/>|>(.*?)</c>)', row, re.S):
                v = re.search(r'<v>(.*?)</v>', body or '', re.S)
                if 't="s"' in attrs and v:
                    val = ss[int(v.group(1))]
                elif 't="inlineStr"' in attrs:
                    val = unesc(''.join(re.findall(r'<t[^>]*>(.*?)</t>', body, re.S)))
                else:
                    val = unesc(v.group(1)) if v else ''
                cells[ref] = val
            rows.append(cells)
        hdr = rows[0]
        cols = sorted(hdr, key=lambda c: (len(c), c))
        out[name] = [{hdr[c]: r.get(c, '') for c in cols} for r in rows[1:]]
    return out


def unesc(s):
    return (s.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
             .replace('&apos;', "'").replace('&amp;', '&'))


def norm(s):
    s = s.lower().replace('’', "'").replace('twp.', 'township').replace('hwy.', 'highway')
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', s)).strip()


def zone(v):
    try:
        return int(float(v))
    except ValueError:
        return None


def ogf(v):
    return str(int(float(v))) if v not in ('', None) else ''


def metres(lat, lng, geom):
    from shapely.geometry import Point, shape
    from shapely.affinity import affine_transform
    k = 111320.0; c = math.cos(math.radians(43.8))
    g = affine_transform(shape(geom), [k * c, 0, 0, k, 0, 0])
    return g.distance(Point(lng * k * c, lat * k))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else (sorted(glob.glob(D + '../regs/fishingregulationsexceptionopendata_*.xlsx')) or [None])[-1]
    if not path:
        sys.exit('No dataset found. Run "py fetch_regs.py" in boundaries\\ first, or pass the .xlsx path.')
    X = read_xlsx(path)
    SL = {ogf(r['Fish Sanctuary OGF ID']): (float(r['Latitude']), float(r['Longitude']), '')
          for r in X['Fish Sanctuary Location'] if r['Latitude']}
    WL = {}
    for r in X['Waterbody Location']:
        if r['Latitude']:
            WL.setdefault(ogf(r['Waterbody OGF ID']), []).append(
                (float(r['Latitude']), float(r['Longitude']), r['Official Name'] or r['Unofficial Name']))
    recs = {}   # ogf -> record
    for sheet in ('Fish Sanctuaries', 'Waterbody Exceptions', 'Additional Fishing Opportunity'):
        typ = SHEETS[sheet]
        key = 'Fish Sanctuary OGF ID' if typ == 'S' else 'Waterbody OGF ID'
        for r in X[sheet]:
            z = zone(r['Zone Number'])
            if z not in (16, 17):
                continue
            o = ogf(r[key])
            k = (o, r['Waterbody Description'])
            if k in recs:
                continue
            pts = [SL[o]] if typ == 'S' and o in SL else WL.get(o, []) if typ == 'W' else []
            recs[k] = {'type': typ, 'zone': z, 'ogfId': o, 'description': r['Waterbody Description'],
                       'rule': r.get('Fish Sanctuary', ''), 'points': pts, 'sheet': sheet}
    R = list(recs.values())
    geoms = {}
    for f in ('geoms.json', 'geoms_small.json'):
        if os.path.exists(D + f):
            geoms = json.load(open(D + f)); break

    out, used = {}, set()
    for p in PLACES:
        want = 'S' if p['kind'] == 'sanctuary' else 'W'
        cands = [r for r in R if r['zone'] == p['zone']]   # a reach can hold a sanctuary rule too
        if p['id'] in OVERRIDES:
            best = [r for r in R if r['ogfId'] == OVERRIDES[p['id']]][0]; score = 1.0
        else:
            sc = [(difflib.SequenceMatcher(None, norm(p['desc']), norm(r['description'])).ratio()
                   + (0.05 if r['type'] == want else 0), i) for i, r in enumerate(cands)]
            if not sc:
                continue
            score, i = max(sc); best = cands[i]
            score -= 0.05 if best['type'] == want else 0
            if score < 0.6:
                continue
        used.add((best['ogfId'], best['description']))
        e = {'ogfId': best['ogfId'], 'sheet': best['sheet'], 'description': best['description'],
             'points': best['points'], 'score': round(score, 2)}
        g = geoms.get(p['id'])
        if g and best['points']:
            pts = best['points']
            if best['type'] == 'W':   # several tributaries listed: compare with the one named like the place
                named = [q for q in pts if q[2] and norm(q[2]).split(' ')[0] in norm(p['name'])]
                pts = named or pts
            e['distM'] = round(min(metres(q[0], q[1], g['geometry']) for q in pts))
        e['useOfficialPoint'] = p['id'] in USE_OFFICIAL_POINT and bool(best['points'])
        if e['useOfficialPoint'] and p['id'] in OFFICIAL_RADIUS_M:
            e['radiusM'] = OFFICIAL_RADIUS_M[p['id']]
        out[p['id']] = e

    meta = {'source': 'Recreational fishing regulations data (Ontario Ministry of Natural Resources), Open Government Licence - Ontario',
            'dataset': 'https://data.ontario.ca/dataset/recreational-fishing-regulations-data',
            'file': os.path.basename(path)}
    json.dump({'meta': meta, 'places': out}, open(D + 'official.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

    shared = {}
    for r in R:
        shared[r['ogfId']] = shared.get(r['ogfId'], 0) + 1   # one centroid for several printed places: no fair check
    print('matched %d of %d places to an official record' % (len(out), len(PLACES)))
    for p in PLACES:
        e = out.get(p['id'])
        if not e:
            print('  NO MATCH   ', p['id'], '|', p['desc'][:80])
        elif e['useOfficialPoint']:
            print('  OFFICIAL PT', p['id'], e['points'][0][:2])
        elif best_is_far(p, e, geoms) and shared[e['ogfId']] == 1:
            print('  CHECK      ', p['id'], '%s m from the official sanctuary centroid' % e['distM'])
    for r in R:
        if r['type'] == 'S' and not any(r['ogfId'] == u[0] for u in used) and not any(
                difflib.SequenceMatcher(None, norm(p['desc']), norm(r['description'])).ratio() > 0.7 for p in PLACES):
            print('  NOT IN APP ', r['zone'], r['ogfId'], r['description'][:80])


def best_is_far(p, e, geoms):
    # Only sanctuary centroids are a fair check; waterbody points are the whole river's mouth or centroid.
    return e['sheet'] == 'Fish Sanctuaries' and e.get('distM', 0) > 1000


if __name__ == '__main__':
    main()
