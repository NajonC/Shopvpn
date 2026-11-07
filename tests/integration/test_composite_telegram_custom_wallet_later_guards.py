"""T050as: real full-wallet checkout with later fault injection; legacy defects are pinned."""
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog,USER_ID
from tests.integration.test_composite_telegram_custom_wallet_guards import prepare as wallet_prepare,invoke,initial,LINK
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests._harness.legacy_bot import RecordingBot
from states import CustomConfigFlow
import tests.integration.test_composite_telegram_custom_wallet_guards as wallet_module

FAULTS=['approve','config','history','config_after','delivery','admin']
UNEXPECTED='⛔️ خطای غیرمنتظره‌ای در پردازش سفارش رخ داد.\nاگر مبلغی از کیف پول شما کسر شده بود، به‌طور کامل بازگردانده شد. لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.'


def prepare(c,monkeypatch,representation,kind=None,path='fixed',wallet=1500,fault='config'):
    wallet_prepare(c,monkeypatch,representation,kind,path,wallet)
    c.fault=fault;c.fault_calls=[]
    # Inject at persistence boundaries, delegating to real SQL except the failed operation.
    if fault in ['approve','config','history','config_after']:
        name={'approve':'approve_custom_config_order','config':'add_custom_config','history':'add_custom_config_history','config_after':'add_custom_config'}[fault]
        original=getattr(c.db,name)
        def fail(*a,**kw):
            c.fault_calls.append(fault)
            if fault=='config_after':original(*a,**kw)
            raise RuntimeError('fake-later-error')
        monkeypatch.setattr(c.db,name,fail)
    class Bot(RecordingBot):
        def _send(self,kind,chat_id,text,**kw):
            if (fault=='delivery' and text and LINK in text) or (fault=='admin' and chat_id==9001):
                c.fault_calls.append(fault)
                raise RuntimeError('fake-later-error')
            return super()._send(kind,chat_id,text,**kw)
    monkeypatch.setattr(wallet_module,'RecordingBot',Bot)


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('path',['fixed','choice'])
@pytest.mark.parametrize('fault',FAULTS)
def test_composite_later_checkout_refused(catalog,monkeypatch,representation,path,fault,caplog):
    c=catalog;prepare(c,monkeypatch,representation,'composite',path,fault=fault)
    c.db.update_custom_config_product(c.alpha_id,name='SECRET-COMPOSITE')
    before=dump(c.db);events,state,data=invoke(c)
    assert c.provider_calls==[] and c.debits==[] and c.fault_calls==[] and dump(c.db)==before
    assert state==(CustomConfigFlow.waiting_duration if path=='choice' else CustomConfigFlow.waiting_volume).state and data==initial(c)
    assert len(events)==1 and 'composite' in (events[0].text or '').lower()
    assert 'SECRET-COMPOSITE' not in str(events)+caplog.text and LINK not in str(events)+caplog.text


def check_later(c,wallet):
    events,state,data=invoke(c);days={'fixed':17,'choice':30,'global':45}[c.path];pid=None if c.path=='global' else c.alpha_id
    assert c.provider_calls==[('factory',c.s1,'3xui'),('create','newname',10,days)] and c.fault_calls==[c.fault]
    refunded=c.fault=='approve'
    assert c.debits==[(USER_ID,-1000)]+([(USER_ID,1000)] if refunded else [])
    assert c.db.get_wallet_credit(USER_ID)==(wallet if refunded else wallet-1000)
    orders=c.db.get_user_orders(USER_ID);assert len(orders)==1;o=orders[0]
    assert {k:o[k] for k in ['user_id','status','base_price','wallet_used','final_price','custom_product_id','custom_duration_days','custom_volume_gb','custom_username','custom_panel_server_id','admin_message_id']}==dict(user_id=USER_ID,status='rejected' if refunded else 'approved',base_price=1000,wallet_used=1000,final_price=0,custom_product_id=pid,custom_duration_days=days,custom_volume_gb=10,custom_username='newname',custom_panel_server_id=c.s1,admin_message_id=None)
    configs=c.db.get_custom_configs_for_user(USER_ID)
    persisted=c.fault in ['history','config_after','delivery','admin']
    assert len(configs)==int(persisted)
    if persisted:
        row=configs[0]
        assert {k:row[k] for k in ['user_id','panel_server_id','username','volume_gb','duration_days','subscription_url','order_id','product_id','source']}==dict(user_id=USER_ID,panel_server_id=c.s1,username='panel_name',volume_gb=10,duration_days=days,subscription_url=LINK,order_id=o['id'],product_id=pid,source='custom_config')
        history=c.db.get_custom_config_history(row['id'])
        assert len(history)==int(c.fault!='history')
        if history:assert history[0]['event_type']=='purchase' and history[0]['detail']==f'10 گیگ / {days} روز'
    else:
        with c.db._get_conn() as conn:assert conn.execute('SELECT COUNT(*) FROM custom_config_history').fetchone()[0]==0
    assert state is None and data=={}
    if c.fault in ['approve','config','history','config_after']:
        assert len(events)==1 and events[0].kind=='message_answer' and events[0].text==UNEXPECTED
    elif c.fault=='delivery':
        assert [(e.kind,e.chat_id) for e in events]==[('message_answer',USER_ID),('send_photo',USER_ID),('message_answer',USER_ID)]
        assert events[-1].text==UNEXPECTED
    else:
        assert [(e.kind,e.chat_id) for e in events]==[('message_answer',USER_ID),('send_photo',USER_ID),('send_message',USER_ID),('send_message',USER_ID)]
        assert events[2].text==f'🔗 لینک اشتراک شما (برای کپی):\n`{LINK}`'
        assert all(e.text!=UNEXPECTED for e in events)
    before=dump(c.db);debits=list(c.debits)
    assert c.db.reject_order(o['id']) is False and dump(c.db)==before and c.debits==debits


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('path',['fixed','choice','global'])
@pytest.mark.parametrize('fault',FAULTS)
def test_legacy_later_exact_state(catalog,monkeypatch,representation,kind,path,fault):
    c=catalog;prepare(c,monkeypatch,representation,kind,path,fault=fault);check_later(c,1500)


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('fault',FAULTS)
def test_unrelated_composite_allows_later(catalog,monkeypatch,representation,fault):
    c=catalog;prepare(c,monkeypatch,representation,None,'choice',wallet=1000,fault=fault)
    c.configure(overrides={c.beta_id:'composite'},representation=representation);check_later(c,1000)
