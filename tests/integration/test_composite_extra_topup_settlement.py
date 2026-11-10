"""T050ed/ee actual wallet settlement; unrelated composite orders stay isolated.
Legacy authority/crash limitations are characterized, not repaired here.
"""
import asyncio
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog,USER_ID
from tests.integration.test_composite_legacy_guards import as_row
from tests.integration.test_composite_ai_catalog_legacy import dump
import extra_gateway_payment as egp

GATEWAYS=['zarinpal','tetra98','cubepay','nowpayments','aqayepardakht','tgstars']
MISSING='⚠️ درخواست شارژ یافت نشد.'
PRIOR='✅ این درخواست شارژ قبلاً بررسی شده است.'
OK='✅ پرداخت تایید شد و 1,234 تومان به کیف پول کاربر اضافه شد.'

def setup(c,mp,representation='sqlite',marker=None,gateway='zarinpal',scenario='success'):
    c.db.add_or_update_user(9002,'other','Other');c.db.add_wallet_credit(USER_ID,77)
    c.tid=c.db.create_topup(USER_ID,1234);c.sibling=c.db.create_topup(9002,999)
    # The topup reference collides with an unrelated composite custom order.
    c.oid=c.db.create_custom_config_order(USER_ID,1,'collision',c.s1,100,0,custom_product_id=c.alpha_id)
    assert c.oid==c.tid
    c.configure(overrides={c.alpha_id:marker},representation=representation)
    get_order=c.db.get_order
    def order(oid):
        row=dict(get_order(oid));row['service_kind']=marker;return as_row(row,representation)
    mp.setattr(c.db,'get_order',order)
    c.db.create_extra_invoice(gateway,'wallet_topup',99999,9002,1)
    c.iid=c.db.create_extra_invoice(gateway,'wallet_topup',c.tid,USER_ID,1234)
    c.invoice=as_row(dict(c.db.get_extra_invoice(c.iid)),representation)
    c.trace=[]
    class Bot:
        async def send_message(self,*a,**k):raise AssertionError('unexpected Telegram')
    c.bot=Bot()
    for name in ['get_topup','approve_topup','add_wallet_credit']:
        original=getattr(c.db,name)
        def wrap(*a,_name=name,_original=original,**kw):
            c.trace.append((_name,a,kw))
            if scenario==_name:raise RuntimeError('synthetic failure')
            return _original(*a,**kw)
        mp.setattr(c.db,name,wrap)
    async def forbidden(*a,**k):raise AssertionError('unexpected order settlement')
    mp.setattr(egp.abangateway_payment,'finalize_paid_order',forbidden)
    mp.setattr(egp,'_notify_admins',forbidden)

def invoke(c):return asyncio.run(egp.deliver(c.db,c.bot,c.invoice))
def snapshot(c):
    with c.db._get_conn() as conn:
        return {t:[tuple(r) for r in conn.execute('SELECT * FROM '+t+' ORDER BY 1')] for t in ['orders','custom_configs','extra_gateway_invoices']}

@pytest.mark.parametrize('gateway',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',[None,'legacy','composite'])
def test_topup_actual_success_repeat(catalog,monkeypatch,gateway,representation,marker):
    c=catalog;setup(c,monkeypatch,representation,marker,gateway);before=snapshot(c)
    assert c.iid!=c.tid
    assert invoke(c)==OK
    assert c.trace==[('get_topup',(c.tid,),{}),('approve_topup',(c.tid,),{}),('get_topup',(c.tid,),{}),('add_wallet_credit',(USER_ID,1234),{})]
    assert c.db.get_topup(c.tid)['status']=='approved'
    assert c.db.get_wallet_credit(USER_ID)==1311 and c.db.get_wallet_credit(9002)==0
    assert c.db.get_topup(c.sibling)['status']=='pending' and snapshot(c)==before
    c.trace.clear();before=dump(c.db);assert invoke(c)==PRIOR
    assert c.trace==[('get_topup',(c.tid,),{}),('approve_topup',(c.tid,),{}),('get_topup',(c.tid,),{})]
    assert dump(c.db)==before

@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('scenario',['approved','rejected','processing','missing','get_topup','approve_topup','add_wallet_credit','foreign_invoice','wrong_amount','completed_invoice','bad_reference','unknown_gateway'])
def test_topup_actual_boundaries(catalog,monkeypatch,representation,scenario):
    c=catalog;setup(c,monkeypatch,representation,'composite',scenario=scenario)
    inv=dict(c.invoice)
    if scenario in ['approved','rejected','processing']:
        with c.db._get_conn() as conn:conn.execute('UPDATE wallet_topups SET status=? WHERE id=?',(scenario,c.tid))
    if scenario=='missing':inv['ref_id']=99999
    if scenario=='foreign_invoice':inv['user_id']=9002
    if scenario=='wrong_amount':inv['amount_toman']=1
    if scenario=='completed_invoice':inv['status']='completed'
    if scenario=='bad_reference':inv['ref_id']='invalid'
    if scenario=='unknown_gateway':inv['gateway']='unknown'
    c.invoice=as_row(inv,representation);before=dump(c.db);isolated=snapshot(c)
    if scenario in ['get_topup','approve_topup','add_wallet_credit']:
        with pytest.raises(RuntimeError,match='synthetic failure'):invoke(c)
    elif scenario=='bad_reference':
        with pytest.raises(ValueError):invoke(c)
    elif scenario=='unknown_gateway':
        with pytest.raises(KeyError):invoke(c)
    else:assert invoke(c)==(MISSING if scenario=='missing' else PRIOR if scenario in ['approved','rejected','processing'] else OK)
    assert snapshot(c)==isolated
    if scenario in ['foreign_invoice','wrong_amount','completed_invoice']:
        # deliver assumes verification upstream; these are retained authority limitations.
        assert c.db.get_wallet_credit(USER_ID)==1311 and c.db.get_wallet_credit(9002)==0
    elif scenario=='add_wallet_credit':
        assert c.db.get_topup(c.tid)['status']=='approved' and c.db.get_wallet_credit(USER_ID)==77
        c.trace.clear();assert invoke(c)==PRIOR # committed status prevents credit recovery
    else:assert dump(c.db)==before
