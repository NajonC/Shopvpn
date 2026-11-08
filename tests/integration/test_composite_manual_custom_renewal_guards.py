"""T050cb/cc: manual custom renewal callback, actual engine/SQL/factory."""
import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
import handlers_admin
from tests.integration.test_composite_gateway_renewal_guards import catalog, setup as shared_setup, state, LINK, USER_ID, dump
from tests.integration.test_composite_manual_catalog_guards import ALREADY
from tests._harness.legacy_bot import FakeCallbackQuery, FakeUser, FakeMessage, TelegramLog, RecordingBot, find_handler
import asyncio


def invoke(c):
    async def run():
        log=TelegramLog()
        class Bot(RecordingBot):
            async def send_message(self,uid,text,**kw):
                if text=='✅ سرویس شما با موفقیت تمدید شد.':
                    assert c.db.get_order(c.oid)['status']=='approved'
                    with c.db._get_conn() as conn:assert [r[0] for r in conn.execute('SELECT action FROM admin_logs')]==['renewal_approve']
                    if c.scenario=='delivery':raise RuntimeError('synthetic delivery')
                return await super().send_message(uid,text,**kw)
        user=FakeUser(9001)
        call=FakeCallbackQuery(log,user,f'order_approve:{c.oid}',FakeMessage(log,9001,from_user=user))
        await find_handler(c.router,'callback_query','cb_order_approve')(call,Bot(log))
        return log.events
    return asyncio.run(run())


def setup(c,mp,representation,kind=None,marker='both',mode='full',scenario='success'):
    c.scenario=scenario
    shared_setup(c,mp,'abangateway_payment',representation,kind,marker,mode,scenario)
    with c.db._get_conn() as conn:conn.execute('UPDATE custom_configs SET product_id=? WHERE id=?',(c.alpha_id,c.target))
    c.configure(overrides={c.alpha_id:kind if marker in {'product','both'} else None,c.beta_id:'composite'},representation=representation)
    if scenario=='inactive':
        with c.db._get_conn() as conn:conn.execute('UPDATE panel_servers SET is_active=0 WHERE id=?',(c.s1,))
    original=c.db.log_admin_action
    def audit(*a,**kw):c.trace.append(('audit',a,kw));return original(*a,**kw)
    mp.setattr(c.db,'log_admin_action',audit)
    c.router=handlers_admin.create_admin_router(c.db,is_main_bot=True);c.trace.clear()


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','target','product'])
@pytest.mark.parametrize('scenario',['success','update','prior'])
def test_composite_manual_custom_renewal(catalog,monkeypatch,representation,marker,scenario,caplog):
    c=catalog;setup(c,monkeypatch,representation,'composite',marker,scenario=scenario)
    before=dump(c.db);events=invoke(c)
    assert not c.trace and dump(c.db)==before
    assert len(events)==1 and events[0].show_alert and 'composite' in (events[0].text or '').lower()
    assert all(s not in str(events)+caplog.text for s in [LINK,'renew_name','fake_pass_1'])


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('mode',['full','volume','time'])
@pytest.mark.parametrize('scenario',['success','delivery','factory','update','usage','foreign','inactive','prior','lost_claim','apply_custom_config_renewal','approve_renewal_order'])
def test_legacy_manual_custom_renewal(catalog,monkeypatch,representation,kind,mode,scenario):
    c=catalog;setup(c,monkeypatch,representation,kind,mode=mode,scenario=scenario)
    before=dump(c.db);before_row=state(c)[0]
    with c.db._get_conn() as conn:sibling=dict(conn.execute('SELECT * FROM custom_configs WHERE id=?',(c.sibling,)).fetchone())
    error=scenario in {'factory','update','foreign','inactive'} or scenario=='usage' and mode=='full'
    crash=scenario in {'apply_custom_config_renewal','approve_renewal_order'}
    if crash:
        with pytest.raises(RuntimeError,match='synthetic failure'):invoke(c)
        events=[]
    else:events=invoke(c)
    answers=[e for e in events if e.kind=='callback_answer']
    if scenario in {'prior','lost_claim'}:
        assert len(answers)==1 and answers[0].text==ALREADY and dump(c.db)==before
        assert [e[0] for e in c.trace]==([] if scenario=='prior' else ['claim_order'])
        return
    if error:
        assert len(answers)==1 and answers[0].show_alert and answers[0].text.startswith('⛔️ تمدید ناموفق بود:')
        assert state(c)==(before_row,'pending') and len(c.db.get_custom_config_history(c.target))==1
        assert c.trace[-1]==('release_order_claim',(c.oid,),{})
    else:
        v,d={'full':(20,30),'volume':(5,0),'time':(0,10)}[mode]
        expected=['claim_order','factory','update']+(['usage'] if mode=='full' else [])+['apply_custom_config_renewal']+([] if scenario=='apply_custom_config_renewal' else ['approve_renewal_order'])+([] if crash else ['audit'])
        assert [e[0] for e in c.trace]==expected
        assert c.trace[2]==('update','renew_name',dict(add_volume_gb=v,add_days=d,reset_usage=mode=='full',preserve_remaining=mode=='full'))
        idx=4 if mode=='full' else 3
        assert c.trace[idx]==('apply_custom_config_renewal',(c.target,v,d),dict(full_reset=mode=='full',set_volume_gb=26 if mode=='full' else None))
        row,status=state(c);assert status==('processing' if crash else 'approved')
        if scenario=='apply_custom_config_renewal':assert row==before_row
        else:
            assert (row['volume_gb'],row['duration_days'],row['expires_at'])=={'full':(26,60,'2030-01-31T00:00:00'),'volume':(15,30,'2030-01-01T00:00:00'),'time':(10,40,'2030-01-11T00:00:00')}[mode]
            assert (row['user_id'],row['product_id'],row['username'],row['subscription_url'])==(USER_ID,c.alpha_id,'renew_name',LINK)
            h=c.db.get_custom_config_history(c.target);assert [(r['event_type'],r['detail']) for r in h]==[('renewal',f'+{v} گیگ / +{d} روز'),('purchase','10 گیگ / 30 روز')]
        if not crash:
            assert len(answers)==1 and answers[0].text=='سفارش تایید و سرویس تمدید شد.'
            assert scenario=='delivery' or any(e.kind=='send_message' and e.text=='✅ سرویس شما با موفقیت تمدید شد.' and e.chat_id==USER_ID for e in events)
            with c.db._get_conn() as conn:assert [r[0] for r in conn.execute('SELECT action FROM admin_logs')]==['renewal_approve']
            state_after=dump(c.db);c.trace.clear();assert [e.text for e in invoke(c) if e.kind=='callback_answer']==[ALREADY]
            assert not c.trace and dump(c.db)==state_after
    with c.db._get_conn() as conn:assert dict(conn.execute('SELECT * FROM custom_configs WHERE id=?',(c.sibling,)).fetchone())==sibling
    assert c.db.get_wallet_credit(USER_ID)==0 and c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==0
