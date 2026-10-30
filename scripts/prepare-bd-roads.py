"""Prepare a complete named public-road reference index from the pinned BD OSM extract.
ODbL-1.0 derived data; no defect/safety labels, coordinates or contributor metadata.
"""
import argparse, collections, hashlib, json, os, sqlite3, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE='https://download.geofabrik.de/asia/bangladesh-261028.osm.pbf'
SHA='59b394608adbffe28185091d637806954ddd65fd48d39ddbdf29ad90cfb1bf27'
MD5='0e9db373accaa20f98f1c344ee6543ee'
SIZE=355896654
ALLOWED={'motorway','motorway_link','trunk','trunk_link','primary','primary_link','secondary','secondary_link','tertiary','tertiary_link','unclassified','residential','living_street'}

def file_sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def prepare(source,target):
    import osmium
    if source.stat().st_size!=SIZE or file_sha(source)!=SHA: raise RuntimeError('BD extract checksum mismatch')
    target.mkdir(parents=True,exist_ok=True)
    database=target/'roads.sqlite.partial';database.unlink(missing_ok=True)
    rows_path=target/'roads.jsonl.partial'
    db=sqlite3.connect(database);db.execute('PRAGMA journal_mode=OFF');db.execute('PRAGMA synchronous=OFF')
    db.execute('CREATE TABLE roads (osm_way_id TEXT PRIMARY KEY,name_bn TEXT NOT NULL,name_en TEXT NOT NULL,highway TEXT NOT NULL,ref TEXT NOT NULL)')
    db.execute("CREATE VIRTUAL TABLE roads_fts USING fts5(osm_way_id UNINDEXED,name_bn,name_en,ref,tokenize='unicode61')")
    counters=collections.Counter();classes=collections.Counter();digest=hashlib.sha256();samples=[]
    with rows_path.open('wb') as output:
        class Roads(osmium.SimpleHandler):
            def way(self,w):
                counters['ways_seen']+=1
                highway=w.tags.get('highway')
                if highway not in ALLOWED or w.tags.get('access') in {'private','no'}: return
                counters['eligible_public_road_ways']+=1
                original=w.tags.get('name','').strip();bn=w.tags.get('name:bn',original).strip();en=w.tags.get('name:en',original).strip();ref=w.tags.get('ref','').strip()
                if not bn and not en and not ref: counters['missing_name_and_ref']+=1;return
                if max(map(len,[bn,en,ref]))>300: counters['oversized_text_quarantined']+=1;return
                bn=bn or en or ref;en=en or bn or ref
                record={'osm_way_id':str(w.id),'name_bn':bn,'name_en':en,'highway':highway,'ref':ref}
                encoded=(json.dumps(record,ensure_ascii=False,separators=(',',':'))+'\n').encode()
                output.write(encoded);digest.update(encoded)
                values=tuple(record[k] for k in ['osm_way_id','name_bn','name_en','highway','ref'])
                db.execute('INSERT INTO roads VALUES(?,?,?,?,?)',values)
                db.execute('INSERT INTO roads_fts VALUES(?,?,?,?)',(record['osm_way_id'],bn,en,ref))
                counters['prepared_rows']+=1;classes[highway]+=1
                if len(samples)<20:samples.append(record)
        Roads().apply_file(str(source),locations=False)
    db.commit();db.execute('PRAGMA optimize');db.close()
    rows_path.replace(target/'roads.jsonl');database.replace(target/'roads.sqlite')
    manifest={'schema':'osm_public_road_reference_v1','source_url':SOURCE,'source_as_of':'2026-10-28','source_sha256':SHA,'publisher_checksum_url':SOURCE+'.md5','publisher_md5':MD5,'source_bytes':SIZE,'rows_sha256':digest.hexdigest(),'sqlite_sha256':file_sha(target/'roads.sqlite'),'counts':dict(counters),'highway_counts':dict(classes),'license':'ODbL-1.0','license_uri':'https://opendatacommons.org/licenses/odbl/1-0/','terms_url':'https://www.geofabrik.de/data/download.html','attribution':'© OpenStreetMap contributors','metadata_removed':['user_name','user_id','changeset_id','coordinates'],'coverage':'Named non-private road ways from the Bangladesh extract; border-crossing ways and OSM omissions are possible. Not a complete official road register.','not_labels':['road defects','current traffic','crash probability','road safety','government verification'],'publication_state':'prepared_requires_independent_application_rights_review','samples':samples}
    (target/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    return manifest

def download(destination):
    if destination.is_file() and destination.stat().st_size==SIZE and file_sha(destination)==SHA:return
    destination.parent.mkdir(parents=True,exist_ok=True);temporary=destination.with_suffix('.partial')
    try:
        with urllib.request.urlopen(SOURCE+'.md5',timeout=45) as response: publisher=response.read(300).decode().split()[0]
        if publisher!=MD5: raise RuntimeError('Publisher snapshot checksum changed')
        size=0;md5=hashlib.md5();sha=hashlib.sha256()
        with urllib.request.urlopen(SOURCE,timeout=120) as response,temporary.open('wb') as output:
            for block in iter(lambda:response.read(1024*1024),b''):
                size+=len(block)
                if size>SIZE:raise RuntimeError('Extract exceeds expected bound')
                md5.update(block);sha.update(block);output.write(block)
        if size!=SIZE or md5.hexdigest()!=MD5 or sha.hexdigest()!=SHA:raise RuntimeError('Extract integrity mismatch')
        temporary.replace(destination)
    finally:temporary.unlink(missing_ok=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,default=ROOT/'.state/datasets/osm/bangladesh-261028.osm.pbf');parser.add_argument('--output',type=Path,default=Path(os.getenv('PUBLIC_DATASET_DIR') or ROOT/'.state/public-datasets')/'bd-roads-20261028');parser.add_argument('--download',action='store_true');args=parser.parse_args()
    if args.download:download(args.source)
    report=prepare(args.source,args.output)
    print(json.dumps({k:v for k,v in report.items() if k!='samples'},ensure_ascii=False))
