"""T050dp/dq: independent settlement caller guards over real alias getters."""
import asyncio
import pytest
from tests.integration.test_composite_extra_cancel_alias_guards import alias, ALIASES, STATUSES, catalog, dump, USER_ID
from tests.integration.test_composite_extra_admin_guards import egp


@pytest.mark.parametrize('entry',['check','process'])
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('name',ALIASES)
@pytest.mark.parametrize('status',STATUSES)
@pytest.mark.parametrize('kind',['composite',None,'legacy'])
def test_settlement_alias(catalog,monkeypatch,entry,representation,name,status,kind):
    c=catalog;alias(c,monkeypatch,name,kind,representation)
    c.db.update_extra_invoice_status(c.iid,status);c.invoice_trace.clear()
    row=c.db.get_extra_invoice(c.iid);calls=[]
    async def check(db, invoice):calls.append(('check',db,dict(invoice)));return 'verified_now'
    async def deliver(db, bot, invoice, notify):calls.append(('deliver',db,bot,dict(invoice),notify));return 'alias delivered'
    if entry=='process':
        monkeypatch.setattr(egp,'check_invoice',check);monkeypatch.setattr(egp,'deliver',deliver)
    before=dump(c.db);decoy=dict(c.db.get_extra_invoice(c.decoy))
    def invoke():return asyncio.run(egp.check_invoice(c.db,row)) if entry=='check' else asyncio.run(egp.process_invoice(c.db,c.bot,row,c.notify))
    result=invoke()
    if kind=='composite':
        text=result if entry=='check' else result[0]
        assert text.startswith('error:') and 'composite' in text.lower(), 'missing T052 settlement alias refusal'
        if entry=='process':assert result[1]==''
        assert invoke()==result and dump(c.db)==before and not calls and not c.remote and not c.invoice_trace and not c.trace
    elif entry=='process':
        assert result==('verified_now','alias delivered')
        assert calls==[('check',c.db,dict(row)),('deliver',c.db,c.bot,dict(row),c.notify)]
        assert dump(c.db)==before and not c.remote and not c.invoice_trace and not c.trace
    else:
        expected='already_delivered' if status=='completed' else 'expired' if status in {'expired','cancelled'} else 'verified_now'
        assert result==expected
        assert c.remote==([('zarinpal','synthetic-remote','synthetic-number',990)] if status in {'new','pending'} else [])
        assert c.invoice_trace==([('claim_extra_invoice',(c.iid,))] if status in {'new','pending'} else [])
        assert c.db.get_extra_invoice(c.iid)['status']==('completed' if status in {'new','pending'} else status)
        retained=lambda rows:[x for x in rows if not x.startswith('INSERT INTO "extra_gateway_invoices"')]
        assert retained(dump(c.db))==retained(before) and not c.trace and not calls
        fresh=c.db.get_extra_invoice(c.iid);saved=dump(c.db);remote=list(c.remote);trace=list(c.invoice_trace)
        assert asyncio.run(egp.check_invoice(c.db,fresh))==('expired' if status in {'expired','cancelled'} else 'already_delivered')
        assert dump(c.db)==saved and c.remote==remote and c.invoice_trace==trace
    assert dict(c.db.get_extra_invoice(c.decoy))==decoy


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('name',ALIASES)
@pytest.mark.parametrize('status',['pending','approved','rejected'])
@pytest.mark.parametrize('kind',['composite',None,'legacy'])
def test_deliver_alias(catalog,monkeypatch,representation,name,status,kind):
    c=catalog;alias(c,monkeypatch,name,kind,representation)
    with c.db._get_conn() as conn:conn.execute('UPDATE orders SET status=? WHERE id=?',(status,c.oid))
    calls=[];messages=[]
    async def finalize(db,bot,ref,notify_admins_fn=None):calls.append((db,bot,ref,notify_admins_fn));return 'alias delivered'
    async def send(uid,text,**kw):messages.append((uid,text,kw))
    monkeypatch.setattr(egp.abangateway_payment,'finalize_paid_order',finalize)
    monkeypatch.setattr(c.bot,'send_message',send)
    monkeypatch.setattr(c.db,'list_admins',lambda:[9001,9002])
    before=dump(c.db);row=c.db.get_extra_invoice(c.iid)
    def invoke():return asyncio.run(egp.deliver(c.db,c.bot,row,c.notify))
    result=invoke()
    if kind=='composite':
        assert 'composite' in result.lower(), 'missing T052 deliver alias refusal'
        assert invoke()==result and not calls and not messages
    elif status in {'pending','approved'}:
        assert result=='alias delivered' and calls==[(c.db,c.bot,c.oid,c.notify)] and not messages
    else:
        assert result=='⚠️ پرداخت شما دریافت شد ولی این سفارش دیگر فعال نیست. با پشتیبانی تماس بگیرید.'
        title=egp.registry.GATEWAYS['zarinpal']['title']
        expected=f'⚠️ پرداخت {title} برای سفارش #{c.oid} (کاربر {USER_ID}) دریافت شد ولی وضعیت سفارش «rejected» است. لطفاً دستی رسیدگی کنید.'
        assert messages==[(9001,expected,{}),(9002,expected,{})] and not calls
    assert dump(c.db)==before and not c.trace and not c.remote and not c.invoice_trace
