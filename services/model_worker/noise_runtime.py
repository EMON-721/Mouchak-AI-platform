"""Actual CPU YAMNet inference, bounded private PCM processing, no dB/identity claims."""
import csv, hashlib, importlib.util, io, json, math, os, threading, time, wave
from functools import lru_cache
from pathlib import Path
import numpy as np
from fastapi import HTTPException
from .domain import InputError, result

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=json.loads((ROOT/'docs/audit/noise-assets.json').read_text())
MODEL_ID=MANIFEST['model_id']
FRAME=15600
RATE=16000
HOP=7680
BN_LABELS={'Speech':'কথার শব্দ','Music':'সংগীত','Silence':'নীরবতা','Vehicle':'যানবাহন','Car':'গাড়ি','Traffic noise, roadway noise':'সড়কের যানবাহনের শব্দ','Car passing by':'পাশ দিয়ে যাওয়া গাড়ি','Vehicle horn, car horn, honking':'যানবাহনের হর্ন','Rain':'বৃষ্টি','Water':'পানি','Wind':'বাতাস','Dog':'কুকুর','Bark':'ঘেউ ঘেউ','Bird':'পাখি','Siren':'সাইরেন','Engine':'ইঞ্জিন','Motorcycle':'মোটরসাইকেল','Truck':'ট্রাক','Train':'ট্রেন','Aircraft':'উড়োজাহাজ','Construction':'নির্মাণকাজ','Hammer':'হাতুড়ি','Whistling':'শিস'}

def model_dir(): return Path(os.getenv('MODEL_DIR',ROOT/'models'))/'yamnet'

def verify_assets():
    folder=model_dir()
    for name,asset in MANIFEST['assets'].items():
        p=folder/name
        if not p.is_file() or p.stat().st_size!=asset['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=asset['sha256']:
            raise HTTPException(503,'Noise model missing or checksum mismatch / শব্দের মডেল নেই বা checksum মেলেনি')
    return folder

def availability():
    try: verify_assets(); verified=True
    except HTTPException: verified=False
    runtime=importlib.util.find_spec('ai_edge_litert') is not None
    return {'checkpoint':MODEL_ID,'weights_verified':verified,'runtime_available':runtime,'interpreter_loaded_in_this_process':globals().get('runtime') is not None and globals()['runtime'].cache_info().currsize>0,'classes':521,'license':'Apache-2.0','experimental_enabled':verified and runtime and os.getenv('ENABLE_EXPERIMENTAL_NOISE')=='1' and os.getenv('MOUCHAK_ENV')!='production','production_enabled':False,'evaluated_for_production':False,'bangladesh_holdout_rows':0,'reason':'Bangladesh annotated sound-event holdout and privacy/abstention review are not approved'}

class Runtime:
    def __init__(self):
        folder=verify_assets()
        try: from ai_edge_litert.interpreter import Interpreter
        except ImportError: raise HTTPException(503,'Noise CPU runtime unavailable / শব্দ বিশ্লেষণের runtime নেই')
        with (folder/'class_map.csv').open(newline='') as f: self.labels=list(csv.DictReader(f))
        if len(self.labels)!=521 or any(int(x['index'])!=i for i,x in enumerate(self.labels)): raise HTTPException(503,'Noise taxonomy mismatch')
        self.interpreter=Interpreter(model_path=str(folder/'classification.tflite'),num_threads=2)
        self.interpreter.allocate_tensors()
        inp=self.interpreter.get_input_details();out=self.interpreter.get_output_details()
        if len(inp)!=1 or inp[0]['shape'].tolist()!=[FRAME] or inp[0]['dtype']!=np.float32 or len(out)!=1 or out[0]['shape'].tolist()!=[1,521]: raise HTTPException(503,'Unsupported noise model signature')
        self.input=inp[0]['index']; self.output=out[0]['index'];self.lock=threading.Lock()
    def score(self,frame):
        with self.lock:
            self.interpreter.set_tensor(self.input,np.asarray(frame,np.float32))
            self.interpreter.invoke()
            values=self.interpreter.get_tensor(self.output)[0].copy()
        if values.shape!=(521,) or not np.isfinite(values).all() or np.any(values<0) or np.any(values>1): raise HTTPException(503,'Invalid noise model output')
        return values

@lru_cache(maxsize=1)
def runtime(): return Runtime()

def read_wav(data):
    if not isinstance(data,bytes) or len(data)>10*1024*1024: raise InputError('PCM WAV exceeds 10 MiB / WAV ফাইল বেশি বড়')
    try:
        with wave.open(io.BytesIO(data),'rb') as source:
            channels,rate,width,frames=source.getnchannels(),source.getframerate(),source.getsampwidth(),source.getnframes()
            if channels not in [1,2] or width!=2 or not 8000<=rate<=96000 or not .975<=frames/rate<=60: raise InputError('Use 16-bit mono/stereo PCM WAV, 0.975–60 seconds, 8–96 kHz / সঠিক মাপের PCM WAV দিন')
            raw=source.readframes(frames)
            if len(raw)!=frames*channels*width: raise InputError('Truncated audio / অডিও অসম্পূর্ণ')
    except (wave.Error,EOFError,ZeroDivisionError): raise InputError('Unreadable PCM WAV / WAV পড়া যায়নি')
    audio=np.frombuffer(raw,dtype='<i2').astype(np.float32).reshape(-1,channels).mean(axis=1)/32768
    if rate!=RATE:
        from scipy.signal import resample_poly
        divisor=math.gcd(rate,RATE);audio=resample_poly(audio,RATE//divisor,rate//divisor).astype(np.float32)
    return np.clip(audio,-1,1),{'original_sample_rate':rate,'original_channels':channels,'seconds':round(frames/rate,4),'resampled_rate':RATE}

def classify(data):
    verify_assets()  # Recheck files even when a verified interpreter is cached.
    started=time.perf_counter();audio,signal=read_wav(data);model=runtime()
    starts=list(range(0,len(audio)-FRAME+1,HOP))
    if not starts: raise InputError('Recording is shorter than one model window')
    if starts[-1]+FRAME<len(audio): starts.append(len(audio)-FRAME)
    scores=[];timeline=[]
    for offset in starts:
        values=model.score(audio[offset:offset+FRAME]);scores.append(values)
        top=int(np.argmax(values));label=model.labels[top]['display_name']
        timeline.append({'start_seconds':round(offset/RATE,4),'end_seconds':round((offset+FRAME)/RATE,4),'class_id':model.labels[top]['mid'],'label_en':label,'label_bn':BN_LABELS.get(label,label),'uncalibrated_score':round(float(values[top]),6)})
    mean=np.asarray(scores).mean(axis=0);order=np.argsort(mean)[::-1][:5]
    rms=float(np.sqrt(np.mean(audio.astype(np.float64)**2)))
    clipped=float(np.mean(np.abs(audio)>=.999))
    accepted=rms>=.0001 and clipped<=.25 and float(mean[order[0]])>=.08
    tags=[{'class_id':model.labels[int(i)]['mid'],'label_en':model.labels[int(i)]['display_name'],'label_bn':BN_LABELS.get(model.labels[int(i)]['display_name'],model.labels[int(i)]['display_name']),'uncalibrated_mean_score':round(float(mean[i]),6)} for i in order] if accepted else []
    waveform=[round(float(np.sqrt(np.mean(chunk.astype(np.float64)**2))),6) for chunk in np.array_split(audio,80)]
    output=result('Experimental YAMNet audio-event inference / পরীক্ষামূলক শব্দের ধরন বিশ্লেষণ',{'supported':accepted,'signal':{**signal,'rms_amplitude':round(rms,6),'clipped_fraction':round(clipped,6)},'event_tags':tags,'sound_class_inferred':accepted,'calibrated_decibels_available':False,'voice_identity_inferred':False},detail={'timeline':timeline if accepted else [],'waveform_rms':waveform,'inference_windows':len(starts),'taxonomy_classes':521,'original_taxonomy_language':'en','bangladesh_holdout_evaluated':False},warnings=['Experimental general AudioSet tags can be wrong in Bangladesh; review the recording. / সাধারণ মডেলটি বাংলাদেশে ভুল করতে পারে; নিজে যাচাই করুন।','Scores are not calibrated probabilities, legal dB measurements or proof of a person/activity. / স্কোর নিশ্চিত সম্ভাবনা, আইনি dB বা ব্যক্তির পরিচয়ের প্রমাণ নয়।']+([] if accepted else ['Insufficient or low-quality evidence; no event label accepted. / প্রমাণ যথেষ্ট নয়; শব্দের ধরন দেওয়া হয়নি।']))
    output['references']=[{'title':'Official YAMNet model card','url':MANIFEST['model_card_url'],'license':'Apache-2.0','kind':'model_provenance_not_recording_ground_truth'}]
    output.update(model_version=MODEL_ID+'@'+MANIFEST['assets']['classification.tflite']['sha256'],source_kind='owner_uploaded_audio',latency_ms=round((time.perf_counter()-started)*1000,2),full_module_complete=False)
    return output
