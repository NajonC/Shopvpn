"""T050ct/cu: direct check, real remote dispatch and invoice SQL; synthetic providers."""
import asyncio
import pytest
from tests.integration.test_composite_extra_order_entry_guards import catalog, setup, dump, USER_ID, GATEWAYS, user
from tests.integration.test_composite_legacy_guards import as_row
egp=user.egp


def prepare(c,mp,key,representation,kind=None,marker='order',scenario='paid'):
    setup(c,mp,key,representation,kind,marker)
    c.iid=c.db.create_extra_invoice(key,'order',c.oid,USER_ID,900,990 if key=='cubepay' else 36 if key=='tgstars' else 900,'selected-remote','selected-number',meta={'payment_id':'selected-payment','price_usd':1.25})
    if scenario in {'completed','cancelled','expired','pending_status'}:c.db.update_extra_invoice_status(c.iid,'pending' if scenario=='pending_status' else scenario)
    if scenario=='no_payment_id':
        with c.db._get_conn() as conn:conn.execute("UPDATE extra_gateway_invoices SET meta='{}' WHERE id=?",(c.iid,))
    c.checks=[];c.writes=[]
    for name in ['claim_extra_invoice','update_extra_invoice_status','release_extra_invoice']:
        original=getattr(c.db,name)
        def call(*args,_name=name,_fn=original):
            c.writes.append((_name,args))
            if scenario=='claim_lost' and _name=='claim_extra_invoice':assert _fn(*args)
            return _fn(*args)
        mp.setattr(c.db,name,call)
    for gateway in GATEWAYS[:-1]:
        name=gateway+'_verify' if gateway!='nowpayments' else 'nowpayments_payment_status'
        async def remote(*args,_gateway=gateway):
            c.checks.append((_gateway,args))
            if scenario=='error':raise egp.clients.GatewayError('synthetic verify failure')
            return {'synthetic':'payment'} if _gateway=='nowpayments' else egp.clients.FAILED if scenario=='failed' else egp.clients.PENDING if scenario=='pending' else egp.clients.PAID
        mp.setattr(egp.clients,name,remote)
    def classify(*args):
        c.checks.append(('classify',args))
        return egp.clients.FAILED if scenario=='failed' else egp.clients.PENDING if scenario=='pending' else egp.clients.PAID
    mp.setattr(egp.clients,'nowpayments_classify',classify)
    return as_row(dict(c.db.get_extra_invoice(c.iid)),representation)


def run(c,row):return asyncio.run(egp.check_invoice(c.db,row))


@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('scenario',['paid','failed','completed','cancelled'])
def test_direct_check_composite_admission(catalog,monkeypatch,key,representation,marker,scenario):
    c=catalog;row=prepare(c,monkeypatch,key,representation,'composite',marker,scenario);before=dump(c.db)
    result=run(c,row)
    assert result.startswith('error:') and 'composite' in result.lower(), 'missing T052 direct check composite refusal'
    assert run(c,row)==result and dump(c.db)==before and not c.checks and not c.writes and not c.trace


@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('scenario',['paid','pending_status','pending','failed','error','completed','cancelled','expired','claim_lost','no_payment_id'])
def test_direct_check_legacy_contract(catalog,monkeypatch,key,representation,kind,scenario):
    c=catalog;row=prepare(c,monkeypatch,key,representation,kind,scenario=scenario);before=dump(c.db);decoy=dict(c.db.get_extra_invoice(c.decoy));order=dict(c.db.get_order(c.oid))
    terminal=scenario in {'completed','cancelled','expired'}
    remote=not terminal and key!='tgstars' and not(key=='nowpayments' and scenario=='no_payment_id')
    result=run(c,row)
    expected='already_delivered' if scenario=='completed' else 'expired' if scenario in {'cancelled','expired'} else 'not_paid_yet' if not remote or scenario=='pending' else 'expired' if scenario=='failed' else 'error:synthetic verify failure' if scenario=='error' else 'already_delivered' if scenario=='claim_lost' else 'verified_now'
    assert result==expected
    args=('synthetic-key',900,'selected-remote') if key in {'zarinpal','aqayepardakht'} else ('synthetic-key','selected-remote') if key=='tetra98' else ('synthetic-key','selected-remote','selected-number',9900) if key=='cubepay' else ('synthetic-key','selected-payment')
    checks=[(key,args)] if remote else []
    if remote and key=='nowpayments' and scenario!='error':checks.append(('classify',({'synthetic':'payment'},'selected-remote','selected-number',1.25)))
    assert c.checks==checks
    writes=[('update_extra_invoice_status',(c.iid,'expired'))] if remote and scenario=='failed' else [('claim_extra_invoice',(c.iid,))] if remote and scenario not in {'pending','error'} else []
    assert c.writes==writes
    status='expired' if remote and scenario=='failed' else 'completed' if writes and writes[0][0]=='claim_extra_invoice' else row['status']
    assert c.db.get_extra_invoice(c.iid)['status']==status and dict(c.db.get_extra_invoice(c.decoy))==decoy
    assert dict(c.db.get_order(c.oid))==order and not c.trace and not c.remote
    if not writes:assert dump(c.db)==before
    saved=dump(c.db);c.checks.clear();c.writes.clear()
    fresh=as_row(dict(c.db.get_extra_invoice(c.iid)),representation)
    repeat=run(c,fresh)
    assert repeat==('already_delivered' if status=='completed' else 'expired' if status=='expired' else expected)
    assert dump(c.db)==saved
    if status in {'completed','expired','cancelled'}:assert not c.checks and not c.writes
