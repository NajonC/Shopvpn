"""T050cp/cq: direct shared creation, independent of registered callbacks."""
import asyncio
import json
import pytest
from tests.integration.test_composite_extra_order_entry_guards import catalog, setup, invoices, GATEWAYS, USER_ID, user, dump
egp=user.egp


def create(c,ref=None,actor=USER_ID):
    return asyncio.run(egp.create_invoice_for(c.db,'synthetic-tenant',actor,c.key,'order',c.oid if ref is None else ref,900,'Direct selected order'))


@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('existing',[False,True])
def test_direct_composite_creation_refused(catalog,monkeypatch,key,representation,marker,existing):
    c=catalog;setup(c,monkeypatch,key,representation,'composite',marker)
    if existing:c.db.create_extra_invoice(key,'order',c.oid,USER_ID,900,36)
    lookups=[];lookup=c.db.get_pending_extra_invoice_for_ref
    def pending(*args):lookups.append(args);return lookup(*args)
    monkeypatch.setattr(c.db,'get_pending_extra_invoice_for_ref',pending)
    before=dump(c.db);reason=''
    try:create(c)
    except egp.ExtraGatewayError as exc:reason=str(exc)
    assert 'composite' in reason.lower(), 'missing T052 direct create composite refusal'
    assert not lookups and not c.remote and not c.sent and not c.trace and dump(c.db)==before


@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
def test_direct_legacy_creation_reuse(catalog,monkeypatch,key,representation,kind):
    c=catalog;setup(c,monkeypatch,key,representation,kind)
    before=invoices(c);order=dict(c.db.get_order(c.oid))
    result=create(c);row=invoices(c)[-1]
    payable=36 if key=='tgstars' else 990 if key=='cubepay' else 900
    meta={} if key=='tgstars' else {'retained':'selected','pay_amount_toman':991,'bot_url':'https://t.me/synthetic_payment_bot'}
    assert result==dict(invoice_id=row['id'],payment_url=None if key=='tgstars' else 'https://pay.example.invalid/selected',meta=meta,payable_amount=payable,gateway=key)
    assert invoices(c)[:-1]==before and row['id']!=c.oid
    assert (row['gateway'],row['kind'],row['ref_id'],row['user_id'],row['amount_toman'],row['payable_amount'],row['status'],row['order_number'])==(key,'order',c.oid,USER_ID,900,payable,'new',f'o{c.oid}x1234abcd')
    assert row['remote_id']==(None if key=='tgstars' else 'synthetic-remote') and json.loads(row['meta'])==meta
    if key!='tgstars':
        args=c.remote[0][1];assert args[0]=='synthetic-key'
        if key=='nowpayments':assert args[1:]==(1.25,f'o{c.oid}x1234abcd','Direct selected order','https://shop.example.invalid/api/webhooks/nowpayments?b=synthetic-tenant')
        else:
            assert args[1:5]==(payable,'https://shop.example.invalid/api/pay-return/'+key+'?b=synthetic-tenant','Direct selected order',f'o{c.oid}x1234abcd')
            assert args[5:]==((USER_ID,) if key=='cubepay' else ())
    saved=dump(c.db)
    assert create(c)==result and dump(c.db)==saved and len(c.remote)==int(key!='tgstars')
    assert dict(c.db.get_order(c.oid))==order and not c.trace and not c.sent and not c.hooks


@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('scenario',['disabled','remote','conversion'])
def test_direct_creation_failure(catalog,monkeypatch,key,scenario):
    c=catalog;setup(c,monkeypatch,key,scenario='remote' if scenario=='remote' else 'success')
    if scenario=='disabled':
        c.db.set_setting(user.registry.enable_setting(key),'0')
        c.db.create_extra_invoice(key,'order',c.oid,USER_ID,900,36)
    elif key=='tgstars':
        c.db.set_setting('tgstars_rate_toman_per_star','0')
        async def exchange(**kw):raise RuntimeError('synthetic conversion refusal')
        monkeypatch.setattr(egp.exchange_rate,'get_usd_to_toman_rate',exchange)
    elif scenario=='conversion':
        # Non-Stars/non-NowPayments creators have no conversion boundary.
        if key!='nowpayments':
            c.db.set_setting(user.registry.enable_setting(key),'0')
        else:
            async def usd(*args):raise egp.crypto_payment.CryptoPaymentError('synthetic conversion refusal')
            monkeypatch.setattr(egp.crypto_payment,'toman_to_usd',usd)
    before=dump(c.db)
    with pytest.raises(egp.ExtraGatewayError) as exc:create(c)
    assert str(exc.value) and dump(c.db)==before and not c.trace and not c.sent
    assert len(c.remote)==int(scenario=='remote' and key!='tgstars')
