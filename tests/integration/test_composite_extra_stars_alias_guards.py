"""T050dx/dy: direct Stars aliases and inline metadata/claim failure boundaries."""
import asyncio
import json
import pytest
from tests.integration.test_composite_extra_cancel_alias_guards import alias, ALIASES, STATUSES, catalog, dump, USER_ID
from tests.integration.test_composite_extra_admin_guards import egp
REPEAT='✅ این پرداخت قبلاً ثبت و تحویل داده شده است.'


def prepare(c,mp,name,kind,representation,status='new',domain='order',scenario='ok'):
    alias(c,mp,name,kind,representation)
    with c.db._get_conn() as conn:conn.execute('UPDATE extra_gateway_invoices SET gateway=?,status=?,kind=?,meta=? WHERE id=?',('zarinpal' if scenario=='gateway' else 'tgstars',status,domain,json.dumps({'retained':'selected'}),c.iid))
    c.steps=[];c.deliveries=[];c.warnings=[];c.notifier=object()
    for method in ['merge_extra_invoice_meta','claim_extra_invoice']:
        old=getattr(c.db,method)
        def wrap(*a,_fn=old,_method=method,**kw):
            c.steps.append((_method,a,kw))
            if scenario==('merge_error' if _method=='merge_extra_invoice_meta' else 'claim_error'):raise RuntimeError('synthetic '+scenario)
            if scenario=='claim_lost' and _method=='claim_extra_invoice':assert _fn(*a,**kw)
            return _fn(*a,**kw)
        mp.setattr(c.db,method,wrap)
    async def deliver(*a):
        c.deliveries.append((a,dict(a[2])))
        assert a[2]['status']=='completed' and json.loads(a[2]['meta'])=={'retained':'selected','charge_id':'synthetic-alias-charge'}
        if scenario=='delivery_error':raise RuntimeError('synthetic delivery')
        return 'direct alias delivered'
    async def notify(db,bot,text):c.warnings.append((db,bot,text))
    mp.setattr(egp,'deliver',deliver);mp.setattr(egp,'_notify_admins',notify)
    c.args=(99999 if scenario=='missing' else c.iid,USER_ID+1 if scenario=='foreign' else USER_ID,991 if scenario=='amount' else 990,'USD' if scenario=='currency' else 'XTR','synthetic-alias-charge',c.notifier)


def invoke(c):return asyncio.run(egp.process_stars_payment(c.db,c.bot,*c.args))


def assert_valid(c,before,status):
    row=dict(c.db.get_extra_invoice(c.iid));assert json.loads(row['meta'])=={'retained':'selected','charge_id':'synthetic-alias-charge'}
    assert row['status']==('completed' if status in {'new','pending'} else status)
    assert c.steps==[('merge_extra_invoice_meta',(c.iid,{'charge_id':'synthetic-alias-charge'}),{}),('claim_extra_invoice',(c.iid,),{})]
    assert not c.warnings
    if status in {'new','pending'}:
        assert len(c.deliveries)==1 and c.deliveries[0][0][:2]==(c.db,c.bot) and c.deliveries[0][0][3] is c.notifier
        assert c.deliveries[0][1]==row
    else:assert not c.deliveries
    retained=lambda rows:[x for x in rows if not x.startswith('INSERT INTO "extra_gateway_invoices"')]
    assert retained(dump(c.db))==retained(before) and not c.trace and not c.remote


@pytest.mark.parametrize('name',ALIASES)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',['composite',None,'legacy'])
@pytest.mark.parametrize('status',STATUSES)
def test_stars_alias(catalog,monkeypatch,name,representation,kind,status):
    c=catalog;prepare(c,monkeypatch,name,kind,representation,status)
    before=dump(c.db);decoy=dict(c.db.get_extra_invoice(c.decoy));text=invoke(c)
    if kind=='composite':
        assert not c.steps and not c.deliveries and not c.warnings and dump(c.db)==before, 'missing T052 Stars alias admission before metadata/claim'
        assert 'composite' in text.lower()
        assert invoke(c)==text and dump(c.db)==before and not c.steps
    else:
        assert text==('direct alias delivered' if status in {'new','pending'} else REPEAT)
        assert_valid(c,before,status)
        c.steps.clear();c.deliveries.clear();assert invoke(c)==REPEAT;assert_valid(c,before,'completed' if status in {'new','pending'} else status)
    assert dict(c.db.get_extra_invoice(c.decoy))==decoy


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('scenario',['foreign','missing','gateway','amount','currency','merge_error','claim_error','delivery_error','claim_lost'])
def test_stars_inline_boundaries(catalog,monkeypatch,representation,kind,scenario):
    c=catalog;prepare(c,monkeypatch,'global_renewal_target',kind,representation,scenario=scenario)
    before=dump(c.db);selected=dict(c.db.get_extra_invoice(c.iid));decoy=dict(c.db.get_extra_invoice(c.decoy))
    if scenario in {'merge_error','claim_error'}:
        with pytest.raises(RuntimeError,match='synthetic '+scenario):invoke(c)
        assert len(c.steps)==(1 if scenario=='merge_error' else 2) and not c.deliveries and not c.warnings
        if scenario=='merge_error':assert dump(c.db)==before
        else:assert json.loads(c.db.get_extra_invoice(c.iid)['meta'])=={'retained':'selected','charge_id':'synthetic-alias-charge'} and c.db.get_extra_invoice(c.iid)['status']=='new'
    else:
        text=invoke(c)
        if scenario in {'foreign','missing','gateway','amount','currency'}:
            assert text==('⚠️ پرداخت دریافت شد ولی فاکتور یافت نشد. با پشتیبانی تماس بگیرید.' if scenario in {'foreign','missing','gateway'} else '⚠️ مبلغ پرداخت‌شده با فاکتور نمی‌خواند. با پشتیبانی تماس بگیرید.')
            assert dump(c.db)==before and not c.steps and not c.deliveries and len(c.warnings)==1
            expected=f'⚠️ پرداخت استارز با payload نامعتبر از کاربر {c.args[1]} (شارژ synthetic-alias-charge). دستی بررسی کن.' if scenario in {'foreign','missing','gateway'} else f'⚠️ مبلغ استارز فاکتور #{c.iid} با مقدار پرداخت‌شده نمی‌خواند (شارژ synthetic-alias-charge).'
            assert c.warnings==[(c.db,c.bot,expected)]
        elif scenario=='claim_lost':assert text==REPEAT;assert_valid(c,before,'completed')
        else:
            assert text=='⚠️ پرداخت شما دریافت شد ولی تحویل با خطا مواجه شد. ادمین به‌زودی رسیدگی می‌کند.'
            assert len(c.deliveries)==1 and len(c.steps)==2 and c.db.get_extra_invoice(c.iid)['status']=='completed'
            assert c.warnings==[(c.db,c.bot,f'⚠️ خطای غیرمنتظره در تحویل فاکتور استارز #{c.iid} (شارژ synthetic-alias-charge). دستی بررسی کن.')]
            c.deliveries.clear();c.steps.clear();c.warnings.clear();assert invoke(c)==REPEAT and not c.deliveries and not c.warnings
    assert dict(c.db.get_extra_invoice(c.decoy))==decoy and not c.trace and not c.remote


@pytest.mark.parametrize('domain',['wallet_topup','reseller_request'])
@pytest.mark.parametrize('status',STATUSES)
def test_stars_other_domains(catalog,monkeypatch,domain,status):
    c=catalog;prepare(c,monkeypatch,'global_renewal_target','composite','sqlite',status,domain)
    before=dump(c.db);assert invoke(c)==('direct alias delivered' if status in {'new','pending'} else REPEAT);assert_valid(c,before,status)
