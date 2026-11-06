"""Versioned original lessons with independent editorial approval.

The preserved seed kit is read-only and never implicitly licensed or published.
Only reviewed, currently authorized content is exposed; learner attempts use the
existing private encrypted Run/queue path, not this administrative catalogue.
"""
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select, text
from sqlalchemy.orm import load_only
from .auth import authorize, audit, db_session
from .store import Config, User, now, uid
from .domain import result

ROOT = Path(__file__).resolve().parents[2]
SEED_ROOT = ROOT / 'requirements/original-kit/reference/legacy-v5/projects/32_banglaread-coach/ORIGINAL_SUPPORTING_FILES/data/seed'
SEED_FILES = ['original_passages.json', 'original_comprehension_questions.json']
SEED_HASHES = {name: hashlib.sha256((SEED_ROOT/name).read_bytes()).hexdigest() for name in SEED_FILES}
SEEDS = {p['passage_id']: p for p in json.loads((SEED_ROOT/SEED_FILES[0]).read_text())}
QUESTIONS = {q['passage_id']: q for q in json.loads((SEED_ROOT/SEED_FILES[1]).read_text())}
PREFIX = 'reading-content:'
ROLES = {'content_editor', 'super_admin'}
router = APIRouter(prefix='/api/admin/reading-content')

class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class Copy(Strict):
    bn: str = Field(min_length=1, max_length=600)
    en: str = Field(min_length=1, max_length=600)

class Lesson(Strict):
    lesson_id: str = Field(pattern=r'^(BRP[0-9]{3}|OWN-[A-Za-z0-9-]{1,40})$')
    source_seed_id: str | None = None
    title: Copy
    passage: str = Field(min_length=10, max_length=4000)
    level: int = Field(strict=True, ge=1, le=5)
    topic: Copy
    age_band: Literal['general', 'new_reader', 'child_or_new_reader']
    educational_goal: Copy
    question: Copy
    options: list[Copy] = Field(min_length=2, max_length=6)
    correct_option_index: int = Field(strict=True, ge=0)
    explanation: Copy
    publisher: str = Field(min_length=2, max_length=160)
    license: Literal['CC0-1.0', 'CC-BY-4.0', 'CC-BY-SA-4.0', 'permission_granted']
    rights_note: str = Field(min_length=10, max_length=2000)

    @model_validator(mode='after')
    def safe(self):
        if max(len(self.title.bn), len(self.title.en)) > 160 or len(self.passage.split()) > 250:
            raise ValueError('Use a short title and at most 250 passage words')
        if self.correct_option_index >= len(self.options):
            raise ValueError('Correct option is outside the option list')
        for lang in ('bn', 'en'):
            options = [unicodedata.normalize('NFC', getattr(o, lang)).casefold() for o in self.options]
            if len(set(options)) != len(options): raise ValueError('Options must be distinct in each language')
        if self.lesson_id.startswith('BRP') and self.source_seed_id != self.lesson_id:
            raise ValueError('Preserve the source seed identity')
        if self.source_seed_id and self.source_seed_id not in SEEDS:
            raise ValueError('Unknown seed')
        if re.search(r'[<>]|javascript:', json.dumps(self.model_dump(), ensure_ascii=False), re.I):
            raise ValueError('Plain text content required')
        return self

class Revision(Strict):
    expected_revision: str | None = Field(default=None, max_length=100)

class Draft(Revision):
    lesson: Lesson

class Checks(Strict):
    spelling: bool = Field(strict=True)
    age_suitability: bool = Field(strict=True)
    answer_grounded_in_passage: bool = Field(strict=True)
    educational_goal: bool = Field(strict=True)
    publication_rights: bool = Field(strict=True)

class Review(Strict):
    decision: Literal['approved', 'rejected']
    checks: Checks
    reason: str = Field(min_length=10, max_length=1000)

class Publish(Revision):
    rollback: bool = Field(default=False, strict=True)
    reason: str = Field(min_length=10, max_length=1000)

class Withdraw(Revision):
    lesson_id: str = Field(max_length=80)
    reason: str = Field(min_length=10, max_length=1000)

class Order(Revision):
    lesson_ids: list[str] = Field(max_length=240)


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def get(db, key, default=None):
    row = db.get(Config, PREFIX+key)
    if not row: return default
    try: return json.loads(row.value)
    except (ValueError, TypeError): raise HTTPException(503, 'Reading content configuration needs operator repair / পাঠাগারের সেটিংস যাচাই প্রয়োজন')


def put(db, key, value):
    row = db.get(Config, PREFIX+key)
    encoded = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
    if row: row.value = encoded
    else: db.add(Config(key=PREFIX+key, value=encoded))


def state(db):
    s = get(db, 'active', {'revision': None, 'lessons': {}})
    if not isinstance(s, dict) or not isinstance(s.get('lessons'), dict) or len(s['lessons']) > 240:
        raise HTTPException(503, 'Reading content configuration needs operator repair')
    return s


def lock(db):
    if db.bind.dialect.name == 'postgresql': db.execute(text('SELECT pg_advisory_xact_lock(742011)'))


def current(db, expected):
    lock(db)
    s = state(db)
    if s['revision'] != expected: raise HTTPException(409, 'Library changed; reload / পাঠাগার বদলেছে, আবার খুলুন')
    return s


def draft_record(db, vid):
    value = get(db, 'draft:'+vid)
    if not value: raise HTTPException(404, 'Lesson version not found')
    return value


def commit_state(db, s, actor, action, detail):
    s['revision'] = uid()
    put(db, 'active', s)
    put(db, 'history:'+s['revision'], {**s, 'action': action, 'actor': actor, 'created_at': now(), 'detail': detail})
    # Reasons/rights evidence stay in the restricted history, not general audit text.
    audit(db, actor, 'reading_'+action, s['revision'], {'lesson_id': detail.get('lesson_id')})
    return {'revision': s['revision'], 'published': action in {'publish', 'rollback'}}


def approved(db, d, review=None, actors=None, check_mfa=False):
    lesson = Lesson.model_validate(d['lesson']).model_dump()
    review = review if review is not None else get(db, 'review:'+d['id'], {})
    r = Review.model_validate({k: review[k] for k in ('decision', 'checks', 'reason')})
    if (r.decision != 'approved' or not all(r.checks.model_dump().values())
        or review.get('body_hash') != fingerprint(lesson) or d.get('body_hash') != fingerprint(lesson)
        or d['author'] == review.get('reviewer')):
        raise ValueError('Independent approval of the exact content is required')
    if actors is None:
        columns = [User.id, User.role, User.banned] + ([User.mfa_enabled] if check_mfa else [])
        actors = {u.id: u for u in db.scalars(select(User).options(load_only(*columns)).where(User.id.in_([d['author'], review.get('reviewer')])))}
    for aid in [d['author'], review.get('reviewer')]:
        actor = actors.get(aid)
        if not actor or actor.role not in ROLES or actor.banned or (check_mfa and not actor.mfa_enabled):
            raise ValueError('Author or reviewer is no longer authorized')
    return lesson


def active_lessons(db):
    """Bounded batch queries; no answer keys or private actor columns returned."""
    s = state(db)
    keys = [PREFIX+k+v['version'] for v in s['lessons'].values() for k in ('draft:', 'review:') if isinstance(v, dict) and isinstance(v.get('version'), str)]
    records = {}
    for c in db.scalars(select(Config).where(Config.key.in_(keys))):
        try: records[c.key] = json.loads(c.value)
        except (ValueError, TypeError): continue  # corrupt individual content fails closed
    ids = set()
    for row in records.values():
        if isinstance(row, dict): ids.update(x for x in (row.get('author'), row.get('reviewer')) if isinstance(x, str))
    actors = {u.id: u for u in db.scalars(select(User).options(load_only(User.id, User.role, User.banned)).where(User.id.in_(ids)))}
    rows = []
    for lid, slot in s['lessons'].items():
        try:
            vid = slot['version']
            d, r = records[PREFIX+'draft:'+vid], records[PREFIX+'review:'+vid]
            lesson = approved(db, d, r, actors)
            if d['id'] != vid or lesson['lesson_id'] != lid: continue
            rows.append((slot['order'], d, lesson))
        except (ValueError, TypeError, KeyError, HTTPException): continue
    return sorted(rows, key=lambda x: (x[2]['level'], x[0], x[2]['lesson_id']))


def public_lessons(db):
    return [{'id': 'lesson:'+p['lesson_id'], 'revision': d['id'], 'title': p['title']['bn'],
             'title_en': p['title']['en'], 'text': p['passage'], 'level': p['level'], 'topic': p['topic'],
             'educational_goal': p['educational_goal'], 'question': p['question']['bn'], 'question_en': p['question']['en'],
             'options': p['options'], 'publisher': p['publisher'], 'license': p['license'],
             'created_at': d['created_at'], 'quality': 'independently_reviewed_original'}
            for _, d, p in active_lessons(db)]


@router.get('')
def overview(u=Depends(authorize('cms')), db=Depends(db_session, scope='function')):
    versions = []
    for c in db.scalars(select(Config).where(Config.key.like(PREFIX+'draft:%')).order_by(Config.key).limit(501)):
        try:
            d = json.loads(c.value)
            review = get(db, 'review:'+d['id'])
            versions.append({'id': d['id'], 'lesson_id': d['lesson']['lesson_id'], 'title': d['lesson']['title'],
                             'author': d['author'], 'created_at': d['created_at'], 'status': review['decision'] if review else 'draft'})
        except (ValueError, KeyError, TypeError): continue
    return {'state': state(db), 'versions': sorted(versions, key=lambda d: (d['created_at'], d['id']), reverse=True),
            'seeds': [{'id': p['passage_id'], 'title': p['title'], 'approved': False} for p in SEEDS.values()],
            'seed_hashes': SEED_HASHES, 'published': public_lessons(db)}


@router.get('/seeds/{seed_id}')
def seed(seed_id: str, u=Depends(authorize('cms'))):
    if seed_id not in SEEDS: raise HTTPException(404)
    return {'passage': SEEDS[seed_id], 'question': QUESTIONS[seed_id], 'seed_hashes': SEED_HASHES, 'published': False}


@router.post('/drafts', status_code=201)
def create(p: Draft, u=Depends(authorize('cms')), db=Depends(db_session, scope='function')):
    s = current(db, p.expected_revision)
    if len(list(db.scalars(select(Config.key).where(Config.key.like(PREFIX+'draft:%')).limit(500)))) >= 500:
        raise HTTPException(409, 'Library version capacity reached; retain reviewed history and plan an audited migration')
    lesson = p.lesson.model_dump()
    d = {'id': uid(), 'lesson': lesson, 'body_hash': fingerprint(lesson), 'author': u.id, 'created_at': now(),
         'base_revision': s['revision'], 'provenance': {'source_seed_id': p.lesson.source_seed_id, 'seed_hashes': SEED_HASHES if p.lesson.source_seed_id else {}, 'original_copyright': SEEDS[p.lesson.source_seed_id].get('copyright') if p.lesson.source_seed_id else None}}
    put(db, 'draft:'+d['id'], d)
    audit(db, u.id, 'reading_draft', d['id'])
    return {'id': d['id'], 'status': 'draft'}


@router.get('/drafts/{vid}')
def detail(vid: str, u=Depends(authorize('cms')), db=Depends(db_session, scope='function')):
    return {**draft_record(db, vid), 'review': get(db, 'review:'+vid), 'previously_published': bool(get(db, 'published:'+vid))}


@router.post('/drafts/{vid}/review')
def review(vid: str, p: Review, u=Depends(authorize('cms')), db=Depends(db_session, scope='function')):
    lock(db); d = draft_record(db, vid)
    if d['author'] == u.id: raise HTTPException(403, 'A different editor must review / অন্য সম্পাদককে পর্যালোচনা করতে হবে')
    if get(db, 'review:'+vid): raise HTTPException(409, 'Review is immutable; create a new draft')
    if p.decision == 'approved' and not all(p.checks.model_dump().values()):
        raise HTTPException(422, 'All five editorial checks are required')
    lesson = Lesson.model_validate(d['lesson']).model_dump()
    if fingerprint(lesson) != d['body_hash']: raise HTTPException(409, 'Draft content changed')
    put(db, 'review:'+vid, {**p.model_dump(), 'reviewer': u.id, 'body_hash': d['body_hash'], 'reviewed_at': now()})
    audit(db, u.id, 'reading_review_'+p.decision, vid)
    return {'id': vid, 'status': p.decision}


@router.post('/drafts/{vid}/publish')
def publish(vid: str, p: Publish, u=Depends(authorize('cms')), db=Depends(db_session, scope='function')):
    s = current(db, p.expected_revision); d = draft_record(db, vid)
    try: lesson = approved(db, d, check_mfa=True)
    except (ValueError, TypeError, KeyError): raise HTTPException(409, 'Independent current approval required / বর্তমান স্বাধীন অনুমোদন প্রয়োজন')
    if p.rollback:
        if not get(db, 'published:'+vid): raise HTTPException(409, 'Rollback requires a previously published version')
    elif d['base_revision'] != s['revision']:
        raise HTTPException(409, 'Draft base is stale; create and review a fresh draft')
    lid = lesson['lesson_id']
    if lid not in s['lessons'] and len(s['lessons']) >= 240: raise HTTPException(409, 'Active lesson capacity reached')
    order = s['lessons'].get(lid, {}).get('order', max((v['order'] for v in s['lessons'].values()), default=-1)+1)
    s['lessons'][lid] = {'version': vid, 'order': order}
    if not get(db, 'published:'+vid): put(db, 'published:'+vid, {'first_published_at': now(), 'lesson_id': lid})
    return commit_state(db, s, u.id, 'rollback' if p.rollback else 'publish', {'lesson_id': lid, 'version': vid, 'reason': p.reason})


@router.post('/withdraw')
def withdraw(p: Withdraw, u=Depends(authorize('cms')), db=Depends(db_session, scope='function')):
    s = current(db, p.expected_revision)
    if p.lesson_id not in s['lessons']: raise HTTPException(404)
    del s['lessons'][p.lesson_id]
    return commit_state(db, s, u.id, 'withdraw', {'lesson_id': p.lesson_id, 'reason': p.reason})


@router.post('/order')
def reorder(p: Order, u=Depends(authorize('cms')), db=Depends(db_session, scope='function')):
    s = current(db, p.expected_revision)
    if len(set(p.lesson_ids)) != len(p.lesson_ids) or set(p.lesson_ids) != set(s['lessons']):
        raise HTTPException(422, 'Supply every active lesson exactly once')
    for index, lid in enumerate(p.lesson_ids): s['lessons'][lid]['order'] = index
    return commit_state(db, s, u.id, 'reorder', {'lesson_ids': p.lesson_ids})


def exercise(db, inputs):
    # Hold a shared publication fence through encrypted Run commit. An editor's
    # withdrawal/publish cannot race an already executing lesson into a newer
    # revision; queued attempts resolve content only after claiming the job.
    if db.bind.dialect.name == 'postgresql': db.execute(text('SELECT pg_advisory_xact_lock_shared(742011)'))
    match = next(((d, p) for _, d, p in active_lessons(db) if 'lesson:'+p['lesson_id'] == inputs.get('passage_id')), None)
    if not match: raise HTTPException(404, 'This lesson is unavailable / এই পাঠ পাওয়া যাচ্ছে না')
    d, p = match
    if inputs.get('passage_revision') != d['id']: raise HTTPException(409, 'Lesson changed; reload before practice / পাঠ বদলেছে, আবার খুলুন')
    words = unicodedata.normalize('NFC', p['passage']).split()
    indices = inputs.get('difficult_indices', [])
    if (not isinstance(indices, list) or len(indices) > len(words)
        or any(type(i) is not int or not 0 <= i < len(words) for i in indices)):
        raise HTTPException(422, 'Invalid selected word positions')
    answer = inputs.get('answer_choice')
    if answer is not None and (type(answer) is not int or not 0 <= answer < len(p['options'])):
        raise HTTPException(422, 'Choose an available answer')
    assessment = 'skipped' if answer is None else 'matched' if answer == p['correct_option_index'] else 'review'
    details = {'question': p['question'], 'selected_option': answer, 'passage': p['passage']}
    if answer is not None: details.update({'correct_option': p['correct_option_index'], 'explanation': p['explanation']})
    output = result('Reviewed reading comprehension / পর্যালোচিত পাঠের অনুশীলন',
                    {'passage_id': inputs['passage_id'], 'passage_revision': d['id'], 'total_words': len(words),
                     'self_marked_difficult_words': list(dict.fromkeys(words[i] for i in sorted(set(indices)))),
                     'comprehension': assessment}, details,
                    ['Self-reported practice and literal quiz, not an AI pronunciation or clinical assessment. / নিজের অনুশীলন ও প্রশ্নের উত্তর; উচ্চারণের AI নম্বর নয়।'])
    output['references'] = [{'id': p['lesson_id'], 'revision': d['id'], 'title': p['title']['bn'], 'publisher': p['publisher'], 'license': p['license'], 'kind': 'reviewed_original_lesson', 'official': False, 'source_date': d['created_at']}]
    return output
