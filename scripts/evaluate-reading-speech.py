"""Measure the fixed public Bangladesh corpus selection; no reference-conditioned decoding."""
from pathlib import Path
import hashlib,json,sys,time,importlib.metadata
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from services.model_worker import reading_speech as speech
folder=ROOT/'.state/evaluation/reading-speech';p=folder/'manifest.json';manifest=json.loads(p.read_text())
rows=[];started=time.perf_counter()
for item in manifest['rows']:
    raw=(folder/item['file']).read_bytes()
    if len(raw)!=item['bytes'] or hashlib.sha256(raw).hexdigest()!=item['sha256']:raise RuntimeError('Evaluation clip checksum mismatch')
    out=speech.transcribe(raw,diagnostic=True)
    # Include refusals in the denominator, using only the actual accepted transcript.
    measured=speech.metrics(item['reference'],out['text'])
    rows.append({**{k:v for k,v in item.items() if k!='file'},'hypothesis':out['text'],'candidate_before_script_gate':out.get('_evaluation_hypothesis',''),'supported':out['supported'],'inference_performed':out['model_inference_performed'],'metrics':measured,'latency_ms':out.get('latency_ms')})
    print(item['source_clip_id'],json.dumps(measured),flush=True)
totals={k:sum(x['metrics'][k] for x in rows) for k in ['word_errors','reference_words','character_errors','reference_characters','grapheme_errors','reference_graphemes']}
totals.update(wer=totals['word_errors']/max(1,totals['reference_words']),cer=totals['character_errors']/max(1,totals['reference_characters']),grapheme_error_rate=totals['grapheme_errors']/max(1,totals['reference_graphemes']))
report={'schema_version':1,'checkpoint':speech.MODEL_ID,'model_assets':speech.MANIFEST['assets'],'evaluation_manifest_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':manifest['source'],'license_id':manifest['license_id'],'attribution':manifest['attribution'],'selection':manifest['selection'],'source_rows':manifest['source_rows'],'speaker_groups':manifest['speaker_groups'],'clips':len(rows),'accepted_clips':sum(x['supported'] for x in rows),'decode':speech.DECODE,'runtime_versions':{x:importlib.metadata.version(x) for x in ['faster-whisper','ctranslate2','av','regex']},'elapsed_seconds':round(time.perf_counter()-started,2),'aggregate':totals,'production_release_approved':False,'child_field_validation_approved':False,'limitations':['Only twelve short public bn-BD read-speech recordings from six source speaker groups; not representative child/guardian field validation.','Age, gender, region and verified guardian labels are unknown.','Pretraining overlap has not been independently excluded; no independent holdout or child pronunciation accuracy claim.','The model can hallucinate, repeat or substitute words; no clinical or pronunciation score.','WER/CER are not child ability measures. Standard uncertainty gates are applied without reference conditioning.'],'rows':rows}
(ROOT/'docs/audit/reading-speech-evaluation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'aggregate':totals,'elapsed_seconds':report['elapsed_seconds']},indent=2))
