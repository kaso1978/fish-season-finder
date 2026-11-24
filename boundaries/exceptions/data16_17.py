# Exceptions for FMZ 16 and 17, transcribed by hand from the 2026 Ontario
# Fishing Regulations Summary (pp. 118-124 and 128-129).
# Each PLACE is one area in the zone document; its rules become provisions.
#
# Window expressions are JS source using fx(), nth(), and these constants
# (defined in index.html beside the exceptions):
#   APR4  = fourth Saturday in April        APR4F = Friday before it
#   MAY2  = second Saturday in May          MAY2F = Friday before it, MAY2A = Friday after it
#   JUN1, JUN4 = first / fourth Saturday in June

PLACES = []

def place(zone, pid, kind, name, desc, page, water=None, twp=None, pt=None, rules=None, note=None, within=None):
    PLACES.append(dict(zone=zone, id=pid, kind=kind, name=name, desc=desc, page=page,
                       water=water or [], twp=twp or [], pt=pt, rules=rules or [], note=note, within=within))

# rule helpers ---------------------------------------------------------
def sanct(windows, text, night=False):  return dict(t='closure', windows=windows, text=text, night=night)
def closed_all_year(text='Fish sanctuary - closed all year'): return dict(t='closure', windows='ALL_YEAR', text=text, night=False)
def season(target, windows, text):      return dict(t='season', target=target, windows=windows, text=text)
def closed(target, text):               return dict(t='season', target=target, closed=True, text=text)
def limit(target, s, c, text, bands=None, size=None, when=None, whenText=None, extra=None):
    return dict(t='limit', target=target, s=s, c=c, text=text, bands=bands, size=size, when=when, whenText=whenText, extra=extra)
def restr(text, code):                  return dict(t='restriction', text=text, code=code)

SAL4 = ['atlantic_salmon', 'brown_trout', 'g:on_pacific_salmon', 'rainbow_trout']   # "Atlantic Salmon, Brown Trout, Pacific Salmon and Rainbow Trout"
TROUT3 = ['brook_trout', 'brown_trout', 'rainbow_trout']

S_JAN_APR = '[[fx(1,1), APR4F]]'
S_JAN_APR_OCT = '[[fx(1,1), APR4F], [fx(10,1), fx(12,31)]]'
T_JAN_APR = 'Fish Sanctuary - no fishing from January 1 to Friday before fourth Saturday in April'
T_JAN_APR_OCT = 'Fish Sanctuary - no fishing from January 1 to Friday before fourth Saturday in April and October 1 to December 31'
S_APR_MAY31 = '[[APR4, fx(5,31)]]'
T_APR_MAY31 = 'Fish Sanctuary - no fishing from fourth Saturday in April to May 31'
LURES = restr('Only artificial lures may be used', 'artificial_lures_only')
BARBLESS = restr('Only one barbless hook may be used', 'one_barbless_hook')

# ======================================================================
# FMZ 16 - Species exceptions (pp. 118-119)
# ======================================================================
# Brook Trout, additional opportunity: open all year
place(16, 'X16-BELLS', 'waterbody', 'Bells Lake', 'Bells Lake (44°19\'15"N, 80°44\'09"W)', 118,
      water=['Bells Lake'], pt=(44.3208, -80.7358),
      rules=[season('brook_trout', 'ALL_YEAR', 'Brook Trout - additional fishing opportunity: open all year')])

# Brown Trout and Rainbow Trout, open all year, S-5 and C-2
BR_ALL = lambda: [season('brown_trout', 'ALL_YEAR', 'Brown Trout - additional fishing opportunity: open all year'),
                  season('rainbow_trout', 'ALL_YEAR', 'Rainbow Trout - additional fishing opportunity: open all year'),
                  limit('brown_trout', 5, 2, 'S-5 and C-2'), limit('rainbow_trout', 5, 2, 'S-5 and C-2')]
place(16, 'X16-BIGCREEK-LOWER', 'reach', 'Big Creek (below Regional Road 21)',
      'Big Creek - Walsingham Township, downstream from Regional Road 21 to Long Point Bay of Lake Erie', 118,
      water=['Big Creek'], twp=['Walsingham'], rules=BR_ALL())
place(16, 'X16-NTHAMES', 'reach', 'North Thames River (main branch)',
      'North Thames River (main branch only) - Middlesex County', 118,
      water=['North Thames River'], twp=['Middlesex County'], rules=BR_ALL())

# Atlantic Salmon, Brown Trout, Pacific Salmon and Rainbow Trout: open all year, zone-wide limits
def sal_all(): return [season(t, 'ALL_YEAR', 'Additional fishing opportunity: open all year; zone-wide limits apply') for t in SAL4]
def sal_ext(): return [season(t, '[[APR4, fx(12,31)]]', 'Additional fishing opportunity: open from fourth Saturday in April to December 31 (extended fall season); zone-wide limits apply') for t in SAL4]
LOWER = [
 ('X16-BLACKCREEK', 'Black Creek', 'Black Creek - City of Nanticoke, from Highway 3 to the junction with the Lynn River', ['Black Creek'], ['Nanticoke']),
 ('X16-BRONTE-LOWER', 'Bronte Creek (below Lakeshore Road)', 'Bronte Creek - Town of Oakville, from Highway 2 (Lakeshore Road West) to Lake Ontario', ['Bronte Creek'], ['Oakville']),
 ('X16-CREDIT-LOWER', 'Credit River (below Highway 403)', 'Credit River and tributaries - City of Mississauga, from the south side of Highway 403 bridge downstream to Lake Ontario', ['Credit River'], ['Mississauga']),
 ('X16-DON-LOWER', 'Don River (below Eglinton Avenue)', 'Don River and tributaries - City of Toronto, from Lake Ontario upstream to Eglinton Avenue', ['Don River'], ['Toronto']),
 ('X16-FIFTEEN', 'Fifteen Mile Creek (below the QEW)', 'Fifteen Mile Creek - City of St. Catharines and Town of Lincoln, between the Queen Elizabeth Way and Lake Ontario', ['Fifteen Mile Creek'], ['Lincoln']),
 ('X16-FORTY', 'Forty Mile Creek (below the QEW)', 'Forty Mile Creek - Town of Grimsby, between the Queen Elizabeth Way and Lake Ontario', ['Forty Mile Creek'], ['Grimsby']),
 ('X16-GRINDSTONE-LOWER', 'Grindstone Creek (below Plains Road)', 'Grindstone Creek - City of Burlington, from Highway 2 (Plains Road) to Hamilton Harbour of Lake Ontario (City of Hamilton in the Region of Halton)', ['Grindstone Creek'], ['Burlington']),
 ('X16-HIGHLAND', 'Highland Creek (below Kingston Road)', 'Highland Creek - City of Toronto from the downstream edge of the Highway 2 (Kingston Road) bridge to Lake Ontario', ['Highland Creek'], ['Toronto']),
 ('X16-HUMBER-LOWER', 'Humber River (below Eglinton Avenue)', 'Humber River - City of Toronto, between Eglinton Avenue and Lake Ontario', ['Humber River'], ['Toronto']),
 ('X16-NOTTAWASAGA-LOWER', 'Nottawasaga River (Boyne River to Georgian Bay)', 'Nottawasaga River - from the Boyne River downstream (north) to Georgian Bay', ['Nottawasaga River'], []),
 ('X16-ROUGE-LOWER', 'Rouge River (below Kingston Road)', 'Rouge River - City of Toronto, between Highway 2 (Kingston Road) and Lake Ontario', ['Rouge River'], ['Toronto']),
 ('X16-SIXTEEN-OAK-LOWER', 'Sixteen Mile Creek, Oakville (below Lakeshore Road)', 'Sixteen Mile Creek (Oakville Creek) - Town of Oakville, from Highway 2 (Lakeshore Road) to Lake Ontario', ['Sixteen Mile Creek', 'Oakville Creek'], ['Oakville']),
 ('X16-SIXTEEN-LINCOLN', 'Sixteen Mile Creek, Lincoln (below the QEW)', 'Sixteen Mile Creek - Town of Lincoln, between the Queen Elizabeth Way and Lake Ontario', ['Sixteen Mile Creek'], ['Lincoln']),
 ('X16-SPENCER', 'Spencer Creek (below Cootes Drive)', 'Spencer Creek - City of Hamilton, from Highway 102 (Cootes Drive) to Lake Ontario', ['Spencer Creek'], ['Hamilton']),
 ('X16-THAMES-MAIN', 'Thames River (main branch)', 'Thames River - Elgin County and Middlesex County and the Municipality of Chatham-Kent, main branch only', ['Thames River'], ['Elgin County', 'Middlesex County', 'Chatham-Kent']),
 ('X16-WATERFORD', 'Trout Pond of Waterford Ponds', 'Trout Pond of Waterford Ponds - City of Nanticoke', ['Waterford Ponds'], ['Nanticoke']),
 ('X16-TWELVE', 'Twelve Mile Creek (below Lakeport Road)', 'Twelve Mile Creek (Zone 20) - City of St. Catharines, between Lakeport Road and Lake Ontario', ['Twelve Mile Creek'], ['St. Catharines']),
 ('X16-TWENTY', 'Twenty Mile Creek (below the QEW)', 'Twenty Mile Creek - Town of Lincoln, between the Queen Elizabeth Way and Lake Ontario', ['Twenty Mile Creek'], ['Lincoln']),
 ('X16-YOUNGS-LOWER', 'Young’s Creek (below Front Road)', 'Young’s Creek (Ryerse Creek) - Woodhouse Township, from the downstream side of the Front Road bridge to Lake Erie at Port Ryerse', ['Youngs Creek', 'Ryerse Creek'], ['Woodhouse']),
]
for pid, nm, desc, w, t in LOWER:
    place(16, pid, 'reach', nm, desc, 118, water=w, twp=t, rules=sal_all())

EXT = [
 ('X16-BAYFIELD-EXT', 'Bayfield River (Highway 4 to Highway 21)', 'Bayfield River - Goderich and Stanley Townships, from Highway 4 to the downstream side of the Highway 21 bridge (Huron County)', ['Bayfield River'], ['Goderich', 'Stanley']),
 ('X16-BEAVER-THORNBURY', 'Beaver River (Thornbury Dam to Georgian Bay)', 'Beaver River - Collingwood Township, from the Thornbury Dam to Georgian Bay (Grey County)', ['Beaver River'], ['Collingwood']),
 ('X16-BIGCREEK-MID', 'Big Creek (Quance Dam to Regional Road 21)', 'Big Creek - Walsingham Township, south of the Quance Dam to Regional Road 21 at Lynedoch', ['Big Creek'], ['Walsingham']),
 ('X16-BIGOTTER', 'Big Otter Creek (Bayham Township)', 'Big Otter Creek - Bayham Township (Elgin County)', ['Big Otter Creek'], ['Bayham']),
 ('X16-BIGHEAD', 'Bighead River (St. Vincent Township)', 'Bighead River - St. Vincent Township (Grey County)', ['Bighead River'], ['St. Vincent']),
 ('X16-BRONTE-MID', 'Bronte Creek (Lakeshore Road to Highway 407)', 'Bronte Creek - Town of Oakville from Highway 2 (Lakeshore Road West) upstream to the south side of Highway 407', ['Bronte Creek'], ['Oakville', 'Trafalgar', 'Nelson']),
 ('X16-CREDIT-MID', 'Credit River (Britannia Road to Highway 407)', 'Credit River and tributaries - from the south side of Britannia Road in the City of Mississauga upstream to the south side of the Highway 407 Bridge in the City of Brampton', ['Credit River'], ['Mississauga', 'Brampton']),
 ('X16-DON-UPPER', 'Don River (Eglinton Avenue to Highway 407)', 'Don River and tributaries - upstream from Eglinton Avenue in the City of Toronto to the south side of Highway 407 in the Regional Municipality of York', ['Don River'], ['Toronto', 'York']),
 ('X16-GRAND-EXT', 'Grand River (Paris to Lake Erie)', 'Grand River - from a line across the Grand River in Paris at 100 m downstream of the Highway 2 (Dundas Street West) bridge to the edge of Lake Erie (refer to Waterbody Exceptions for catch and possession limits)', ['Grand River'], []),
 ('X16-HOG', 'Hog Creek (C.P.R. bridge to Georgian Bay)', 'Hog Creek - Tay Township from the C.P.R. bridge (Lot 10, Concession 6) downstream (north) to Georgian Bay (Simcoe County)', ['Hog Creek'], ['Tay']),
 ('X16-HUMBER-UPPER', 'Humber River (Eglinton Avenue to Highway 407)', 'Humber River and tributaries - upstream from Eglinton Avenue in the City of Toronto to the south side of the Highway 407 bridge in the Regional Municipality of York', ['Humber River'], ['Toronto', 'York']),
 ('X16-LITTLEOTTER', 'Little Otter Creek', 'Little Otter Creek - Bayham Township, East branch of Big Otter Creek', ['Little Otter Creek'], ['Bayham']),
 ('X16-LSAUBLE-EXT', 'Little Sauble River (Highway 21 to Lake Huron)', 'Little Sauble River - Bruce Township, from Highway 21 to Lake Huron (Bruce County)', ['Little Sauble River'], ['Bruce']),
 ('X16-MAITLAND-EXT', 'Maitland River (County Road 4 to Highway 21)', 'Maitland River - Colborne, Goderich, Hullett, East and West Wawanosh and Turnberry Townships, between County Road 4 and the downstream side of the Highway 21 bridge (Huron County)', ['Maitland River'], ['Colborne', 'Goderich', 'Hullett', 'East Wawanosh', 'West Wawanosh', 'Turnberry']),
 ('X16-NINEMILE-EXT', 'Nine Mile River (County Road 86 to Lake Huron)', 'Nine Mile River (Lucknow River) - Ashfield and West Wawanosh Townships, between County Road 86 and Lake Huron', ['Nine Mile River', 'Lucknow River'], ['Ashfield', 'West Wawanosh']),
 ('X16-NORTHCREEK-MID', 'North Creek (below Highway 3)', 'North Creek - Middleton Township, downstream of Highway 3', ['North Creek'], ['Middleton']),
 ('X16-ROUGE-UPPER', 'Rouge River (Kingston Road to Highway 407)', 'Rouge River - from Highway 2 (Kingston Road) in the City of Toronto upstream to the south side of Highway 407 in the Town of Markham', ['Rouge River'], ['Toronto', 'Markham']),
 ('X16-SAUBLE-FALLS', 'Sauble River (below Sauble Falls)', 'Sauble River - Amabel Township, from the lowest ledge of Sauble Falls 440 m downstream to a line drawn perpendicular to the river’s current', ['Sauble River'], ['Amabel']),
 ('X16-SAUGEEN-EXT', 'Saugeen River (Brockton to Denny’s Dam)', 'Saugeen River - Arran, Amabel, Brant, Carrick, Elderslie and Saugeen Townships and in the Town of Walkerton and the Village of Paisley, between the southerly edge of the Municipality of Brockton Concession 2 SDR. bridge and the westerly edge of the concrete abutments downstream of Denny’s Dam', ['Saugeen River'], ['Arran', 'Amabel', 'Brant', 'Carrick', 'Elderslie', 'Saugeen']),
 ('X16-SIXTEEN-OAK-UPPER', 'Sixteen Mile Creek, Oakville (Lakeshore Road to Highway 407)', 'Sixteen Mile Creek (Oakville Creek) and tributaries - Town of Oakville from Highway 2 (Lakeshore Road) upstream to the south side of Highway 407', ['Sixteen Mile Creek', 'Oakville Creek'], ['Oakville', 'Trafalgar']),
 ('X16-STURGEON-EXT', 'Sturgeon River (Tay and Oro-Medonte)', 'Sturgeon River and tributaries - Tay and Oro-Medonte Townships (Simcoe County), including the mouth of the Sturgeon River at Georgian Bay', ['Sturgeon River'], ['Tay', 'Medonte', 'Oro']),
 ('X16-YOUNGS-MID', 'Young’s Creek (dam to Front Road)', 'Young’s Creek - from the dam on Lot 23, Concession 3 to the downstream side of the Front Road bridge', ['Youngs Creek', 'Ryerse Creek'], ['Woodhouse', 'Charlotteville']),
]
for pid, nm, desc, w, t in EXT:
    place(16, pid, 'reach', nm, desc, 119 if pid not in ('X16-BAYFIELD-EXT','X16-BEAVER-THORNBURY','X16-BIGCREEK-MID','X16-BIGOTTER','X16-BIGHEAD') else 118,
          water=w, twp=t, rules=sal_ext())

# Walleye: open all year, S-6 and C-2, no size limits
WAL = lambda: [season('walleye', 'ALL_YEAR', 'Walleye - additional fishing opportunity: open all year'),
               limit('walleye', 6, 2, 'S-6 and C-2; no size limits', extra='nosize')]
place(16, 'X16-CHENAIL', 'reach', 'Chenail Ecarte', 'Chenail Ecarte - from the mouth of the Chenail Ecarte at Lake St. Clair to the mouth of the Sydenham River', 119,
      water=['Chenail Ecarte'], rules=WAL())
place(16, 'X16-SYDENHAM-DRESDEN', 'reach', 'Sydenham River (below Dresden)', 'Sydenham River - from the mouth of the Sydenham River at the Chenail Ecarte to the downstream side of the St. George Street Bridge in the Town of Dresden', 119,
      water=['Sydenham River'], twp=['Chatham-Kent', 'Camden', 'Dover', 'Chatham'], rules=WAL())
place(16, 'X16-THAMES-CHATHAM', 'reach', 'Thames River (below Chatham)', 'Thames River - from the mouth of the Thames River at Lake St. Clair to the downstream side of the Keil Street Bridge in the Municipality of Chatham', 119,
      water=['Thames River'], twp=['Chatham-Kent', 'Dover', 'Chatham'],
      rules=WAL() + [limit('muskellunge', 1, 0, 'S-1; must be greater than 112 cm, and C-0', bands=[{'max':112,'maxInclusive':True,'maxCount':0}], size='Must be greater than 112 cm')])
#   (the musky limit is the Waterbody Exception on p. 122 for the same reach)

# ======================================================================
# FMZ 16 - Waterbody exceptions (pp. 119-122)
# ======================================================================
place(16, 'X16-BAYFIELD-21', 'sanctuary', 'Bayfield River at Highway 21', 'Bayfield River - on upstream side of Highway 21 bridge in Huron County', 119,
      water=['Bayfield River'], twp=['Goderich', 'Stanley'], rules=[sanct(S_JAN_APR, T_JAN_APR)])
place(16, 'X16-BAYFIELD-TRIBS', 'sanctuary', 'Bayfield River tributaries', 'Bayfield River tributaries - Huron County', 119,
      water=['Bayfield River'], twp=['Huron County'], rules=[sanct(S_JAN_APR_OCT, T_JAN_APR_OCT)],
      note='Applies to the tributaries only, not the Bayfield River itself.')
place(16, 'X16-BIGCREEK-QUANCE', 'sanctuary', 'Big Creek (Quance Dam to Regional Road 21)', 'Big Creek - Walsingham Township, south of the Quance Dam to Regional Road 21 at Lynedoch', 119,
      water=['Big Creek'], twp=['Walsingham'], rules=[sanct(S_JAN_APR, T_JAN_APR)], within='X16-BIGCREEK-MID')
place(16, 'X16-BIGCREEK-TEETER', 'sanctuary', 'Big Creek (Teeterville to Quance Dam)', 'Big Creek - Walsingham Township, lying southerly of the dam in the Hamlet of Teeterville to the Quance Dam in the Town of Delhi', 119,
      water=['Big Creek'], twp=['Walsingham', 'Windham', 'Middleton'], rules=[sanct(S_JAN_APR_OCT, T_JAN_APR_OCT)])

BG_EXC = ['largemouth_bass', 'smallmouth_bass', 'muskellunge', 'lake_sturgeon', 'northern_pike', 'walleye', 'sauger', 'warmouth']
place(16, 'X16-BRUCEGREY', 'county_waters', 'Bruce and Grey Counties inland rivers and streams',
      'Bruce and Grey Counties inland rivers and streams only, excluding those waters identified for this area in Zone 16 Additional Fishing Opportunities', 120,
      twp=['Bruce County', 'Grey County'],
      note='Rivers and streams only. Lakes in Bruce and Grey keep the zone-wide rules.',
      rules=[dict(t='season_all_except', exclude=BG_EXC, windows='[[APR4, fx(9,30)]]',
                  text='All species (except Largemouth and Smallmouth Bass, Muskellunge, Lake Sturgeon, Northern Pike, Walleye and Sauger) - open from fourth Saturday in April to September 30'),
             season('g:on_bass', '[[JUN4, fx(9,30)]]', 'Largemouth and Smallmouth Bass - open from fourth Saturday in June to September 30'),
             season('muskellunge', '[[JUN1, fx(9,30)]]', 'Muskellunge - open from first Saturday in June to September 30'),
             season('northern_pike', '[[MAY2, fx(9,30)]]', 'Northern Pike - open from second Saturday in May to September 30'),
             season('g:on_walleye_sauger', '[[MAY2, fx(9,30)]]', 'Walleye and Sauger - open from second Saturday in May to September 30')])

place(16, 'X16-CREDIT-CALEDON', 'reach', 'Credit River (above Old Baseline Road)', 'Credit River and its tributaries - Town of Caledon in Regional Municipality of Peel, Upstream of Old Baseline Road', 120,
      water=['Credit River'], twp=['Caledon', 'Erin'],
      rules=[LURES, restr('Only one single-pointed barbless hook may be used', 'one_barbless_hook')] +
            [limit(t, 0, 0, 'Brook Trout, Brown Trout and Rainbow Trout - S-0 and C-0') for t in TROUT3])
place(16, 'X16-CREDIT-STREETSVILLE', 'sanctuary', 'Credit River (Britannia Road to Old Baseline Road)',
      'Credit River and tributaries - from the south side of the Britannia Road bridge in the Village of Streetsville, upstream to the south side of the Old Baseline Road bridge in the Town of Caledon, Regional Municipalities of Peel and Halton, excluding Levi’s Creek (43°37\'N, 79°44\'W) and Fletchers Creek (43°37\'N, 79°43\'W)', 120,
      water=['Credit River'], twp=['Mississauga', 'Brampton', 'Caledon', 'Halton Hills'], rules=[sanct(S_JAN_APR, T_JAN_APR)])
place(16, 'X16-CREDIT-403', 'sanctuary', 'Credit River (Highway 403 to Britannia Road)',
      'Credit River and tributaries - from the south side of the Highway 403 bridge in the City of Mississauga, upstream to the south side of the Britannia Road bridge in the Village of Streetsville', 120,
      water=['Credit River'], twp=['Mississauga'],
      rules=[sanct('[[fx(1,1), APR4F], [fx(8,15), fx(12,31)]]', 'Fish Sanctuary - no fishing from January 1 to Friday before fourth Saturday in April and August 15 to December 31')])
place(16, 'X16-CREDIT-HWY9', 'sanctuary', 'Credit River (Old Baseline Road to Highway 9)',
      'Credit River and tributaries - from the south side of the Old Baseline Road bridge in the Town of Caledon, Regional Municipality of Peel, upstream to Highway 9', 120,
      water=['Credit River'], twp=['Caledon', 'Erin', 'Mono'], rules=[sanct(S_JAN_APR_OCT, T_JAN_APR_OCT)])

place(16, 'X16-GRAND-FERGUS', 'reach', 'Grand River (Fergus to Highway 86)',
      'Grand River - between the West Garafraxa second Line and Scotland Street in the Town of Fergus; between Tower Street in the Town of Fergus and the Bissell Dam in Nichol Township; between 100 m downstream of a bridge located at the southern boundary of the Elora Gorge Conservation Area and a point 100 m upstream of Pilkington 8th Line in Pilkington Township; between 100 m downstream of Pilkington 8th Line bridge and 100 m upstream of Pilkington Township and Woolwich Township boundary line; and between 100 m downstream of Pilkington Township and Woolwich Township boundary line and 100 m upstream of Highway 86 bridge', 120,
      water=['Grand River'], twp=['West Garafraxa', 'Nichol', 'Pilkington', 'Woolwich'],
      rules=[LURES, BARBLESS] + [limit(t, 0, 0, 'Brook Trout, Brown Trout and Rainbow Trout - S-0 and C-0') for t in TROUT3])
place(16, 'X16-GRAND-PARIS', 'reach', 'Grand River (Paris to Brantford)',
      'Grand River - between the former Town of Paris (City of Brant) and Brantford from a line across the Grand River in Paris at 100 m downstream of the Highway 2 (Dundas Street West) bridge downstream to the pedestrian and service bridge that crosses the Grand River on an angle upstream (west) of the Brant Conservation Area in the City of Brantford', 120,
      water=['Grand River'], twp=['Brantford', 'Paris', 'Brant'],
      rules=[LURES, BARBLESS,
             sanct('[[fx(3,1), APR4F]]', 'Fish Sanctuary - no fishing from March 1 to Friday before fourth Saturday in April')] +
            [limit(t, 0, 0, 'Brown Trout, Northern Pike, Rainbow Trout, Smallmouth Bass and Walleye - S-0 and C-0')
             for t in ['brown_trout', 'northern_pike', 'rainbow_trout', 'smallmouth_bass', 'walleye']])
place(16, 'X16-GRAND-BRANTFORD', 'reach', 'Grand River (Brantford to Lake Erie)',
      'Grand River - from the pedestrian and service bridge that crosses the Grand River on an angle upstream (west) of the Brant Conservation Area in the City of Brantford to the edge of Lake Erie', 120,
      water=['Grand River'], twp=['Brantford', 'Haldimand', 'Onondaga', 'Tuscarora', 'Oneida', 'Seneca', 'Cayuga', 'Dunn', 'Moulton', 'Sherbrooke'],
      rules=[limit('brown_trout', 1, 0, 'Brown Trout and Rainbow Trout (combined) - S-1 and C-0; from October 1 to December 31', when='[[fx(10,1), fx(12,31)]]', whenText='From October 1 to December 31'),
             limit('rainbow_trout', 1, 0, 'Brown Trout and Rainbow Trout (combined) - S-1 and C-0; from October 1 to December 31', when='[[fx(10,1), fx(12,31)]]', whenText='From October 1 to December 31')])
place(16, 'X16-GRAND-PENMAN', 'sanctuary', 'Grand River (Penman Dam to William Street)',
      'Grand River - from the Penman Dam downstream to the William Street Bridge in the former town of Paris (City of Brant)', 120,
      water=['Grand River'], twp=['Paris', 'Brant', 'South Dumfries'],
      rules=[sanct('[[fx(10,1), fx(11,30)]]', 'Fish Sanctuary - no fishing from October 1 to November 30')])
place(16, 'X16-GRAND-CALEDONIA', 'reach', 'Grand River (Caledonia to Lake Erie)',
      'Grand River - Haldimand County, from the water’s edge of Lake Erie upstream to the dam in the Town of Caledonia', 120,
      water=['Grand River'], twp=['Haldimand County'],
      rules=[limit('walleye', 4, 2, 'Walleye - S-4 and C-2; any size', extra='nosize')])
place(16, 'X16-GRAND-ONONDAGA', 'reach', 'Grand River and tributaries (below Onondaga–Tuscarora line)',
      'Grand River and its tributaries - downstream of the Onondaga and Tuscarora Townships line to Lake Erie', 121,
      water=['Grand River'], twp=['Tuscarora', 'Oneida', 'Seneca', 'Cayuga', 'Dunn', 'Moulton', 'Sherbrooke', 'Haldimand County'],
      rules=[season('walleye', '[[MAY2, fx(2,28)]]', 'Walleye and Northern Pike - open from January 1 to last day in February and second Saturday in May to December 31'),
             season('northern_pike', '[[MAY2, fx(2,28)]]', 'Walleye and Northern Pike - open from January 1 to last day in February and second Saturday in May to December 31')])
#  ^ "last day in February": fx(2,28) is fine for 2026 (not a leap year); use last_day in the generator.

place(16, 'X16-HUMBER-TROUT', 'reach', 'Humber River (above Eglinton Avenue)', 'Humber River and its tributaries - upstream from Eglinton Avenue', 121,
      water=['Humber River'], twp=['Toronto', 'York', 'Peel', 'Vaughan', 'King', 'Caledon'],
      rules=[limit(t, 2, 1, 'Brook Trout, Brown Trout and Rainbow Trout combined - S-2 and C-1') for t in TROUT3])
place(16, 'X16-HUMBER-407', 'sanctuary', 'Humber River (above Highway 407)',
      'Humber River and tributaries - Regional Municipalities of York and Peel and Counties of Dufferin and Simcoe, upstream of Highway 407', 121,
      water=['Humber River'], twp=['Vaughan', 'King', 'Caledon', 'Mono', 'Adjala', 'Tecumseth'], rules=[sanct(S_JAN_APR_OCT, T_JAN_APR_OCT)])
# Lake Simcoe is already in the app (FMZ16-SIMCOE).

place(16, 'X16-MAITLAND-FALLS', 'sanctuary', 'Maitland River (Falls Reserve, 550 m)',
      'Maitland River - Colborne and Goderich Townships, extending 550 m downstream from Falls Reserve Waterfall to the first natural waterfall', 121,
      water=['Maitland River'], twp=['Colborne', 'Goderich'],
      rules=[sanct('[[fx(9,15), fx(10,31)]]', 'Fish Sanctuary - closed to night fishing from September 15 to October 31 (one-half hour after sunset to one-half hour before sunrise)', night=True)])
place(16, 'X16-MAITLAND-21', 'sanctuary', 'Maitland River (Highway 21 to County Road 4)',
      'Maitland River - Huron County, from the downstream side of the bridge on Highway 21 to the upstream side of the bridge on County Road 4', 121,
      water=['Maitland River'], twp=['Colborne', 'Goderich', 'Hullett', 'East Wawanosh', 'West Wawanosh', 'Turnberry'], rules=[sanct(S_JAN_APR, T_JAN_APR)])
place(16, 'X16-MAITLAND-TRIBS', 'sanctuary', 'Maitland River tributaries (Highway 21 to County Road 4)',
      'Maitland River tributaries - Huron County, from the downstream side of the bridge on Highway 21 to the upstream side of the bridge on County Road 4', 121,
      water=['Maitland River'], twp=['Colborne', 'Goderich', 'Hullett', 'East Wawanosh', 'West Wawanosh', 'Turnberry'], rules=[sanct(S_JAN_APR_OCT, T_JAN_APR_OCT)],
      note='Applies to the tributaries only, not the Maitland River itself.')
place(16, 'X16-NINEMILE-FISHWAY', 'sanctuary', 'Nine Mile River (Port Albert Fishway)',
      'Nine Mile River - Ashfield Township, from the Port Albert Fishway to 100 m upstream', 121,
      water=['Nine Mile River'], twp=['Ashfield'],
      rules=[sanct('[[APR4, fx(5,15)], [fx(9,1), fx(11,30)]]', 'Fish Sanctuary - no fishing from fourth Saturday in April to May 15 and September 1 to November 30')])
place(16, 'X16-NINEMILE-86', 'sanctuary', 'Nine Mile River (County Road 86 to Lake Huron)',
      'Nine Mile River (Lucknow River) - Ashfield and West Wawanosh Townships, between County Road 86 and Lake Huron', 121,
      water=['Nine Mile River', 'Lucknow River'], twp=['Ashfield', 'West Wawanosh'], rules=[sanct(S_JAN_APR, T_JAN_APR)], within='X16-NINEMILE-EXT')
place(16, 'X16-NINEMILE-TRIBS', 'sanctuary', 'Nine Mile River tributaries', 'Nine Mile River tributaries - Huron County, Highway 86 downstream to Lake Huron', 121,
      water=['Nine Mile River'], twp=['Ashfield', 'West Wawanosh'], rules=[sanct(S_JAN_APR_OCT, T_JAN_APR_OCT)],
      note='Applies to the tributaries only, not the Nine Mile River itself.')
place(16, 'X16-NOTTAWASAGA-NICHOLSON', 'sanctuary', 'Nottawasaga River (Nicholson Dam)',
      'Nottawasaga River - Essa Township, waters lying within Lot 1, Concession 5, from Highway 89 above Nicholson Dam downstream to near the confluence of the Boyne River', 121,
      water=['Nottawasaga River'], twp=['Essa'],
      rules=[sanct('[[fx(1,1), MAY2F], [fx(10,1), fx(12,31)]]', 'Fish Sanctuary - no fishing from January 1 to Friday before second Saturday in May and October 1 to December 31')])
place(16, 'X16-NOTTAWASAGA-PINE', 'reach', 'Nottawasaga River (Boyne River to Pine River)', 'Nottawasaga River - from the Boyne River downstream (north) to the Pine River', 121,
      water=['Nottawasaga River'], twp=['Essa', 'Tosorontio', 'Tecumseth'], rules=[limit('rainbow_trout', 0, 0, 'Rainbow Trout - S-0 and C-0')])
place(16, 'X16-PRETTY-UPPER', 'sanctuary', 'Pretty River (Collingwood and Osprey Townships)', 'Pretty River and tributaries - Collingwood and Osprey Townships', 121,
      water=['Pretty River'], twp=['Collingwood', 'Osprey'], rules=[sanct(S_APR_MAY31, T_APR_MAY31)])
place(16, 'X16-PRETTY-LOWER', 'sanctuary', 'Pretty River (Collingwood and Nottawasaga)', 'Pretty River and tributaries - Town of Collingwood and Nottawasaga Township', 121,
      water=['Pretty River'], twp=['Collingwood', 'Nottawasaga'], rules=[sanct(S_JAN_APR_OCT, T_JAN_APR_OCT)])
place(16, 'X16-SAUGEEN-DENNYS', 'sanctuary', 'Saugeen River (Denny’s Dam)', 'Saugeen River - Amabel and Saugeen Townships, Denny’s Dam to the concrete abutments downstream', 122,
      water=['Saugeen River'], twp=['Amabel', 'Saugeen'],
      rules=[sanct('[[fx(10,1), fx(10,31)]]', 'Fish Sanctuary - closed to night fishing from October 1 to October 31 (one-half hour after sunset to one-half hour before sunrise)', night=True)])
place(16, 'X16-SAUGEEN-MAPLEHILL', 'sanctuary', 'Saugeen River (Maple Hill Dam, 300 m)',
      'Saugeen River - Township of Brant in the County of Bruce, from the dam face of the Maple Hill Dam to a point 300 m downstream and including the hydro-electric power channel', 122,
      water=['Saugeen River'], twp=['Brant'], rules=[closed_all_year()])
place(16, 'X16-SYDENHAM-CHANNELS', 'sanctuary', 'Sydenham River spawning channels', 'Sydenham River - Derby Township, Artificial Spawning Channels Numbers 1 and 2', 122,
      water=['Sydenham River'], twp=['Derby'], rules=[closed_all_year()])
place(16, 'X16-SYDENHAM-MILLDAM', 'sanctuary', 'Sydenham River (Mill Dam, 177 m)', 'Sydenham River - City of Owen Sound, from the Mill Dam to a point 177 m downstream', 122,
      water=['Sydenham River'], twp=['Owen Sound', 'Sydenham', 'Derby'], rules=[closed_all_year()])
place(16, 'X16-SYDENHAM-INGLIS', 'sanctuary', 'Sydenham River (Inglis Falls to Mill Dam)', 'Sydenham River - City of Owen Sound and Derby Township, from Inglis Falls to Mill Dam, excluding Artificial Spawning Channels Numbers 1 and 2', 122,
      water=['Sydenham River'], twp=['Owen Sound', 'Derby'], rules=[sanct(S_APR_MAY31, T_APR_MAY31)])
place(16, 'X16-SYDENHAM-HARRISON', 'sanctuary', 'Sydenham River (Inglis Falls to Harrison Park)',
      'Sydenham River and tributaries - City of Owen Sound and Derby Township, from the base of Inglis Falls downstream to a line drawn due east from the north end of the bridge known locally as either Chinese or Rainbow Bridge to the permanent steel post marker affixed to the shore of the Sydenham River in Harrison Park', 122,
      water=['Sydenham River'], twp=['Owen Sound', 'Derby'], rules=[sanct('[[fx(9,1), fx(9,30)]]', 'Fish Sanctuary - no fishing from September 1 to September 30')])
place(16, 'X16-THAMES-PITTOCK', 'sanctuary', 'Thames River (Pittock Dam to Highway 59)', 'Thames River - between the dam at Gordon Pittock Reservoir and the bridge at Highway 59', 122,
      water=['Thames River'], twp=['Woodstock', 'East Oxford', 'Blandford'],
      rules=[sanct('[[fx(3,15), MAY2F]]', 'Fish Sanctuary - no fishing from March 15 to Friday before second Saturday in May')])
place(16, 'X16-WHITEMANS-RULES', 'reach', 'Whitemans Creek (Robinson Road to Cleaver Sideroad)',
      'Whitemans Creek (Horner Creek) - Brantford Township, between Robinson Road and Cleaver Sideroad', 122,
      water=['Whitemans Creek', 'Horner Creek'], twp=['Brantford'],
      rules=[LURES, BARBLESS] + [limit(t, 1, 1, 'Brown Trout or Rainbow Trout - S-1 and C-1; must be greater than 50 cm',
                                        bands=[{'max':50,'maxInclusive':True,'maxCount':0}], size='Must be greater than 50 cm') for t in ['brown_trout', 'rainbow_trout']])
place(16, 'X16-WHITEMANS-SANCT', 'sanctuary', 'Whitemans Creek (East Quarter Town Line to Grand River)',
      'Whitemans Creek (Horner Creek) and tributaries - from the East Quarter Town Line Road downstream to the edge of the Grand River', 122,
      water=['Whitemans Creek', 'Horner Creek'], twp=['Brantford', 'Burford'], rules=[sanct(S_JAN_APR_OCT, T_JAN_APR_OCT)])

# ======================================================================
# FMZ 16 - Fish sanctuaries list (pp. 122-124), entries not already above
# ======================================================================
def fs(pid, name, desc, w, t, windows, text, pt=None, page=122, night=False):
    place(16, pid, 'sanctuary', name, desc, page, water=w, twp=t, pt=pt, rules=[sanct(windows, text, night)])

T_ALL = 'No fishing - closed all year'
fs('X16-COLPOYS', 'Colpoy’s Creek', 'Colpoy’s Creek - Albemarle Township, from the upper bridge on County Road 9 downstream to the mouth', ['Colpoys Creek'], ['Albemarle'], 'ALL_YEAR', T_ALL)
fs('X16-GLEASON', 'Gleason Brook', 'Gleason Brook - Keppel Township, from the bridge on County Road 26 to the mouth', ['Gleason Brook'], ['Keppel'], 'ALL_YEAR', T_ALL)
T1 = 'No fishing - January 1 to Friday before the fourth Saturday in April'
fs('X16-BIGOTTER-TILL', 'Big Otter Creek (Tillsonburg)', 'Big Otter Creek - Town of Tillsonburg, from Black’s Dam to the north side of the bridge at Oxford Street', ['Big Otter Creek'], ['Tillsonburg', 'Dereham'], S_JAN_APR, T1)
fs('X16-BRADLEYS', 'Bradleys Creek', 'Bradleys Creek - Yarmouth Township, from the Elgin County Road 35 dam to Catfish Creek', ['Bradleys Creek'], ['Yarmouth'], S_JAN_APR, T1)
fs('X16-LAFONTAINE', 'Lafontaine Creek', 'Lafontaine Creek and its tributaries - Township of Tiny in the County of Simcoe, at 44°43\'15.167"N, 80°01\'48.461"W', ['Lafontaine Creek'], ['Tiny'], S_JAN_APR, T1, pt=(44.7209, -80.0301))
fs('X16-NORTHCREEK-WALS', 'North Creek (south of Highway 3)', 'North Creek - Walsingham Township, south of Highway 3', ['North Creek'], ['Walsingham'], S_JAN_APR, T1)
fs('X16-STONEY', 'Stoney Creek (Walsingham)', 'Stoney Creek - Walsingham Township, south of Highway 3 to Big Creek', ['Stoney Creek'], ['Walsingham'], S_JAN_APR, T1)
fs('X16-STURGEON-BARRIER', 'Sturgeon River (above lamprey barrier)', 'Sturgeon River and tributaries - Tay and Oro-Medonte Townships, upstream (south) from the lamprey barrier', ['Sturgeon River'], ['Tay', 'Medonte', 'Oro'], S_JAN_APR, T1)
fs('X16-YOUNGS-SANCT', 'Young’s Creek (dam to Port Ryerse)', 'Young’s Creek (Ryerse Creek) - Woodhouse Township and the City of Nanticoke, between the dam on Lot 23, Concession 3 (former Township of Charlotteville) and the downstream side of the bridge on the Lakeshore Road at Port Ryerse', ['Youngs Creek', 'Ryerse Creek'], ['Woodhouse', 'Charlotteville'], S_JAN_APR, T1)
T2 = 'No fishing - January 1 to Friday before the fourth Saturday in April and October 1 to December 31'
fs('X16-BRONTE-PROGRESTON', 'Bronte Creek (Progreston to Highway 407)', 'Bronte Creek - City of Burlington and Flamborough Township, from the C.P.R. track in the Village of Progreston downstream to the south side of Highway 407, including part of Limestone Creek upstream to Steeles Avenue in the Town of Milton', ['Bronte Creek', 'Limestone Creek'], ['Burlington', 'Flamborough', 'Nelson', 'Nassagaweya', 'Milton'], S_JAN_APR_OCT, T2, page=123)
fs('X16-FISHERS', 'Fisher’s Creek', 'Fisher’s Creek - Walsingham Township', ['Fishers Creek'], ['Walsingham'], S_JAN_APR_OCT, T2, page=123)
fs('X16-GALT', 'Galt Creek (Mill Creek)', 'Galt Creek (Mill Creek) - upstream from the boundary of North Dumfries and Puslinch Townships, including Aberfoyle Creek', ['Galt Creek', 'Mill Creek', 'Aberfoyle Creek'], ['Puslinch'], S_JAN_APR_OCT, T2, page=123)
fs('X16-GRINDSTONE-UPPER', 'Grindstone Creek (Waterdown Road to Plains Road)', 'Grindstone Creek - Flamborough Township and City of Burlington, from Waterdown Road to Highway 2 (Plains Road)', ['Grindstone Creek'], ['Flamborough', 'Burlington', 'East Flamborough'], S_JAN_APR_OCT, T2, page=123)
fs('X16-GULLY', 'Gully Creek', 'Gully Creek and tributaries - Goderich Township', ['Gully Creek'], ['Goderich'], S_JAN_APR_OCT, T2, page=123)
fs('X16-NAFTELS', 'Naftel’s Creek', 'Naftel’s Creek and tributaries - Huron County', ['Naftels Creek'], ['Huron County'], S_JAN_APR_OCT, T2, page=123)
fs('X16-NORMANDALE', 'Normandale Creek (Potters Creek)', 'Normandale Creek (Potters Creek) - Walsingham Township', ['Normandale Creek', 'Potters Creek'], ['Walsingham', 'Charlotteville'], S_JAN_APR_OCT, T2, page=123)
fs('X16-BOYNE', 'Boyne River (Earl Rowe Provincial Park)', 'Boyne River - Tosorontio Township, from the dam in Earl Rowe Provincial Park downstream (east) to the park boundary', ['Boyne River'], ['Tosorontio', 'Tecumseth'],
   '[[fx(1,1), MAY2F], [fx(10,1), fx(12,31)]]', 'No fishing - January 1 to Friday before the second Saturday in May and October 1 to December 31', page=123)
fs('X16-SILVER', 'Silver Creek (Collingwood)', 'Silver Creek and tributaries - Town of Collingwood, Collingwood and Nottawasaga Townships', ['Silver Creek'], ['Collingwood', 'Nottawasaga'],
   '[[fx(1,1), fx(5,31)], [fx(10,1), fx(12,31)]]', 'No fishing - January 1 to May 31 and October 1 to December 31', page=123)
T3 = 'No fishing - March 1 to Friday before second Saturday in May'
S3 = '[[fx(3,1), MAY2F]]'
fs('X16-BEAVER-BEAVERTON', 'Beaver River (Beaverton)', 'Beaver River - Thorah Township, from the CNR railway bridge in the town of Beaverton upstream to Highway 12/48', ['Beaver River'], ['Thorah'], S3, T3, page=123)
fs('X16-PEFFERLAW', 'Pefferlaw River (Highway 48 to dam)', 'Pefferlaw River - Town of Georgina, from Highway 48 upstream to the dam in the village of Pefferlaw', ['Pefferlaw River'], ['Georgina'], S3, T3, page=123)
fs('X16-SEVERN-COOPERS', 'Severn River (Coopers Falls)', 'Severn River - Morrison Township, between Coopers Falls Road bridge, downstream to a line extending southerly across the river from the westerly limit of Lot 17, Concession A', ['Severn River'], ['Morrison'], S3, T3, page=123)
fs('X16-TALBOT-16', 'Talbot River (Highway 12 to dam)', 'Talbot River and tributaries excluding the Trent Canal system - Thorah and Mara Townships, the area between the eastern side of Highway 12 upstream to the dam in Lot 6, Concession 11', ['Talbot River'], ['Thorah', 'Mara'], S3, T3, page=123)
T4 = 'No fishing - fourth Saturday in April to May 31'
for pid, nm, desc, w, t, pg in [
 ('X16-BEATTY', 'Beatty Saugeen River', 'Beatty Saugeen River and tributaries - Normanby and Bentinck Townships and that part of Egremont Township from Highway 6 upstream to the dams at Orchard Park', ['Beatty Saugeen River'], ['Normanby', 'Bentinck', 'Egremont'], 123),
 ('X16-BIGHEAD-TRIBS', 'Bighead River tributaries', 'Bighead River tributaries - Sydenham, St. Vincent and Holland Townships', ['Bighead River'], ['Sydenham', 'St. Vincent', 'Holland'], 123),
 ('X16-INDIANBROOK', 'Indian Brook', 'Indian Brook and tributaries - Collingwood Township', ['Indian Brook'], ['Collingwood'], 123),
 ('X16-INDIANRIVER', 'Indian River (Georgian Bay to Indian Falls)', 'Indian River - Sarawak Township, from Georgian Bay to Indian Falls', ['Indian River'], ['Sarawak'], 123),
 ('X16-JUDGES', 'Judges Creek', 'Judges Creek - Eastnor Township, from the first falls above County Road 9 to Georgian Bay', ['Judges Creek'], ['Eastnor'], 123),
 ('X16-KEEFERS', 'Keefer’s Creek', 'Keefer’s Creek - Sydenham Township, between the water’s edge of Owen Sound and Slattery Mills Falls', ['Keefers Creek'], ['Sydenham'], 123),
 ('X16-LSAUBLE-INVERHURON', 'Little Sauble River (Inverhuron)', 'Little Sauble River and tributaries - Bruce Township, all waters upstream of a line drawn across the river at a point 180 m upstream from the foot bridge in Inverhuron Provincial Park', ['Little Sauble River'], ['Bruce'], 123),
 ('X16-MEUX', 'Meux Creek', 'Meux Creek - Neustadt Village in Normanby Township, from dam face to South Saugeen River', ['Meux Creek'], ['Normanby'], 123),
 ('X16-MILLCREEK-GREY', 'Mill Creek (Euphrasia and Collingwood)', 'Mill Creek and tributaries - Euphrasia and Collingwood Townships, downstream of Mitchell’s Falls to the Euphrasia and Collingwood Townline', ['Mill Creek'], ['Euphrasia', 'Collingwood'], 123),
 ('X16-ORCHARD', 'Orchard Creek (Centreville Creek)', 'Orchard Creek (Centreville Creek) and tributaries - St. Vincent Township', ['Orchard Creek', 'Centreville Creek'], ['St. Vincent'], 124),
 ('X16-PARKHEAD', 'Park Head Creek', 'Park Head Creek - Amabel Township, from the confluence of Park Head Creek with the Sauble River upstream to Bruce County Road 10', ['Park Head Creek'], ['Amabel'], 124),
 ('X16-SANGS', 'Sangs Creek', 'Sangs Creek and tributaries - Arran Township', ['Sangs Creek'], ['Arran'], 124),
 ('X16-TELFER', 'Telfer Creek (Bothwell’s Creek)', 'Telfer Creek (Bothwell’s Creek) - Sydenham Township, Grey County', ['Telfer Creek', 'Bothwells Creek'], ['Sydenham'], 124),
 ('X16-WILLOW', 'Willow Creek (St. Edmunds)', 'Willow Creek - St. Edmunds Township', ['Willow Creek'], ['St. Edmunds'], 124)]:
    fs(pid, nm, desc, w, t, S_APR_MAY31, T4, page=pg)
fs('X16-POTTAWATOMI', 'Pottawatomi River and Maxwell Creek', 'Pottawatomi River and Maxwell Creek - City of Owen Sound and Derby Township, from the 4th Avenue West Bridge upstream to the base of the escarpment', ['Pottawatomi River', 'Maxwell Creek'], ['Owen Sound', 'Derby'],
   '[[APR4, fx(5,31)], [fx(9,1), fx(9,30)]]', 'No fishing - fourth Saturday in April to May 31 and September 1 to September 30', page=124)

# ======================================================================
# FMZ 17 - Species exceptions (p. 128)
# ======================================================================
def sal17_all(): return [season(t, 'ALL_YEAR', 'Additional fishing opportunity: open all year; zone-wide limits apply') for t in SAL4]
def sal17_ext(): return [season(t, '[[APR4, fx(12,31)]]', 'Additional fishing opportunity: open from fourth Saturday in April to December 31 (extended fall season); zone-wide limits apply') for t in SAL4]
place(17, 'X17-COBOURG-LOWER', 'reach', 'Cobourg Brook (below the CNR)', 'Cobourg Brook (Cobourg Creek or Factory Creek) - between the southerly limit of the CNR right-of-way and Lake Ontario', 128,
      water=['Cobourg Brook', 'Cobourg Creek'], twp=['Cobourg', 'Hamilton'], rules=sal17_all())
place(17, 'X17-GAGES-LOWER', 'reach', 'Gages Creek (below the CNR)', 'Gages Creek - between the southerly limit of the CNR right-of-way and Lake Ontario', 128,
      water=['Gages Creek'], twp=['Hope'], rules=sal17_all())
place(17, 'X17-GANARASKA-LOWER', 'reach', 'Ganaraska River (below the CNR)', 'Ganaraska River - between the southerly limit of the CNR right-of-way and Lake Ontario', 128,
      water=['Ganaraska River'], twp=['Port Hope', 'Hope'], pt=(43.9468, -78.2922), rules=sal17_all())
place(17, 'X17-DURHAM-CNR', 'county_waters', 'Durham Region waters below the CNR', 'Regional Municipality of Durham - all waters lying between the southerly limit of the CNR right-of-way and Lake Ontario', 128,
      twp=['Durham Region'], note='Only waters south of the CN rail line near the Lake Ontario shore.', rules=sal17_all())
place(17, 'X17-NORTHUMBERLAND-HWY2', 'county_waters', 'Northumberland County waters below Highway 2',
      'Northumberland County - all waters downstream of Highway 2, except the Ganaraska River. Details of additional fishing opportunities for the Ganaraska River can be found below.', 128,
      twp=['Northumberland County'], note='Only waters downstream of Highway 2, near the Lake Ontario shore.', rules=sal17_ext())
place(17, 'X17-DURHAM-HWY2', 'county_waters', 'Durham Region waters between Highway 2 and the CNR',
      'Regional Municipality of Durham - all waters between Highway 2 and the southerly limit of the CNR right-of-way.', 128,
      twp=['Durham Region'], note='Only waters between Highway 2 and the CN rail line near the Lake Ontario shore.', rules=sal17_ext())
GAN_W = '[[APR4, fx(8,31)], [fx(10,15), fx(12,31)]]'
place(17, 'X17-GANARASKA-MID', 'reach', 'Ganaraska River (Jocelyn Street to the CNR)',
      'Ganaraska River – from the south side of the Jocelyn Street Bridge (43°58\'1.77"N, 78°17\'43.77"W) to the southerly limit of the CNR right-of-way (43°56\'48.51"N, 78°17\'31.93"W)', 128,
      water=['Ganaraska River'], twp=['Port Hope'], pt=[(43.9672, -78.2955), (43.9468, -78.2922)],
      rules=[season(t, GAN_W, 'Additional fishing opportunity: open from fourth Saturday in April to August 31 and from October 15 to December 31 (extended fall season); zone-wide limits apply') for t in SAL4] +
            [sanct('[[fx(9,1), fx(10,14)]]', 'No Fishing – September 1 to October 14')])
place(17, 'X17-CROWE', 'waterbody', 'Crowe Lake and Crowe River', 'Crowe Lake (44°29\'00"N, 77°44\'00"W) - Marmora Township, and the waters of the Crowe River (Marmora and Rawdon Townships)', 128,
      water=['Crowe Lake', 'Crowe River'], twp=['Marmora', 'Rawdon'], pt=(44.4833, -77.7333),
      rules=[season('walleye', '[[MAY2, fx(3,1)]]', 'Walleye - January 1 to March 1 and second Saturday in May to December 31; zone-wide limits apply')])
WAL_BAL = lambda: [limit('walleye', 3, 1, 'Walleye - S-3 and C-1; none between 37-55 cm', bands=[{'min':37,'minInclusive':True,'max':55,'maxInclusive':True,'maxCount':0}], size='None between 37-55 cm')]
place(17, 'X17-BALSAM', 'waterbody', 'Balsam Lake and connected waters',
      'Balsam Lake (44°34\'54"N, 78°51\'10"W) - Bexley Township, including the waters of the Gull River upstream to the dam at Coboconk, the waters of the Rosedale River between the Trent dam at Rosedale upstream to Balsam Lake, the waters of the Trent Canal between the upstream lock at Rosedale upstream to its junction with the Rosedale River and the waters of the Trent Canal between Balsam Lake and Mitchell Lake', 128,
      water=['Balsam Lake', 'Gull River', 'Rosedale River'], twp=['Bexley', 'Fenelon', 'Eldon'], pt=(44.5817, -78.8528), rules=WAL_BAL())
place(17, 'X17-MITCHELL', 'waterbody', 'Mitchell Lake', 'Mitchell Lake (44°34\'46"N, 78°56\'54"W) - Eldon Township, including the waters of the Trent Canal between Mitchell Lake and Balsam Lake, and the waters of the Trent Canal between Mitchell Lake and lock number 36 at Kirkfield', 128,
      water=['Mitchell Lake'], twp=['Eldon'], pt=(44.5794, -78.9483), rules=WAL_BAL())

# FMZ 17 - Waterbody exceptions (pp. 128-129)
place(17, 'X17-SCUGOG', 'waterbody', 'Lake Scugog and Scugog River',
      'Lake Scugog and Scugog River - All waters of Lake Scugog and Scugog River - including waters south of Highway 7A, Blackstock Creek, Nonquon River, as well as the Scugog River to the Trent Severn Dam in Lindsay, Mariposa Brook and East Cross Creek', 128,
      water=['Lake Scugog', 'Scugog River', 'Blackstock Creek', 'Nonquon River', 'Mariposa Brook', 'East Cross Creek'], twp=['Scugog', 'Reach', 'Cartwright', 'Mariposa', 'Ops'],
      rules=[closed('walleye', 'Walleye - closed all year')])
S17A = '[[fx(1,1), MAY2F], [fx(11,16), fx(12,31)]]'
T17A = 'No fishing - January 1 to Friday before the second Saturday in May and November 16 to December 31'
S17B = '[[fx(1,1), MAY2A], [fx(11,16), fx(12,31)]]'
T17B = 'No fishing - January 1 to Friday after the second Saturday in May and November 16 to December 31'
place(17, 'X17-SCUGOG-7A', 'sanctuary', 'Lake Scugog causeways (Highway 7A)', 'Lake Scugog - Scugog Township, 100m on both sides of Highway 7A (causeways)', 128,
      water=['Lake Scugog'], twp=['Scugog', 'Cartwright'], rules=[sanct(S17A, 'Fish Sanctuary - no fishing from January 1 to Friday before second Saturday in May and November 16 to December 31')])
place(17, 'X17-SCUGOG-LINDSAY', 'sanctuary', 'Scugog River (Lindsay)', 'Scugog River - Lindsay in Ops Township, from Trent-Severn Dam to Ops-Fenelon Boundary', 128,
      water=['Scugog River'], twp=['Ops', 'Lindsay'], rules=[sanct(S17B, 'Fish Sanctuary - no fishing from January 1 to Friday after second Saturday in May and November 16 to December 31')])
place(17, 'X17-TRENT-HEALEY', 'sanctuary', 'Trent River at Healey Falls', 'Trent River - Healey Falls - Seymour Township, all water flowing from the north-westerly side of the bridge on County Road 50 to Crowe Bay', 128,
      water=['Trent River', 'Crowe Bay'], twp=['Seymour'], rules=[sanct(S17B, 'Fish Sanctuary - No fishing from January 1 to Friday after second Saturday in May and November 16 to December 31')])
place(17, 'X17-TRENT-HASTINGS', 'sanctuary', 'Trent River at Hastings', 'Trent River - Village of Hastings, 500 m upstream of the dam and 1 km downstream of the dam', 128,
      water=['Trent River'], twp=['Hastings', 'Asphodel', 'Percy'], rules=[sanct(S17B, 'Fish Sanctuary - No fishing from January 1 to Friday after second Saturday in May and November 16 to December 31')])
place(17, 'X17-TRENT-LOWER', 'reach', 'Trent River (Dam No. 1 to Myers Lock)', 'Trent River - waters from the first dam (Number One) above Lake Ontario upstream to Lock Number 9 (Myers Lock) at the head of Percy Reach', 129,
      water=['Trent River'], twp=['Murray', 'Sidney', 'Seymour', 'Percy', 'Trenton'],
      rules=[season('walleye', '[[MAY2, fx(3,1)]]', 'Walleye - open from January 1 to March 1 and second Saturday in May to December 31')])

# FMZ 17 - Fish sanctuaries list (p. 129), entries not already above
def fs17(pid, name, desc, w, t, windows, text, pt=None):
    place(17, pid, 'sanctuary', name, desc, 129, water=w, twp=t, pt=pt, rules=[sanct(windows, text)])
fs17('X17-COBOURG-BARRIER', 'Cobourg Brook (lamprey barrier to King Street)', 'Cobourg Brook - Town of Cobourg, from the downstream side of the lamprey barrier downstream to the south side of the King Street Bridge', ['Cobourg Brook', 'Cobourg Creek'], ['Cobourg'], 'ALL_YEAR', T_ALL)
fs17('X17-GANARASKA-401', 'Ganaraska River (Highway 401 to Jocelyn Street)', 'Ganaraska River - Town of Port Hope, from Highway 401 downstream to the south side of the Jocelyn Street Bridge', ['Ganaraska River'], ['Port Hope', 'Hope'], 'ALL_YEAR', T_ALL, pt=(43.9672, -78.2955))
fs17('X17-CHEMONG', 'Chemong Lake causeway (Bridgenorth)', 'Chemong Lake - Smith and Ennismore Townships, 100 m on both sides of causeway (Bridgenorth Causeway) on County Road 16', ['Chemong Lake'], ['Smith', 'Ennismore'], S17A, T17A)
fs17('X17-CROWE-MARMORA', 'Crowe River (Marmora Dam to Highway 7)', 'Crowe River - from the Marmora Dam downstream to the north side of the Highway 7 bridge', ['Crowe River'], ['Marmora'], S17A, T17A)
fs17('X17-GANNONS', 'Gannon’s Narrows', 'Gannon’s Narrows - Harvey and Ennismore Townships, within 100 m of both sides of the causeway on County Road 16', ['Gannons Narrows', 'Pigeon Lake', 'Buckhorn Lake'], ['Harvey', 'Ennismore'], S17A, T17A)
for pid, nm, desc, w, t, pt in [
 ('X17-BOBCAYGEON', 'Bobcaygeon River (dams to Pigeon Lake)', 'Bobcaygeon River - Bobcaygeon, from Trent-Severn Dam to Pigeon Lake and Little Bob Dam to Pigeon Lake (100 m from Little Bob Dam)', ['Bobcaygeon River'], ['Verulam', 'Harvey'], None),
 ('X17-BURLEIGH', 'Burleigh Falls and Perry’s Creek', 'Burleigh Falls, Perry’s Creek, Stony Lake - Smith and Harvey Townships, Trent-Severn Dam to Stony Lake', ['Perrys Creek', 'Stony Lake'], ['Smith', 'Harvey', 'Burleigh'], None),
 ('X17-FENELON', 'Fenelon River (Fenelon Falls)', 'Fenelon River - Fenelon Falls in Fenelon Township, from Trent-Severn Dam to second power line 1 km downstream', ['Fenelon River'], ['Fenelon'], None),
 ('X17-FISHOG', 'Fishog River (Head Lake to falls)', 'Fishog River - from the mouth of the river at Head Lake (44°45\'N, 78°54\'W) to the base of the waterfalls approximately 1.5 km upstream', ['Fishog River'], ['Laxton', 'Digby'], (44.75, -78.9)),
 ('X17-GULL-COBOCONK', 'Gull River (Coboconk)', 'Gull River - Coboconk in Bexley and Somerville Townships, from Trent-Severn Dam downstream to narrows approaching Balsam Lake', ['Gull River'], ['Bexley', 'Somerville'], None),
 ('X17-KATCHEWANOOKA', 'Katchewanooka Lake (Young’s Point)', 'Katchewanooka Lake - Young’s Point in Smith and Douro Townships, from Trent-Severn Dam to the downstream (west) side of the Highway 28 bridge', ['Katchewanooka Lake'], ['Smith', 'Douro'], None),
 ('X17-LOVESICK', 'Lovesick Dams', 'Lovesick Dams - Smith and Harvey Townships, 100 m downstream from each dam', ['Lovesick Lake'], ['Smith', 'Harvey', 'Burleigh'], None),
 ('X17-BUCKHORN', 'Lower Buckhorn Lake (Buckhorn dam)', 'Lower Buckhorn Lake (Buckhorn) - Smith and Harvey Townships, from Trent-Severn Dam to a point 400 m below the dam', ['Lower Buckhorn Lake'], ['Smith', 'Harvey'], None),
 ('X17-OTONABEE', 'Otonabee River (Lock 19 to Bensfort Bridge)', 'Otonabee River - Peterborough, from Trent-Severn Dam at Lock 19 to Bensfort Bridge at County Road 2 (20 km downstream)', ['Otonabee River'], ['Peterborough', 'Otonabee', 'Douro', 'Asphodel'], None),
 ('X17-PIGEONRIVER', 'Pigeon River (Omemee)', 'Pigeon River - Omemee in Emily Township, from Omemee Dam to CNR bridge', ['Pigeon River'], ['Emily'], None),
 ('X17-ROSEDALE', 'Rosedale River', 'Rosedale River - Rosedale in Fenelon Township, from the Trent-Severn Dam to Cameron Lake', ['Rosedale River'], ['Fenelon'], None),
 ('X17-TALBOT-KIRKFIELD', 'Talbot River (Kirkfield)', 'Talbot River - Kirkfield in Carden Township, fronting Concessions 7, 8 and 9', ['Talbot River'], ['Carden'], None)]:
    fs17(pid, nm, desc, w, t, S17B, T17B, pt=pt)
