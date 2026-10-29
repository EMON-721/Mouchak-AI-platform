"""A successful network response must acknowledge an already committed write."""
import asyncio
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import event, func, select
from services.model_worker.main import app
from services.model_worker.store import DB, User


def users():
    with DB() as db:
        return db.scalar(select(func.count()).select_from(User))


def test_committed_session_is_visible_to_a_fresh_reader_before_response_starts():
    before=users()
    observed=[]
    async def observed_app(scope,receive,send):
        async def inspect(message):
            if message['type']=='http.response.start':
                observed.append((message['status'],users()))
            await send(message)
        await app(scope,receive,inspect)
    async def run():
        transport=httpx.ASGITransport(app=observed_app)
        async with httpx.AsyncClient(transport=transport,base_url='http://testserver') as client:
            response=await client.post('/api/session')
            assert response.status_code==200
    asyncio.run(run())
    assert observed==[(200,before+1)]


def test_commit_failure_rolls_back_without_success_or_session_cookie():
    before=users()
    def reject_commit(session):
        raise RuntimeError('DEMO injected transaction commit failure')
    with TestClient(app,raise_server_exceptions=False) as client:
        event.listen(DB.class_,'before_commit',reject_commit)
        try:
            response=client.post('/api/session')
        finally:
            event.remove(DB.class_,'before_commit',reject_commit)
    assert response.status_code==500
    assert 'set-cookie' not in response.headers
    assert users()==before
