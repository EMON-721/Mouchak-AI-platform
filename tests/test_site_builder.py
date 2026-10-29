"""Typed CMS: private drafts, immutable approval, schema and permission boundaries."""
import json, time
from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from conftest import Client
from services.model_worker.main import app
from services.model_worker.store import DB, Config, User
from services.model_worker import site_builder as sb
from services.model_worker.operations import run_due

@pytest.fixture
def team(admin):
    with DB.begin() as db:
        previous={k:(db.get(Config,k).value if db.get(Config,k) else None) for k in [sb.KEY,'site-active-revision']}
        for k in previous:
            if db.get(Config,k): db.delete(db.get(Config,k))
    with TestClient(app) as c:
        second=Client(c).register().admin('content_editor')
        yield admin,second
    with DB.begin() as db:
        for k,value in previous.items():
            current=db.get(Config,k)
            if value is None:
                if current: db.delete(current)
            else: sb.put(db,k,value)

def config(name='DEMO reviewed brand'):
    value=deepcopy(sb.DEFAULT); value['brand']['name_en']=name
    return value

def draft(author,value=None,revision=None):
    r=author.request('POST','/api/admin/site-builder',json={'config':value or config(),'expected_revision':revision})
    assert r.status_code==201,r.text
    return r.json()['id']

def review(actor,vid):
    return actor.request('POST',f'/api/admin/site-builder/{vid}/review',json={'decision':'approved','reason':'DEMO checked presentation and source rights.'})

def publish(actor,vid,revision=None,rollback=False):
    return actor.request('POST',f'/api/admin/site-builder/{vid}/publish',json={'expected_revision':revision,'rollback':rollback})

def test_independent_review_private_draft_publish_and_rollback(team):
    a,b=team; vid=draft(a)
    assert a.request('GET','/api/public/site').json()['revision'] is None
    assert review(a,vid).status_code==403
    assert publish(a,vid).status_code==409
    assert publish(a,vid,rollback=True).status_code==409
    assert review(b,vid).status_code==200
    assert review(b,vid).status_code==409
    assert publish(a,vid).status_code==200
    assert a.request('GET','/api/public/site').json()['config']['brand']['name_en']=='DEMO reviewed brand'
    newer=draft(b,config('DEMO second brand'),vid)
    assert review(a,newer).status_code==200
    assert publish(b,newer,vid).status_code==200
    assert publish(a,vid,newer,True).status_code==200
    assert a.request('GET','/api/public/site').json()['revision']==vid

def test_generic_cms_and_scheduler_cannot_bypass_review(team):
    a,b=team; vid=draft(a)
    assert a.request('POST','/api/admin/cms',json={'value':{'page':sb.PAGE,'body':config()}}).status_code==409
    assert a.request('POST',f'/api/admin/cms/{vid}/publish').status_code==409
    assert a.request('POST','/api/admin/publishing',json={'version_id':vid,'due_at':int(time.time())+60}).status_code==409
    assert review(b,vid).status_code==200
    r=a.request('POST','/api/admin/publishing',json={'version_id':vid,'due_at':int(time.time())+60})
    assert r.status_code==201,r.text
    with DB.begin() as db: result=run_due(db,int(time.time())+120)
    assert next(x for x in result if x['id']==r.json()['id'])['state']=='published'
    assert a.request('GET','/api/public/site').json()['revision']==vid

def test_stale_and_revoked_reviews_fail_closed(team):
    a,b=team; first=draft(a); stale=draft(a,config('DEMO stale'))
    assert review(b,first).status_code==200
    assert review(b,stale).status_code==200
    assert publish(a,first).status_code==200
    assert a.request('POST','/api/admin/site-builder',json={'config':config('DEMO outdated editor'),'expected_revision':None}).status_code==409
    assert publish(a,stale,first).status_code==409
    fresh=draft(a,config('DEMO revocation'),first)
    assert review(b,fresh).status_code==200
    with DB.begin() as db: db.get(User,b.user['id']).banned=True
    assert publish(a,fresh,first).status_code==409

def test_scheduled_publication_rechecks_reviewer(team):
    a,b=team; vid=draft(a); assert review(b,vid).status_code==200
    r=a.request('POST','/api/admin/publishing',json={'version_id':vid,'due_at':int(time.time())+60}); assert r.status_code==201
    with DB.begin() as db: db.get(User,b.user['id']).role='user'
    with DB.begin() as db: result=run_due(db,int(time.time())+120)
    assert next(x for x in result if x['id']==r.json()['id'])['state']=='review_unavailable'
    assert a.request('GET','/api/public/site').json()['revision'] is None

@pytest.mark.parametrize('change',[
    lambda c:c.update(auth={'signup':True}),
    lambda c:c['brand'].update(logo_asset='https://example.test/track.svg'),
    lambda c:c['theme']['light'].update(ink=c['theme']['light']['paper']),
    lambda c:c['theme'].update(font='url(https://example.test/font)'),
    lambda c:c['theme'].update(text_scale=9),
    lambda c:c['navigation'][0].update(href='https://example.test'),
    lambda c:c['footer'].update(links=[]),
    lambda c:c['home'].update(sections=['hero','featured']),
    lambda c:c['home'].update(featured_slugs=['missing']),
    lambda c:c['locales'].update({'Advanced AI is still being evaluated.':{'bn':'প্রস্তুত','en':'All ready'}}),
    lambda c:c['tool_overrides'].update({'pukursos-ai':{'model_ready':True}}),
    lambda c:c['tool_overrides'].update({'pukursos-ai':{'fields':{'not_a_field':{'bn':'দেখুন','en':'View'}}}}),
    lambda c:c['pages'].update({'admin':{'title':{'bn':'প্রশাসন','en':'Admin'},'body':{'bn':'দেখুন','en':'View'}}}),
    lambda c:c['brand'].update(name_en='<script>alert(1)</script>'),
])
def test_unsafe_schema_rejected(team,change):
    a,_=team; value=config(); change(value)
    assert a.request('POST','/api/admin/site-builder/validate',json={'config':value}).status_code==422

def test_owned_asset_publication_and_tool_fields_do_not_mutate_engine_schema(team):
    a,b=team
    with TestClient(app) as public:
        public.request('POST','/api/session')
        original=public.get('/api/modules/pukursos-ai').json()
        svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><circle cx="10" cy="10" r="8" fill="#116f6e"/></svg>'
        r=a.request('POST','/api/admin/site-assets',json={'svg':svg,'license_uri':'https://example.test/owned-mark-license','rights_note':'DEMO original geometric test artwork owned by fixture.','attest_rights':True})
        assert r.status_code==201,r.text
        asset=r.json(); assert public.get(asset['url']).status_code==404
        assert a.request('GET',asset['url']).status_code==200
        value=config(); value['brand']['logo_asset']=asset['id']
        field=next(iter(sb.field_paths('pukursos-ai')))
        baseline=deepcopy(sb.FIELDS)
        value['tool_overrides']['pukursos-ai']={'name':{'bn':'ডেমো পুকুর','en':'DEMO pond'},'fields':{field:{'bn':'পরিমাপ','en':'DEMO measured field','help_en':'Verify your measurement','help_bn':'নিজের মাপ যাচাই করুন'}}}
        vid=draft(a,value); assert review(b,vid).status_code==200; assert publish(a,vid).status_code==200
        response=public.get(asset['url']); assert response.status_code==200
        assert "default-src 'none'" in response.headers['Content-Security-Policy']
        tool=public.get('/api/modules/pukursos-ai').json()
        assert tool['name']=='DEMO pond' and tool['fields'][0]['en']=='DEMO measured field'
        for key in ['engine','release_status','model_ready','full_module_complete','safety']:
            assert tool[key]==original[key]
        assert tool['presentation_base']['name']==original['name']
        assert tool['presentation_base']['fields']==original['fields']
        assert sb.FIELDS==baseline
        with DB() as db: assert db.get(Config,'site-asset:'+asset['id'])

@pytest.mark.parametrize('svg',[
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><script>alert(1)</script></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" onload="alert(1)"/>',
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><image href="https://example.test/pixel"/></svg>',
    '<!DOCTYPE svg [<!ENTITY x "bad">]><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"/>',
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path fill="url(#a)"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><circle r="1e999"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">'+'<g>'*14+'</g>'*14+'</svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">'+'<circle r="1"/>'*301+'</svg>',
])
def test_svg_executable_external_and_resource_content_refused(svg):
    from fastapi import HTTPException
    with pytest.raises(HTTPException): sb.safe_svg(svg)

def test_permission_and_csrf(team):
    a,_=team
    with TestClient(app) as c:
        user=Client(c).register()
        assert user.request("GET","/api/admin/site-builder").status_code==403
        assert user.request("GET","/api/admin/site-builder/missing/preview").status_code==403
    assert a.client.post('/api/admin/site-builder',json={'config':config()}).status_code==403
