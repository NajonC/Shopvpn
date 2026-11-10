"""T050dv/dw: independent admin check admission, authority and result routing."""
import asyncio
from types import SimpleNamespace
import pytest
from tests._harness.legacy_bot import find_handler
from tests.integration.test_composite_extra_cancel_alias_guards import alias, ALIASES, STATUSES, catalog, dump, USER_ID
from tests.integration.test_composite_extra_admin_guards import OWNER, egp

RESULTS={
    'verified_now':'selected delivery',
    'not_paid_yet':'⏳ هنوز پرداختی برای این فاکتور تایید نشده.',
    'already_delivered':'✅ این پرداخت قبلاً تایید و تحویل داده شده است.',
    'expired':'❌ اعتبار این فاکتور تمام شده یا لغو شده است.',
    'error:synthetic':'⚠️ خطا در بررسی وضعیت: synthetic',
    'unknown':None,
}


def run(c,mp,result='verified_now',text='selected delivery',uid=OWNER,suffix=None,fail=False):
    answers=[];messages=[];effects=[]
    async def answer(*a,**kw):answers.append((a,kw))
    async def message(*a,**kw):messages.append((a,kw))
    async def process(*a,**kw):
        effects.append((a,kw))
        if fail:raise RuntimeError('synthetic process')
        return result,text
    mp.setattr(egp,'process_invoice',process)
    call=SimpleNamespace(from_user=SimpleNamespace(id=uid),data=f'check_xgw_invoice:{c.iid if suffix is None else suffix}',answer=answer,message=SimpleNamespace(answer=message))
    bot=object()
    def invoke():asyncio.run(find_handler(c.router,'callback_query','cb_check_xgw_invoice')(call,bot))
    return invoke,answers,messages,effects,bot


@pytest.mark.parametrize('name',ALIASES)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',['composite',None,'legacy'])
@pytest.mark.parametrize('status',STATUSES)
def test_admin_check_alias(catalog,monkeypatch,name,representation,kind,status):
    c=catalog;alias(c,monkeypatch,name,kind,representation)
    with c.db._get_conn() as conn:conn.execute('UPDATE extra_gateway_invoices SET status=? WHERE id=?',(status,c.iid))
    invoke,answers,messages,effects,bot=run(c,monkeypatch)
    before=dump(c.db);selected=dict(c.db.get_extra_invoice(c.iid))
    for _ in range(2):
        answers.clear();messages.clear();effects.clear();invoke()
        if kind=='composite':
            assert not effects and not messages, 'missing T052 admin check admission before processor'
            assert len(answers)==1 and answers[0][1].get('show_alert') and 'composite' in answers[0][0][0].lower()
        else:
            assert answers==[(('در حال بررسی...',),{})]
            assert messages==[(('selected delivery',),{})]
            assert len(effects)==1 and effects[0][1]=={}
            args=effects[0][0];assert args[:2]==(c.db,bot) and dict(args[2])==selected
        assert dump(c.db)==before and not c.trace and not c.remote and not c.invoice_trace and not c.effects


@pytest.mark.parametrize('domain',['order','wallet_topup','reseller_request'])
@pytest.mark.parametrize('result',list(RESULTS)+['empty'])
@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_admin_check_result_domains(catalog,monkeypatch,domain,result,representation):
    c=catalog;alias(c,monkeypatch,'global_renewal_target','composite' if domain!='order' else 'legacy',representation)
    with c.db._get_conn() as conn:conn.execute('UPDATE extra_gateway_invoices SET kind=? WHERE id=?',(domain,c.iid))
    invoke,answers,messages,effects,bot=run(c,monkeypatch,'verified_now' if result=='empty' else result,'' if result=='empty' else 'selected delivery')
    before=dump(c.db);selected=dict(c.db.get_extra_invoice(c.iid));expected='✅ پرداخت تایید و تحویل داده شد.' if result=='empty' else RESULTS[result]
    for _ in range(2):
        effects.clear();answers.clear();messages.clear();invoke()
        assert answers==[(('در حال بررسی...',),{})]
        assert messages==([] if expected is None else [((expected,),{})])
        assert len(effects)==1 and effects[0][0][:2]==(c.db,bot) and dict(effects[0][0][2])==selected and effects[0][1]=={}
        assert dump(c.db)==before and not c.trace and not c.remote and not c.invoice_trace


@pytest.mark.parametrize('scenario',['unauthorized','malformed','missing','failure'])
@pytest.mark.parametrize('kind',['composite',None,'legacy'])
def test_admin_check_boundaries(catalog,monkeypatch,scenario,kind):
    c=catalog;alias(c,monkeypatch,'global_renewal_target',kind,'sqlite')
    invoke,answers,messages,effects,bot=run(c,monkeypatch,uid=USER_ID if scenario=='unauthorized' else OWNER,suffix='bad' if scenario=='malformed' else 99999 if scenario=='missing' else None,fail=scenario=='failure')
    before=dump(c.db)
    if scenario=='failure' and kind!='composite':
        with pytest.raises(RuntimeError,match='synthetic process'):invoke()
        assert answers==[(('در حال بررسی...',),{})] and len(effects)==1
    else:
        invoke();assert not effects
        if scenario=='unauthorized':assert answers==[((),{})]
        elif scenario!='failure':assert answers==[(('فاکتور یافت نشد.',),{'show_alert':True})]
        else:assert len(answers)==1 and answers[0][1].get('show_alert') and 'composite' in answers[0][0][0].lower()
    assert not messages and dump(c.db)==before and not c.trace and not c.remote and not c.invoice_trace
