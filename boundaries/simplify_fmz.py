"""Make the phone-sized copy of the official FMZ boundaries.

Reads the newest boundaries/official/fmz_official_<date>.geojson (or a path given
on the command line) and writes boundaries/fmz_app_<date>.geojson plus a
.meta.json beside it. Standard library only.

Topology is kept: a border shared by two zones is simplified once and used by
both, so the simplified zones neither overlap nor leave gaps along it. Each
removed point lies within TOL degrees of the simplified line (Douglas-Peucker),
which the meta file reports in metres so the app can warn near edges.

Usage:  py simplify_fmz.py [path\\to\\fmz_official_<date>.geojson] [--tol 0.0015]
"""
import json, sys, os, glob, math, hashlib, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
args = [a for a in sys.argv[1:]]
TOL = 0.0015            # degrees; about 165 m north-south, 105-115 m east-west in Ontario
if '--tol' in args:
    i = args.index('--tol'); TOL = float(args[i+1]); del args[i:i+2]
MIN_AREA = 2e-6         # deg^2 (~1.5-2 ha): drop specks, the same way for islands and their holes
Q = 1e5                 # snap input to 1e-5 deg (~1 m) so shared vertices match exactly
OUT_DP = 4              # output decimals (~11 m)

src = args[0] if args else sorted(glob.glob(os.path.join(HERE, 'official', 'fmz_official_*.geojson')))[-1]
print('reading', src)
raw = open(src, 'rb').read()
fc = json.loads(raw)
edition = os.path.basename(src).replace('fmz_official_', '').replace('.geojson', '')

def zone_no(f):
    p = f['properties']
    return int(p.get('FISHERIES_MANAGEMENT_ZONE_ID') or p.get('fisheries_management_zone_id'))

# --- collect rings as lists of integer points ---------------------------------
feats = []   # (zone, [polygon = [ring, ...]])
for f in fc['features']:
    g = f['geometry']
    polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    out = []
    for poly in polys:
        rings = []
        for ring in poly:
            pts = []
            for x, y in ring:
                p = (round(x*Q), round(y*Q))
                if not pts or pts[-1] != p: pts.append(p)
            if len(pts) > 1 and pts[0] == pts[-1]: pts.pop()
            if len(pts) >= 3: rings.append(pts)
        if rings: out.append(rings)
    feats.append((zone_no(f), out))

# --- which zones own each point -------------------------------------------------
owners = {}
for z, polys in feats:
    for poly in polys:
        for ring in poly:
            for p in ring:
                s = owners.get(p)
                if s is None: owners[p] = {z}
                else: s.add(z)

def is_node(ring, i):
    n = len(ring); o = owners[ring[i]]
    return len(o) >= 3 or owners[ring[i-1]] != o or owners[ring[(i+1) % n]] != o

def dp(pts, tol):
    """Douglas-Peucker on a list of points (ints), keeping both ends."""
    keep = [False]*len(pts); keep[0] = keep[-1] = True
    stack = [(0, len(pts)-1)]
    t2 = (tol*Q)**2
    while stack:
        a, b = stack.pop()
        if b <= a+1: continue
        ax, ay = pts[a]; bx, by = pts[b]
        dx, dy = bx-ax, by-ay; L = dx*dx+dy*dy
        best, bi = -1.0, -1
        for i in range(a+1, b):
            px, py = pts[i]
            if L == 0: d = (px-ax)**2+(py-ay)**2
            else:
                t = max(0.0, min(1.0, ((px-ax)*dx+(py-ay)*dy)/L))
                d = (px-ax-t*dx)**2+(py-ay-t*dy)**2
            if d > best: best, bi = d, i
        if best > t2:
            keep[bi] = True; stack += [(a, bi), (bi, b)]
    return [p for p, k in zip(pts, keep) if k]

cache = {}
def simplify_arc(arc):
    """Same arc, same answer, whichever direction a zone walks it."""
    fwd = tuple(arc); rev = fwd[::-1]
    key = min(fwd, rev)
    if key not in cache: cache[key] = dp(list(key), TOL)
    s = cache[key]
    return s if key == fwd else s[::-1]

def area(r):
    return abs(sum(r[i-1][0]*r[i][1]-r[i][0]*r[i-1][1] for i in range(len(r))))/2/(Q*Q)

def simplify_ring(ring):
    if area(ring) < MIN_AREA: return None
    n = len(ring)
    nodes = [i for i in range(n) if is_node(ring, i)]
    if not nodes:
        # free-standing ring (island, or a ring nobody shares): cut at two fixed,
        # direction-independent points so both copies of it simplify alike
        i0 = ring.index(min(ring))
        far = max(range(n), key=lambda i: (ring[i][0]-ring[i0][0])**2+(ring[i][1]-ring[i0][1])**2)
        nodes = sorted({i0, far})
    out = []
    for k in range(len(nodes)):
        a = nodes[k]; b = nodes[(k+1) % len(nodes)]
        arc = ring[a:b+1] if b > a else ring[a:]+ring[:b+1]
        s = simplify_arc(arc)
        out.extend(s[:-1])
    if len(out) < 3 or area(out) < MIN_AREA: return None
    out.append(out[0])
    return [[round(x/Q, OUT_DP), round(y/Q, OUT_DP)] for x, y in out]

nv_in = sum(len(r) for _, ps in feats for p in ps for r in p)
features = []
for z, polys in sorted(feats):
    mp = []
    for poly in polys:
        outer = simplify_ring(poly[0])
        if not outer: continue
        holes = [h for h in (simplify_ring(r) for r in poly[1:]) if h]
        mp.append([outer]+holes)
    features.append({'type':'Feature', 'properties':{'zone':z, 'code':'FMZ-%d' % z},
                     'geometry':{'type':'MultiPolygon', 'coordinates':mp}})
nv_out = sum(len(r) for f in features for p in f['geometry']['coordinates'] for r in p)

out_path = os.path.join(HERE, 'fmz_app_%s.geojson' % edition)
body = json.dumps({'type':'FeatureCollection', 'features':features}, separators=(',', ':'))
open(out_path, 'w').write(body)
tol_m = round(TOL*111320)
meta = {
  'derivedFrom': os.path.basename(src),
  'derivedFromSha256': hashlib.sha256(raw).hexdigest(),
  'edition': edition,
  'made': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
  'method': 'shared-border Douglas-Peucker (simplify_fmz.py)',
  'toleranceDeg': TOL, 'maxShiftM': tol_m,
  'droppedRingsSmallerThanDeg2': MIN_AREA,
  'outputDecimals': OUT_DP,
  'verticesIn': nv_in, 'verticesOut': nv_out,
  'zones': [f['properties']['zone'] for f in features],
  'bytes': len(body),
  'sha256': hashlib.sha256(body.encode()).hexdigest()
}
json.dump(meta, open(out_path.replace('.geojson', '.meta.json'), 'w'), indent=1)
print(json.dumps(meta, indent=1))
