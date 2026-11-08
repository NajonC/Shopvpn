"""T050cl/cm: real registered order entry, invoice SQL and presentation.
Remote create and Telegram only are synthetic; this is no wire-protocol evidence.
"""
import asyncio
import json
from types import SimpleNamespace
import pytest
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import SendInvoice
from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
import extra_gateway_user as user
from tests._harness.legacy_bot import FakeUser, FakeMessage, TelegramLog
from tests.integration.test_composite_gateway_stock_guards import catalog, setup as stock_setup, dump, USER_ID
GATEWAYS=['zarinpal','aqayepardakht','tetra98','cubepay','nowpayments','tgstars']


def invoices(c):
    with c.db._get_conn() as conn:return [dict(r) for r in conn.execute('SELECT * FROM extra_gateway_invoices ORDER BY id')]


def setup(c,mp,key,representation='sqlite',kind=None,marker='order',scenario='success'):
    stock_setup(c,mp,'abangateway_payment',representation,kind,marker)
    c.key=key;c.scenario=scenario;c.remote=[];c.sent=[];c.hooks=[]
    mp.setattr(user.egp,'API_BASE_URL','https://shop.example.invalid')
    c.db.set_setting('miniapp_tenant_id','synthetic-tenant')
    for k in GATEWAYS:
        c.db.set_setting(user.registry.enable_setting(k),'1')
        for f in user.registry.GATEWAYS[k]['fields']:
            if f['required']:c.db.set_setting(f['setting'],'synthetic-key')
    c.db.set_setting('tgstars_rate_toman_per_star','25')
    c.db.set_setting('cubepay_fee','10')
    for k in GATEWAYS[:-1]:
        async def remote(*args,_key=k):
            c.remote.append((_key,args))
            if scenario=='remote':raise user.egp.clients.GatewayError('synthetic remote refusal')
            return dict(remote_id='synthetic-remote',payment_url='https://pay.example.invalid/selected',meta={'retained':'selected','pay_amount_toman':991,'bot_url':'https://t.me/synthetic_payment_bot'})
        mp.setattr(user.egp.clients, k+'_create' if k!='nowpayments' else 'nowpayments_create_invoice',remote)
    async def usd(db,amount):
        assert db is c.db and amount==900
        return 1.25
    mp.setattr(user.egp.crypto_payment,'toman_to_usd',usd)
    mp.setattr(user.egp.secrets,'token_hex',lambda n:'1234abcd')
    c.log=TelegramLog();c.message=FakeMessage(c.log,USER_ID,from_user=FakeUser(USER_ID));c.answers=[]
    async def answer(text,**kw):c.answers.append((text,kw))
    c.call=SimpleNamespace(data='pay_'+key,from_user=FakeUser(USER_ID+1 if scenario=='foreign' else USER_ID),message=c.message,answer=answer)
    class Bot:
        async def send_invoice(self,**kw):
            c.sent.append(kw)
            if scenario=='telegram':raise TelegramBadRequest(method=SendInvoice(**kw),message='synthetic presentation failure')
    c.bot=Bot();c.data={'order_id':c.oid,'keep':'unchanged'}
    if scenario=='missing':c.data['order_id']=99999
    if scenario=='empty':c.data.pop('order_id')
    if scenario=='closed':
        with c.db._get_conn() as conn:conn.execute("UPDATE orders SET status='rejected' WHERE id=?",(c.oid,))
    if scenario=='disabled':c.db.set_setting(user.registry.enable_setting(key),'0')
    async def get_data():return dict(c.data)
    c.state=SimpleNamespace(get_data=get_data)
    async def order_error(order,key):
        c.hooks.append((dict(order),key))
        return 'synthetic policy refusal' if scenario=='policy' else None
    async def topup_error(*args):raise AssertionError('wrong flow')
    c.router=Router();user.register(c.router,c.db,True,order_error,topup_error,c.notify)
    handlers=c.router.callback_query.handlers
    # Four registrations per gateway, with the same order closure for three flows.
    offset=GATEWAYS.index(key)*4
    c.handler=handlers[offset].callback
    assert all(handlers[offset+i].callback is c.handler for i in range(3))
    assert user.egp._order_notifiers[id(c.db)] is c.notify
    c.decoy=c.db.create_extra_invoice(key,'order',99999,USER_ID,111,11,meta={'decoy':True})


def invoke(c):return asyncio.run(c.handler(c.call,c.state,c.bot))


def check_present(c,row):
    label=f'سفارش #{c.oid} - Stock'
    if c.key=='tgstars':
        assert len(c.sent)>=1
        assert c.sent[-1]==dict(chat_id=USER_ID,title='پرداخت با استارز تلگرام',description=f'{label} - 900 تومان معادل 36 استارز',payload=f'xg:{row["id"]}',provider_token='',currency='XTR',prices=[user.LabeledPrice(label=label,amount=36)])
        if c.scenario=='telegram':assert c.log.events[-1].text=='⚠️ ساخت فاکتور استارز ناموفق بود: synthetic presentation failure'
        else:assert not c.log.events
    else:
        e=c.log.events[-1];meta=user.registry.GATEWAYS[c.key]
        lines=[f"{meta['icon']} فاکتور پرداخت ({meta['title']}) ساخته شد. روی دکمه‌ی زیر بزن و پرداخت رو تکمیل کن."]
        if c.key=='cubepay':lines.append('💰 مبلغ دقیق قابل پرداخت: 991 تومان')
        lines+=['⏳ اعتبار این فاکتور محدود است.',user._DONE_TEXT['order']+'؛ اگر چند دقیقه طول کشید، دکمه‌ی «بررسی وضعیت پرداخت» را بزن.']
        assert e.text=='\n'.join(lines)
        rows=e.reply_markup.inline_keyboard
        assert rows[0][0].url=='https://pay.example.invalid/selected'
        assert rows[-1][0].callback_data==f'xgw_check:{row["id"]}'
        assert len(rows)==(3 if c.key=='tetra98' else 2)
        if c.key=='tetra98':assert rows[1][0].url=='https://t.me/synthetic_payment_bot'


@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('existing',[False,True])
@pytest.mark.parametrize('scenario',['success','foreign'])
def test_composite_order_entry(catalog,monkeypatch,key,representation,marker,existing,scenario):
    c=catalog;setup(c,monkeypatch,key,representation,'composite',marker,scenario)
    if existing:c.db.create_extra_invoice(key,'order',c.oid,USER_ID,900,36,payment_url='https://pay.example.invalid/selected')
    before=dump(c.db);invoke(c)
    assert not c.remote and not c.sent and not c.hooks and dump(c.db)==before
    assert len(c.answers)==1 and c.answers[0][1]=={'show_alert':True}
    assert 'composite' in c.answers[0][0].lower() and not c.log.events


@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
def test_legacy_order_entry_repeat(catalog,monkeypatch,key,representation,kind):
    c=catalog;setup(c,monkeypatch,key,representation,kind)
    before=dump(c.db);order=dict(c.db.get_order(c.oid));decoy=invoices(c)[0]
    invoke(c);rows=invoices(c);assert len(rows)==2 and rows[0]==decoy
    row=rows[-1]
    assert (row['gateway'],row['kind'],row['ref_id'],row['user_id'],row['amount_toman'],row['payable_amount'],row['status'])==(key,'order',c.oid,USER_ID,900,36 if key=='tgstars' else 990 if key=='cubepay' else 900,'new')
    assert row['id']!=c.oid and row['order_number']==f'o{c.oid}x1234abcd'
    assert dict(c.db.get_order(c.oid))==order and not c.trace
    assert c.answers==[('در حال ساخت فاکتور...',{})] and len(c.hooks)==1
    check_present(c,row)
    if key!='tgstars':
        args=c.remote[0][1];assert args[0]=='synthetic-key'
        if key=='nowpayments':assert args[1:]==(1.25,f'o{c.oid}x1234abcd',f'سفارش #{c.oid} - Stock','https://shop.example.invalid/api/webhooks/nowpayments?b=synthetic-tenant')
        else:
            assert args[1:5]==(990 if key=='cubepay' else 900,f'https://shop.example.invalid/api/pay-return/{key}?b=synthetic-tenant',f'سفارش #{c.oid} - Stock',f'o{c.oid}x1234abcd')
            if key=='cubepay':assert args[5:]==(USER_ID,)
        assert json.loads(row['meta'])['retained']=='selected'
    saved=dump(c.db);invoke(c);assert dump(c.db)==saved and len(c.remote)==int(key!='tgstars')
    assert len(c.hooks)==2 and len(c.answers)==2
    check_present(c,row)


@pytest.mark.parametrize('key,scenario',[(k,s) for k in GATEWAYS for s in ['empty','missing','closed','disabled','policy','remote','foreign'] if (k,s)!=('tgstars','remote')])
def test_legacy_order_entry_boundaries(catalog,monkeypatch,key,scenario):
    c=catalog;setup(c,monkeypatch,key,scenario=scenario);before=dump(c.db);invoke(c)
    if scenario=='foreign':
        # Characterize existing legacy missing-owner fence; composite guard must
        # still refuse a selected composite alias. No authority fix in T050.
        assert invoices(c)[-1]['user_id']==USER_ID+1 and invoices(c)[-1]['ref_id']==c.oid
        assert dict(c.db.get_order(c.oid))['user_id']==USER_ID
        return
    assert dump(c.db)==before and not c.sent and not c.trace
    expected='سفارش معتبر یافت نشد.' if scenario in {'empty','missing','closed'} else 'این روش پرداخت در حال حاضر در دسترس نیست.' if scenario=='disabled' else 'synthetic policy refusal' if scenario=='policy' else 'در حال ساخت فاکتور...'
    assert c.answers==[(expected,{} if scenario=='remote' else {'show_alert':True})]
    assert len(c.remote)==int(scenario=='remote') and len(c.hooks)==int(scenario in {'policy','remote'})
    assert [e.text for e in c.log.events]==(['⚠️ synthetic remote refusal'] if scenario=='remote' else [])


def test_stars_presentation_failure_retains_invoice(catalog,monkeypatch):
    c=catalog;setup(c,monkeypatch,'tgstars',scenario='telegram');invoke(c)
    row=invoices(c)[-1];assert row['ref_id']==c.oid and row['status']=='new'
    check_present(c,row);saved=invoices(c);invoke(c);assert invoices(c)==saved and len(c.sent)==2


def test_secondary_register_has_no_handlers_or_notifier(catalog):
    router=Router();user.egp._order_notifiers.pop(id(catalog.db),None)
    user.register(router,catalog.db,False,None,None,None)
    assert not router.callback_query.handlers and id(catalog.db) not in user.egp._order_notifiers
