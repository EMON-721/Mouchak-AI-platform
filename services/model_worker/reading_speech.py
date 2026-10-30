"""Ephemeral, local adult Bengali reading speech experiment. No child release gate."""
from functools import lru_cache
from pathlib import Path
from typing import Literal
import hashlib, importlib.util, io, json, math, os, threading, time, unicodedata, wave
import numpy as np
import regex
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text as sql
from .auth import identify, authorize, db_session, audit
from .store import Config, ROOT, uid, now
from .legacy_workflows import READING
from .domain import InputError

router=APIRouter()
MANIFEST=json.loads((ROOT/'docs/audit/reading-speech-assets.json').read_text())
MODEL_ID=MANIFEST['model_id']
POLICY_KEY='reading-speech-policy'
LOCK=threading.BoundedSemaphore(1)
MAX_BYTES=10*1024*1024
DECODE={'language':'bn','task':'transcribe','beam_size':3,'temperature':0.0,'condition_on_previous_text':False,'without_timestamps':True,'word_timestamps':True,'vad_filter':True,'max_new_tokens':440}

def model_dir():return Path(os.getenv('MODEL_DIR',ROOT/'models'))/MANIFEST['directory']
def signature():
    folder=model_dir();rows=[]
    for name,a in MANIFEST['assets'].items():
        p=folder/name
        if p.is_symlink() or not p.is_file():raise HTTPException(503,'Speech model missing / মডেল পাওয়া যায়নি')
        s=p.stat()
        if s.st_size!=a['bytes']:raise HTTPException(503,'Speech model size mismatch / মডেল সঠিক নয়')
        rows.append((name,s.st_ino,s.st_mtime_ns,s.st_size))
    return tuple(rows)

def verify_assets():
    before=signature()
    for name,a in MANIFEST['assets'].items():
        with (model_dir()/name).open('rb') as f:
            if hashlib.file_digest(f,'sha256').hexdigest()!=a['sha256']:raise HTTPException(503,'Speech model checksum mismatch / মডেলের checksum মেলেনি')
    if signature()!=before:raise HTTPException(503,'Model files changed during verification')
    return before

@lru_cache(maxsize=1)
def runtime():
    sig=verify_assets()
    from faster_whisper import WhisperModel
    model=WhisperModel(str(model_dir()),device='cpu',compute_type='int8',cpu_threads=2,num_workers=1,local_files_only=True)
    if signature()!=sig:raise HTTPException(503,'Model changed during load')
    return model,sig

def availability():
    try:signature();present=True
    except HTTPException:present=False
    available=importlib.util.find_spec('faster_whisper') is not None
    return {'checkpoint':MODEL_ID,'assets_present':present,'checksum_verification_required_at_load':True,'runtime_available':available,'experimental_enabled':present and available and os.getenv('ENABLE_EXPERIMENTAL_READING_ASR')=='1' and os.getenv('MOUCHAK_ENV')!='production','production_enabled':False,'child_recording_enabled':False,'adult_self_recording_only':True,'raw_voice_retained':False,'field_validation_approved':False,'reason':'Local adult experiment; guardian verification, child field validation and independent model/data review remain unapproved.'}

def normalize(value):
    value=unicodedata.normalize('NFC',str(value)).translate(str.maketrans('০১২৩৪৫৬৭৮৯','0123456789'))
    value=value.replace('\u200c','').replace('\u200d','')
    return regex.sub(r'\s+',' ',regex.sub(r'[\p{P}\p{S}]',' ',value)).strip().casefold()

def edits(a,b,alignment=False):
    if not alignment:
        if len(a)<len(b):a,b=b,a
        previous=list(range(len(b)+1))
        for i,x in enumerate(a,1):
            current=[i]
            for j,y in enumerate(b,1):current.append(min(previous[j]+1,current[-1]+1,previous[j-1]+(x!=y)))
            previous=current
        return previous[-1]
    d=[[0]*(len(b)+1) for _ in range(len(a)+1)]
    for i in range(len(a)+1):d[i][0]=i
    for j in range(len(b)+1):d[0][j]=j
    for i,x in enumerate(a,1):
        for j,y in enumerate(b,1):d[i][j]=min(d[i-1][j]+1,d[i][j-1]+1,d[i-1][j-1]+(x!=y))
    rows=[];i=len(a);j=len(b)
    while i or j:
        if i and j and d[i][j]==d[i-1][j-1]+(a[i-1]!=b[j-1]):
            rows.append({'reference_index':i-1,'hypothesis_index':j-1,'reference_word':a[i-1],'heard_word':b[j-1],'state':'detected' if a[i-1]==b[j-1] else 'review_uncertain'});i-=1;j-=1
        elif i and d[i][j]==d[i-1][j]+1:
            rows.append({'reference_index':i-1,'hypothesis_index':None,'reference_word':a[i-1],'heard_word':'','state':'not_detected'});i-=1
        else:
            rows.append({'reference_index':None,'hypothesis_index':j-1,'reference_word':'','heard_word':b[j-1],'state':'extra_heard'});j-=1
    return list(reversed(rows))

def metrics(reference,hypothesis):
    r,h=normalize(reference),normalize(hypothesis)
    if len(r)>4000 or len(h)>4000 or len(r.split())>250 or len(h.split())>300:raise InputError('Speech comparison exceeds bounded length')
    rw,hw=r.split(),h.split();rg,hg=regex.findall(r'\X',r),regex.findall(r'\X',h)
    we,ce,ge=edits(rw,hw),edits(r,h),edits(rg,hg)
    return {'word_errors':we,'reference_words':len(rw),'wer':we/max(1,len(rw)),'character_errors':ce,'reference_characters':len(r),'cer':ce/max(1,len(r)),'grapheme_errors':ge,'reference_graphemes':len(rg),'grapheme_error_rate':ge/max(1,len(rg))}

def word_alignment(reference,hypothesis):
    metrics(reference,hypothesis) # Enforce bounds before matrix allocation.
    return edits(normalize(reference).split(),normalize(hypothesis).split(),True)

def read_wav(data):
    if not isinstance(data,bytes) or len(data)>MAX_BYTES:raise InputError('PCM WAV exceeds 10 MiB / WAV বেশি বড়')
    try:
        with wave.open(io.BytesIO(data),'rb') as source:
            channels,rate,width,frames=source.getnchannels(),source.getframerate(),source.getsampwidth(),source.getnframes()
            if channels not in (1,2) or width!=2 or not 8000<=rate<=96000 or not 1<=frames/rate<=30:raise InputError('Use 1–30 second 16-bit mono/stereo PCM WAV, 8–96 kHz / সঠিক PCM WAV দিন')
            raw=source.readframes(frames)
            if len(raw)!=frames*channels*width:raise InputError('Truncated audio / অডিও অসম্পূর্ণ')
    except (wave.Error,EOFError,ZeroDivisionError):raise InputError('Unreadable PCM WAV / WAV পড়া যায়নি')
    audio=np.frombuffer(raw,dtype='<i2').astype(np.float32).reshape(-1,channels).mean(axis=1)/32768
    if rate!=16000:
        from scipy.signal import resample_poly
        divisor=math.gcd(rate,16000);audio=resample_poly(audio,16000//divisor,rate//divisor).astype(np.float32)
    return audio,{'seconds':round(frames/rate,4),'original_sample_rate':rate,'original_channels':channels,'resampled_rate':16000}

def bengali_evidence(value):
    letters=regex.findall(r'\p{L}',value)
    return bool(letters) and '\ufffd' not in value and sum('\u0980'<=x<='\u09ff' for x in letters)/len(letters)>=.6

def transcribe(data,diagnostic=False):
    started=time.perf_counter();audio,signal=read_wav(data)
    rms=float(np.sqrt(np.mean(audio.astype(np.float64)**2)));clipped=float(np.mean(np.abs(audio)>=.999))
    output={'checkpoint':MODEL_ID,'supported':False,'model_inference_performed':False,'text':'','words':[],'segments':[],'signal':{**signal,'rms_amplitude':rms,'clipped_fraction':clipped},'raw_voice_retained':False,'transcript_saved':False,'production_approved':False,'child_recording_enabled':False,'pronunciation_score_available':False}
    if rms<.0001 or clipped>.25:
        output['message']='শব্দটি পরিষ্কার শোনা যায়নি; আবার পড়ুন বা হাতে লিখুন। / Low-quality recording; rerecord or use typed practice.'
        return output
    model,sig=runtime()
    if signature()!=sig:raise HTTPException(503,'Model changed after load; restart the worker')
    segments,info=model.transcribe(audio,**DECODE)
    output['model_inference_performed']=True
    accepted=[];words=[]
    for segment in segments:
        if segment.no_speech_prob>.7 or segment.avg_logprob < -1 or segment.compression_ratio>2.4:continue
        accepted.append({'start_seconds':float(segment.start),'end_seconds':float(segment.end),'text':segment.text,'avg_logprob':float(segment.avg_logprob),'compression_ratio':float(segment.compression_ratio)})
        for word in segment.words or []:
            words.append({'word':word.word.strip(),'start_seconds':float(word.start),'end_seconds':float(word.end),'uncalibrated_probability':float(word.probability)})
    candidate=' '.join(x['text'].strip() for x in accepted).strip()
    if diagnostic:output['_evaluation_hypothesis']=candidate # CLI only, never an API option.
    if bengali_evidence(candidate) and len(candidate)<=4000 and len(candidate.split())<=300:
        output.update(supported=True,text=candidate,words=words,segments=accepted)
    output.update(latency_ms=round((time.perf_counter()-started)*1000,2),message='যন্ত্রের লেখা ভুল হতে পারে; নিজে যাচাই করুন। / Review the transcript; ASR can be wrong.' if output['supported'] else 'শব্দটি পরিষ্কার শোনা যায়নি; হাতে লিখুন। / Uncertain Bengali evidence; use manual practice.')
    return output

def policy(db):
    c=db.get(Config,POLICY_KEY)
    return json.loads(c.value) if c else {'revision':None,'state':'experimental','reason':'Explicit local environment opt-in required; no production or child release'}

def status(db):
    value=availability();p=policy(db);c=db.get(Config,'module:banglaread-coach')
    module=json.loads(c.value) if c else {}
    disabled=p['state']=='disabled' or module.get('enabled') is False
    value.update(operator_disabled=disabled,experimental_enabled=value['experimental_enabled'] and not disabled)
    return value

@router.get('/api/reading/speech/status')
def public_status(db=Depends(db_session,scope='function')):return status(db)

@router.post('/api/reading/speech/transcribe')
def speech(file:UploadFile=File(...),recording_subject:Literal['self_adult']=Form(...),adult_processing_consent:bool=Form(...),passage_id:str|None=Form(default=None,max_length=100),u=Depends(identify),db=Depends(db_session,scope='function')):
    try:
        if not adult_processing_consent:raise HTTPException(422,'Adult self-recording consent required / নিজের প্রাপ্তবয়স্ক কণ্ঠ প্রক্রিয়াকরণের সম্মতি দিন')
        if not status(db)['experimental_enabled']:raise HTTPException(503,'Local speech experiment unavailable; use typed/tap practice / হাতে অনুশীলন করুন')
        passage=None
        if passage_id:
            authored=json.loads((ROOT/'data/authored/learning.json').read_text())
            passage=next((x.get('text_bn',x.get('text','')) for x in [*authored,*READING] if x['id']==passage_id),None)
            if passage is None:raise HTTPException(422,'Unknown passage / পাঠ পাওয়া যায়নি')
        data=file.file.read(MAX_BYTES+1)
        if len(data)>MAX_BYTES:raise HTTPException(413,'Audio exceeds 10 MiB')
        if not LOCK.acquire(blocking=False):raise HTTPException(429,'Speech worker busy; retry later',headers={'Retry-After':'30'})
        try:out=transcribe(data)
        finally:LOCK.release()
        if passage and out['supported']:out['alignment']=word_alignment(passage,out['text'])
        return out
    finally:file.file.close()

class PolicyInput(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)
    state:Literal['disabled','experimental']
    expected_revision:str|None=Field(default=None,max_length=100)
    reason:str=Field(min_length=10,max_length=1000)

def evaluation():
    p=ROOT/'docs/audit/reading-speech-evaluation.json'
    if not p.is_file():return None
    value=json.loads(p.read_text())
    return value if value.get('checkpoint')==MODEL_ID and value.get('schema_version')==1 else None

@router.get('/api/admin/reading-speech')
def overview(u=Depends(authorize('models')),db=Depends(db_session,scope='function')):
    return {'runtime':status(db),'policy':policy(db),'manifest':MANIFEST,'evaluation':evaluation(),'production_release_allowed':False,'private_recordings_listed':False}

@router.post('/api/admin/reading-speech/policy')
def change_policy(p:PolicyInput,u=Depends(authorize('models')),db=Depends(db_session,scope='function')):
    if db.bind.dialect.name=='postgresql':db.execute(sql('SELECT pg_advisory_xact_lock(742010)'))
    old=policy(db)
    if old['revision']!=p.expected_revision:raise HTTPException(409,'Policy changed; reload before updating')
    value={'revision':uid(),'state':p.state,'reason':p.reason,'actor':u.id,'created_at':now(),'previous_revision':old['revision']}
    c=db.get(Config,POLICY_KEY)
    if c:c.value=json.dumps(value,ensure_ascii=False)
    else:db.add(Config(key=POLICY_KEY,value=json.dumps(value,ensure_ascii=False)))
    db.add(Config(key=POLICY_KEY+'-history:'+value['revision'],value=json.dumps(value,ensure_ascii=False)))
    audit(db,u.id,'reading_speech_policy',value['revision'],{'state':p.state,'previous_revision':old['revision']})
    return {**value,'production_release_allowed':False}

class SpeechBodyLimit:
    """Bound actual incoming multipart bytes before parsing, including chunked bodies."""
    def __init__(self,app):self.app=app
    async def __call__(self,scope,receive,send):
        if scope['type']!='http' or scope.get('path')!='/api/reading/speech/transcribe' or scope.get('method')!='POST':
            return await self.app(scope,receive,send)
        parts=[];size=0
        while True:
            message=await receive()
            if message['type']=='http.disconnect':return
            chunk=message.get('body',b'');size+=len(chunk)
            if size>MAX_BYTES+65536:
                from starlette.responses import JSONResponse
                return await JSONResponse({'detail':'Speech multipart request too large'},status_code=413)(scope,receive,send)
            parts.append(chunk)
            if not message.get('more_body',False):break
        body=b''.join(parts);sent=False
        async def replay():
            nonlocal sent
            if not sent:
                sent=True;return {'type':'http.request','body':body,'more_body':False}
            return await receive()
        return await self.app(scope,replay,send)
