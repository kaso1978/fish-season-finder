# Downloads the province's "Recreational fishing regulations data" (zone-wide
# rules, waterbody exceptions, fish sanctuaries and their official locations)
# from Ontario's open data catalogue into boundaries/regs/.
#
#   py fetch_regs.py
#
# Run it on a PC that can reach data.ontario.ca (the cloud can't). It asks the
# catalogue for the newest English .xlsx, so it finds next year's edition on
# its own. Licence: Open Government Licence - Ontario.
import json, os, sys, urllib.request
from datetime import datetime, timezone

DATASET = 'recreational-fishing-regulations-data'
API = 'https://data.ontario.ca/api/3/action/package_show?id=' + DATASET
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'regs')


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'fish-season-finder-tools'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def main():
    os.makedirs(OUT, exist_ok=True)
    pkg = json.loads(get(API))['result']
    picked = []
    for r in pkg['resources']:
        fmt = (r.get('format') or '').upper()
        name = (r.get('name') or '')
        if fmt in ('XLSX', 'XLS') and 'french' not in name.lower() and 'fran' not in name.lower():
            picked.append(r)
        elif fmt == 'DOCX' and 'english' in name.lower():
            picked.append(r)
    if not any((r.get('format') or '').upper() in ('XLSX', 'XLS') for r in picked):
        sys.exit('No English spreadsheet found in the catalogue entry; check ' + API)
    files = []
    for r in picked:
        fn = r['url'].rsplit('/', 1)[-1]
        data = get(r['url'])
        open(os.path.join(OUT, fn), 'wb').write(data)
        files.append({'name': r.get('name'), 'file': fn, 'url': r['url'], 'bytes': len(data),
                      'last_modified': r.get('last_modified') or r.get('created')})
        print('saved %-80s %9d bytes' % (fn, len(data)))
    meta = {'dataset': 'https://data.ontario.ca/dataset/' + DATASET, 'title': pkg.get('title'),
            'licence': 'Open Government Licence - Ontario', 'licence_url': 'https://www.ontario.ca/page/open-government-licence-ontario',
            'catalogue_modified': pkg.get('metadata_modified'), 'downloaded_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'files': files}
    json.dump(meta, open(os.path.join(OUT, 'fetch_regs.meta.json'), 'w'), indent=1)
    print('Done. Next: python exceptions/official.py (see exceptions/HOW-TO-UPDATE-EXCEPTIONS.md)')


if __name__ == '__main__':
    main()
