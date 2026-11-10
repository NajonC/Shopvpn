"""T050dr/ds: nested label and upstream entry independently of direct create."""
import asyncio
from types import SimpleNamespace
import pytest
from aiogram import Router
from tests.integration.test_composite_extra_cancel_alias_guards import alias, ALIASES, catalog, dump, USER_ID
from tests.integration.test_composite_extra_order_entry_guards import GATEWAYS
import extra_gateway_user as user


def setup(c,mp,name,kind,representation,key):
    alias(c,mp,name,kind,representation)
    c.effects=[];c.answers=[];c.messages=[]
    async def answer(text,**kw):c.answers.append((text,kw))
    async def message(text,**kw):c.messages.append((text,kw))
    c.call=SimpleNamespace(from_user=SimpleNamespace(id=USER_ID),answer=answer,message=SimpleNamespace(answer=message))
    async def data():return {'order_id':c.oid,'retained':'yes'}
    c.state=SimpleNamespace(get_data=data);c.bot=object()
    async def policy(order,k):c.effects.append(('policy',dict(order),k));return None
    async def notify(*a):raise AssertionError('unexpected notifier')
    mp.setattr(user.egp,'is_available',lambda *a:True)
    async def create(*a):
        c.effects.append(('create',a));return {'invoice_id':765,'payable_amount':36,'payment_url':'https://pay.example.invalid','meta':{}}
    async def present(*a):c.effects.append(('present',a))
    mp.setattr(user.egp,'create_invoice_for',create);mp.setattr(user,'present_invoice',present)
    router=Router();user.register(router,c.db,True,policy,None,notify)
    c.handler=router.callback_query.handlers[GATEWAYS.index(key)*4].callback
    c.label=dict(zip(c.handler.__code__.co_freevars,c.handler.__closure__))['_order_label'].cell_contents
    order=c.db.get_order(c.oid)
    c.expected=f'تمدید سرویس #{c.oid}' if order['is_renewal'] else f"کانفیگ شخصی #{c.oid} - {order['custom_username']}"
    c.db.set_setting('miniapp_tenant_id','alias-tenant')


@pytest.mark.parametrize('entry',['label','handler'])
@pytest.mark.parametrize('name',ALIASES)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',['composite',None,'legacy'])
@pytest.mark.parametrize('key',GATEWAYS)
def test_entry_alias(catalog,monkeypatch,entry,name,representation,kind,key):
    c=catalog;setup(c,monkeypatch,name,kind,representation,key)
    before=dump(c.db);order=c.db.get_order(c.oid)
    for _ in range(2):
        c.effects.clear();c.answers.clear();c.messages.clear()
        if entry=='label':
            if kind=='composite':
                with pytest.raises(user.egp.ExtraGatewayError,match='(?i)composite'):
                    asyncio.run(c.label(order,c.oid))
            else:assert asyncio.run(c.label(order,c.oid))==c.expected
            assert not c.effects and not c.answers and not c.messages
        else:
            # A permissive label prevents the nested guard masking caller admission.
            async def label(*a):c.effects.append(('label',a));return c.expected
            dict(zip(c.handler.__code__.co_freevars,c.handler.__closure__))['_order_label'].cell_contents=label
            asyncio.run(c.handler(c.call,c.state,c.bot))
            if kind=='composite':
                assert not c.effects and not c.messages, 'missing T052 upstream alias refusal'
                assert len(c.answers)==1 and c.answers[0][1]=={'show_alert':True} and 'composite' in c.answers[0][0].lower()
            else:
                assert c.answers==[('در حال ساخت فاکتور...',{})] and not c.messages
                assert [e[0] for e in c.effects]==['policy','label','create','present']
                assert c.effects[0][1:]==(dict(order),key)
                assert c.effects[1][1]==(order,c.oid)
                assert c.effects[2][1]==(c.db,'alias-tenant',USER_ID,key,'order',c.oid,1000,c.expected)
                assert c.effects[3][1]==(c.call.message,c.bot,key,{'invoice_id':765,'payable_amount':36,'payment_url':'https://pay.example.invalid','meta':{}},'order',c.expected,1000)
        assert dump(c.db)==before and not c.trace and not c.remote and not c.invoice_trace
