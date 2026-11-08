"""T050cf/cg: direct Stars admission and real inline metadata/claim/stock effects."""
import asyncio
import json
import pytest
from tests.integration.test_composite_extra_admin_guards import egp
from tests.integration.test_composite_gateway_stock_guards import catalog, setup as stock_setup, rows, dump, LINKS, USER_ID, REFERRER, SUCCESS
REPEAT='✅ این پرداخت قبلاً ثبت و تحویل داده شده است.'
SCENARIOS=['paid','prior','shortage','delivery','completed','expired','cancelled','claim_lost','foreign','amount','currency','missing','gateway']


def setup(c,mp,representation,kind=None,marker='order',scenario='paid'):
    stock_setup(c,mp,'abangateway_payment',representation,kind,marker,scenario if scenario in {'prior','shortage','delivery'} else 'success')
    c.decoy=c.db.create_extra_invoice('tgstars','order',99999,USER_ID,111,11,meta={'retained':'decoy'})
    c.iid=c.db.create_extra_invoice('zarinpal' if scenario=='gateway' else 'tgstars','order',c.oid,USER_ID,900,37,meta={'retained':'selected'})
    if scenario in {'completed','expired','cancelled'}:c.db.update_extra_invoice_status(c.iid,scenario)
    c.invoice_trace=[];c.raced=False
    for method in ['merge_extra_invoice_meta','claim_extra_invoice','release_extra_invoice']:
        original=getattr(c.db,method)
        def call(*args,_fn=original,_name=method,**kw):
            c.invoice_trace.append((_name,args))
            if scenario=='claim_lost' and _name=='claim_extra_invoice' and not c.raced:
                assert _fn(*args,**kw);c.raced=True
            return _fn(*args,**kw)
        mp.setattr(c.db,method,call)
    c.args=(99999 if scenario=='missing' else c.iid,USER_ID+1 if scenario=='foreign' else USER_ID,38 if scenario=='amount' else 37,'USD' if scenario=='currency' else 'XTR','synthetic-charge')


def invoke(c):return asyncio.run(egp.process_stars_payment(c.db,c.bot,*c.args))


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('scenario',['paid','prior','completed','delivery'])
def test_composite_extra_stars(catalog,monkeypatch,representation,marker,scenario,caplog):
    c=catalog;setup(c,monkeypatch,representation,'composite',marker,scenario)
    before=dump(c.db);text=invoke(c)
    assert not c.invoice_trace and not c.trace and dump(c.db)==before
    assert 'composite' in text.lower() and 'synthetic-charge' not in text+caplog.text


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('scenario',SCENARIOS)
def test_legacy_extra_stars(catalog,monkeypatch,representation,kind,scenario):
    c=catalog;setup(c,monkeypatch,representation,kind,scenario=scenario)
    before=rows(c);selected=dict(c.db.get_extra_invoice(c.iid));decoy=dict(c.db.get_extra_invoice(c.decoy));text=invoke(c)
    invalid=scenario in {'foreign','amount','currency','missing','gateway'}
    expected='⚠️ پرداخت دریافت شد ولی فاکتور یافت نشد. با پشتیبانی تماس بگیرید.' if scenario in {'foreign','missing','gateway'} else '⚠️ مبلغ پرداخت‌شده با فاکتور نمی‌خواند. با پشتیبانی تماس بگیرید.' if scenario in {'amount','currency'} else SUCCESS if scenario=='paid' else '✅ این سفارش قبلاً بررسی و تحویل داده شده است.' if scenario=='prior' else '⚠️ پرداخت تایید شد ولی موجودی هم‌زمان تمام شده؛ ادمین به‌زودی دستی رسیدگی می‌کند.' if scenario=='shortage' else '⚠️ پرداخت شما دریافت شد ولی تحویل با خطا مواجه شد. ادمین به‌زودی رسیدگی می‌کند.' if scenario=='delivery' else REPEAT
    assert text==expected and dict(c.db.get_extra_invoice(c.decoy))==decoy
    now=dict(c.db.get_extra_invoice(c.iid))
    if invalid:
        assert now==selected and not c.invoice_trace and rows(c)==before
        assert len(c.trace)==1 and c.trace[0][0:2]==('send',9001)
        assert 'synthetic-charge' in c.trace[0][2]
    else:
        assert c.invoice_trace==[('merge_extra_invoice_meta',(c.iid,{'charge_id':'synthetic-charge'})),('claim_extra_invoice',(c.iid,))]
        assert json.loads(now['meta'])=={'retained':'selected','charge_id':'synthetic-charge'}
        assert now['status']==(scenario if scenario in {'expired','cancelled'} else 'completed')
        for key in selected:
            if key not in {'status','meta','updated_at'}:assert now[key]==selected[key]
        if scenario in {'paid','delivery'}:
            assert c.db.get_order(c.oid)['status']=='approved'
            assert c.trace[:3]==[('claim_order',(c.oid,),{}),('take_unused_configs',(c.pid,USER_ID,2),{}),('approve_order',(c.oid,[r['id'] for r in before[:2]]),{})]
            assert ('delivery',USER_ID,'Stock',LINKS[:2],dict(final_price=900,order_id=c.oid,db=c.db),'approved') in c.trace
            assert all((r['is_used'],r['assigned_user_id'],r['order_id'])==(1,USER_ID,c.oid) for r in rows(c)[:2]) and rows(c)[2:]==before[2:]
            assert c.db.get_wallet_credit(REFERRER)==(130 if scenario=='paid' else 0)
            assert c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==int(scenario=='paid')
            if scenario=='delivery':assert c.trace[-1][0:2]==('send',9001)
        elif scenario=='shortage':
            assert c.db.get_order(c.oid)['status']=='pending' and rows(c)==before
            assert ('release_order_claim',(c.oid,),{}) in c.trace and c.trace[-1][0:2]==('send',9001)
        else:assert not c.trace and rows(c)==before
        # Repeat still writes metadata, but cannot allocate/reward again.
        saved=rows(c);order=dict(c.db.get_order(c.oid));ref=c.db.get_wallet_credit(REFERRER)
        c.trace.clear();c.invoice_trace.clear()
        assert invoke(c)==REPEAT and not c.trace and rows(c)==saved and dict(c.db.get_order(c.oid))==order and c.db.get_wallet_credit(REFERRER)==ref
        assert c.invoice_trace==[('merge_extra_invoice_meta',(c.iid,{'charge_id':'synthetic-charge'})),('claim_extra_invoice',(c.iid,))]
    assert c.db.get_wallet_credit(USER_ID)==0
