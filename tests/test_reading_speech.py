"""Actual public Bengali speech inference plus API privacy, bounds and role controls."""
import asyncio, hashlib, io, json, wave
import numpy as np
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from services.model_worker import reading_speech as speech
from services.model_worker.domain import InputError
from services.model_worker.main import app
from services.model_worker.store import DB, Run, Asset, Config, Session
from services.model_worker.auth import digest

ROOT=speech.ROOT
CORPUS=ROOT/'.state/evaluation/reading-speech'

def wav(seconds=1.5,rate=16000,channels=1,mode='silence'):
    values=np.zeros(int(seconds*rate)) if mode=='silence' else np.ones(int(seconds*rate))*.99999
    frames=(values*32767).astype('<i2')
    if channels==2:frames=np.column_stack([frames,frames]).ravel()
    output=io.BytesIO()
    with wave.open(output,'wb') as w:w.setparams((channels,2,rate,0,'NONE',''));w.writeframes(frames.tobytes())
    return output.getvalue()

def corpus():
    value=json.loads((CORPUS/'manifest.json').read_text())
    assert value['source_rows']==1891 and value['speaker_groups']==6 and len(value['rows'])==12
    return value['rows']

def clip(row):
    raw=(CORPUS/row['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==row['sha256'];return raw

def scope(c):
    r=c.post('/api/session');assert r.status_code==200
    c.headers['x-csrf-token']=r.json()['csrf'];return r.json()['visitor_id']

def post(c,raw=None,**overrides):
    data={'recording_subject':'self_adult','adult_processing_consent':'true','passage_id':'AUTH-READ-01'};data.update(overrides)
    return c.post('/api/reading/speech/transcribe',files={'file':('own.wav',wav() if raw is None else raw,'audio/wav')},data=data)

def test_normalization_digits_joiners_and_nfc():
    assert speech.normalize('ক্ষ\u200dমা, ১২৩!')=='ক্ষমা 123'
    assert speech.normalize('ক\u200cর্ম')==speech.normalize('কর্ম')
    assert speech.normalize('কথা  কথা\n')=='কথা কথা'

def test_grapheme_errors_and_rates_not_clamped():
    m=speech.metrics('কি','কী');assert m['reference_graphemes']==1 and m['grapheme_errors']==1
    m=speech.metrics('আমি','আমি আমি আমি');assert m['wer']==2 and m['cer']>1
    assert speech.metrics('বাংলা ১২','বাংলা 12')['wer']==0

def test_alignment_positions_are_unique_and_uncertain():
    rows=speech.word_alignment('আমি বাংলা পড়ি','আমি বই বাংলা লিখি')
    assert rows[0]['state']=='detected'
    assert {r['state'] for r in rows}>={'detected','extra_heard','review_uncertain'}
    assert [r['reference_index'] for r in rows if r['reference_index'] is not None]==[0,1,2]

@pytest.mark.parametrize('text',['hello world','नमस्ते दुनिया','বাংলা\ufffd','1234',''])
def test_wrong_script_or_corruption_is_not_accepted(text):assert not speech.bengali_evidence(text)

@pytest.mark.parametrize('mode',['silence','clipped'])
def test_bad_signal_abstains_before_loading_model(mode,monkeypatch,tmp_path):
    monkeypatch.setenv('MODEL_DIR',str(tmp_path))
    out=speech.transcribe(wav(mode=mode));assert not out['supported'] and not out['model_inference_performed']
    assert out['text']=='' and out['words']==[] and out['raw_voice_retained'] is False

@pytest.mark.parametrize('data',[b'invalid',wav(seconds=.5),wav(seconds=31),wav(rate=4000),wav()[:-40]])
def test_wav_bounds_and_truncation(data):
    with pytest.raises(InputError):speech.read_wav(data)

def test_stereo_resampling():
    audio,signal=speech.read_wav(wav(rate=22050,channels=2));assert signal['resampled_rate']==16000 and len(audio)==24000
    assert signal['original_channels']==2

def test_missing_or_symlinked_weights_never_claim_available(tmp_path,monkeypatch):
    monkeypatch.setenv('MODEL_DIR',str(tmp_path));assert not speech.availability()['assets_present']
    with pytest.raises(HTTPException):speech.verify_assets()
    folder=tmp_path/speech.MANIFEST['directory'];folder.mkdir()
    (folder/'config.json').symlink_to(ROOT/'models'/speech.MANIFEST['directory']/'config.json')
    with pytest.raises(HTTPException):speech.verify_assets()

def test_actual_two_bangladesh_clips_have_distinct_supported_transcripts():
    values=[]
    for row in corpus()[:2]:
        result=speech.transcribe(clip(row))
        assert result['supported'] and result['model_inference_performed']
        assert result['checkpoint']==speech.MODEL_ID and result['words']
        assert speech.metrics(row['reference'],result['text'])['wer']<.5
        assert all(0<=w['start_seconds']<=w['end_seconds']<=30 for w in result['words'])
        assert '_evaluation_hypothesis' not in result
        values.append(result['text'])
    assert len(set(values))==2

def test_real_endpoint_does_not_create_voice_asset_or_tool_run(monkeypatch):
    monkeypatch.setenv('ENABLE_EXPERIMENTAL_READING_ASR','1')
    monkeypatch.setenv('MOUCHAK_ENV','test')
    with TestClient(app) as c:
        scope(c)
        with DB() as db:before=(db.scalar(select(func.count()).select_from(Asset)),db.scalar(select(func.count()).select_from(Run)))
        result=post(c,clip(corpus()[0]));assert result.status_code==200,result.text
        out=result.json();assert out['supported'] and out['alignment']
        assert not out['raw_voice_retained'] and not out['transcript_saved'] and '_evaluation_hypothesis' not in out
        with DB() as db:assert before==(db.scalar(select(func.count()).select_from(Asset)),db.scalar(select(func.count()).select_from(Run)))

@pytest.mark.parametrize('overrides',[{'adult_processing_consent':'false'},{'recording_subject':'child'},{'recording_subject':'someone_else'},{'passage_id':'missing-passage'}])
def test_consent_subject_and_passage_refused(monkeypatch,overrides):
    monkeypatch.setenv('ENABLE_EXPERIMENTAL_READING_ASR','1')
    with TestClient(app) as c:
        scope(c);assert post(c,**overrides).status_code==422

def test_csrf_and_local_production_optin(monkeypatch):
    with TestClient(app) as c:
        scope(c);c.headers.pop('x-csrf-token');assert post(c).status_code==403
        scope(c);monkeypatch.delenv('ENABLE_EXPERIMENTAL_READING_ASR',raising=False)
        assert post(c).status_code==503
        monkeypatch.setenv('ENABLE_EXPERIMENTAL_READING_ASR','1');monkeypatch.setenv('MOUCHAK_ENV','production')
        assert not speech.availability()['experimental_enabled'] and post(c).status_code==503

def test_actual_chunked_bytes_bounded_before_multipart_parser():
    called=[];sent=[];messages=iter([{'type':'http.request','body':b'a'*(speech.MAX_BYTES//2),'more_body':True},{'type':'http.request','body':b'a'*(speech.MAX_BYTES//2+65537),'more_body':False}])
    async def inner(*args):called.append(True)
    async def receive():return next(messages)
    async def send(message):sent.append(message)
    asyncio.run(speech.SpeechBodyLimit(inner)({'type':'http','path':'/api/reading/speech/transcribe','method':'POST'},receive,send))
    assert not called and sent[0]['status']==413

def test_worker_busy_refuses_without_inference(monkeypatch):
    monkeypatch.setenv('ENABLE_EXPERIMENTAL_READING_ASR','1')
    with TestClient(app) as c:
        scope(c);assert speech.LOCK.acquire(False)
        try:assert post(c).status_code==429
        finally:speech.LOCK.release()

def test_operator_mfa_policy_revision_and_no_stable_release(admin):
    with TestClient(app) as c:
        scope(c);assert c.get('/api/admin/reading-speech').status_code==403
    overview=admin.request('GET','/api/admin/reading-speech');assert overview.status_code==200
    value=overview.json();assert not value['production_release_allowed'] and not value['private_recordings_listed']
    old=value['policy'];body={'state':'disabled','expected_revision':old['revision'],'reason':'DEMO stop adult experimental speech for evaluation'}
    response=admin.request('POST','/api/admin/reading-speech/policy',json=body);assert response.status_code==200
    assert admin.request('GET','/api/reading/speech/status').json()['operator_disabled']
    assert admin.request('POST','/api/admin/reading-speech/policy',json=body).status_code==409
    assert admin.request('POST','/api/admin/reading-speech/policy',json={**body,'state':'stable'}).status_code==422
    assert admin.request('POST','/api/admin/reading-speech/policy',json={'state':'experimental','expected_revision':response.json()['revision'],'reason':'DEMO restore environment opt in eligibility'}).status_code==200
    with DB.begin() as db:
        s=db.get(Session,digest(admin.client.cookies.get('mouchak_session')));s.mfa_until=0
    assert admin.request('GET','/api/admin/reading-speech').status_code==403

def test_module_disabled_is_respected(monkeypatch):
    monkeypatch.setenv('ENABLE_EXPERIMENTAL_READING_ASR','1')
    with DB.begin() as db:
        original=db.get(Config,'module:banglaread-coach');old=original.value if original else None
        if original:original.value=json.dumps({'enabled':False})
        else:db.add(Config(key='module:banglaread-coach',value=json.dumps({'enabled':False})))
    try:
        with TestClient(app) as c:
            scope(c);assert not c.get('/api/reading/speech/status').json()['experimental_enabled'];assert post(c).status_code==503
    finally:
        with DB.begin() as db:
            c=db.get(Config,'module:banglaread-coach')
            if old is None:db.delete(c)
            else:c.value=old
