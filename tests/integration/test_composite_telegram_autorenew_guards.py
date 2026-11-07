"""T050w: refuse unsupported composite auto-renew toggles before any effect."""
import asyncio
from types import SimpleNamespace

import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
import database
import handlers_user
from panel_providers.base import PanelUserResult
from tests._harness.legacy_bot import FakeCallbackQuery, FakeMessage, FakeUser, TelegramLog, find_handler
from tests.integration.test_composite_legacy_guards import as_row
from tests.integration.test_composite_ai_catalog_legacy import dump

BUYER, FOREIGN = 5101, 5102
ON = '✅ تمدید خودکار فعال شد. هر بار نزدیک انقضا، از کیف پول کسر و تمدید می‌شود.'
OFF = '✅ تمدید خودکار غیرفعال شد.'


@pytest.fixture
def controls(tmp_path, monkeypatch):
    db = database.Database(str(tmp_path/'controls.db'))
    db.init_db(9001)
    for uid in (BUYER, FOREIGN):
        db.add_or_update_user(uid, f'u{uid}', 'Synthetic')
    server = db.add_panel_server('Synthetic', '3xui', 'https://panel.example.invalid', 'fake-user', 'fake-pass')
    target = db.add_custom_config(BUYER, server, 'alpha', 10, 30, '')
    sibling = db.add_custom_config(BUYER, server, 'beta', 20, 60, '')
    calls = []
    class Provider:
        async def get_user(self, username):
            calls.append(('get', username))
            return PanelUserResult(username, '')
    def provider(row):
        calls.append(('provider',row['id']))
        return Provider()
    async def fetch(url):
        calls.append(('fetch',url))
        return {'ok':False}
    monkeypatch.setattr(handlers_user,'get_provider',provider)
    monkeypatch.setattr(handlers_user,'fetch_sub_info',fetch)
    original = db.get_custom_configs_for_user
    def inject(selected, kind, representation):
        def rows(uid, source=None):
            result=[]
            for row in original(uid, source):
                data=dict(row); data.pop('service_kind',None)
                if data['id']==selected and kind is not None:
                    data['service_kind']=kind
                    if kind=='composite': data['subscription_url']='https://SECRET-COMPOSITE.example.invalid'
                result.append(as_row(data,representation))
            return result
        monkeypatch.setattr(db,'get_custom_configs_for_user',rows)
    router=handlers_user.create_user_router(db)
    handler=find_handler(router,'callback_query','cb_service_autorenew_toggle')
    try:
        yield SimpleNamespace(db=db,target=target,sibling=sibling,server=server,calls=calls,inject=inject,handler=handler)
    finally:
        db.close()


def invoke(c, uid=BUYER, target=None):
    log=TelegramLog(); user=FakeUser(uid)
    msg=FakeMessage(log,uid,from_user=user)
    call=FakeCallbackQuery(log,user,f'svc_autorenew:x{target or c.target}',msg)
    asyncio.run(c.handler(call))
    return log.events


def row(c):
    return dict(c.db.get_custom_config_owned(c.target,BUYER))


def other_tables(db):
    with db._get_conn() as conn:
        names=[r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        return {t:[tuple(r) for r in conn.execute('SELECT * FROM "'+t+'"')] for t in names if t not in {'custom_configs','custom_config_history','sqlite_sequence'}}


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('initial',[0,1])
def test_composite_autorenew_refused(controls,representation,initial,caplog):
    c=controls; c.db.set_custom_config_auto_renew(c.target,BUYER,bool(initial))
    c.inject(c.target,'composite',representation);before=dump(c.db)
    events=invoke(c)
    assert len(events)==1 and events[0].kind=='callback_answer'
    assert 'composite' in (events[0].text or '').lower()
    assert 'SECRET-COMPOSITE' not in str(events)+caplog.text
    assert c.calls==[]
    assert dump(c.db)==before


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('initial',[0,1])
def test_legacy_autorenew_exact_toggle(controls,representation,kind,initial):
    c=controls;c.db.set_custom_config_auto_renew(c.target,BUYER,bool(initial));c.inject(c.target,kind,representation)
    before=row(c);sibling=dict(c.db.get_custom_config_owned(c.sibling,BUYER));others=other_tables(c.db)
    history=[dict(r) for r in c.db.get_custom_config_history(c.target)]
    for desired in (1-initial,initial):
        events=invoke(c)
        assert row(c)==before|{'auto_renew':desired}
        assert dict(c.db.get_custom_config_owned(c.sibling,BUYER))==sibling
        assert other_tables(c.db)==others
        current=[dict(r) for r in c.db.get_custom_config_history(c.target)]
        assert len(current)==len(history)+1 and current[1:]==history
        assert current[0]['event_type']=='auto_renew_toggle'
        assert current[0]['detail']==('فعال شد' if desired else 'غیرفعال شد')
        assert current[0]['custom_config_id']==c.target
        history=current
        assert [e.kind for e in events]==['edit_text','callback_answer']
        assert events[-1].text==(ON if desired else OFF)
        assert ('تمدید خودکار: '+('🟢 فعال' if desired else '🔴 غیرفعال')) in events[0].text
        assert events[0].parse_mode=='Markdown'
    assert c.calls==[('provider',c.server),('get','alpha')]*2


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_unselected_composite_does_not_block_autorenew(controls,representation):
    c=controls;c.inject(c.sibling,'composite',representation)
    sibling=dict(c.db.get_custom_config_owned(c.sibling,BUYER))
    events=invoke(c)
    assert row(c)['auto_renew']==1
    assert events[-1].text==ON
    assert dict(c.db.get_custom_config_owned(c.sibling,BUYER))==sibling
    assert c.calls==[('provider',c.server),('get','alpha')]


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_foreign_autorenew_opaque_refusal(controls,representation):
    c=controls;c.inject(c.target,'composite',representation);before=dump(c.db)
    events=invoke(c,FOREIGN)
    assert len(events)==1 and events[0].kind=='callback_answer'
    assert events[0].text=='این مورد یافت نشد.' and events[0].show_alert
    assert c.calls==[] and dump(c.db)==before


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('restriction',['off','test','unlimited'])
def test_existing_autorenew_restrictions(controls,representation,restriction):
    c=controls;c.inject(c.target,'legacy',representation)
    if restriction=='off': c.db.set_setting('svc_show_auto_renew','0')
    else:
        with c.db._get_conn() as conn:
            if restriction=='test': conn.execute("UPDATE custom_configs SET source='test' WHERE id=?",(c.target,))
            else: conn.execute('UPDATE custom_configs SET duration_days=0 WHERE id=?',(c.target,))
    before=dump(c.db);events=invoke(c)
    expected={'off':'این قابلیت غیرفعال است.','test':'این قابلیت برای کانفیگ تست در دسترس نیست.','unlimited':'این کانفیگ نامحدود است و نیازی به تمدید خودکار ندارد.'}[restriction]
    assert len(events)==1 and events[0].kind=='callback_answer'
    assert events[0].text==expected and events[0].show_alert
    assert c.calls==[] and dump(c.db)==before
