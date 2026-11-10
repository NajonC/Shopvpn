"""T050dt/du: independent Stars and user-status alias admission."""
import asyncio
from types import SimpleNamespace
import pytest
from aiogram import Router
from tests._harness.legacy_bot import find_handler
from tests.integration.test_composite_extra_cancel_alias_guards import alias,ALIASES,STATUSES,catalog,dump,USER_ID
import extra_gateway_user as user


@pytest.mark.parametrize('entry',['pre','success','check'])
@pytest.mark.parametrize('name',ALIASES)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',['composite',None,'legacy'])
@pytest.mark.parametrize('status',STATUSES)
def test_adapter_alias(catalog,monkeypatch,entry,name,representation,kind,status):
    c=catalog;alias(c,monkeypatch,name,kind,representation)
    gateway='zarinpal' if entry=='check' else 'tgstars'
    with c.db._get_conn() as conn:conn.execute('UPDATE extra_gateway_invoices SET gateway=?,status=? WHERE id=?',(gateway,status,c.iid))
    c.effects=[];c.answers=[];c.messages=[];c.bot=object()
    async def answer(*a,**kw):c.answers.append((a,kw))
    async def message(*a,**kw):c.messages.append((a,kw))
    async def payable(*a):c.effects.append(('payable',a));return True
    async def stars(*a):c.effects.append(('stars',a));return 'selected Stars result'
    async def process(*a):c.effects.append(('process',a));return 'verified_now','selected check result'
    monkeypatch.setattr(user.egp,'ref_still_payable',payable)
    monkeypatch.setattr(user.egp,'process_stars_payment',stars)
    monkeypatch.setattr(user.egp,'process_invoice',process)
    notifier=object();monkeypatch.setitem(user.egp._order_notifiers,id(c.db),notifier)
    row=c.db.get_extra_invoice(c.iid);amount=row['payable_amount']
    router=Router();user.register_early(router,c.db,True)
    payment=SimpleNamespace(invoice_payload=f'xg:{c.iid}',total_amount=amount,currency='XTR',telegram_payment_charge_id='synthetic-alias-charge')
    obj=SimpleNamespace(invoice_payload=payment.invoice_payload,total_amount=amount,currency='XTR',from_user=SimpleNamespace(id=USER_ID),answer=answer,successful_payment=payment,data=f'xgw_check:{c.iid}',message=SimpleNamespace(answer=message))
    fn=find_handler(router,{'pre':'pre_checkout_query','success':'message','check':'callback_query'}[entry],{'pre':'stars_pre_checkout','success':'stars_successful_payment','check':'cb_check_extra_gateway'}[entry])
    before=dump(c.db)
    for _ in range(2):
        c.effects.clear();c.answers.clear();c.messages.clear()
        asyncio.run(fn(obj) if entry=='pre' else fn(obj,c.bot))
        if kind=='composite':
            assert not c.effects, 'missing T052 adapter alias admission'
            assert not c.messages and len(c.answers)==1
            a,kw=c.answers[0]
            if entry=='pre':assert not a and kw['ok'] is False and 'composite' in kw['error_message'].lower()
            else:
                assert len(a)==1 and 'composite' in a[0].lower()
                assert kw==({'show_alert':True} if entry=='check' else {})
        elif entry=='pre':
            assert c.answers==[((),{'ok':True})] if status in {'new','pending'} else c.answers==[((),{'ok':False,'error_message':'این فاکتور دیگر معتبر نیست. لطفاً دوباره از منو اقدام کن.'})]
            assert c.effects==([('payable',(c.db,row))] if status in {'new','pending'} else []) and not c.messages
        elif entry=='success':
            assert c.effects==[('stars',(c.db,c.bot,c.iid,USER_ID,amount,'XTR','synthetic-alias-charge',notifier))]
            assert c.answers==[(('selected Stars result',),{})] and not c.messages
        else:
            assert c.effects==[('process',(c.db,c.bot,row,notifier))]
            assert c.answers==[(('در حال بررسی وضعیت پرداخت...',),{})]
            assert c.messages==[(('selected check result',),{})]
        assert dump(c.db)==before and not c.trace and not c.remote and not c.invoice_trace
