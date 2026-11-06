"""Disposable original-text fixtures; no production content approvals or AI claims."""
import hashlib
import json
import subprocess
import sys
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from conftest import Client
from services.model_worker.main import app
from services.model_worker import reading_content as content, inference_queue as queue
from services.model_worker.store import DB, Config, Run, User, Session, open_sealed

BASE = '/api/admin/reading-content'
REASON = 'DEMO disposable original text checked for this test only'
CHECKS = {k: True for k in content.Checks.model_fields}


def sample(lid='OWN-test'):
    return {'lesson_id': lid, 'source_seed_id': None, 'title': {'bn': 'গাছের যত্ন', 'en': 'Caring for a tree'},
            'passage': 'মিনা সকালে গাছে পানি দেয়। গাছের নিচে একটি পাখি বসে আছে।', 'level': 1,
            'topic': {'bn': 'প্রকৃতি', 'en': 'Nature'}, 'age_band': 'new_reader',
            'educational_goal': {'bn': 'পাঠের তথ্য চিহ্নিত করা', 'en': 'Find a fact in the passage'},
            'question': {'bn': 'মিনা কখন পানি দেয়?', 'en': 'When does Mina water the tree?'},
            'options': [{'bn': 'রাতে', 'en': 'At night'}, {'bn': 'সকালে', 'en': 'In the morning'}],
            'correct_option_index': 1, 'explanation': {'bn': 'পাঠে সকালে পানি দেওয়ার কথা আছে।', 'en': 'The passage states that she waters it in the morning.'},
            'publisher': 'DEMO test author', 'license': 'permission_granted', 'rights_note': REASON}


@pytest.fixture(autouse=True)
def isolated_library():
    # Restore only our namespace so preserved legacy tests retain their 12 texts.
    with DB.begin() as db:
        rows = [(c.key, c.value) for c in db.scalars(select(Config).where(Config.key.like(content.PREFIX+'%')))]
        db.execute(delete(Config).where(Config.key.like(content.PREFIX+'%')))
    yield
    with DB.begin() as db:
        db.execute(delete(Config).where(Config.key.like(content.PREFIX+'%')))
        for key, value in rows: db.add(Config(key=key, value=value))


@pytest.fixture
def admin():
    with TestClient(app) as raw: yield Client(raw).register("DEMO lesson author").admin()


@pytest.fixture
def reviewer():
    with TestClient(app) as raw: yield Client(raw).register('DEMO second editor').admin('content_editor')


def revision(c): return c.request('GET', BASE).json()['state']['revision']


def draft(c, lesson=None, rev='current'):
    r = c.request('POST', BASE+'/drafts', json={'expected_revision': revision(c) if rev == 'current' else rev, 'lesson': lesson or sample()})
    assert r.status_code == 201, r.text
    return r.json()['id']


def review(c, vid, **updates):
    return c.request('POST', BASE+f'/drafts/{vid}/review', json={'decision': 'approved', 'checks': CHECKS, 'reason': REASON, **updates})


def publish(c, vid, **updates):
    return c.request('POST', BASE+f'/drafts/{vid}/publish', json={'expected_revision': revision(c), 'reason': REASON, **updates})


def ready(admin, reviewer, lesson=None):
    vid = draft(admin, lesson)
    assert review(reviewer, vid).status_code == 200
    r = publish(admin, vid); assert r.status_code == 200, r.text
    return vid


def attempt(c, vid, **updates):
    return c.request('POST', '/api/tools/banglaread-coach/runs', json={'consent': True, 'inputs': {
        'passage_id': 'lesson:OWN-test', 'passage_revision': vid, 'difficult_indices': [0], 'answer_choice': 1, **updates}})


def test_preserved_seed_identity_and_not_public(admin, user):
    data = admin.request('GET', BASE).json()
    assert len(data['seeds']) == 120
    assert all(s['approved'] is False for s in data['seeds'])
    for name, expected in data['seed_hashes'].items(): assert hashlib.sha256((content.SEED_ROOT/name).read_bytes()).hexdigest() == expected
    assert len(user.request('GET', '/api/reading/passages').json()) == 12
    seed = admin.request('GET', BASE+'/seeds/BRP001').json()
    assert seed['passage']['approved'] is False and seed['published'] is False
    assert user.request('GET', BASE+'/seeds/BRP001').status_code == 403
    assert admin.request('GET', BASE+'/seeds/BRP999').status_code == 404


def test_roles_csrf_and_recent_mfa(user, admin):
    assert user.request('GET', BASE).status_code == 403
    assert admin.client.post(BASE+'/drafts', json={'lesson': sample()}).status_code == 403
    with DB.begin() as db:
        for s in db.scalars(select(Session).where(Session.user_id == admin.user['id'])): s.mfa_until = 0
    assert admin.request('GET', BASE).status_code == 403
    assert admin.request('POST', BASE+'/drafts', json={'lesson': sample()}).status_code == 403


@pytest.mark.parametrize('mutation', [
    {'correct_option_index': True}, {'correct_option_index': 2}, {'level': True}, {'level': 6},
    {'source_seed_id': 'BRP999'}, {'lesson_id': 'BRP001'}, {'passage': '<script>test</script>'},
    {'options': [{'bn': 'এক', 'en': 'One'}, {'bn': 'এক', 'en': 'Two'}]},
    {'passage': 'শব্দ '*251}, {'rights_note': ''}, {'license': 'unverified'}, {'unexpected': 'value'},
])
def test_invalid_draft_is_not_saved(admin, mutation):
    lesson = {**sample(), **mutation}
    response = admin.request('POST', BASE+'/drafts', json={'lesson': lesson, 'expected_revision': None})
    assert response.status_code == 422, response.text
    assert admin.request('GET', BASE).json()['versions'] == []


def test_independent_all_checks_immutable_review(admin, reviewer):
    vid = draft(admin)
    assert review(admin, vid).status_code == 403
    assert publish(admin, vid).status_code == 409
    assert review(reviewer, vid, checks={**CHECKS, 'publication_rights': False}).status_code == 422
    assert review(reviewer, vid, checks={**CHECKS, 'spelling': 'true'}).status_code == 422
    assert review(reviewer, vid).status_code == 200
    assert review(reviewer, vid, decision='rejected').status_code == 409
    assert publish(admin, vid).status_code == 200
    assert admin.request('GET', BASE+f'/drafts/{vid}').json()['previously_published'] is True


def test_rejected_content_never_public(admin, reviewer, user):
    vid = draft(admin)
    assert review(reviewer, vid, decision='rejected', checks={k: False for k in CHECKS}).status_code == 200
    assert publish(admin, vid).status_code == 409
    assert len(user.request('GET', '/api/reading/passages').json()) == 12


def test_quiz_keys_private_attempt_is_encrypted_and_owner_scoped(admin, reviewer, user):
    vid = ready(admin, reviewer)
    rows = user.request('GET', '/api/reading/passages').json()
    assert len(rows) == 13 and rows[-1]['revision'] == vid
    assert 'correct_option' not in json.dumps(rows) and 'rights_note' not in json.dumps(rows) and 'reviewer' not in json.dumps(rows)
    r = attempt(user, vid)
    assert r.status_code == 201, r.text
    assert r.json()['facts']['comprehension'] == 'matched'
    assert r.json()['details']['correct_option'] == 1
    assert r.json()['details']['explanation']['en'] == sample()['explanation']['en']
    rid = r.json()['id']
    with DB() as db:
        saved = db.get(Run, rid)
        assert 'মিনা' not in saved.encrypted
        assert open_sealed(saved.encrypted)['output']['references'][0]['revision'] == vid
    assert admin.request('GET', '/api/runs/'+rid).status_code == 404
    assert user.request('GET', '/api/runs/'+rid).status_code == 200
    assert attempt(user, vid, answer_choice=0).json()['facts']['comprehension'] == 'review'
    skipped = attempt(user, vid, answer_choice=None).json()
    assert skipped['facts']['comprehension'] == 'skipped'
    assert 'correct_option' not in skipped['details'] and 'explanation' not in skipped['details']


@pytest.mark.parametrize('inputs,code', [
    ({'answer_choice': True}, 422), ({'answer_choice': 2}, 422), ({'answer_choice': -1}, 422),
    ({'difficult_indices': [True]}, 422), ({'difficult_indices': [100]}, 422),
    ({'passage_revision': 'stale-version'}, 409),
])
def test_invalid_or_stale_attempt_not_saved(admin, reviewer, user, inputs, code):
    vid = ready(admin, reviewer)
    with DB() as db: before = set(db.scalars(select(Run.id).where(Run.user_id == user.user['id'])))
    assert attempt(user, vid, **inputs).status_code == code
    with DB() as db: assert set(db.scalars(select(Run.id).where(Run.user_id == user.user['id']))) == before


def test_revision_conflicts_withdrawal_and_exact_rollback(admin, reviewer, user):
    first = ready(admin, reviewer)
    stale = draft(admin, sample('OWN-other'))
    updated = sample(); updated['title']['en'] = 'Revised tree lesson'
    second = draft(admin, updated)
    assert review(reviewer, second).status_code == 200
    assert publish(admin, second).status_code == 200
    assert attempt(user, first).status_code == 409
    assert review(reviewer, stale).status_code == 200
    assert publish(admin, stale).status_code == 409
    assert publish(admin, second, expected_revision=None).status_code == 409
    assert publish(admin, stale, rollback=True).status_code == 409
    assert publish(admin, first, rollback=True).status_code == 200
    assert attempt(user, first).status_code == 201
    r = admin.request('POST', BASE+'/withdraw', json={'lesson_id': 'OWN-test', 'expected_revision': revision(admin), 'reason': REASON})
    assert r.status_code == 200
    with DB() as db:
        history = content.get(db, 'history:'+r.json()['revision'])
        assert history['detail']['reason'] == REASON and history['action'] == 'withdraw'
    assert len(user.request('GET', '/api/reading/passages').json()) == 12
    assert attempt(user, first).status_code == 404
    restored = publish(admin, first, rollback=True)
    assert restored.status_code == 200
    with DB() as db: assert content.get(db, 'history:'+restored.json()['revision'])['detail']['reason'] == REASON


@pytest.mark.parametrize('revoke', ['role', 'banned', 'mfa'])
def test_revoked_authority_blocks_publication(admin, reviewer, user, revoke):
    vid = ready(admin, reviewer)
    with DB.begin() as db:
        actor = db.get(User, reviewer.user['id'])
        if revoke == 'role': actor.role = 'user'
        elif revoke == 'banned': actor.banned = True
        else: actor.mfa_enabled = False
    assert publish(admin, vid, rollback=True).status_code == 409
    if revoke != 'mfa':
        assert len(user.request('GET', '/api/reading/passages').json()) == 12
        assert attempt(user, vid).status_code == 404


def test_body_tampering_and_corrupt_records_fail_closed(admin, reviewer, user):
    vid = ready(admin, reviewer)
    with DB.begin() as db:
        d = content.get(db, 'draft:'+vid); d['lesson']['correct_option_index'] = 0; content.put(db, 'draft:'+vid, d)
    assert len(user.request('GET', '/api/reading/passages').json()) == 12
    assert publish(admin, vid, rollback=True).status_code == 409
    with DB.begin() as db: db.get(Config, content.PREFIX+'draft:'+vid).value = '{bad-json'
    assert user.request('GET', '/api/reading/passages').status_code == 200
    assert len(user.request('GET', '/api/reading/passages').json()) == 12


def test_reordering_requires_exact_active_set(admin, reviewer, user):
    ready(admin, reviewer)
    other = sample('OWN-second'); other['title']['en'] = 'Second original lesson'
    ready(admin, reviewer, other)
    for ids in [['OWN-test'], ['OWN-test','OWN-test'], ['OWN-test','unknown']]:
        assert admin.request('POST', BASE+'/order', json={'expected_revision': revision(admin), 'lesson_ids': ids}).status_code == 422
    expected = revision(admin)
    r = admin.request('POST', BASE+'/order', json={'expected_revision': expected, 'lesson_ids': ['OWN-second','OWN-test']})
    assert r.status_code == 200
    assert [p['id'] for p in user.request('GET', '/api/reading/passages').json()[-2:]] == ['lesson:OWN-second','lesson:OWN-test']
    assert admin.request('POST', BASE+'/order', json={'expected_revision': expected, 'lesson_ids': ['OWN-test','OWN-second']}).status_code == 409


def test_real_queue_worker_and_withdrawn_pending_lesson(admin, reviewer, user, monkeypatch):
    monkeypatch.setenv('ENABLE_DURABLE_INFERENCE', '1')
    vid = ready(admin, reviewer)
    with DB.begin() as db: db.execute(delete(queue.InferenceJob))
    def enqueue():
        r = user.request('POST', '/api/tools/banglaread-coach/jobs', json={'consent': True, 'inputs': {
            'passage_id': 'lesson:OWN-test', 'passage_revision': vid, 'answer_choice': 1}, 'idempotency_key': uuid.uuid4().hex})
        assert r.status_code == 202, r.text
        return r.json()['id']
    jid = enqueue()
    claimed = queue.claim()
    completed = subprocess.run([sys.executable, '-m', 'services.model_worker.inference_worker', '--execute-claim'], input=json.dumps(claimed), text=True, capture_output=True, timeout=60)
    assert completed.returncode == 0, completed.stderr
    done = user.request('GET', '/api/jobs/'+jid).json()
    assert done['state'] == 'succeeded', done
    assert user.request('GET', '/api/runs/'+done['run_id']).json()['output']['facts']['comprehension'] == 'matched'
    pending = enqueue(); claimed = queue.claim()
    assert admin.request('POST', BASE+'/withdraw', json={'lesson_id': 'OWN-test', 'expected_revision': revision(admin), 'reason': REASON}).status_code == 200
    assert queue.publish_claim(claimed) is False
    failure = user.request('GET', '/api/jobs/'+pending).json()
    assert failure['state'] == 'failed' and failure['run_id'] is None
    with DB() as db: assert open_sealed(db.get(queue.InferenceJob, pending).encrypted) == {}
    with DB.begin() as db: db.execute(delete(queue.InferenceJob))
