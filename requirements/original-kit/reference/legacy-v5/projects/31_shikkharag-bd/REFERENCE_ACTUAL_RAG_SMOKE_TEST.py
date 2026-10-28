# ShikkhaRAG BD: minimal genuine semantic model smoke test (NOT the finished site).
# Install: pip install sentence-transformers rank-bm25 numpy
# Internet/model weight download required first run, model license and data rights must be confirmed.
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import numpy as np

MODEL_ID = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
# Original miniature examples owned by project; these are NOT copied NCTB textbook passages.
DOCS = [
 {'id':'own-math-01','class':6,'subject':'গণিত','chapter':'ভগ্নাংশ','text':'ভগ্নাংশের লব উপরে এবং হর নিচে থাকে। দুই ভগ্নাংশের হর সমান হলে লব যোগ করতে হয়।','rights':'original_author_written'},
 {'id':'own-sci-01','class':6,'subject':'বিজ্ঞান','chapter':'পানি','text':'পানি গরম হয়ে বাষ্পে পরিণত হলে তাকে বাষ্পীভবন বলে।','rights':'original_author_written'},
 {'id':'own-bn-01','class':6,'subject':'বাংলা','chapter':'বাক্য','text':'সম্পূর্ণ অর্থ প্রকাশকারী শব্দসমষ্টিকে বাক্য বলা হয়।','rights':'original_author_written'},
]

def search(query, school_class=6, subject=None, top_k=3):
    eligible = [d for d in DOCS if d['class']==school_class and (subject is None or subject==d['subject']) and d['rights']=='original_author_written']
    if not eligible: return []
    model=SentenceTransformer(MODEL_ID) # actual checkpoint loads; failure is not swallowed
    docs=[d['text'] for d in eligible]
    emb=np.array(model.encode([query]+docs,normalize_embeddings=True))
    sem=emb[1:]@emb[0]
    lex=BM25Okapi([x.split() for x in docs]).get_scores(query.split())
    lexical=np.asarray(lex,dtype=float)
    if np.ptp(lexical)>0: lexical=(lexical-lexical.min())/(np.ptp(lexical))
    final=0.75*sem+0.25*lexical
    return [{'source_id':eligible[i]['id'],'score':float(final[i]),'excerpt':docs[i], 'model_id':MODEL_ID} for i in np.argsort(-final)[:top_k]]

if __name__=='__main__':
    for q in ['ভগ্নাংশের হর কী?', 'পানি বাষ্প হওয়ার নাম কী?']:
        r=search(q)
        print(q,r)
    assert search('ভগ্নাংশের লব কী?',subject='গণিত')[0]['source_id']=='own-math-01'
    print('REAL MODEL SMOKE TEST FINISHED; NO WEBSITE/DEPLOYMENT CLAIMED')
