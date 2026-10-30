"""Real pinned YAMNet CPU inference. Owned synthetic audio is not a BD holdout."""
import io,json,wave
import numpy as np
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from services.model_worker.main import app
from services.model_worker import noise_runtime as noise
from services.model_worker.store import DB,Run,Config,open_sealed
from services.model_worker.domain import InputError

def recording(mode='sine',rate=16000,channels=1,seconds=1.5):
    t=np.arange(int(rate*seconds))/rate
    if mode=='sine':audio=np.sin(2*np.pi*440*t)*.2
    elif mode=='noise':audio=np.random.default_rng(53).normal(0,.12,len(t))
    elif mode=='clipped':audio=np.ones(len(t))
    else:audio=np.zeros(len(t))
    data=(np.clip(audio,-1,1)*32767).astype('<i2')
    if channels==2:data=np.column_stack([data,data]).ravel()
    out=io.BytesIO()
    with wave.open(out,'wb') as w:w.setparams((channels,2,rate,0,'NONE',''));w.writeframes(data.tobytes())
    return out.getvalue()

def scope(c):
    r=c.post('/api/session');assert r.status_code==200
    c.headers['x-csrf-token']=r.json()['csrf'];return r.json()['visitor_id']
def upload(c,data):
    r=c.post('/api/upload',files={'file':('owned.wav',data,'audio/wav')},data={'consent':'true'});assert r.status_code==201,r.status_code;return r.json()['id']

def test_actual_two_distinct_yamnet_outputs_and_provenance():
    a=noise.classify(recording('sine'));b=noise.classify(recording('noise'))
    assert a['facts']['supported'] and b['facts']['supported']
    assert a['facts']['event_tags']!=b['facts']['event_tags']
    assert a['facts']['event_tags'][0]['label_en']=='Sine wave'
    assert a['model_version'].startswith('google/yamnet/classification-tflite/1@10c95e')
    scores=[x['uncalibrated_mean_score'] for x in a['facts']['event_tags']]
    assert scores==sorted(scores,reverse=True) and all(0<=x<=1 for x in scores)
    assert a['details']['inference_windows']>=2 and len(a['details']['waveform_rms'])==80
    assert a['facts']['calibrated_decibels_available'] is False
    assert a['facts']['voice_identity_inferred'] is False and a['full_module_complete'] is False
    assert a['details']['bangladesh_holdout_evaluated'] is False
    assert a['references'][0]['license']=='Apache-2.0'

@pytest.mark.parametrize('mode',['silence','clipped'])
def test_bad_signal_abstains_despite_real_inference(mode):
    r=noise.classify(recording(mode));assert not r['facts']['supported'];assert r['facts']['event_tags']==[]
    assert r['details']['inference_windows']>=2 and r['details']['timeline']==[]

@pytest.mark.parametrize('data',[b'not a wav',recording(seconds=.2),recording(rate=4000),recording()[:-50]])
def test_invalid_short_low_rate_or_truncated_recording_refused(data):
    with pytest.raises(InputError):noise.classify(data)

def test_stereo_resampling_and_finite_features():
    r=noise.classify(recording(rate=22050,channels=2));assert r['facts']['signal']['resampled_rate']==16000
    assert r['facts']['signal']['original_channels']==2

def test_missing_or_tampered_model_never_fakes_results(tmp_path,monkeypatch):
    monkeypatch.setenv('MODEL_DIR',str(tmp_path))
    with pytest.raises(HTTPException) as error:noise.classify(recording())
    assert error.value.status_code==503
    (tmp_path/'yamnet').mkdir();(tmp_path/'yamnet/classification.tflite').write_bytes(b'not a model')
    with pytest.raises(HTTPException):noise.classify(recording())

def test_actual_endpoint_private_encrypted_and_production_gate(monkeypatch):
    monkeypatch.setenv('ENABLE_EXPERIMENTAL_NOISE','1');monkeypatch.setenv('MOUCHAK_ENV','test')
    with TestClient(app) as owner,TestClient(app) as other:
        scope(owner);scope(other);aid=upload(owner,recording())
        body={'inputs':{'analysis_mode':'events'},'asset_ids':[aid],'consent':True}
        wrong=other.post('/api/tools/noisetrace-ai/runs',json=body);assert wrong.status_code==404
        response=owner.post('/api/tools/noisetrace-ai/runs',json=body);assert response.status_code==201,response.status_code
        value=response.json();assert value['facts']['event_tags'] and value['model_version'].startswith(noise.MODEL_ID)
        assert other.get('/api/runs/'+value['id']).status_code==404
        with DB() as db:
            run=db.get(Run,value['id']);assert run.encrypted.startswith('gAAAA');assert open_sealed(run.encrypted)['output']['facts']['event_tags']
        monkeypatch.setenv('MOUCHAK_ENV','production')
        assert not noise.availability()['experimental_enabled']
        assert owner.post('/api/tools/noisetrace-ai/runs',json=body).status_code==503

def test_processing_consent_and_optin_required(monkeypatch):
    monkeypatch.delenv('ENABLE_EXPERIMENTAL_NOISE',raising=False)
    with TestClient(app) as c:
        scope(c);aid=upload(c,recording())
        assert c.post('/api/tools/noisetrace-ai/runs',json={'inputs':{'analysis_mode':'events'},'asset_ids':[aid],'consent':True}).status_code==503
        assert c.post('/api/tools/noisetrace-ai/runs',json={'inputs':{'analysis_mode':'events'},'asset_ids':[aid],'consent':False}).status_code==422
        signal=c.post('/api/tools/noisetrace-ai/runs',json={'inputs':{'analysis_mode':'signal'},'asset_ids':[aid],'consent':True})
        assert signal.status_code==201 and signal.json()['facts']['sound_class_inferred'] is False

def test_model_operator_policy_revision_and_permission(admin):
    assert admin.request('GET','/api/admin/model-operations').status_code==200
    with TestClient(app) as stranger:
        scope(stranger);assert stranger.get('/api/admin/model-operations').status_code==403
    before=admin.request('GET','/api/admin/model-operations').json()['policy']
    body={'state':'disabled','expected_revision':before['revision'],'reason':'DEMO temporary model pause for review'}
    result=admin.request('POST','/api/admin/model-operations/noise-policy',json=body);assert result.status_code==200
    assert result.json()['production_release_allowed'] is False
    assert admin.request('POST','/api/admin/model-operations/noise-policy',json=body).status_code==409
    assert admin.request('POST','/api/admin/model-operations/noise-policy',json={**body,'state':'stable'}).status_code==422
    restore=admin.request('POST','/api/admin/model-operations/noise-policy',json={'state':'experimental','expected_revision':result.json()['revision'],'reason':'DEMO restore local opt in gate only'})
    assert restore.status_code==200


def test_actual_noise_inference_through_durable_worker(monkeypatch):
    from services.model_worker import inference_queue as queue
    monkeypatch.setenv('ENABLE_EXPERIMENTAL_NOISE','1');monkeypatch.setenv('MOUCHAK_ENV','test');monkeypatch.setenv('ENABLE_DURABLE_INFERENCE','1')
    with TestClient(app) as c:
        scope(c);aid=upload(c,recording())
        response=c.post('/api/tools/noisetrace-ai/jobs',json={'inputs':{'analysis_mode':'events'},'asset_ids':[aid],'consent':True,'idempotency_key':'owned-yamnet-queued-fixture'})
        assert response.status_code==202
        claimed=queue.claim();assert claimed['id']==response.json()['id']
        assert queue.publish_claim(claimed)
        done=c.get('/api/jobs/'+response.json()['id']).json();assert done['state']=='succeeded'
        output=c.get('/api/runs/'+done['run_id']).json()['output'];assert output['model_version'].startswith(noise.MODEL_ID) and output['facts']['event_tags']
