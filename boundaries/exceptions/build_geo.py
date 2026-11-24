# Match each FMZ 16/17 exception place to official OHN shapes and cut river stretches
# between the roads, rail lines, dams or points that the summary names.
# Inputs: w/*.geojson (from boundaries/fetch_waters.py on Andrew's PC), data16_17.py, ends.py
# Output: geoms.json {place id: {precision, geometry, lineBuffer?, why}}
import json, math, re, sys
from shapely.geometry import shape, mapping, Point, LineString, MultiLineString, Polygon, MultiPolygon, GeometryCollection
from shapely.ops import unary_union, nearest_points, transform
from shapely.strtree import STRtree

import os
D = os.path.dirname(os.path.abspath(__file__)) + '/'
W = D + '../waters/'
exec(open(D + 'data16_17.py', encoding='utf-8').read())
exec(open(D + 'ends.py', encoding='utf-8').read())   # ENDS, TWP_MAP

LAT0 = 43.8
KX = 111320 * math.cos(math.radians(LAT0)); KY = 110540
def fwd(x, y, z=None): return ((x + 79.5) * KX, (y - LAT0) * KY)
def inv(x, y, z=None): return (x / KX - 79.5, y / KY + LAT0)
P = lambda g: transform(fwd, g)
U = lambda g: transform(inv, g)

def load(n): return json.load(open(W + n + '.geojson'))['features']
WB = load('waterbody'); WC = load('watercourse'); TW = load('townships'); NM = load('names'); DM = load('dams'); RD = load('roads'); RL = load('rail')
from shapely.validation import make_valid
for f in WB + WC + TW + NM + DM + RD + RL:
    g = P(shape(f['geometry']))
    f['g'] = make_valid(g) if not g.is_valid else g
TWP = {}
for f in TW: TWP.setdefault(f['properties']['name'], []).append(f['g'])
TWP = {k: unary_union(v) for k, v in TWP.items()}
FMZ = {f['properties']['zone']: make_valid(P(shape(f['geometry']))) for f in json.load(open(D + '../fmz_app_2026-10-22.geojson'))['features']}
GREAT = unary_union([FMZ[z] for z in (13, 14, 19, 20)])
SIMCOE = None

def rlabel(p):
    s = [p.get('name') or '']
    for k in ('alternate_names', 'route_names'):
        if p.get(k): s += p[k]
    if p.get('route_numbers'): s += ['#' + str(n) for n in p['route_numbers']]
    return ' | '.join(s)
for f in RD: f['label'] = rlabel(f['properties'])
for f in RL: f['label'] = ' | '.join(str(f['properties'].get(k) or '') for k in ('name', 'operator', 'subdivision', 'subdivision_2'))
RD_TREE = STRtree([f['g'] for f in RD]); RL_TREE = STRtree([f['g'] for f in RL])

def norm(s): return re.sub(r"[’'`]", '', s.lower())
def twp_area(hints):
    names = []
    for h in hints:
        names += TWP_MAP.get(h, [h.upper()])
    gs = [TWP[n] for n in names if n in TWP]
    missing = [n for n in names if n not in TWP]
    return (unary_union(gs) if gs else None), missing

def water_feats(names, area, zone):
    zg = FMZ[zone].buffer(3000)
    out = []
    for f in WB + WC:
        mn = f['properties'].get('matched_names') or [f['properties']['matched_name']]
        if not any(n in mn for n in names): continue
        if not f['g'].intersects(zg): continue
        if area is not None and not f['g'].intersects(area.buffer(1500)): continue
        out.append(f)
    return out

def river_geom(feats):
    """Polygons as they are, lines buffered 8 m, unioned."""
    parts = [f['g'] if f['g'].geom_type in ('Polygon', 'MultiPolygon') else f['g'].buffer(8, cap_style=2) for f in feats]
    return unary_union(parts) if parts else None

def crossings(river, regex, tree, feats, near=None):
    """Road or rail lines matching regex that touch the river; returns list of cutter lines."""
    rx = re.compile(regex, re.I)
    idx = tree.query(river.buffer(30))
    cs = [feats[i] for i in idx if rx.search(feats[i]['label']) and feats[i]['g'].intersects(river.buffer(15))]
    return cs

def cutter_from_point(river, pt, half=400):
    """A line through pt across the river: perpendicular to the river's local direction."""
    loc = river.intersection(pt.buffer(120))
    if loc.is_empty: loc = river.intersection(pt.buffer(400))
    if loc.is_empty: return None
    r = loc.minimum_rotated_rectangle
    cs = list(r.exterior.coords)[:4]
    e = [(cs[i], cs[(i + 1) % 4]) for i in range(2)]
    a, b = max(e, key=lambda s: math.dist(*s))          # long side = along the river
    ang = math.atan2(b[1] - a[1], b[0] - a[0]) + math.pi / 2
    snap = nearest_points(river, pt)[0]
    return LineString([(snap.x - half * math.cos(ang), snap.y - half * math.sin(ang)), (snap.x + half * math.cos(ang), snap.y + half * math.sin(ang))])

def dam_point(regex):
    rx = re.compile(regex, re.I)
    ds = [f for f in DM if f['properties']['name'] and rx.search(f['properties']['name'])]
    return ds[0]['g'] if len(ds) == 1 else (ds and ds[0]['g'])

def pt_ll(lat, lng): return Point(fwd(lng, lat))

def end_cutter(river, spec, zone):
    """Return (cutter_geometry or None, kind). kind 'mouth' means the downstream end at a lake."""
    if spec == 'mouth': return None, 'mouth'
    if spec is None: return None, 'upstream'
    t, arg = spec.split(':', 1)
    if t == 'R':
        cs = crossings(river, arg, RD_TREE, RD)
        if not cs:
            # the river outline often has a gap under the bridge: use the nearest matching road within 80 m
            rx = re.compile(arg, re.I)
            near = [RD[i] for i in RD_TREE.query(river.buffer(80)) if rx.search(RD[i]['label']) and RD[i]['g'].distance(river) <= 80]
            if not near: return None, 'missing road ' + arg
            f = min(near, key=lambda f: f['g'].distance(river))
            c = cutter_from_point(river, nearest_points(f['g'], river)[1])
            return (c, 'ok') if c else (None, 'no cutter near road ' + arg)
        return unary_union([c['g'] for c in cs]), 'ok'
    if t == 'RR':
        cs = crossings(river, arg, RL_TREE, RL)
        if not cs: return None, 'missing rail ' + arg
        return unary_union([c['g'] for c in cs]), 'ok'
    if t in ('D', 'P', 'C'):
        if t == 'D':
            p = dam_point(arg)
            if not p: return None, 'missing dam ' + arg
        elif t == 'P':
            la, ln = map(float, arg.split(','))
            p = pt_ll(la, ln)
        else:
            other = river_geom(water_feats([arg], None, zone))
            if other is None:
                nm = [f['g'] for f in NM if arg in (f['properties'].get('matched_names') or [])]
                other = unary_union(nm) if nm else None
            if other is None: return None, 'missing confluence ' + arg
            p = nearest_points(other, river)[0]
        if p.distance(river) > 600: return None, 'point %d m from river (%s)' % (p.distance(river), spec)
        c = cutter_from_point(river, p)
        return (c, 'ok') if c else (None, 'no cutter ' + spec)
    if t == 'T':
        a, b = arg.split('|')
        A = TWP.get(a); B = TWP.get(b)
        if A is None or B is None: return None, 'missing township ' + arg
        line = A.boundary.intersection(B.boundary)
        if line.is_empty: line = A.buffer(5).intersection(B.buffer(5)).boundary
        return line.buffer(1), 'ok'
    raise Exception(spec)

GAP_TOL = 300   # OHN rivers come in pieces (polygons for wide parts, lines for narrow ones); bridge gaps up to this
def cut_between(river, ca, cb, kinds, zone, lake=None):
    """Pieces of the river lying between cutter a and cutter b (or between a and the mouth / the upstream end)."""
    cutters = [c for c in (ca, cb) if c is not None]
    gap = unary_union([c.buffer(3) for c in cutters])
    wall = unary_union([c.buffer(5) for c in cutters])
    pieces = river.difference(gap)
    pieces = list(pieces.geoms) if hasattr(pieces, 'geoms') else [pieces]
    pieces = [p for p in pieces if p.area > 20]
    n = len(pieces)
    tree = STRtree(pieces)
    adj = {i: set() for i in range(n)}
    for i, p in enumerate(pieces):
        for j in tree.query(p.buffer(GAP_TOL)):
            j = int(j)
            if j <= i: continue
            q = pieces[j]
            if p.distance(q) > GAP_TOL: continue
            a, bpt = nearest_points(p, q)
            link = LineString([a, bpt]) if a.distance(bpt) > 0 else a.buffer(0.5)
            if link.intersects(wall) and p.distance(q) > 0.5: continue
            if p.distance(q) <= 0.5 and p.intersection(q).within(wall): continue
            adj[i].add(j); adj[j].add(i)
    comp = [-1] * n; k = 0
    for i in range(n):
        if comp[i] >= 0: continue
        st = [i]; comp[i] = k
        while st:
            x = st.pop()
            for y in adj[x]:
                if comp[y] < 0: comp[y] = k; st.append(y)
        k += 1
    groups = {}
    for i in range(n): groups.setdefault(comp[i], []).append(i)
    def touches(ids, c): return any(pieces[i].distance(c) < 8 for i in ids)
    target = lake if lake is not None else GREAT
    def at_lake(ids): return any(pieces[i].distance(target) < 1000 for i in ids)
    if ca is not None and cb is not None:
        sel = [g for g in groups.values() if touches(g, ca) and touches(g, cb)]
        if not sel: return None, 'no piece touches both ends'
        g = max(sel, key=lambda g: sum(pieces[i].area for i in g))
    else:
        c = ca if ca is not None else cb
        up = 'upstream' in kinds
        area = lambda g: sum(pieces[i].area for i in g)
        sel = [g for g in groups.values() if touches(g, c)]
        big = [g for g in sel if area(g) >= 300]
        sel = big if len(big) >= 2 else sel
        dist = lambda g: min(pieces[i].distance(target) for i in g)
        if len(sel) < 2:
            if not up and sel and dist(sel[0]) < 1000: return unary_union([pieces[i] for i in sel[0]]), 'ok'
            return None, 'cut did not split the river'
        sel.sort(key=dist)
        g = sel[-1] if up else sel[0]
        if not up and dist(g) > 5000: return None, 'no piece near the mouth'
    return unary_union([pieces[i] for i in g]), 'ok'

def lonlat(g, prec=5):
    g = U(g)
    def r(c):
        if isinstance(c, (list, tuple)) and c and isinstance(c[0], (int, float)): return [round(c[0], prec), round(c[1], prec)]
        return [r(x) for x in c]
    m = mapping(g)
    if m['type'] == 'GeometryCollection':
        return {'type': 'GeometryCollection', 'geometries': [lonlat(P(shape(x))) for x in m['geometries']]}
    return {'type': m['type'], 'coordinates': r(m['coordinates'])}

def simplify(g, tol=6):
    return g.simplify(tol, preserve_topology=True)

def as_app_geom(g):
    """Polygons stay polygons; thin buffered lines are sent back as their centre lines to keep the file small."""
    return simplify(g)

ONLY = set(sys.argv[1:])
OUT = json.load(open(D + 'geoms.json')) if ONLY else {}; REPORT = []
for p in PLACES:
    if ONLY and p['id'] not in ONLY: continue
    pid = p['id']; zone = p['zone']; spec = ENDS.get(pid, {})
    if spec.get('skip'): continue
    area, missing = twp_area(spec.get('twp', p['twp']))
    if p['kind'] == 'county_waters':
        g = area
        if spec.get('shore_km') and g is not None:
            g = g.intersection(GREAT.buffer(spec['shore_km'] * 1000))
        if g is None: REPORT.append((pid, 'FAIL no area')); continue
        OUT[pid] = {'precision': 'approx', 'geometry': lonlat(simplify(g, 60)), 'why': 'townships'}
        REPORT.append((pid, 'county area', missing)); continue
    feats = water_feats(spec.get('water', p['water']), area, zone) if (spec.get('water', p['water'])) else []
    river = river_geom(feats)
    pts = p['pt'] if isinstance(p['pt'], list) else ([p['pt']] if p['pt'] else [])
    if spec.get('anchor'):      # small area around a point: dam, falls, causeway
        t = spec['anchor']
        if t.startswith('D:'): ap = dam_point(t[2:])
        elif t.startswith('P:'): la, ln = map(float, t[2:].split(',')); ap = pt_ll(la, ln)
        elif t.startswith('R:'):
            rx = re.compile(t[2:], re.I)
            cs = [RD[i] for i in RD_TREE.query(river.buffer(40)) if rx.search(RD[i]['label']) and RD[i]['g'].distance(river) <= 40] if river is not None else []
            ap = unary_union([c['g'] for c in cs]).intersection(river.buffer(40)) if cs else None
        else: ap = None
        if ap is not None and not ap.is_empty and river is None and ap.geom_type == 'Point':
            q = U(ap); OUT[pid] = {'precision': 'point', 'geometry': {'type': 'Point', 'coordinates': [round(q.x, 5), round(q.y, 5)]}, 'why': 'anchor point only ' + t}
            REPORT.append((pid, 'anchor point only')); continue
        if ap is None or ap.is_empty or river is None:
            REPORT.append((pid, 'FAIL anchor', t, len(feats))); continue
        rad = spec.get('radius', 300)
        g = river.intersection(ap.buffer(rad))
        if g.is_empty:
            REPORT.append((pid, 'FAIL anchor not on water', t, ap.distance(river))); continue
        OUT[pid] = {'precision': spec.get('precision', 'approx'), 'geometry': lonlat(simplify(g)), 'why': 'anchor ' + t}
        REPORT.append((pid, 'anchor', round(g.area))); continue
    if river is None:
        if pts:
            OUT[pid] = {'precision': 'point', 'geometry': {'type': 'MultiPoint', 'coordinates': [[q[1], q[0]] for q in pts]} if len(pts) > 1 else {'type': 'Point', 'coordinates': [pts[0][1], pts[0][0]]}, 'why': 'printed coordinate'}
            REPORT.append((pid, 'point from coords')); continue
        # names layer point
        nm = [f for f in NM if any(n in (f['properties'].get('matched_names') or []) for n in p['water']) and (area is None or f['g'].intersects(area.buffer(2000)))]
        if nm:
            f = nm[0]; OUT[pid] = {'precision': 'point', 'geometry': {'type': 'Point', 'coordinates': [round(f['properties']['longitude_decimal_degrees'], 5), round(f['properties']['latitude_decimal_degrees'], 5)]}, 'why': 'Geographic Names point'}
            REPORT.append((pid, 'point from names')); continue
        REPORT.append((pid, 'FAIL no water', p['water'], missing)); continue
    ends = spec.get('ends')
    lake = None
    if spec.get('lake'):
        lake = river_geom(water_feats([spec['lake']], None, zone))
    if not ends:
        OUT[pid] = {'precision': spec.get('precision', 'approx' if p['kind'] != 'waterbody' else 'drawn'), 'geometry': lonlat(simplify(river)), 'why': 'whole named water in townships'}
        REPORT.append((pid, 'whole', len(feats), missing)); continue
    ca, ka = end_cutter(river, ends[0], zone)
    cb, kb = end_cutter(river, ends[1], zone)
    if (ka not in ('ok', 'mouth', 'upstream')) or (kb not in ('ok', 'mouth', 'upstream')):
        OUT[pid] = {'precision': 'approx', 'geometry': lonlat(simplify(river)), 'why': 'ends not found: %s / %s' % (ka, kb)}
        REPORT.append((pid, 'APPROX', ka, kb)); continue
    g, why = cut_between(river, ca, cb, (ka, kb), zone, lake)
    if g is None:
        OUT[pid] = {'precision': 'approx', 'geometry': lonlat(simplify(river)), 'why': why}
        REPORT.append((pid, 'APPROX', why)); continue
    OUT[pid] = {'precision': spec.get('precision', 'drawn'), 'geometry': lonlat(simplify(g)), 'why': 'cut %s .. %s' % tuple(ends)}
    REPORT.append((pid, 'CUT', round(g.area), round(g.length)))

json.dump(OUT, open(D + 'geoms.json', 'w'))
for r in REPORT: print(*r)
print(len(OUT), 'of', len(PLACES), 'size', len(json.dumps(OUT)))
