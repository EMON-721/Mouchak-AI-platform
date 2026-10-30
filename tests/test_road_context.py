"""Actual ODbL road-name subset + real FTS, rights and owner/session boundaries."""
import hashlib,json,sqlite3
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from conftest import Client
from services.model_worker.main import app
from services.model_worker.store import DB,Config,User,Source,Run
from services.model_worker import road_context as roads
from sqlalchemy import func,select

@pytest.fixture
def dataset(tmp_path,monkeypatch):
    monkeypatch.setenv('PUBLIC_DATASET_DIR',str(tmp_path))
    folder=tmp_path/'bd-roads-20261028';folder.mkdir()
    example=json.loads(Path('data/public/bd-road-reference-sample.json').read_text())
    rows=example['records'];database=folder/'roads.sqlite'
    with sqlite3.connect(database) as c:
        c.execute('CREATE TABLE roads(osm_way_id TEXT PRIMARY KEY,name_bn TEXT,name_en TEXT,highway TEXT,ref TEXT)')
        c.execute("CREATE VIRTUAL TABLE roads_fts USING fts5(osm_way_id UNINDEXED,name_bn,name_en,ref,tokenize='unicode61')")
        for row in rows:
            c.execute('INSERT INTO roads VALUES(?,?,?,?,?)',tuple(row[k] for k in ['osm_way_id','name_bn','name_en','highway','ref']))
            c.execute('INSERT INTO roads_fts VALUES(?,?,?,?)',tuple(row[k] for k in ['osm_way_id','name_bn','name_en','ref']))
    payload=''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows).encode()
    manifest={'schema':'osm_public_road_reference_v1','source_url':roads.SOURCE_URL,'source_as_of':example['source_as_of'],'source_sha256':roads.SOURCE_SHA,'license_uri':roads.LICENSE,'license':'ODbL-1.0','attribution':example['attribution'],'sqlite_sha256':hashlib.sha256(database.read_bytes()).hexdigest(),'rows_sha256':hashlib.sha256(payload).hexdigest(),'counts':{'prepared_rows':len(rows)},'coverage':'Public development subset only; not a representative holdout','test_subset':True}
    (folder/'manifest.json').write_text(json.dumps(manifest))
    with DB.begin() as db:
        old_source=db.get(Source,roads.source_id(manifest))
        if old_source:db.delete(old_source)
        old=db.get(Config,roads.KEY);previous=old.value if old else None
        if old:db.delete(old)
    yield manifest,database,rows
    with DB.begin() as db:
        current=db.get(Config,roads.KEY)
        if previous is None:
            if current:db.delete(current)
        else:roads.put(db,roads.KEY,json.loads(previous))

@pytest.fixture
def visitor():
    with TestClient(app) as c:
        actor=Client(c);actor.csrf=actor.request('POST','/api/session').json()['csrf'];yield actor

@pytest.fixture
def team(admin):
    with TestClient(app) as c:
        other=Client(c).register().admin('dataset_reviewer')
        yield admin,other

def review(actor,sid,decision='approved_train_and_reuse'):
    return actor.request('POST',f'/api/admin/sources/{sid}/reviews',json={'decision':decision,'asset_url':roads.SOURCE_URL,'terms_url':'https://www.geofabrik.de/data/download.html','license_uri':roads.LICENSE,'scope':'DEMO application workflow review over an actual ODbL nonpersonal public road-name subset','coverage':'Bangladesh OSM extract; development subset','source_date':'2026-10-28','evidence':'DEMO test review only; real OpenStreetMap names under ODbL, not a production human approval or defect evaluation.','sensitivity':'public_nonpersonal'})

def setup(a,b):
    response=a.request('POST','/api/admin/road-data/register');assert response.status_code==201,response.status_code
    sid=response.json()['source_id']
    assert a.request('POST','/api/admin/road-data/publish',json={'source_id':sid}).status_code==403
    assert review(a,sid).status_code==201
    assert b.request('POST','/api/admin/road-data/publish',json={'source_id':sid}).status_code==409
    assert review(b,sid).status_code==201
    response=b.request('POST','/api/admin/road-data/publish',json={'source_id':sid});assert response.status_code==200,response.status_code
    return sid,response.json()['revision']

def test_real_reference_lookup_review_publish_revoke_and_withdraw(dataset,team,visitor):
    client=visitor
    a,b=team
    query=next((r['ref'] for r in dataset[2] if len(r['ref'])>=2),dataset[2][0]['name_en'])
    assert client.request('POST','/api/tools/roadfix-bd/road-context',json={'query':query,'processing_consent':True}).status_code==503
    sid,revision=setup(a,b)
    with DB() as db:before=db.scalar(select(func.count()).select_from(Run))
    response=client.request('POST','/api/tools/roadfix-bd/road-context',json={'query':query,'processing_consent':True})
    assert response.status_code==200,response.status_code
    result=response.json();assert result['supported'] and result['matches']
    assert result['license']=='ODbL-1.0' and result['source_url']==roads.SOURCE_URL
    assert result['government_verified'] is False and result['road_defect_inferred'] is False and result['safe_route_inferred'] is False
    assert all('user_id' not in r and 'coordinates' not in r for r in result['matches'])
    with DB() as db:assert db.scalar(select(func.count()).select_from(Run))==before
    assert review(b,sid,'revoked').status_code==201
    assert client.request('POST','/api/tools/roadfix-bd/road-context',json={'query':query,'processing_consent':True}).status_code==503
    assert b.request('POST','/api/admin/road-data/withdraw',json={'expected_revision':revision}).status_code==200

def test_reference_bytes_and_reviewer_revocation_rechecked(dataset,team,visitor):
    client=visitor
    a,b=team;sid,revision=setup(a,b)
    with DB.begin() as db:db.get(User,b.user['id']).banned=True
    assert client.request('POST','/api/tools/roadfix-bd/road-context',json={'query':'N2','processing_consent':True}).status_code==503
    with DB.begin() as db:db.get(User,b.user['id']).banned=False
    with dataset[1].open('ab') as f:f.write(b'tampered')
    assert client.request('POST','/api/tools/roadfix-bd/road-context',json={'query':'N2','processing_consent':True}).status_code==503

def test_permissions_explicit_consent_and_unknown_fields(dataset,team,visitor):
    client=visitor
    assert client.request('GET','/api/admin/road-data').status_code==403
    assert client.request('POST','/api/admin/road-data/register').status_code==403
    assert client.request('POST','/api/tools/roadfix-bd/road-context',json={'query':'N2','processing_consent':False}).status_code==422
    assert client.request('POST','/api/tools/roadfix-bd/road-context',json={'query':'N2','processing_consent':True,'path':'/etc/passwd'}).status_code==422
    a,_=team
    assert a.client.post('/api/admin/road-data/register').status_code==403

def test_missing_index_never_reports_ready(tmp_path,monkeypatch,admin):
    monkeypatch.setenv('PUBLIC_DATASET_DIR',str(tmp_path))
    assert admin.request('GET','/api/admin/road-data').json()['prepared'] is False
    assert admin.request('POST','/api/admin/road-data/register').status_code==503
