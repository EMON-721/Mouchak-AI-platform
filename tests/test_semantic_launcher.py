"""Actual multilingual model routing; examples are authored development cases."""
import json
import pytest
from services.model_worker.launcher import recommend,DATA,CAT
from services.model_worker.store import DB,Config,Run
from sqlalchemy import select,func

@pytest.mark.parametrize('query,slug',[
 ('পুকুরের মাছের আচরণ লিখব','pukursos-ai'),
 ('আমার দোকানে কোন পণ্যের মেয়াদ শেষ হবে','dokanlens-ai'),
 ('বাষ্পীভবন কীভাবে হয় বুঝব','shikkharag-bd'),
 ('compare my rent expenses','rentalfair-bd'),
 ('চুক্তির দুটি কাগজে কী বদলেছে','chuktishield-ai'),
 ('Calculate appliance energy consumption','biddutplan-bd'),
 ('বাসার বিদ্যুৎ খরচ কমানোর হিসাব করতে চাই','biddutplan-bd'),
 ('ফ্যান ফ্রিজ কত বিদ্যুৎ ব্যবহার করে','biddutplan-bd'),
 ('বিদ্যুৎ বিলের যোগফল ঠিক আছে কিনা দেখব','billdetect-ai'),
 ('ডেঙ্গুর তারিখসহ দেওয়া সংখ্যা তুলনা করব','denguesignal-bd'),
 ('পণ্যের মজুদ আর মেয়াদ লিখে রাখব','dokanlens-ai'),
 ('বাড়ি ভাড়া আর মাসের খরচ তুলনা','rentalfair-bd'),
 ('দুইটা চুক্তির ধারা তুলনা করতে চাই','chuktishield-ai'),
])
def test_real_model_ranks_relevant_tool(query,slug):
    r=recommend(query);assert r['supported'];assert slug in [x['slug'] for x in r['suggestions']]
    assert r['model_inference_performed'] and not r['query_stored']
    assert r['scores_are_calibrated_probabilities'] is False

def test_fifty_exact_tool_names_have_real_inference_and_correct_routes():
    assert len(DATA['records'])==50 and {x['slug'] for x in DATA['records']}=={x['slug'] for x in CAT}
    for m in CAT:
        r=recommend(m['name']);assert r['suggestions'][0]['slug']==m['slug'];assert r['suggestions'][0]['route']=='/tools/'+m['slug']
        assert r['model_inference_performed'] and r['full_module_complete'] is False

@pytest.mark.parametrize('query',['asdfghqwerty zzzz','galaxies and space telescope'])
def test_no_supported_evidence_abstains(query):
    r=recommend(query);assert not r['supported'];assert r['suggestions']==[]

@pytest.mark.parametrize('query',['এখন শ্বাস নিতে পারছি না','I have chest pain','kill myself'])
def test_urgent_requests_are_not_routed_as_tool_advice(query):
    r=recommend(query);assert r['state']=='urgent_help' and r['suggestions']==[] and not r['model_inference_performed']

def test_endpoint_csrf_owner_session_and_disabled_tools(client):
    response=client.request('POST','/api/session');client.csrf=response.json()['csrf']
    with DB() as db:before=db.scalar(select(func.count()).select_from(Run))
    r=client.request('POST','/api/launcher',json={'query':'BiddutPlan BD','language':'en'})
    assert r.status_code==200 and r.json()['suggestions'][0]['slug']=='biddutplan-bd'
    assert client.client.post('/api/launcher',json={'query':'BiddutPlan BD'}).status_code==403
    with DB.begin() as db:db.add(Config(key='module:biddutplan-bd',value=json.dumps({'enabled':False})))
    try:
        r=client.request('POST','/api/launcher',json={'query':'BiddutPlan BD'});assert r.status_code==200
        assert 'biddutplan-bd' not in [s['slug'] for s in r.json()['suggestions']]
    finally:
        with DB.begin() as db:db.delete(db.get(Config,'module:biddutplan-bd'))
    with DB() as db:assert db.scalar(select(func.count()).select_from(Run))==before
    assert client.request('POST','/api/launcher',json={'query':'x'*801}).status_code==422

def test_bangla_electricity_task_excludes_unrelated_medical_and_forms():
    r=recommend('বাসার বিদ্যুৎ খরচ কমানোর হিসাব করতে চাই')
    slugs={x['slug'] for x in r['suggestions']}
    assert r['suggestions'][0]['slug']=='biddutplan-bd'
    assert not slugs & {'labtrend-bd','civicform-ai','repairright-bd'}
