"""T050y: composite refusal before Telegram rename submission effects."""
import asyncio
import pytest
from tests.integration.test_composite_telegram_autorenew_guards import controls, BUYER, FOREIGN, other_tables
from tests.integration.test_composite_telegram_rename_entry_guards import configure_label
import handlers_user
from panel_providers.base import PanelError, PanelUserResult
from states import ServiceRenameFlow
from tests._harness.legacy_bot import FakeUser, FakeMessage, TelegramLog, find_handler, make_state
from tests.integration.test_composite_ai_catalog_legacy import dump

LOCAL_NOTE='(فقط نام نمایشی داخل بات تغییر کرد؛ لینک/کانفیگ فعلی روی پنل بدون تغییر کار می‌کند)'
PANEL_NOTE='(روی خودِ پنل هم اعمال شد)'


def external(c, monkeypatch, remote):
    if remote=='inactive': c.db.update_panel_server(c.server,is_active=0)
    class Provider:
        async def rename_user(self, old, new):
            c.calls.append(('rename',old,new))
            if remote=='error': raise PanelError('synthetic panel rejection')
        async def get_user(self, username):
            c.calls.append(('get',username))
            return PanelUserResult(username,'')
    def provider(row):
        c.calls.append(('provider',row['id']))
        return Provider()
    monkeypatch.setattr(handlers_user,'get_provider',provider)


def invoke(c, uid=BUYER, text='new_name'):
    async def run():
        state=make_state(uid);await state.set_state(ServiceRenameFlow.waiting_suffix)
        await state.set_data({'sentinel':'keep','cb_id':f'x{c.target}'})
        log=TelegramLog();message=FakeMessage(log,uid,from_user=FakeUser(uid),text=text)
        fn=find_handler(handlers_user.create_user_router(c.db),'message','service_rename_receive')
        await fn(message,state)
        return log.events,await state.get_state(),await state.get_data()
    return asyncio.run(run())


def initial_data(c):
    return {'sentinel':'keep','cb_id':f'x{c.target}'}


def assert_supported(c, remote, mode, text='new_name'):
    before=dict(c.db.get_custom_config_owned(c.target,BUYER));sibling=dict(c.db.get_custom_config_owned(c.sibling,BUYER));others=other_tables(c.db)
    history=[dict(r) for r in c.db.get_custom_config_history(c.target)]
    sibling_history=[dict(r) for r in c.db.get_custom_config_history(c.sibling)]
    old_label='shop-alpha' if mode=='matching' else 'alpha'
    new_label='shop-'+text if mode=='matching' else text
    note=PANEL_NOTE if remote=='success' else LOCAL_NOTE
    events,state,data=invoke(c,text=text)
    after=dict(c.db.get_custom_config_owned(c.target,BUYER))
    expected=before|{'display_name':new_label}
    if remote=='success': expected['username']=new_label
    assert after==expected
    assert dict(c.db.get_custom_config_owned(c.sibling,BUYER))==sibling and other_tables(c.db)==others
    current=[dict(r) for r in c.db.get_custom_config_history(c.target)]
    assert len(current)==len(history)+1 and current[1:]==history
    assert [dict(r) for r in c.db.get_custom_config_history(c.sibling)]==sibling_history
    assert current[0]['event_type']=='rename' and current[0]['custom_config_id']==c.target
    assert current[0]['detail']==f'{old_label} ← {new_label} {note}'
    assert state is None and data=={}
    assert len(events)==1 and events[0].kind=='edit_text'
    assert events[0].text.startswith(f'✅ نام کانفیگ به «{new_label}» تغییر کرد. {note}\n\n')
    assert events[0].parse_mode=='Markdown'
    if remote=='inactive': assert c.calls==[]
    else:
        expected_name=new_label if remote=='success' else 'alpha'
        assert c.calls==[('provider',c.server),('rename','alpha',new_label),('provider',c.server),('get',expected_name)]


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('remote',['success','error','inactive'])
def test_composite_rename_submission_refused(controls,monkeypatch,representation,remote,caplog):
    c=controls;external(c,monkeypatch,remote);c.inject(c.target,'composite',representation);before=dump(c.db)
    events,state,data=invoke(c)
    assert len(events)==1 and events[0].kind=='message_answer'
    assert 'composite' in (events[0].text or '').lower()
    assert 'SECRET-COMPOSITE' not in str(events)+caplog.text
    assert state==ServiceRenameFlow.waiting_suffix.state and data==initial_data(c)
    assert c.calls==[] and dump(c.db)==before


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('remote',['success','error','inactive'])
@pytest.mark.parametrize('mode',['none','matching','nonmatching'])
def test_legacy_rename_submission_exact(controls,monkeypatch,representation,kind,remote,mode):
    c=controls;configure_label(c,mode);external(c,monkeypatch,remote);c.inject(c.target,kind,representation)
    assert_supported(c,remote,mode)


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('text',['abc','a'*20])
def test_legacy_rename_length_boundaries(controls,monkeypatch,representation,text):
    c=controls;external(c,monkeypatch,'success');c.inject(c.target,'legacy',representation)
    assert_supported(c,'success','none',text)


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_sibling_does_not_block_rename_submission(controls,monkeypatch,representation):
    c=controls;external(c,monkeypatch,'success');c.inject(c.sibling,'composite',representation)
    assert_supported(c,'success','none')


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_foreign_rename_submission_opaque(controls,monkeypatch,representation):
    c=controls;external(c,monkeypatch,'success');c.inject(c.target,'composite',representation);before=dump(c.db)
    events,state,data=invoke(c,FOREIGN)
    assert len(events)==1 and events[0].kind=='message_answer'
    assert events[0].text=='این مورد دیگر یافت نشد.'
    assert state is None and data=={} and c.calls==[] and dump(c.db)==before


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('text',['aa','a'*21,'bad name','نام'])
def test_legacy_rename_invalid_names_preserved(controls,monkeypatch,representation,text):
    c=controls;external(c,monkeypatch,'success');c.inject(c.target,'legacy',representation);before=dump(c.db)
    events,state,data=invoke(c,text=text)
    assert len(events)==1 and events[0].kind=='message_answer'
    assert events[0].text=='❌ نامعتبر است. فقط حروف انگلیسی، عدد و آندرلاین، بین ۳ تا ۲۰ کاراکتر.'
    assert state==ServiceRenameFlow.waiting_suffix.state and data==initial_data(c)
    assert c.calls==[] and dump(c.db)==before


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('case',['unchanged','taken'])
def test_legacy_rename_name_conflicts_preserved(controls,monkeypatch,representation,case):
    c=controls;external(c,monkeypatch,'success');c.inject(c.target,'legacy',representation);before=dump(c.db)
    events,state,data=invoke(c,text='alpha' if case=='unchanged' else 'beta')
    assert len(events)==1 and events[0].kind=='message_answer'
    assert events[0].text==('این نام همان نام فعلی است.' if case=='unchanged' else '❌ این نام قبلاً استفاده شده. نام دیگری بفرست.')
    assert state==ServiceRenameFlow.waiting_suffix.state and data==initial_data(c)
    assert c.calls==[] and dump(c.db)==before
