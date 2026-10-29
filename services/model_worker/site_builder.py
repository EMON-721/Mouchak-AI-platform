"""Typed public presentation CMS. No executable content or model/security switches."""
import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlalchemy import select, text
from sqlalchemy.orm import load_only
from .store import Config, CMSVersion, User, now
from .auth import authorize, identify, db_session, audit

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = json.loads((ROOT / 'packages/ui-tokens/site-defaults.json').read_text())
EDITABLE = json.loads((ROOT / 'packages/ui-tokens/editable-locales.json').read_text())
MODULES = {m['slug']: m for m in json.loads((ROOT / 'packages/module-registry/catalogue.json').read_text())['modules']}
FIELDS = json.loads((ROOT / 'packages/module-registry/fields.json').read_text())
CATEGORIES = sorted({m['category'] for m in MODULES.values()})
PAGES = {'about', 'methodology', 'help', 'privacy', 'terms', 'contact'}
ROUTES = {'/', '/explore', '/work', '/sources', '/status', '/#faq'} | {'/'+p for p in PAGES} | {'/tools/'+s for s in MODULES}
PAGE, KEY = 'site-builder', 'cms:site-builder'
router = APIRouter(prefix='/api')

class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class Copy(Strict):
    bn: str = Field(min_length=1, max_length=4000)
    en: str = Field(min_length=1, max_length=4000)

class Link(Copy):
    href: str
    @model_validator(mode='after')
    def safe(self):
        if self.href not in ROUTES or max(len(self.bn),len(self.en)) > 100:
            raise ValueError('Use an existing public route and short labels')
        return self

AssetID = str | None
class Brand(Strict):
    name_bn: str = Field(min_length=1,max_length=100)
    name_en: str = Field(min_length=1,max_length=100)
    tagline_bn: str = Field(min_length=1,max_length=200)
    tagline_en: str = Field(min_length=1,max_length=200)
    logo_asset: AssetID = None
    favicon_asset: AssetID = None

class Theme(Strict):
    light: dict[str,str]
    dark: dict[str,str]
    font: Literal['bengali_sans','system_serif']
    text_scale: float = Field(ge=1,le=1.2,allow_inf_nan=False)
    @model_validator(mode='after')
    def accessible(self):
        for palette in [self.light,self.dark]:
            if set(palette) != set(DEFAULT['theme']['light']) or any(not re.fullmatch(r'#[0-9a-fA-F]{6}',c) for c in palette.values()):
                raise ValueError('Exact palette keys and six-digit hex colours required')
            for foreground,background in [('ink','paper'),('ink','white'),('muted','paper'),('muted','white'),('teal','paper'),('danger','white')]:
                a,b=sorted([luminance(palette[foreground]),luminance(palette[background])])
                if (b+.05)/(a+.05) < 4.5:
                    raise ValueError('Text contrast must be at least 4.5:1 in both themes')
        return self

def luminance(colour):
    rgb=[int(colour[i:i+2],16)/255 for i in (1,3,5)]
    linear=[c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in rgb]
    return sum(c*w for c,w in zip(linear,[.2126,.7152,.0722]))

class Footer(Strict):
    text: Copy
    note: Copy
    links: list[Link] = Field(min_length=2,max_length=12)

class FAQ(Strict):
    question: Copy
    answer: Copy

class Home(Strict):
    sections: list[Literal['hero','statement','featured','principles','faq','closing']] = Field(min_length=2,max_length=6)
    featured_slugs: list[str] = Field(min_length=1,max_length=8)
    text: dict[str,Copy]
    faqs: list[FAQ] = Field(max_length=12)
    @model_validator(mode='after')
    def known(self):
        if len(set(self.sections))!=len(self.sections) or self.sections[0]!='hero' or 'principles' not in self.sections:
            raise ValueError('Keep hero first and readiness principles visible')
        if len(set(self.featured_slugs))!=len(self.featured_slugs) or any(s not in MODULES for s in self.featured_slugs):
            raise ValueError('Unknown or duplicate featured tool')
        if set(self.text)!=set(DEFAULT['home']['text']):
            raise ValueError('Unknown or missing homepage text keys')
        if any(max(len(v.bn),len(v.en)) > (1000 if k=='hero_intro' else 200) for k,v in self.text.items()):
            raise ValueError('Homepage text too long')
        return self

class FieldCopy(Copy):
    help_bn: str = Field(default='',max_length=800)
    help_en: str = Field(default='',max_length=800)
    placeholder_bn: str = Field(default='',max_length=200)
    placeholder_en: str = Field(default='',max_length=200)
    @model_validator(mode='after')
    def short(self):
        if max(len(self.bn),len(self.en)) > 160: raise ValueError('Field label too long')
        return self

class ToolCopy(Strict):
    name: Copy | None = None
    description: Copy | None = None
    logo_asset: AssetID = None
    fields: dict[str,FieldCopy] = Field(default_factory=dict)
    @model_validator(mode='after')
    def short(self):
        for value,limit in [(self.name,160),(self.description,800)]:
            if value and max(len(value.bn),len(value.en))>limit: raise ValueError('Tool text too long')
        return self

class PageCopy(Strict):
    title: Copy
    body: dict[Literal['bn','en'],str]
    @model_validator(mode='after')
    def lengths(self):
        if set(self.body)!={'bn','en'} or any(not 1<=len(v)<=12000 for v in self.body.values()) or max(len(self.title.bn),len(self.title.en))>300:
            raise ValueError('Bilingual page title/body required within limits')
        return self

class SEO(Strict):
    title_bn: str = Field(min_length=1,max_length=160)
    title_en: str = Field(min_length=1,max_length=160)
    description_bn: str = Field(min_length=1,max_length=500)
    description_en: str = Field(min_length=1,max_length=500)
    index: bool = Field(strict=True)

class Site(Strict):
    schema_version: Literal[1]
    brand: Brand
    theme: Theme
    navigation: list[Link] = Field(min_length=1,max_length=6)
    footer: Footer
    home: Home
    category_labels: dict[str,Copy]
    tool_overrides: dict[str,ToolCopy]
    pages: dict[str,PageCopy]
    locales: dict[str,Copy]
    seo: SEO
    @model_validator(mode='after')
    def safe(self):
        for links,required in [(self.navigation,{'/explore'}),(self.footer.links,{'/privacy','/terms'})]:
            routes=[l.href for l in links]
            if len(set(routes))!=len(routes) or not required.issubset(routes):
                raise ValueError('Keep unique links, Explore and legal pages')
        if set(self.category_labels)-set(CATEGORIES) or set(self.pages)-PAGES or set(self.tool_overrides)-set(MODULES) or set(self.locales)-set(EDITABLE):
            raise ValueError('Unknown category, page, locale or tool')
        if any(max(len(v.bn),len(v.en))>160 for v in [*self.category_labels.values(),*self.locales.values()]):
            raise ValueError('UI labels too long')
        for slug,override in self.tool_overrides.items():
            if set(override.fields)-set(field_paths(slug)):
                raise ValueError('Unknown field path')
        encoded=json.dumps(self.model_dump(),ensure_ascii=False)
        if len(encoded)>120000 or re.search(r'<\s*/?\s*(script|iframe|svg|object|embed|style)|javascript:',encoded,re.I):
            raise ValueError('Executable content and oversized configuration prohibited')
        for asset in asset_ids(self.model_dump()):
            if not re.fullmatch(r'[a-f0-9]{64}',asset): raise ValueError('Invalid asset id')
        return self

def field_paths(slug):
    result={}
    for f in FIELDS[MODULES[slug]['engine']]:
        result[f['key']]={k:f[k] for k in ['bn','en','type']}
        for c in f.get('columns',[]): result[f['key']+'.'+c['key']]={k:c[k] for k in ['bn','en','type']}
    if MODULES[slug]['engine'] in ['directory','pharmacy']:
        result['district']={'bn':'জেলা','en':'District','type':'text'}
    return result

def asset_ids(config):
    return {x for x in [config['brand'].get('logo_asset'),config['brand'].get('favicon_asset'),*[v.get('logo_asset') for v in config['tool_overrides'].values()]] if x}

def validate(value):
    try: return Site.model_validate(value).model_dump()
    except (ValueError,TypeError): raise HTTPException(422,'Invalid site configuration / সাইটের সেটিংস যাচাই করুন')

def active_config(db):
    c=db.get(Config,KEY)
    if not c: return deepcopy(DEFAULT)
    cached=db.info.get('site-config')
    if not cached or cached[0]!=c.value:
        cached=(c.value,validate(json.loads(c.value)));db.info['site-config']=cached
    return deepcopy(cached[1])

def active_revision(db):
    c=db.get(Config,'site-active-revision')
    return c.value if c else None

def publication_lock(db):
    if db.bind.dialect.name=='postgresql': db.execute(text('SELECT pg_advisory_xact_lock(742007)'))

def fingerprint(value): return hashlib.sha256(value.encode()).hexdigest()
def current_hash(db):
    c=db.get(Config,KEY)
    return fingerprint(c.value if c else '')
def put(db,key,value):
    c=db.get(Config,key)
    if c: c.value=value
    else: db.add(Config(key=key,value=value))
def assets_exist(db,config):
    if any(not db.get(Config,'site-asset:'+a) for a in asset_ids(config)):
        raise HTTPException(422,'An owned public brand asset is missing')

def validate_publication(db,v,check_base=True):
    value=validate(json.loads(v.body)); assets_exist(db,value)
    review=db.get(Config,'site-review:'+v.id)
    review=json.loads(review.value) if review else {}
    if review.get('decision')!='approved' or review.get('body_hash')!=fingerprint(v.body) or review.get('reviewer')==v.author:
        raise HTTPException(409,'Independent approval of this exact version is required')
    for uid in [v.author,review.get('reviewer')]:
        u=db.scalar(select(User).options(load_only(User.id,User.role,User.banned,User.mfa_enabled)).where(User.id==uid))
        if not u or u.banned or not u.mfa_enabled or u.role not in {'super_admin','content_editor'}:
            raise HTTPException(409,'Author or reviewer is no longer authorized')
    base=db.get(Config,'site-base:'+v.id)
    if check_base and (not base or base.value!=current_hash(db)):
        raise HTTPException(409,'Published site changed; create and review a fresh draft')
    return value

def set_active(db,v):
    put(db,KEY,v.body); put(db,'site-active-revision',v.id); v.status='published'

def version(db,vid,locked=False):
    query=select(CMSVersion).where(CMSVersion.id==vid,CMSVersion.page==PAGE)
    v=db.scalar(query.with_for_update() if locked else query)
    if not v: raise HTTPException(404)
    return v

class DraftInput(Strict):
    config: Site
    expected_revision: str | None = None
class ReviewInput(Strict):
    decision: Literal['approved','rejected']
    reason: str = Field(min_length=10,max_length=1000)
class PublishInput(Strict):
    expected_revision: str | None = None
    rollback: bool = Field(default=False,strict=True)

@router.get('/public/site')
def public_site(db=Depends(db_session, scope="function")):
    return {'revision':active_revision(db),'config':active_config(db)}

@router.get('/admin/site-builder')
def editor(u=Depends(authorize('cms')),db=Depends(db_session, scope="function")):
    versions=list(db.scalars(select(CMSVersion).where(CMSVersion.page==PAGE).order_by(CMSVersion.created_at.desc(),CMSVersion.id.desc()).limit(100)))
    assets=[]
    for c in db.scalars(select(Config).where(Config.key.like('site-asset:%')).limit(200)):
        value=json.loads(c.value); assets.append({k:v for k,v in value.items() if k!='svg'})
    return {'active':public_site(db),'defaults':DEFAULT,'editable_locales':EDITABLE,'categories':CATEGORIES,'tools':[{'slug':s,'name':m['name'],'description_bn':m['description_bn'],'description_en':m['description_en'],'fields':field_paths(s)} for s,m in MODULES.items()],'assets':assets,'versions':[{'id':v.id,'status':v.status,'author':v.author,'created_at':v.created_at} for v in versions]}

@router.post('/admin/site-builder/validate')
def check(p:DraftInput,u=Depends(authorize('cms')),db=Depends(db_session, scope="function")):
    value=p.config.model_dump(); assets_exist(db,value)
    return {'valid':True,'published':False,'config':value}

@router.post('/admin/site-builder',status_code=201)
def draft(p:DraftInput,u=Depends(authorize('cms')),db=Depends(db_session, scope="function")):
    publication_lock(db)
    if active_revision(db)!=p.expected_revision: raise HTTPException(409,'Published revision changed; reload before drafting')
    value=p.config.model_dump(); assets_exist(db,value)
    v=CMSVersion(page=PAGE,body=json.dumps(value,ensure_ascii=False,separators=(',',':')),author=u.id,status='draft')
    db.add(v); db.flush(); put(db,'site-base:'+v.id,current_hash(db))
    audit(db,u.id,'site_draft',v.id)
    return {'id':v.id,'status':v.status}

@router.get('/admin/site-builder/{vid}/preview')
def preview(vid:str,u=Depends(authorize('cms')),db=Depends(db_session, scope="function")):
    v=version(db,vid)
    return {'id':v.id,'status':v.status,'author':v.author,'config':validate(json.loads(v.body))}

@router.post('/admin/site-builder/{vid}/review')
def review(vid:str,p:ReviewInput,u=Depends(authorize('cms')),db=Depends(db_session, scope="function")):
    publication_lock(db); v=version(db,vid,True)
    if v.author==u.id: raise HTTPException(403,'A different content editor must review')
    if v.status!='draft': raise HTTPException(409,'Only an unreviewed immutable draft can be reviewed')
    put(db,'site-review:'+v.id,json.dumps({'decision':p.decision,'reviewer':u.id,'reason':p.reason,'body_hash':fingerprint(v.body),'reviewed_at':now()},ensure_ascii=False))
    v.status='reviewed' if p.decision=='approved' else 'rejected'
    audit(db,u.id,'site_review_'+p.decision,v.id)
    return {'id':v.id,'status':v.status}

@router.post('/admin/site-builder/{vid}/publish')
def publish(vid:str,p:PublishInput,u=Depends(authorize('cms')),db=Depends(db_session, scope="function")):
    publication_lock(db); v=version(db,vid,True)
    if active_revision(db)!=p.expected_revision: raise HTTPException(409,'Published revision changed; reload')
    if p.rollback:
        if v.status!='published': raise HTTPException(409,'Rollback requires a previously published version')
    elif v.status!='reviewed': raise HTTPException(409,'Publish requires independent review')
    validate_publication(db,v,check_base=not p.rollback); set_active(db,v)
    audit(db,u.id,'site_rollback' if p.rollback else 'site_publish',v.id)
    return {'published':True,'revision':v.id}

class AssetInput(Strict):
    svg: str = Field(min_length=20,max_length=30000)
    license_uri: str = Field(min_length=10,max_length=2000)
    rights_note: str = Field(min_length=20,max_length=2000)
    attest_rights: Literal[True]
    @field_validator('license_uri')
    @classmethod
    def url(cls,value):
        url=urlparse(value)
        if url.scheme!='https' or not url.netloc or url.username or url.password: raise ValueError('Credential-free HTTPS licence URL required')
        return value

def safe_svg(value):
    if len(value.encode())>30000 or re.search(r'<!|<\?',value): raise HTTPException(422,'Unsupported SVG declarations')
    try: root=ET.fromstring(value)
    except ET.ParseError: raise HTTPException(422,'Invalid SVG')
    ns='{http://www.w3.org/2000/svg}'
    tags={'svg','g','path','rect','circle','ellipse','line','polyline','polygon','title','desc','text'}
    numeric={'width','height','x','y','x1','x2','y1','y2','cx','cy','r','rx','ry','stroke-width','opacity','fill-opacity','stroke-opacity','font-size'}
    attrs=numeric|{'viewBox','d','points','fill','stroke','fill-rule','stroke-linecap','stroke-linejoin','text-anchor'}
    count=0
    def walk(node,depth):
        nonlocal count
        count+=1
        if count>300 or depth>12 or node.tag not in {ns+t for t in tags} or len(node.text or '')>1000 or len(node.tail or '')>1000: raise HTTPException(422,'Unsupported SVG structure')
        for key,val in node.attrib.items():
            if key not in attrs or len(val)>12000 or not re.fullmatch(r'[a-zA-Z0-9#.,+\-\s]*',val): raise HTTPException(422,'Unsupported SVG attribute')
            if key in {'fill','stroke'} and not re.fullmatch(r'#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?|none|currentColor|transparent|black|white',val): raise HTTPException(422,'Unsupported paint')
            if key in numeric|{'viewBox','d','points'}:
                for number in re.findall(r'[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?',val):
                    if not math.isfinite(float(number)) or abs(float(number))>1e6: raise HTTPException(422,'SVG geometry out of bounds')
        for child in node: walk(child,depth+1)
    if root.tag!=ns+'svg' or not root.get('viewBox'): raise HTTPException(422,'SVG namespace and viewBox required')
    walk(root,0)
    return ET.tostring(root,encoding='unicode')

@router.post('/admin/site-assets',status_code=201)
def asset(p:AssetInput,u=Depends(authorize('cms')),db=Depends(db_session, scope="function")):
    svg=safe_svg(p.svg); aid=fingerprint(svg)
    if not db.get(Config,'site-asset:'+aid):
        put(db,'site-asset:'+aid,json.dumps({'id':aid,'svg':svg,'license_uri':p.license_uri,'rights_note':p.rights_note,'author':u.id,'created_at':now()},ensure_ascii=False))
        audit(db,u.id,'site_asset_added',aid)
    return {'id':aid,'url':'/api/public/site-assets/'+aid+'.svg'}

@router.get('/public/site-assets/{aid}.svg')
def asset_bytes(aid:str,request:Request,db=Depends(db_session, scope="function")):
    if not re.fullmatch(r'[a-f0-9]{64}',aid): raise HTTPException(404)
    c=db.get(Config,'site-asset:'+aid)
    if not c: raise HTTPException(404)
    public=aid in asset_ids(active_config(db))
    if not public:
        try: authorize('cms')(request,identify(request,db))
        except HTTPException: raise HTTPException(404)
    return Response(json.loads(c.value)['svg'],media_type='image/svg+xml',headers={'Content-Security-Policy':"default-src 'none'; style-src 'none'; sandbox",'X-Content-Type-Options':'nosniff','Cache-Control':'no-store' if not public else 'public, max-age=300'})

def customize_module(db,module):
    override=active_config(db)['tool_overrides'].get(module['slug'])
    if not override: return module
    module=deepcopy(module)
    module['presentation_base']={k:deepcopy(module[k]) for k in ['name','logo','description_bn','description_en','fields'] if k in module}
    for key in ['name','description']:
        if override.get(key):
            for lang in ['bn','en']: module[key+'_'+lang]=override[key][lang]
            if key=='name': module['name']=override[key]['en']
    if override.get('logo_asset'): module['logo']='/api/public/site-assets/'+override['logo_asset']+'.svg'
    for f in module.get('fields',[]):
        patch=override.get('fields',{}).get(f['key'])
        if patch: f.update(patch)
        for column in f.get('columns',[]):
            patch=override.get('fields',{}).get(f['key']+'.'+column['key'])
            if patch: column.update(patch)
    return module
