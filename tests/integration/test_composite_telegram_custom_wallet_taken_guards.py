"""T050aq: selected-composite refusal and legacy username-taken compensation."""
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog,USER_ID
from tests.integration.test_composite_telegram_custom_wallet_guards import prepare as wallet_prepare,invoke,initial
from tests.integration.test_composite_ai_catalog_legacy import dump
from states import CustomConfigFlow
import panel_providers
from panel_providers import PanelUsernameTakenError

TAKEN='❌ این نام کاربری تکراری است، یک نام دیگر انتخاب کنید.\nمبلغ به کیف پول بازگردانده شد.'


def prepare(c,monkeypatch,representation,kind=None,path='fixed',wallet=1500,fault='create'):
    wallet_prepare(c,monkeypatch,representation,kind,path,wallet)
    c.fault=fault
    class Provider:
        def __init__(self,row):
            c.provider_calls.append(('factory',row['id'],row['panel_type']))
            if fault=='factory':raise PanelUsernameTakenError('fake-taken')
        async def create_user(self,username,volume,days):
            c.provider_calls.append(('create',username,volume,days))
            raise PanelUsernameTakenError('fake-taken')
    monkeypatch.setitem(panel_providers.PROVIDERS,'3xui',Provider)


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('path',['fixed','choice'])
@pytest.mark.parametrize('fault',['factory','create'])
def test_composite_taken_checkout_refused(catalog,monkeypatch,representation,path,fault,caplog):
    c=catalog;prepare(c,monkeypatch,representation,'composite',path,fault=fault)
    c.db.update_custom_config_product(c.alpha_id,name='SECRET-COMPOSITE')
    before=dump(c.db);events,state,data=invoke(c)
    assert c.provider_calls==[] and c.debits==[] and dump(c.db)==before
    assert state==(CustomConfigFlow.waiting_duration if path=='choice' else CustomConfigFlow.waiting_volume).state and data==initial(c)
    assert len(events)==1 and 'composite' in (events[0].text or '').lower()
    assert 'SECRET-COMPOSITE' not in str(events)+caplog.text and 'fake-taken' not in str(events)+caplog.text


def check_taken(c,wallet):
    events,state,data=invoke(c);days={'fixed':17,'choice':30,'global':45}[c.path]
    assert c.provider_calls==[('factory',c.s1,'3xui')]+([('create','newname',10,days)] if c.fault=='create' else [])
    assert c.debits==[(USER_ID,-1000),(USER_ID,1000)] and c.db.get_wallet_credit(USER_ID)==wallet
    orders=c.db.get_user_orders(USER_ID);assert len(orders)==1;o=orders[0]
    assert {k:o[k] for k in ['user_id','status','base_price','wallet_used','final_price','custom_product_id','custom_duration_days','custom_volume_gb','custom_username','custom_panel_server_id','admin_message_id']}==dict(user_id=USER_ID,status='rejected',base_price=1000,wallet_used=1000,final_price=0,custom_product_id=None if c.path=='global' else c.alpha_id,custom_duration_days=days,custom_volume_gb=10,custom_username='newname',custom_panel_server_id=c.s1,admin_message_id=None)
    assert c.db.get_custom_configs_for_user(USER_ID)==[]
    with c.db._get_conn() as conn:assert conn.execute('SELECT COUNT(*) FROM custom_config_history').fetchone()[0]==0
    assert state is None and data=={}
    assert len(events)==1 and events[0].kind=='message_answer' and events[0].text==TAKEN and events[0].reply_markup is None
    before=dump(c.db);assert c.db.reject_order(o['id']) is False
    assert dump(c.db)==before and c.debits==[(USER_ID,-1000),(USER_ID,1000)]


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('path',['fixed','choice','global'])
@pytest.mark.parametrize('wallet',[1000,1500])
@pytest.mark.parametrize('fault',['factory','create'])
def test_legacy_taken_exact_refund(catalog,monkeypatch,representation,kind,path,wallet,fault):
    c=catalog;prepare(c,monkeypatch,representation,kind,path,wallet,fault);check_taken(c,wallet)


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('path',['fixed','choice'])
def test_unrelated_composite_allows_taken_compensation(catalog,monkeypatch,representation,path):
    c=catalog;prepare(c,monkeypatch,representation,None,path)
    c.configure(overrides={c.beta_id:'composite'},representation=representation);check_taken(c,1500)
