"""T050dn/do: independent direct creation and payable alias admission."""
import asyncio
import pytest
from tests.integration.test_composite_extra_cancel_alias_guards import alias, ALIASES, STATUSES, catalog, dump, USER_ID
from tests.integration.test_composite_extra_order_entry_guards import GATEWAYS
from tests.integration.test_composite_extra_admin_guards import egp


def configure(c, mp, key):
    mp.setattr(egp,'API_BASE_URL','https://shop.example.invalid')
    c.db.set_setting(egp.registry.enable_setting(key),'1')
    for field in egp.registry.GATEWAYS[key]['fields']:
        if field['required']:c.db.set_setting(field['setting'],'123')
    c.db.set_setting('tgstars_rate_toman_per_star','25')
    c.db.set_setting('cubepay_fee','10')
    async def remote(*args):
        c.remote.append(args)
        return {'remote_id':'alias-remote','payment_url':'https://pay.example.invalid/alias','meta':{'alias':True}}
    if key!='tgstars':mp.setattr(egp.clients,key+'_create' if key!='nowpayments' else 'nowpayments_create_invoice',remote)
    async def usd(db, amount):assert db is c.db and amount==900;return 1.25
    mp.setattr(egp.crypto_payment,'toman_to_usd',usd)
    numbers=iter(['1234abcd','1234abce','1234abcf'])
    mp.setattr(egp.secrets,'token_hex',lambda n:next(numbers))


def create(c,key):return asyncio.run(egp.create_invoice_for(c.db,'alias-tenant',USER_ID,key,'order',c.oid,900,'Alias order'))


@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('name',ALIASES)
@pytest.mark.parametrize('existing',[False,True])
def test_create_composite_alias(catalog,monkeypatch,key,representation,name,existing):
    c=catalog;alias(c,monkeypatch,name,'composite',representation);configure(c,monkeypatch,key)
    with c.db._get_conn() as conn:
        conn.execute('DELETE FROM extra_gateway_invoices WHERE id=?',(c.iid,))
    if existing:c.db.create_extra_invoice(key,'order',c.oid,USER_ID,900,36)
    calls=[];old=c.db.get_pending_extra_invoice_for_ref
    def pending(*a):calls.append(a);return old(*a)
    monkeypatch.setattr(c.db,'get_pending_extra_invoice_for_ref',pending)
    before=dump(c.db)
    for _ in range(2):
        with pytest.raises(egp.ExtraGatewayError,match='(?i)composite'):create(c,key)
        assert not calls and not c.remote and not c.trace and not c.invoice_trace and dump(c.db)==before


@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('name',ALIASES)
def test_create_legacy_alias(catalog,monkeypatch,key,kind,name):
    c=catalog;alias(c,monkeypatch,name,kind,'sqlite');configure(c,monkeypatch,key)
    with c.db._get_conn() as conn:conn.execute('DELETE FROM extra_gateway_invoices WHERE id=?',(c.iid,))
    before=dump(c.db);decoy=dict(c.db.get_extra_invoice(c.decoy));result=create(c,key);row=dict(c.db.get_extra_invoice(result['invoice_id']))
    payable=36 if key=='tgstars' else 990 if key=='cubepay' else 900
    assert result==dict(invoice_id=row['id'],gateway=key,payable_amount=payable,payment_url=None if key=='tgstars' else 'https://pay.example.invalid/alias',meta={} if key=='tgstars' else {'alias':True})
    assert (row['kind'],row['ref_id'],row['user_id'],row['amount_toman'],row['status'],row['order_number'])==('order',c.oid,USER_ID,900,'new',f'o{c.oid}x1234abcd')
    assert row['remote_id']==(None if key=='tgstars' else 'alias-remote')
    assert [x for x in dump(c.db) if not x.startswith('INSERT INTO "extra_gateway_invoices"') and not x.startswith('INSERT INTO "sqlite_sequence"')]==[x for x in before if not x.startswith('INSERT INTO "extra_gateway_invoices"') and not x.startswith('INSERT INTO "sqlite_sequence"')]
    saved=dump(c.db);assert create(c,key)==result and dump(c.db)==saved
    assert dict(c.db.get_extra_invoice(c.decoy))==decoy
    assert len(c.remote)==int(key!='tgstars') and not c.trace and not c.invoice_trace


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('name',ALIASES)
@pytest.mark.parametrize('status',STATUSES)
@pytest.mark.parametrize('kind',['composite',None,'legacy'])
def test_payable_alias(catalog,monkeypatch,representation,name,status,kind):
    c=catalog;alias(c,monkeypatch,name,kind,representation)
    c.db.update_extra_invoice_status(c.iid,status);c.invoice_trace.clear()
    row=c.db.get_extra_invoice(c.iid);before=dump(c.db)
    for _ in range(2):
        assert asyncio.run(egp.ref_still_payable(c.db,row)) is (kind!='composite'), 'missing T052 payable alias refusal'
        assert dump(c.db)==before and not c.remote and not c.trace and not c.invoice_trace
