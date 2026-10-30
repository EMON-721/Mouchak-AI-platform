"""Audited disable/restore control for implemented experimental models; no fake release gate."""
import json
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from .auth import authorize, db_session, audit
from .store import Config, uid, now
from . import noise_runtime

router=APIRouter(prefix='/api/admin/model-operations')
KEY='noise-model-policy'
class Policy(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)
    state:Literal['disabled','experimental']
    expected_revision:str|None=None
    reason:str=Field(min_length=10,max_length=1000)

def current(db):
    c=db.get(Config,KEY)
    return json.loads(c.value) if c else {'revision':None,'state':'experimental','reason':'Environment opt-in and verified model required; production remains blocked'}

@router.get('')
def overview(u=Depends(authorize('models')),db=Depends(db_session,scope='function')):
    return {'runtime':noise_runtime.availability(),'policy':current(db),'manifest':noise_runtime.MANIFEST,'production_release_allowed':False,'private_assets_listed':False}

@router.post('/noise-policy')
def policy(p:Policy,u=Depends(authorize('models')),db=Depends(db_session,scope='function')):
    if db.bind.dialect.name=='postgresql':db.execute(text('SELECT pg_advisory_xact_lock(742008)'))
    old=current(db)
    if p.expected_revision!=old['revision']:raise HTTPException(409,'Model policy changed; reload before updating')
    value={'revision':uid(),'state':p.state,'reason':p.reason,'actor':u.id,'created_at':now(),'previous_revision':old['revision']}
    c=db.get(Config,KEY)
    if c:c.value=json.dumps(value,ensure_ascii=False)
    else:db.add(Config(key=KEY,value=json.dumps(value,ensure_ascii=False)))
    db.add(Config(key='noise-model-policy-history:'+value['revision'],value=json.dumps(value,ensure_ascii=False)))
    audit(db,u.id,'noise_model_policy',value['revision'],{'state':p.state,'previous_revision':old['revision']})
    return {**value,'production_release_allowed':False}
