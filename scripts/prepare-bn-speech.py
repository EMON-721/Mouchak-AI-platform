"""Prepare a deterministic CC-BY-SA-4.0 Bangladesh Bengali speech benchmark.
No child/guardian, age, dialect or independent pretraining-holdout labels are inferred.
"""
from pathlib import Path
import collections, hashlib, io, json, re, urllib.request, wave, zipfile
ROOT=Path(__file__).resolve().parents[1]
SOURCE={'url':'https://www.openslr.org/resources/37/bn_bd.zip','bytes':586288792,'sha256':'ea2e57ee593ac91e40cd72f91100aa6e1bffbaec465ba1678923ecf1f4efade8','md5':'5f7b0a1de746d2ac3541c12883b3117f'}
LICENSE={'url':'https://www.openslr.org/resources/37/LICENSE.txt','bytes':20133,'sha256':'9348ddfd44da5a127c59141981954746a860ec8e03e0412cf3af7134af0f97e2'}
cache=ROOT/'.state/datasets/openslr37';target=ROOT/'.state/evaluation/reading-speech'
cache.mkdir(parents=True,exist_ok=True);target.mkdir(parents=True,exist_ok=True)
def acquire(name,a):
    p=cache/name
    def valid():return p.is_file() and p.stat().st_size==a['bytes'] and hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==a['sha256']
    if not valid():
        tmp=p.with_suffix(p.suffix+'.partial')
        try:
            with urllib.request.urlopen(a['url'],timeout=120) as remote,tmp.open('wb') as out:
                total=0
                while b:=remote.read(1024*1024):
                    total+=len(b)
                    if total>a['bytes']:raise RuntimeError('Dataset exceeds manifest size')
                    out.write(b)
            if tmp.stat().st_size!=a['bytes'] or hashlib.file_digest(tmp.open('rb'),'sha256').hexdigest()!=a['sha256']:raise RuntimeError('Dataset checksum mismatch')
            tmp.replace(p)
        finally:tmp.unlink(missing_ok=True)
    if a.get('md5') and hashlib.file_digest(p.open('rb'),'md5').hexdigest()!=a['md5']:raise RuntimeError('Publisher MD5 mismatch')
    return p
archive=acquire('bn_bd.zip',SOURCE);license_path=acquire('LICENSE.txt',LICENSE)
groups=collections.defaultdict(list);all_rows=0;excluded=0
with zipfile.ZipFile(archive) as z:
    index=z.read('line_index.tsv')
    if hashlib.sha256(index).hexdigest()!='f8881ada01ac5bb6ef1d97323e2d8f94153d19e1d961c181404de8b36ef2389a':raise RuntimeError('Transcript index mismatch')
    for line in index.decode('utf-8').splitlines():
        if not line.strip():continue
        clip_id,transcript=line.split('\t',1)
        if not re.fullmatch(r'[A-Za-z0-9_]+',clip_id):raise RuntimeError('Unexpected clip identifier')
        all_rows+=1;name='wavs/'+clip_id+'.wav';member=z.getinfo(name)
        if member.file_size>4*1024*1024:excluded+=1;continue
        raw=z.read(name)
        with wave.open(io.BytesIO(raw),'rb') as w:
            secs=w.getnframes()/w.getframerate()
            eligible=w.getsampwidth()==2 and w.getnchannels()==1 and 3<=secs<=8
        if not eligible:excluded+=1;continue
        speaker='_'.join(clip_id.split('_')[:-1])
        groups[speaker].append((clip_id,transcript,secs,raw))
    chosen=[]
    for speaker,rows in sorted(groups.items()):
        for clip_id,transcript,secs,raw in sorted(rows,key=lambda x:hashlib.sha256(x[0].encode()).hexdigest())[:2]:
            sha=hashlib.sha256(raw).hexdigest();filename=sha+'.wav';(target/filename).write_bytes(raw)
            chosen.append({'source_clip_id':clip_id,'speaker_group':speaker,'reference':transcript,'seconds':secs,'file':filename,'sha256':sha,'bytes':len(raw)})
    if all_rows!=1891 or len(groups)!=6 or len(chosen)!=12:raise RuntimeError('Source census or speaker selection changed')
manifest={'schema_version':1,'source':SOURCE,'license':LICENSE,'license_id':'CC-BY-SA-4.0','attribution':'Google 2015–2018; Sodimana et al., SLTU 2018, DOI 10.21437/SLTU.2018-14','source_rows':all_rows,'eligible_rows':sum(map(len,groups.values())),'excluded_duration_or_format_rows':excluded,'speaker_groups':len(groups),'selection':'Before inference: two eligible 3–8 second clips per source speaker prefix, ordered by SHA256(source_clip_id). No reference conditioning.','child_guardian_field_validation':False,'speaker_demographics':'Unknown; no age, region, gender or guardian labels inferred','pretraining_overlap_independently_excluded':False,'rows':chosen}
(target/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');(target/'LICENSE.txt').write_bytes(license_path.read_bytes())
print(json.dumps({k:v for k,v in manifest.items() if k!='rows'},ensure_ascii=False,indent=2))
print('Prepared',len(chosen),'licensed public clips. No production field approval.')
