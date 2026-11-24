import os; os.chdir(os.path.dirname(os.path.abspath(__file__)))
import json
from shapely.geometry import shape, mapping
d=json.load(open('geoms.json'))
def rnd(c):
    if isinstance(c[0],(int,float)): return [round(c[0],5),round(c[1],5)]
    return [rnd(x) for x in c]
tot=0
for k,v in d.items():
    g=v['geometry']
    if g['type'] in ('Point','MultiPoint'): continue
    tol = 0.0001 if v['precision']=='drawn' else 0.0004
    s=shape(g).simplify(tol, preserve_topology=True)
    if s.geom_type in ('Polygon','MultiPolygon'):
        # drop slivers under 50 m2
        if s.geom_type=='MultiPolygon':
            from shapely.geometry import MultiPolygon
            parts=[p for p in s.geoms if p.area > 50/ (111000*80000)]
            s=MultiPolygon(parts) if len(parts)>1 else (parts[0] if parts else s)
    m=mapping(s); v['geometry']={'type':m['type'],'coordinates':rnd(m['coordinates'])}
json.dump(d,open('geoms_small.json','w'),separators=(',',':'))
print(len(open('geoms_small.json').read()))
