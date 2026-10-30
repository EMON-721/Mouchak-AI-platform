"""Rights-reviewed, nonpersonal OSM public-road references; never safe-route/defect labels."""
import hashlib,json,os,re,sqlite3
from pathlib import Path
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field
from sqlalchemy import select,text
from .auth import identify,authorize,db_session,audit
from .store import Config,Source,User,uid,now
from .operations import SourceReview,rights_round,fingerprint
from sqlalchemy.orm import load_only

ROOT=Path(__file__).resolve().parents[2]
SOURCE_URL='https://download.geofabrik.de/asia/bangladesh-261028.osm.pbf'
SOURCE_SHA='59b394608adbffe28185091d637806954ddd65fd48d39ddbdf29ad90cfb1bf27'
LICENSE='https://opendatacommons.org/licenses/odbl/1-0/'
KEY='public-road-context'
router=APIRouter(prefix='/api')

def folder():
    value=os.getenv('PUBLIC_DATASET_DIR')
    return (Path(value) if value else ROOT/'.state/public-datasets')/'bd-roads-20261028'

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def prepared():
    path=folder()
    try:
        if path.is_symlink() or (path/'manifest.json').is_symlink() or (path/'roads.sqlite').is_symlink():raise ValueError()
        m=json.loads((path/'manifest.json').read_text())
        if m['schema']!='osm_public_road_reference_v1' or m['source_sha256']!=SOURCE_SHA or m['source_url']!=SOURCE_URL or m['license_uri']!=LICENSE or not re.fullmatch('[a-f0-9]{64}',m['sqlite_sha256']) or not re.fullmatch('[a-f0-9]{64}',m['rows_sha256']):raise ValueError()
        if not 1<=m['counts']['prepared_rows']<=500000 or (path/'roads.sqlite').stat().st_size>128*1024*1024 or digest(path/'roads.sqlite')!=m['sqlite_sha256']:raise ValueError()
        return m
    except (OSError,ValueError,KeyError,TypeError):raise HTTPException(503,'Prepared road reference data missing or changed / সড়ক তথ্য প্রস্তুত নেই বা checksum মেলেনি')

def source_id(m):return 'BD-OSM-20261028-'+m['rows_sha256'][:16]
def current(db):
    c=db.get(Config,KEY);return json.loads(c.value) if c else {'revision':None}
def lock(db):
    if db.bind.dialect.name=='postgresql':db.execute(text('SELECT pg_advisory_xact_lock(742009)'))
def put(db,key,value):
    c=db.get(Config,key)
    if c:c.value=json.dumps(value,ensure_ascii=False)
    else:db.add(Config(key=key,value=json.dumps(value,ensure_ascii=False)))

class Strict(BaseModel):model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)
class Publish(Strict):
    source_id:str=Field(min_length=1,max_length=100)
    expected_revision:str|None=None
class Withdraw(Strict):expected_revision:str|None=None
class Query(Strict):
    query:str=Field(min_length=2,max_length=300)
    processing_consent:Literal[True]

def approved(db,sid):
    source=db.get(Source,sid)
    if not source or source.module!='roadfix-bd' or source.state!='approved_train_and_reuse':raise HTTPException(409,'Current independent dataset rights approval is required')
    rd=rights_round(db,sid);reviews=list(db.scalars(select(SourceReview).where(SourceReview.source_id==sid,SourceReview.round==rd,SourceReview.decision=='approved_train_and_reuse')))
    active=json.loads(source.evidence or '{}')
    for chosen in reviews:
        same=[r for r in reviews if r.asset_hash==chosen.asset_hash]
        evidence=json.loads(chosen.evidence)
        ids=sorted({r.reviewer for r in same})
        if len(ids)<2 or active.get('review_id') not in {r.id for r in same} or evidence.get('asset_url')!=SOURCE_URL or evidence.get('license_uri')!=LICENSE or evidence.get('sensitivity')!='public_nonpersonal':continue
        for reviewer in ids:
            user=db.scalar(select(User).options(load_only(User.id,User.role,User.banned,User.mfa_enabled)).where(User.id==reviewer))
            if not user or user.banned or not user.mfa_enabled or user.role not in {'dataset_reviewer','super_admin'}:raise HTTPException(409,'A rights reviewer is no longer authorized')
        return source,{'round':rd,'evidence_hash':fingerprint(source.evidence),'reviewers':ids,'asset_hash':chosen.asset_hash}
    raise HTTPException(409,'Two matching independent ODbL public-nonpersonal reviews are required')

@router.get('/admin/road-data')
def status(u=Depends(authorize('jobs')),db=Depends(db_session,scope='function')):
    try:m=prepared()
    except HTTPException as error:return {'prepared':False,'detail':error.detail,'active':current(db)}
    sid=source_id(m);s=db.get(Source,sid)
    return {'prepared':True,'manifest':m,'source_id':sid,'source_state':s.state if s else 'not_registered','active':current(db),'not_a_defect_training_dataset':True}

@router.post('/admin/road-data/register',status_code=201)
def register(u=Depends(authorize('jobs')),db=Depends(db_session,scope='function')):
    m=prepared();sid=source_id(m);source=db.get(Source,sid)
    if not source:
        metadata={k:v for k,v in m.items() if k!='samples'}
        db.add(Source(id=sid,module='roadfix-bd',metadata_json=json.dumps({'source_id':sid,'publisher':'OpenStreetMap contributors / Geofabrik','url':SOURCE_URL,'license': 'ODbL-1.0','data_type':'nonpersonal_public_road_reference','prepared_dataset':metadata},ensure_ascii=False),state='candidate'))
        put(db,'road-data-stager:'+sid,{'actor':u.id,'created_at':now()});audit(db,u.id,'road_reference_registered',sid)
    return {'source_id':sid,'state':source.state if source else 'candidate','published':False}

@router.post('/admin/road-data/publish')
def publish(p:Publish,u=Depends(authorize('jobs')),db=Depends(db_session,scope='function')):
    lock(db);m=prepared();sid=source_id(m)
    if p.source_id!=sid or current(db).get('revision')!=p.expected_revision:raise HTTPException(409,'Prepared data or active revision changed')
    stage=db.get(Config,'road-data-stager:'+sid)
    if not stage or json.loads(stage.value)['actor']==u.id:raise HTTPException(403,'A different dataset operator must publish the staged index')
    source,rights=approved(db,sid)
    snap={'revision':uid(),'source_id':sid,'rows_sha256':m['rows_sha256'],'sqlite_sha256':m['sqlite_sha256'],'rights':rights,'published_by':u.id,'published_at':now()}
    put(db,KEY,snap);put(db,'road-data-history:'+snap['revision'],snap);audit(db,u.id,'road_reference_published',snap['revision'])
    return {'published':True,'revision':snap['revision'],'rows':m['counts']['prepared_rows'],'defect_model_enabled':False}

@router.post('/admin/road-data/withdraw')
def withdraw(p:Withdraw,u=Depends(authorize('jobs')),db=Depends(db_session,scope='function')):
    lock(db)
    if current(db).get('revision')!=p.expected_revision:raise HTTPException(409,'Active reference changed')
    put(db,KEY,{'revision':None});audit(db,u.id,'road_reference_withdrawn',p.expected_revision)
    return {'withdrawn':True}

@router.post('/tools/roadfix-bd/road-context')
def search(p:Query,u=Depends(identify),db=Depends(db_session,scope='function')):
    module=db.get(Config,"module:roadfix-bd")
    if module and json.loads(module.value).get("enabled") is False:raise HTTPException(503,"Tool disabled by operator")
    snapshot=current(db)
    if not snapshot.get('revision'):raise HTTPException(503,'No independently reviewed road index is published / অনুমোদিত সড়ক তালিকা প্রকাশিত নেই')
    source=db.get(Source,snapshot['source_id']);rights=snapshot['rights']
    if not source or source.state!='approved_train_and_reuse' or rights_round(db,source.id)!=rights['round'] or fingerprint(source.evidence)!=rights['evidence_hash']:raise HTTPException(503,'Road data rights changed; reference withdrawn / অনুমতি বদলেছে')
    for reviewer in rights['reviewers']:
        actor=db.scalar(select(User).options(load_only(User.id,User.role,User.banned,User.mfa_enabled)).where(User.id==reviewer))
        if not actor or actor.banned or not actor.mfa_enabled or actor.role not in {'dataset_reviewer','super_admin'}:raise HTTPException(503,'Road rights review is no longer current')
    m=prepared()
    if any(snapshot[k]!=m[k] for k in ['rows_sha256','sqlite_sha256']):raise HTTPException(503,'Published reference bytes changed')
    words=re.findall(r'[^\W_]+',p.query,re.UNICODE)[:20]
    if not words:return {'matches':[],'supported':False,'query_stored':False}
    fts=' OR '.join('"'+w.replace('"','""')+'"' for w in words)
    dbfile=(folder()/'roads.sqlite').resolve()
    connection=sqlite3.connect(dbfile.as_uri()+'?mode=ro',uri=True)
    try:
        connection.execute('PRAGMA query_only=ON');connection.row_factory=sqlite3.Row
        rows=connection.execute('SELECT r.* FROM roads_fts f JOIN roads r ON r.osm_way_id=f.osm_way_id WHERE roads_fts MATCH ? ORDER BY bm25(roads_fts) LIMIT 5',(fts,)).fetchall()
    except sqlite3.Error:raise HTTPException(503,'Public road index unavailable')
    finally:connection.close()
    matches=[{**dict(r),'url':'https://www.openstreetmap.org/way/'+r['osm_way_id']} for r in rows]
    return {'matches':matches,'supported':bool(matches),'method':'SQLite FTS5 lexical public reference lookup; not AI defect/safety inference','source_as_of':m['source_as_of'],'attribution':m['attribution'],'license':m['license'],'license_uri':LICENSE,'source_url':SOURCE_URL,'dataset_rows':m['counts']['prepared_rows'],'query_stored':False,'government_verified':False,'safe_route_inferred':False,'road_defect_inferred':False,'limitations':m['coverage']}
