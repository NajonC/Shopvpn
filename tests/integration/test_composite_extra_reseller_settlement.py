"""T050ef/eg: actual reseller settlement, supported controls and composite refusal."""
import asyncio
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog,USER_ID
from tests.integration.test_composite_legacy_guards import as_row
from tests.integration.test_composite_ai_catalog_legacy import dump
import extra_gateway_payment as egp

PRIOR='✅ این پرداخت قبلاً ثبت شده است.'
MISSING='⚠️ درخواست نمایندگی یافت نشد.'

def setup(c,mp,representation='sqlite',tier='gold',kind=None,marker='product',scenario='success'):
    c.db.add_or_update_user(9002,'other','Other');c.db.add_wallet_credit(USER_ID,77)
    category=c.db.add_category('supply');c.pid=c.db.add_product(category,'synthetic supply',100)
    c.rid=c.db.create_reseller_request(USER_ID,20,'synthetic request',supply_model='fixed_product',supply_product_id=c.pid,supply_qty=2,tier_code=tier)
    c.sibling=c.db.create_reseller_request(9002,99,'unrelated',tier_code='vip')
    with c.db._get_conn() as conn:
        conn.execute("UPDATE reseller_requests SET status='awaiting_payment', commission_percent=17, discount_percent=23 WHERE id=?",(c.rid,))
    c.db.create_extra_invoice('zarinpal','reseller_request',99999,9002,1)
    c.iid=c.db.create_extra_invoice('zarinpal','reseller_request',c.rid,USER_ID,1234)
    c.invoice=as_row(dict(c.db.get_extra_invoice(c.iid)),representation)
    get_product=c.db.get_product;get_request=c.db.get_reseller_request
    def product(pid):
        row=get_product(pid)
        if row is None:return None
        d=dict(row)
        if pid==c.pid and marker=='product' and kind is not None:d['service_kind']=kind
        return as_row(d,representation)
    def request(rid):
        row=get_request(rid)
        if row is None:return None
        d=dict(row)
        if rid==c.rid and marker=='request' and kind is not None:d['service_kind']=kind
        return as_row(d,representation)
    mp.setattr(c.db,'get_product',product);mp.setattr(c.db,'get_reseller_request',request)
    c.trace=[];c.sent=[]
    for name in ['complete_reseller_request_gateway_payment','switch_agent_tier','enable_inline_reseller','set_user_reseller_tier']:
        original=getattr(c.db,name)
        def wrap(*a,_name=name,_original=original,**kw):
            c.trace.append((_name,a,kw))
            if scenario==_name:raise RuntimeError('synthetic failure')
            result=_original(*a,**kw)
            if scenario=='disappeared' and _name=='complete_reseller_request_gateway_payment':
                with c.db._get_conn() as conn:conn.execute('DELETE FROM reseller_requests WHERE id=?',(c.rid,))
            return result
        mp.setattr(c.db,name,wrap)
    class Bot:
        async def send_message(self,*a,**kw):
            c.sent.append((a,kw))
            if scenario=='send':raise RuntimeError('synthetic failure')
    c.bot=Bot()
    async def forbidden(*a,**kw):raise AssertionError('unexpected order/topup dispatch')
    mp.setattr(egp.abangateway_payment,'finalize_paid_order',forbidden);mp.setattr(egp.abangateway_payment,'finalize_paid_topup',forbidden)
    mp.setattr(egp,'_notify_admins',forbidden)

def invoke(c,entry):return asyncio.run(egp.deliver(c.db,c.bot,c.invoice) if entry=='deliver' else egp._finalize_reseller(c.db,c.bot,c.invoice))
def isolated(c):
    with c.db._get_conn() as conn:
        return ([tuple(r) for r in conn.execute('SELECT * FROM extra_gateway_invoices ORDER BY id')],tuple(conn.execute('SELECT * FROM reseller_requests WHERE id=?',(c.sibling,)).fetchone()),tuple(conn.execute('SELECT * FROM users WHERE telegram_id=9002').fetchone()))
def expected(tier):
    return {'bronze':'✅ پرداخت هزینه 🥉 برنزی تایید شد و نمایندگی شما فعال شد.\n📈 درصد کمیسیون: 17٪','silver':'✅ پرداخت هزینه 🥈 نقره‌ای تایید شد و نمایندگی شما فعال شد.'}.get(tier,'')
def check_send(c,tier):
    if tier in ['bronze','silver']:assert not c.sent;return
    label={'gold':'🥇 طلایی','vip':'👑 VIP',None:'نمایندگی'}[tier]
    assert len(c.sent)==1
    args,kw=c.sent[0]
    assert args==(USER_ID,f'✅ پرداخت هزینه {label} تایید شد!\n\nحالا توکن بات نمایندگی خودتان را از @BotFather ارسال کنید تا فعال‌سازی ادامه پیدا کند:')
    rows=kw['reply_markup'].inline_keyboard
    assert len(rows)==1 and len(rows[0])==1
    assert rows[0][0].text=='🚀 ادامه فعال‌سازی نمایندگی' and rows[0][0].callback_data==f'resreq_continue:{c.rid}'

@pytest.mark.parametrize('entry',['deliver','helper'])
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('tier',['bronze','silver','gold','vip',None])
@pytest.mark.parametrize('kind',[None,'legacy'])
def test_reseller_actual_success_repeat(catalog,monkeypatch,entry,representation,tier,kind):
    c=catalog;setup(c,monkeypatch,representation,tier,kind);before=isolated(c)
    assert c.iid!=c.rid
    assert invoke(c,entry)==expected(tier)
    status='completed' if tier in ['bronze','silver'] else 'awaiting_bot_info'
    assert c.db.get_reseller_request(c.rid)['status']==status
    want=[('complete_reseller_request_gateway_payment',(c.rid,),{})]
    if tier:want+=[('switch_agent_tier',(USER_ID,tier),{})]
    if tier=='bronze':want+=[('enable_inline_reseller',(USER_ID,17),{})]
    if tier in ['bronze','silver']:want+=[('set_user_reseller_tier',(USER_ID,tier,None if tier=='bronze' else 23),{})]
    assert c.trace==want;check_send(c,tier)
    user=c.db.get_user(USER_ID)
    assert (user['reseller_tier'],user['reseller_discount_percent'],user['inline_reseller_enabled'],user['inline_reseller_commission_percent'])==(tier if tier in ['bronze','silver'] else None,23 if tier=='silver' else None,1 if tier=='bronze' else 0,17 if tier=='bronze' else None)
    assert c.db.get_wallet_credit(USER_ID)==77 and isolated(c)==before
    c.trace.clear();c.sent.clear();before=dump(c.db)
    assert invoke(c,entry)==PRIOR and c.trace==[('complete_reseller_request_gateway_payment',(c.rid,),{})] and not c.sent
    assert dump(c.db)==before

@pytest.mark.parametrize('entry',['deliver','helper'])
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['product','request'])
@pytest.mark.parametrize('scenario',['success','complete_reseller_request_gateway_payment','switch_agent_tier'])
def test_composite_reseller_refused_before_settlement(catalog,monkeypatch,entry,representation,marker,scenario,caplog):
    c=catalog;setup(c,monkeypatch,representation,'gold','composite',marker,scenario);before=dump(c.db)
    try:text=invoke(c,entry)
    except RuntimeError as exc:text=str(exc)
    assert not c.trace and not c.sent and dump(c.db)==before
    assert 'composite' in text.lower()
    assert 'synthetic request' not in text+caplog.text

@pytest.mark.parametrize('entry',['deliver','helper'])
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('scenario',['pending_review','completed','awaiting_bot_info','missing','disappeared','complete_reseller_request_gateway_payment','switch_agent_tier','enable_inline_reseller','set_user_reseller_tier','send','foreign_invoice','wrong_amount'])
def test_reseller_actual_boundaries(catalog,monkeypatch,entry,representation,scenario):
    tier='bronze' if scenario in ['enable_inline_reseller','set_user_reseller_tier'] else 'gold'
    c=catalog;setup(c,monkeypatch,representation,tier,scenario=scenario)
    inv=dict(c.invoice)
    if scenario in ['pending_review','completed','awaiting_bot_info']:
        with c.db._get_conn() as conn:conn.execute('UPDATE reseller_requests SET status=? WHERE id=?',(scenario,c.rid))
    if scenario=='missing':inv['ref_id']=99999
    if scenario=='foreign_invoice':inv['user_id']=9002
    if scenario=='wrong_amount':inv['amount_toman']=1
    c.invoice=as_row(inv,representation);before=isolated(c);initial=dump(c.db)
    errors=['complete_reseller_request_gateway_payment','switch_agent_tier','enable_inline_reseller','set_user_reseller_tier']
    if scenario in errors:
        with pytest.raises(RuntimeError,match='synthetic failure'):invoke(c,entry)
    else:assert invoke(c,entry)==(PRIOR if scenario in ['pending_review','completed','awaiting_bot_info','missing'] else MISSING if scenario=='disappeared' else '')
    assert isolated(c)==before and c.db.get_wallet_credit(USER_ID)==77
    if scenario in ['pending_review','completed','awaiting_bot_info','missing','complete_reseller_request_gateway_payment']:
        assert dump(c.db)==initial and not c.sent
    elif scenario=='disappeared':assert c.db.get_reseller_request(c.rid) is None and not c.sent
    else:
        assert c.db.get_reseller_request(c.rid)['status']==('completed' if tier=='bronze' else 'awaiting_bot_info')
        if scenario in errors:assert not c.sent
        else:check_send(c,tier)
        if scenario=='set_user_reseller_tier':assert c.db.get_user(USER_ID)['inline_reseller_enabled']==1
        # Settlement precedes downstream effects. Even a failed effect is not retried.
        c.trace.clear();c.sent.clear();retained=dump(c.db)
        assert invoke(c,entry)==PRIOR and not c.sent and dump(c.db)==retained
