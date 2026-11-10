"""T050eh/ei: independent SQL reseller gateway grant boundary, no caller guard."""
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog, USER_ID
from tests.integration.test_composite_extra_reseller_settlement import setup, isolated
from tests.integration.test_composite_ai_catalog_legacy import dump

ENTRY = 'complete_reseller_request_gateway_payment'
ACTIVE = 'awaiting_payment'

def prepare(c, mp, tier='bronze', kind=None, marker='request', scenario='success', percent=17):
    setup(c, mp, tier=tier, scenario=scenario)
    with c.db._get_conn() as conn:
        conn.execute('ALTER TABLE reseller_requests ADD COLUMN service_kind TEXT')
        conn.execute('ALTER TABLE products ADD COLUMN service_kind TEXT')
        conn.execute('UPDATE reseller_requests SET status=?, commission_percent=? WHERE id=?', (ACTIVE,percent,c.rid))
        if marker=='request':conn.execute('UPDATE reseller_requests SET service_kind=? WHERE id=?',(kind,c.rid))
        elif marker=='product':conn.execute('UPDATE products SET service_kind=? WHERE id=?',(kind,c.pid))
        elif marker=='sibling':conn.execute("UPDATE reseller_requests SET service_kind='composite' WHERE id=?",(c.sibling,))
    c.trace.clear()

def invoke(c):return getattr(c.db, ENTRY)(c.rid)
def effects(c):return [x for x in c.trace if x[0]!=ENTRY]

@pytest.mark.parametrize('marker',['request','product'])
@pytest.mark.parametrize('tier',['bronze','silver','gold',None])
@pytest.mark.parametrize('scenario',['success','switch_agent_tier','set_user_reseller_tier'])
def test_direct_composite_refusal(catalog,monkeypatch,marker,tier,scenario,caplog):
    c=catalog;prepare(c,monkeypatch,tier,'composite',marker,scenario);before=dump(c.db)
    try:invoke(c)
    except (ValueError,RuntimeError) as exc:reason=str(exc)
    else:reason=''
    assert not effects(c) and dump(c.db)==before
    assert 'composite' in reason.lower()
    assert 'synthetic request' not in reason+caplog.text

@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('tier',['bronze','silver','gold','vip',None])
@pytest.mark.parametrize('marker',['request','product','sibling'])
def test_direct_supported_repeat(catalog,monkeypatch,kind,tier,marker):
    c=catalog;prepare(c,monkeypatch,tier,kind,marker);before=isolated(c)
    assert invoke(c) is True
    assert c.db.get_reseller_request(c.rid)['status']==('completed' if tier in ['bronze','silver'] else 'awaiting_bot_info')
    want=[]
    if tier:want.append(('switch_agent_tier',(USER_ID,tier),{}))
    if tier=='bronze':want.append(('enable_inline_reseller',(USER_ID,17),{}))
    if tier in ['bronze','silver']:want.append(('set_user_reseller_tier',(USER_ID,tier,23 if tier=='silver' else None),{}))
    assert effects(c)==want and isolated(c)==before and not c.sent
    u=c.db.get_user(USER_ID)
    assert (u['reseller_tier'],u['reseller_discount_percent'],u['inline_reseller_enabled'],u['inline_reseller_commission_percent'])==(tier if tier in ['bronze','silver'] else None,23 if tier=='silver' else None,1 if tier=='bronze' else 0,17 if tier=='bronze' else None)
    c.trace.clear();before=dump(c.db)
    assert invoke(c) is False and not effects(c) and dump(c.db)==before

@pytest.mark.parametrize('status',['pending_review','awaiting_payment_review','completed','awaiting_bot_info','rejected','missing'])
def test_direct_ineligible(catalog,monkeypatch,status):
    c=catalog;prepare(c,monkeypatch); 
    with c.db._get_conn() as conn:
        if status=='missing':conn.execute('DELETE FROM reseller_requests WHERE id=?',(c.rid,))
        else:conn.execute('UPDATE reseller_requests SET status=? WHERE id=?',(status,c.rid))
    before=dump(c.db)
    assert invoke(c) is False and not effects(c) and dump(c.db)==before

@pytest.mark.parametrize('scenario',['switch_agent_tier','enable_inline_reseller','set_user_reseller_tier'])
def test_direct_downstream_failure_no_recovery(catalog,monkeypatch,scenario):
    c=catalog;prepare(c,monkeypatch,scenario=scenario);before=isolated(c)
    with pytest.raises(RuntimeError,match='synthetic failure'):invoke(c)
    assert c.db.get_reseller_request(c.rid)['status']=='completed' and isolated(c)==before
    u=c.db.get_user(USER_ID)
    assert u['inline_reseller_enabled']==(1 if scenario=='set_user_reseller_tier' else 0)
    c.trace.clear();before=dump(c.db)
    assert invoke(c) is False and not effects(c) and dump(c.db)==before

@pytest.mark.parametrize('percent',[None,0,29])
def test_direct_commission_fallback(catalog,monkeypatch,percent):
    c=catalog;prepare(c,monkeypatch,percent=percent)
    assert invoke(c) is True
    assert c.db.get_user(USER_ID)['inline_reseller_commission_percent']==(29 if percent==29 else 10)
