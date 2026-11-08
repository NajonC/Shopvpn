"""T050cr/cs: direct bool predicate; adapter remains responsible for refusal text."""
import asyncio
import pytest
from tests.integration.test_composite_extra_order_entry_guards import catalog, setup, invoices, USER_ID, user, dump
from tests.integration.test_composite_legacy_guards import as_row
egp=user.egp


def invoice(c,kind='order',ref=None,status='new',representation='sqlite'):
    ident=c.db.create_extra_invoice('tgstars',kind,c.oid if ref is None else ref,USER_ID,900,36)
    c.db.update_extra_invoice_status(ident,status)
    row=as_row(dict(c.db.get_extra_invoice(ident)),representation)
    assert row['id']!=row['ref_id']
    return row


def payable(c,row):return asyncio.run(egp.ref_still_payable(c.db,row))


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('status',['new','pending','completed','cancelled'])
def test_direct_composite_reference_not_payable(catalog,monkeypatch,representation,marker,status):
    c=catalog;setup(c,monkeypatch,'tgstars',representation,'composite',marker)
    row=invoice(c,status=status,representation=representation);before=dump(c.db)
    result=payable(c,row)
    assert result is False, 'missing T052 direct payable composite refusal'
    assert payable(c,row) is False and dump(c.db)==before and not c.trace and not c.remote


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('status',['pending','approved','processing','rejected','missing'])
def test_direct_legacy_order_status(catalog,monkeypatch,representation,kind,status):
    c=catalog;setup(c,monkeypatch,'tgstars',representation,kind)
    with c.db._get_conn() as conn:conn.execute('UPDATE orders SET status=? WHERE id=?',(status if status!='missing' else 'pending',c.oid))
    row=invoice(c,ref=99999 if status=='missing' else None,representation=representation)
    before=dump(c.db)
    assert payable(c,row) is (status=='pending')
    assert payable(c,row) is (status=='pending') and dump(c.db)==before and not c.trace and not c.remote


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('unrelated',[None,'legacy','composite'])
@pytest.mark.parametrize('status',['pending','approved','rejected','missing'])
def test_direct_topup_reference_status(catalog,monkeypatch,representation,unrelated,status):
    c=catalog;setup(c,monkeypatch,'tgstars',representation,unrelated,'both')
    # Separate ID domains and pending decoy: wrong reference must not pass.
    for amount in [111,222,333,900]:tid=c.db.create_topup(USER_ID,amount)
    with c.db._get_conn() as conn:conn.execute('UPDATE wallet_topups SET status=? WHERE id=?',(status if status!='missing' else 'pending',tid))
    get=c.db.get_topup;reads=[]
    def read(ident):
        reads.append(ident);row=get(ident)
        return as_row(dict(row),representation) if row else None
    monkeypatch.setattr(c.db,'get_topup',read)
    target=99999 if status=='missing' else tid
    row=invoice(c,'wallet_topup',target,representation=representation);before=dump(c.db)
    assert payable(c,row) is (status=='pending')
    assert payable(c,row) is (status=='pending')
    assert reads==[target,target] and dump(c.db)==before and not c.trace and not c.remote


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('status',['new','pending','completed','cancelled'])
@pytest.mark.parametrize('reference',[777,99999])
def test_direct_reseller_predicate_is_not_settlement(catalog,monkeypatch,representation,status,reference):
    c=catalog;setup(c,monkeypatch,'tgstars',representation,'composite','both')
    row=invoice(c,'reseller_request',reference,status,representation);before=dump(c.db)
    reads=[]
    for name in ['get_order','get_topup','get_reseller_request']:
        def forbidden(*args,_name=name):reads.append((_name,args));raise AssertionError('unexpected reference lookup')
        monkeypatch.setattr(c.db,name,forbidden)
    # Existing predicate returns True for this kind without status/authority
    # checks. This does not approve settlement or close downstream validation.
    assert payable(c,row) is True and payable(c,row) is True
    assert not reads and dump(c.db)==before and not c.trace and not c.remote
