"""T050cn/co: preserve unrelated topup entry, SQL and presentation controls.
Composite catalog/order aliases must not globally disable wallet topups.
"""
import asyncio
import json
from types import SimpleNamespace
import pytest
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import SendMessage
from tests.integration.test_composite_extra_order_entry_guards import catalog, setup as order_setup, invoices, GATEWAYS, USER_ID, user, dump


def topups(c):
    with c.db._get_conn() as conn:return [dict(r) for r in conn.execute('SELECT * FROM wallet_topups ORDER BY id')]


def setup(c,mp,key,scenario='success',representation='sqlite',kind='composite'):
    order_setup(c,mp,key,representation,kind,'both',scenario)
    c.topup_hooks=[]
    c.data={'topup_amount':900,'order_id':c.oid,'keep':'unchanged'}
    if scenario=='missing':c.data.pop('topup_amount')
    if scenario=='zero':c.data['topup_amount']=0
    c.initial_data=dict(c.data)
    async def order_error(*args):raise AssertionError('order policy incorrectly used')
    async def topup_error(amount,key):
        c.topup_hooks.append((amount,key))
        return 'synthetic topup refusal' if scenario=='policy' else None
    router=Router();user.register(router,c.db,True,order_error,topup_error,c.notify)
    c.handler=router.callback_query.handlers[GATEWAYS.index(key)*4+3].callback
    c.db.create_topup(USER_ID,111);c.db.create_topup(USER_ID,222)
    if scenario=='remote' and key=='tgstars':
        c.db.set_setting('tgstars_rate_toman_per_star','0')
        async def exchange(**kw):raise RuntimeError('synthetic exchange refusal')
        mp.setattr(user.egp.exchange_rate,'get_usd_to_toman_rate',exchange)
    if scenario=='telegram' and key!='tgstars':
        async def answer(*args,**kw):raise TelegramBadRequest(method=SendMessage(chat_id=USER_ID,text='synthetic'),message='synthetic presentation failure')
        mp.setattr(c.message,'answer',answer)


def invoke(c):return asyncio.run(c.handler(c.call,c.state,c.bot))


def check_present(c,row):
    label=f'شارژ کیف پول #{row["ref_id"]}'
    if c.key=='tgstars':
        assert c.sent[-1]==dict(chat_id=USER_ID,title='پرداخت با استارز تلگرام',description=f'{label} - 900 تومان معادل 36 استارز',payload=f'xg:{row["id"]}',provider_token='',currency='XTR',prices=[user.LabeledPrice(label=label,amount=36)])
    else:
        event=c.log.events[-1];meta=user.registry.GATEWAYS[c.key]
        lines=[f"{meta['icon']} فاکتور پرداخت ({meta['title']}) ساخته شد. روی دکمه‌ی زیر بزن و پرداخت رو تکمیل کن."]
        if c.key=='cubepay':lines.append('💰 مبلغ دقیق قابل پرداخت: 991 تومان')
        lines+=['⏳ اعتبار این فاکتور محدود است.', 'معمولاً به‌محض پرداخت، کیف پول خودکار شارژ می‌شود؛ اگر چند دقیقه طول کشید، دکمه‌ی «بررسی وضعیت پرداخت» را بزن.']
        assert event.text=='\n'.join(lines)
        rows=event.reply_markup.inline_keyboard
        assert rows[0][0].url=='https://pay.example.invalid/selected'
        assert rows[-1][0].callback_data==f'xgw_check:{row["id"]}'
        assert len(rows)==(3 if c.key=='tetra98' else 2)
        if c.key=='tetra98':assert rows[1][0].url=='https://t.me/synthetic_payment_bot'


@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy','composite'])
def test_topup_success_repeated_request(catalog,monkeypatch,key,representation,kind):
    c=catalog;setup(c,monkeypatch,key,representation=representation,kind=kind)
    before=topups(c);decoy=invoices(c);order=dict(c.db.get_order(c.oid));wallet=c.db.get_wallet_credit(USER_ID)
    invoke(c);rows=topups(c);assert rows[:-1]==before
    topup=rows[-1];inv=invoices(c)[-1]
    assert (topup['user_id'],topup['amount'],topup['status'])==(USER_ID,900,'pending')
    assert inv['id']!=topup['id']
    assert (inv['gateway'],inv['kind'],inv['ref_id'],inv['user_id'],inv['amount_toman'],inv['payable_amount'],inv['status'])==(key,'wallet_topup',topup['id'],USER_ID,900,36 if key=='tgstars' else 990 if key=='cubepay' else 900,'new')
    assert inv['order_number']==f'w{topup["id"]}x1234abcd' and invoices(c)[:-1]==decoy
    assert c.topup_hooks==[(900,key)] and not c.hooks
    assert c.answers==[('در حال ساخت فاکتور...',{})]
    assert dict(c.db.get_order(c.oid))==order and not c.trace
    check_present(c,inv)
    if key!='tgstars':
        args=c.remote[0][1];assert args[0]=='synthetic-key'
        label=f'شارژ کیف پول #{topup["id"]}'
        if key=='nowpayments':assert args[1:]==(1.25,f'w{topup["id"]}x1234abcd',label,'https://shop.example.invalid/api/webhooks/nowpayments?b=synthetic-tenant')
        else:
            assert args[1:5]==(990 if key=='cubepay' else 900,f'https://shop.example.invalid/api/pay-return/{key}?b=synthetic-tenant',label,f'w{topup["id"]}x1234abcd')
            if key=='cubepay':assert args[5:]==(USER_ID,)
        assert json.loads(inv['meta'])['retained']=='selected'
    # Existing legacy callback creates a fresh topup each time, no settlement.
    saved=topups(c);saved_inv=invoices(c);invoke(c)
    assert topups(c)[:-1]==saved and invoices(c)[:-1]==saved_inv
    assert len(topups(c))==4 and len(invoices(c))==3
    assert invoices(c)[-1]['ref_id']==topups(c)[-1]['id']!=topup['id']
    assert len(c.remote)==2*int(key!='tgstars') and len(c.topup_hooks)==2
    check_present(c,invoices(c)[-1])
    assert c.db.get_wallet_credit(USER_ID)==wallet and c.data==c.initial_data and not c.trace


@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('scenario',['missing','zero','disabled','policy','remote','telegram'])
def test_topup_failure_boundaries(catalog,monkeypatch,key,scenario):
    c=catalog;setup(c,monkeypatch,key,scenario);before=dump(c.db);old=topups(c);inv=invoices(c)
    if scenario=='telegram' and key!='tgstars':
        with pytest.raises(TelegramBadRequest,match='synthetic presentation failure'):invoke(c)
    else:invoke(c)
    if scenario in {'missing','zero','disabled','policy'}:
        assert dump(c.db)==before and not c.remote and not c.sent and not c.log.events
        expected='درخواست معتبر یافت نشد.' if scenario in {'missing','zero'} else 'این روش پرداخت در حال حاضر در دسترس نیست.' if scenario=='disabled' else 'synthetic topup refusal'
        assert c.answers==[(expected,{'show_alert':True})]
        assert c.topup_hooks==([(900,key)] if scenario=='policy' else [])
    else:
        assert topups(c)[:-1]==old and topups(c)[-1]['amount']==900
        assert topups(c)[-1]['status']==('rejected' if scenario=='remote' else 'pending')
        assert c.answers==[('در حال ساخت فاکتور...',{})] and c.topup_hooks==[(900,key)]
        if scenario=='remote':
            assert invoices(c)==inv and not c.sent
            if key=='tgstars':assert 'دریافت خودکار نرخ استارز ناموفق بود' in c.log.events[-1].text
            else:assert c.log.events[-1].text=='⚠️ synthetic remote refusal'
        else:
            assert invoices(c)[:-1]==inv and invoices(c)[-1]['status']=='new'
            assert invoices(c)[-1]['ref_id']==topups(c)[-1]['id']
            if key=='tgstars':assert c.log.events[-1].text=='⚠️ ساخت فاکتور استارز ناموفق بود: synthetic presentation failure'
    assert c.db.get_wallet_credit(USER_ID)==0 and not c.trace and not c.hooks and c.data==c.initial_data
