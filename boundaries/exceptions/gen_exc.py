# Turns data16_17.py + geoms.json into zone-document areas/provisions and inserts them into index.html
import json, sys, re
import os
D = os.path.dirname(os.path.abspath(__file__)) + '/'
exec(open(D + 'data16_17.py', encoding='utf-8').read())
GEO = json.load(open(D + 'geoms_small.json'))          # id -> {precision, geometry}
P = sys.argv[1]
s = open(P, encoding='utf-8').read()

ZW16 = ['atlantic_salmon', 'brook_trout', 'brown_trout', 'channel_catfish', 'g:on_crappie', 'lake_trout', 'lake_whitefish',
        'g:on_pacific_salmon', 'rainbow_trout', 'splake', 'g:on_sunfish', 'yellow_perch']

def tgt(t): return "{group:'%s'}" % t[2:] if t.startswith('g:') else "{species:'%s'}" % t
def q(x): return "'" + x.replace('\\', '\\\\').replace("'", "\\'") + "'"
def win(w): return w.replace('fx(2,28)', 'FEB_END')
def jgeom(g): return json.dumps(g, separators=(',', ':'))

areas = {16: [], 17: []}; provs = {16: [], 17: []}
for p in PLACES:
    z = p['zone']; g = GEO.get(p['id'])
    prec = g['precision'] if g else 'none'
    a = "{id:%s, kind:'%s', exc:true, name:%s, legalDescription:%s, page:%d, precision:'%s'" % (
        q(p['id']), p['kind'], q(p['name']), q(p['desc']), p['page'], prec)
    if p['note']: a += ", note:%s" % q(p['note'])
    if g and g.get('lineBuffer'): a += ", lineBuffer:%d" % g['lineBuffer']
    a += ", geometry:%s}" % (jgeom(g['geometry']) if g else 'null')
    areas[z].append(a)
    n = 0
    for r in p['rules']:
        n += 1; key = "'fmz%d.exc.%s.%d'" % (z, p['id'][4:].lower(), n)
        base = "key:%s, areaId:%s" % (key, q(p['id']))
        t = r['t']
        if t == 'closure':
            provs[z].append("{%s, type:'closure', target:null, windows:%s%s, text:%s}" % (base, win(r['windows']), ", night:true" if r['night'] else '', q(r['text'])))
        elif t == 'restriction':
            provs[z].append("{%s, type:'restriction', target:null, restriction:{code:'%s'}, text:%s}" % (base, r['code'], q(r['text'])))
        elif t == 'season':
            if r.get('closed'):
                provs[z].append("{%s, type:'season', target:%s, closedAllYear:true, text:%s}" % (base, tgt(r['target']), q(r['text'])))
            else:
                provs[z].append("{%s, type:'season', target:%s, windows:%s, text:%s}" % (base, tgt(r['target']), win(r['windows']), q(r['text'])))
        elif t == 'season_all_except':
            for i, sp in enumerate([x for x in ZW16 if x not in r['exclude']]):
                provs[z].append("{key:%s, areaId:%s, type:'season', target:%s, windows:%s, text:%s}" % (
                    "'fmz%d.exc.%s.%d.%d'" % (z, p['id'][4:].lower(), n, i), q(p['id']), tgt(sp), win(r['windows']), q(r['text'])))
        elif t == 'limit':
            x = "{%s, type:'limit', target:%s, limits:lim(%d,%d)" % (base, tgt(r['target']), r['s'], r['c'])
            if r['bands']: x += ", sizeBands:%s, sizeText:%s" % (json.dumps(r['bands']).replace('"', ''), q(r['size']))
            if r['when']: x += ", when:%s, whenText:%s" % (win(r['when']), q(r['whenText']))
            x += ", text:%s}" % q(r['text'])
            provs[z].append(x)
        else:
            raise Exception(t)

hdr = """
/* ---------------------------------------------------------------------
   EXCEPTIONS (pilot): FMZ 16 and 17 species exceptions, waterbody
   exceptions and fish sanctuaries, transcribed from the 2026 summary
   (pp. 118-124, 128-129). Places are matched to the Ontario Hydro Network
   (Land Information Ontario); see boundaries/fetch_waters.py.
   --------------------------------------------------------------------- */
const APR4F = nth(4, SAT, 4, -1), MAY2F = nth(2, SAT, 5, -1), MAY2A = nth(2, SAT, 5, 6);
const FEB_END = {type:'last_day', month:2};
"""
out = hdr
for z in (16, 17):
    out += "const EXC%d_AREAS = [\n  %s\n];\nconst EXC%d_PROVISIONS = [\n  %s\n];\n" % (z, ',\n  '.join(areas[z]), z, ',\n  '.join(provs[z]))

marker = "/* Generated from the 2026 summary's zone-wide tables (gen_docs.py)."
assert s.count(marker) == 1
s = s.replace(marker, out + "\n" + marker)
# attach to docs after ZONE_DOCS is built
anchor = "const ZONE_DOCS = [FMZ16"
i = s.index(anchor); j = s.index('\n', i)
# find end of the ZONE_DOCS statement (first line ending with ';' from i)
k = s.index(';', i)
attach = """
/* attach the pilot exceptions (FMZ 16 and 17) */
[[16, EXC16_AREAS, EXC16_PROVISIONS], [17, EXC17_AREAS, EXC17_PROVISIONS]].forEach(([n, as, ps]) => {
  const d = ZONE_DOCS.find(x => x.zone.code === 'FMZ-'+n);
  d.areas.push(...as); d.provisions.push(...ps);
  d.meta.sourcePages += n === 16 ? ' (exceptions pp. 118–124)' : ' (exceptions pp. 128–129)';
  const nb = d.provisions.find(p => p.kind === 'exceptions_not_loaded');
  if(nb){ nb.kind = 'exceptions_loaded';
    nb.text = 'Lake and river exceptions and fish sanctuaries for '+d.zone.name+' are loaded from the summary as a trial. Most are matched to official river and lake shapes, but where a stretch starts and ends can be approximate, and unnamed tributaries aren’t drawn. Check the description before you fish a river or stream.'; }
});
"""
s = s[:k+1] + attach + s[k+1:]
open(P, 'w', encoding='utf-8').write(s)
print('areas', {z: len(areas[z]) for z in areas}, 'provisions', {z: len(provs[z]) for z in provs})
