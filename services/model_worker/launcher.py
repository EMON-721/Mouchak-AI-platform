"""Actual multilingual MiniLM intent routing over 50 public tool descriptions.
Only public prototype vectors are cached; queries are never stored or trained on.
"""
import json, re, time, unicodedata
from functools import lru_cache
from pathlib import Path
import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from .auth import identify, db_session
from .inference import embed, tokens, MODEL_DIR
from .store import Config

ROOT=Path(__file__).resolve().parents[2]
CAT=json.loads((ROOT/'packages/module-registry/catalogue.json').read_text())['modules']
DATA=json.loads((ROOT/'data/authored/launcher-intents.json').read_text())
EMBEDDING_ASSET=next(x for x in json.loads((ROOT/'docs/audit/model-downloads.json').read_text()) if x['asset']=='minilm/model_quantized.onnx')
MODEL='Xenova/paraphrase-multilingual-MiniLM-L12-v2@'+EMBEDDING_ASSET['sha256']+'+bounded-BM25'
router=APIRouter(prefix='/api')
TASK_STOP=set('আমি আমাকে চাই করতে দিয়ে দেখতে চাচ্ছি ব্যবহার টুল সাহায্য করব করতে পারি হিসাব please help want need tool can could would like show calculate'.split())
def task_tokens(value):return [word for word in tokens(unicodedata.normalize("NFC",value)) if word not in TASK_STOP]
EMERGENCY=re.compile(r'শ্বাস\s*নিতে\s*পারছি\s*না|বুকে\s*(তীব্র\s*)?ব্যথা|অচেতন|আত্মহত্যা|নিজেকে\s*মেরে|cannot\s*breathe|chest\s*pain|kill\s*myself|suicid',re.I)

class Input(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)
    query:str=Field(min_length=3,max_length=800)
    language:str=Field(default='bn',pattern='^(bn|en)$')

@lru_cache(maxsize=1)
def index():
    from rank_bm25 import BM25Okapi
    import hashlib
    path=MODEL_DIR/'minilm/model_quantized.onnx'
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=EMBEDDING_ASSET['sha256']:raise HTTPException(503,'Semantic checkpoint missing or checksum mismatch')
    profiles={x['slug']:x for x in DATA['records']}
    if set(profiles)!={x['slug'] for x in CAT}:raise RuntimeError('Launcher catalogue coverage mismatch')
    texts=[];slugs=[]
    for m in CAT:
        p=profiles[m['slug']]
        for q in [m['name']+' '+m['description_bn']+' '+m['description_en'],p['query_bn'],p['query_en'],p['keywords_bn_en']]:
            texts.append(q);slugs.append(m['slug'])
    vectors=np.concatenate([embed(texts[i:i+8]) for i in range(0,len(texts),8)],axis=0)
    return slugs,vectors,BM25Okapi([task_tokens(x) for x in texts])

def recommend(query,language='bn',disabled=()):
    started=time.perf_counter()
    if EMERGENCY.search(query):
        return {'supported':False,'state':'urgent_help','suggestions':[],'message_bn':'জরুরি চিকিৎসা বা নিরাপত্তার বিকল্প এই launcher নয়। এখনই স্থানীয় জরুরি সেবা বা কাছের উপযুক্ত পেশাজীবীর সাহায্য নিন।','message_en':'This launcher cannot handle urgent medical or safety situations. Seek appropriate local emergency or professional help now.','model_inference_performed':False,'query_stored':False,'full_module_complete':False}
    exact=next((m for m in CAT if query.strip().casefold() in [m['slug'],m['name'].casefold()]),None)
    slugs,vectors,bm25=index()
    try:q=embed([query])[0]
    except Exception:raise HTTPException(503,'Semantic model unavailable; use ordinary catalogue search / semantic মডেল নেই; সাধারণ search ব্যবহার করুন')
    sem=vectors@q;lex=bm25.get_scores(task_tokens(query));maximum=max(float(np.max(lex)),1.)
    by_slug={}
    for i,slug in enumerate(slugs):
        if slug in disabled:continue
        lexical=max(float(lex[i]),0)/maximum
        score=.4*float(sem[i])+.6*lexical
        if slug not in by_slug or score>by_slug[slug][0]:by_slug[slug]=(score,float(sem[i]),lexical)
    if exact and exact['slug'] not in disabled:by_slug[exact['slug']]=(2.,1.,1.)
    ordered=sorted(by_slug,key=lambda s:by_slug[s][0],reverse=True)
    meaningful=set(task_tokens(query))
    known=set()
    for record in DATA['records']: known.update(task_tokens(record['query_bn']+' '+record['query_en']+' '+record['keywords_bn_en']))
    has_evidence=bool(meaningful & known)
    margin=by_slug[ordered[0]][0]-by_slug[ordered[1]][0] if len(ordered)>1 else 1.
    best=by_slug[ordered[0]] if ordered else (0.,0.,0.)
    # Bengali semantic scores can be broad: require task-specific lexical evidence
    # or a strong semantic margin rather than admitting unrelated high cosine hits.
    accepted=bool(ordered and (exact or (has_evidence and best[2]>=.6 and best[1]>=.25) or (best[1]>=.6 and margin>=.1)))
    selected=[s for s in ordered[:3] if by_slug[ordered[0]][0]-by_slug[s][0]<=.12] if accepted else []
    tools={m['slug']:m for m in CAT}
    suggestions=[{'slug':slug,'name':tools[slug]['name'],'route':'/tools/'+slug,'why_bn':tools[slug]['description_bn'],'why_en':tools[slug]['description_en'],'release_status':tools[slug]['release_status'],'similarity_not_probability':round(by_slug[slug][1],5)} for slug in selected if by_slug[slug][1]>=.25]
    ambiguous=len(suggestions)>1 and abs(by_slug[selected[0]][0]-by_slug[selected[1]][0])<.08
    return {'supported':bool(suggestions),'state':'choose_between_tasks' if ambiguous else 'suggestions' if suggestions else 'no_supported_intent','suggestions':suggestions,'message_bn':'কাজটি নিজে মিলিয়ে টুল বেছে নিন; কোনো তথ্য অন্য টুলে পাঠানো হয়নি।' if suggestions else 'নির্ভরযোগ্য মিল পাওয়া যায়নি। আরও নির্দিষ্ট করে লিখুন বা সাধারণ search ব্যবহার করুন।','message_en':'Compare the tasks and choose a tool yourself; no information was sent to another tool.' if suggestions else 'No reliable match. Describe the task more precisely or use ordinary search.','model_version':MODEL,'model_inference_performed':True,'query_stored':False,'scores_are_calibrated_probabilities':False,'latency_ms':round((time.perf_counter()-started)*1000,2),'full_module_complete':False}

@router.post('/launcher')
def launch(p:Input,u=Depends(identify),db=Depends(db_session,scope='function')):
    disabled=[]
    for m in CAT:
        conf=db.get(Config,'module:'+m['slug'])
        if conf and json.loads(conf.value).get('enabled') is False:disabled.append(m['slug'])
    try:return recommend(p.query,p.language,disabled)
    except HTTPException:raise
    except Exception:raise HTTPException(503,'Semantic model unavailable; ordinary catalogue search is available / semantic মডেল পাওয়া যাচ্ছে না')
