"""T050fb/fc: actual upstream payment policies, SQL and registered continuations."""
import asyncio
import pytest
from tests.integration.test_composite_extra_order_entry_guards import catalog, setup as old_setup, invoices, GATEWAYS, USER_ID, dump
from tests.integration.test_composite_extra_topup_entry_controls import topups
from tests.integration.test_composite_legacy_guards import as_row
import handlers_user

KEYS=['zarinpal','cubepay','tgstars']
ORDER_DENIED='⛔️ این روش پرداخت برای این محصول مجاز نیست.'
CUSTOM_DENIED='⛔️ این روش پرداخت برای ساخت کانفیگ شخصی مجاز نیست.'
TOPUP_DENIED='⛔️ این روش پرداخت برای شارژ کیف پول در حال حاضر مجاز نیست.'
MINIMUM='⛔️ حداقل مبلغ قابل پرداخت با این روش 901 تومان است.'


def closure(fn,name):
    return dict(zip(fn.__code__.co_freevars,[c.cell_contents for c in fn.__closure__ or ()]))[name]


def prepare(c,mp,key,representation='dict',kind=None):
    old_setup(c,mp,key,representation,kind)
    router=handlers_user.create_user_router(c.db,is_main_bot=True)
    candidates=[h.callback for h in router.callback_query.handlers if h.callback.__name__=='handler' and 'key' in h.callback.__code__.co_freevars and closure(h.callback,'key')==key]
    c.order_handler=next(h for h in candidates if 'order_error' in h.__code__.co_freevars)
    c.topup_handler=next(h for h in candidates if 'topup_error' in h.__code__.co_freevars)
    c.order_policy=closure(c.order_handler,'order_error');c.topup_policy=closure(c.topup_handler,'topup_error')
    c.data={'order_id':c.oid,'topup_amount':900,'keep':'unchanged'}


@pytest.mark.parametrize('key',KEYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy','composite'])
@pytest.mark.parametrize('scenario',['unrestricted','equal','below','denied','denied_below'])
def test_actual_order_policy_selected_sql_readonly(catalog,monkeypatch,key,representation,kind,scenario):
    c=catalog;prepare(c,monkeypatch,key,representation,kind)
    c.db.set_product_payment_methods(c.pid,None if scenario=='unrestricted' else ['wallet'] if scenario.startswith('denied') else [key])
    c.db.set_setting('min_amount_'+key,'901' if scenario in {'below','denied_below'} else '900')
    before=dump(c.db)
    order=c.db.get_order(c.oid)
    expected=ORDER_DENIED if scenario.startswith('denied') else MINIMUM if scenario=='below' else None
    for _ in range(2):assert asyncio.run(c.order_policy(order,key))==expected
    assert dump(c.db)==before and not c.remote and not c.sent and not c.trace
    # Composite admission here is a payment-policy control, never fulfillment authority.


@pytest.mark.parametrize('key',KEYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('domain',['custom','global','renewal'])
@pytest.mark.parametrize('allowed',[True,False])
def test_actual_order_domain_precedence(catalog,monkeypatch,key,representation,domain,allowed):
    c=catalog;prepare(c,monkeypatch,key,representation)
    row=dict(c.db.get_order(c.oid))
    if domain in {'custom','global'}:
        row.update(is_custom_config=1,custom_product_id=c.alpha_id if domain=='custom' else None)
        c.db.set_custom_config_payment_methods([key] if allowed else ['wallet'])
        c.db.set_custom_config_product_payment_methods(c.alpha_id,[key] if allowed else ['wallet'])
        c.db.set_product_payment_methods(c.pid,['wallet'] if allowed else [key])
    else:
        row.update(product_id=0,is_renewal=1)
        c.db.set_product_payment_methods(c.pid,['wallet'])
    c.db.set_setting('min_amount_'+key,'0' if allowed else '901')
    expected=None if allowed else MINIMUM if domain=='renewal' else CUSTOM_DENIED
    before=dump(c.db)
    assert asyncio.run(c.order_policy(as_row(row,representation),key))==expected
    assert dump(c.db)==before


@pytest.mark.parametrize('key',KEYS)
@pytest.mark.parametrize('kind',[None,'legacy','composite'])
@pytest.mark.parametrize('scenario',['unrestricted','equal','below','denied','denied_below'])
def test_actual_topup_policy_independent(catalog,monkeypatch,key,kind,scenario):
    c=catalog;prepare(c,monkeypatch,key,kind=kind)
    c.db.set_product_payment_methods(c.pid,['wallet'])
    c.db.set_wallet_topup_payment_methods(None if scenario=='unrestricted' else ['wallet'] if scenario.startswith('denied') else [key])
    c.db.set_setting('min_amount_'+key,'901' if scenario in {'below','denied_below'} else '900')
    expected=TOPUP_DENIED if scenario.startswith('denied') else MINIMUM if scenario=='below' else None
    before=dump(c.db)
    for _ in range(2):assert asyncio.run(c.topup_policy(900,key))==expected
    assert dump(c.db)==before and not c.remote and not c.sent


@pytest.mark.parametrize('key',KEYS)
@pytest.mark.parametrize('flow',['order','topup'])
@pytest.mark.parametrize('scenario',['equal','below','denied','permission_fault','minimum_fault'])
def test_actual_policy_registered_continuation(catalog,monkeypatch,key,flow,scenario):
    c=catalog;prepare(c,monkeypatch,key)
    c.db.set_product_payment_methods(c.pid,['wallet'] if scenario=='denied' else [key])
    c.db.set_wallet_topup_payment_methods(['wallet'] if scenario=='denied' else [key])
    c.db.set_setting('min_amount_'+key,'901' if scenario=='below' else '900')
    def fail(*a):raise RuntimeError('synthetic policy read fault')
    if scenario=='permission_fault':monkeypatch.setattr(c.db,'product_allows_payment_method' if flow=='order' else 'wallet_topup_allows_payment_method',fail)
    if scenario=='minimum_fault':monkeypatch.setattr(c.db,'get_payment_method_min_amount',fail)
    before=dump(c.db);old_inv=invoices(c);old_topups=topups(c)
    handler=c.order_handler if flow=='order' else c.topup_handler
    if scenario.endswith('fault'):
        with pytest.raises(RuntimeError,match='synthetic policy read fault'):asyncio.run(handler(c.call,c.state,c.bot))
        assert not c.answers
    else:
        asyncio.run(handler(c.call,c.state,c.bot))
        if scenario=='equal':
            assert len(invoices(c))==len(old_inv)+1 and len(c.remote)==int(key!='tgstars')
            assert len(topups(c))==len(old_topups)+int(flow=='topup')
            assert c.answers==[('در حال ساخت فاکتور...',{})]
            inv=invoices(c)[-1]
            assert (inv['gateway'],inv['kind'],inv['amount_toman'],inv['user_id'])==(key,'order' if flow=='order' else 'wallet_topup',900,USER_ID)
            assert inv['ref_id']==(c.oid if flow=='order' else topups(c)[-1]['id'])
        else:assert c.answers==[(MINIMUM if scenario=='below' else ORDER_DENIED if flow=='order' else TOPUP_DENIED,{'show_alert':True})]
    if scenario!='equal':assert dump(c.db)==before and not c.remote and not c.sent and not c.log.events
    assert c.data=={'order_id':c.oid,'topup_amount':900,'keep':'unchanged'} and not c.trace
