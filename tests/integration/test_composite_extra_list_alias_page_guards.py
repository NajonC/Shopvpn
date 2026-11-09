"""T050df/dg: list aliases and global housekeeping beyond visible page."""
import pytest
from tests.integration.test_composite_extra_cancel_alias_guards import alias, ALIASES
from tests.integration.test_composite_extra_admin_view_cancel_guards import catalog, dump
from tests.integration.test_composite_extra_admin_list_guards import invoke


def buttons(c):
    return [b.callback_data for row in c.views[-1][2]['reply_markup'].inline_keyboard for b in row]


def check(c, expected):
    before=dump(c.db)
    for n in range(2):
        events=invoke(c,'zarinpal')
        assert any(e.show_alert and 'composite' in (e.text or '').lower() for e in events), 'missing T052 list alias/page composite refusal'
        assert dump(c.db)==before
        assert all(e[0]=='list_extra_invoices' for e in c.effects)
        assert [s for s in buttons(c) if s and s.startswith('view_xgw_invoice:')]==[f'view_xgw_invoice:{i}' for i in expected]
        assert len(c.views)==n+1 and not c.remote and not c.trace and not c.invoice_trace


@pytest.mark.parametrize('name',ALIASES)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('status',['pending','cancelled'])
def test_list_alias_admission(catalog,monkeypatch,name,representation,status):
    c=catalog;alias(c,monkeypatch,name,'composite',representation)
    with c.db._get_conn() as conn:
        conn.execute("UPDATE extra_gateway_invoices SET status=?,created_at='2000-01-01',updated_at='2000-01-01' WHERE id=?",(status,c.iid))
    check(c,[c.decoy])


@pytest.mark.parametrize('name',ALIASES)
@pytest.mark.parametrize('kind',[None,'legacy'])
def test_list_alias_legacy(catalog,monkeypatch,name,kind):
    c=catalog;alias(c,monkeypatch,name,kind,'sqlite');before=dump(c.db)
    events=invoke(c,'zarinpal')
    assert len(events)==1 and events[0].text is None
    assert [x[0] for x in c.effects]==['expire_stale_extra_invoices','purge_old_extra_invoices','list_extra_invoices']
    assert [x for x in buttons(c) if x and x.startswith('view_xgw_invoice:')]==[f'view_xgw_invoice:{i}' for i in sorted([c.iid,c.decoy],reverse=True)]
    assert dump(c.db)==before


@pytest.mark.parametrize('position',['beyond50','beyond200','other_gateway'])
@pytest.mark.parametrize('status',['pending','completed'])
def test_hidden_composite_housekeeping(catalog,monkeypatch,position,status):
    c=catalog;alias(c,monkeypatch,'global_renewal_target','composite','sqlite')
    with c.db._get_conn() as conn:
        conn.execute("UPDATE extra_gateway_invoices SET status=?,gateway=?,created_at='2000-01-01',updated_at='2000-01-01' WHERE id=?",(status,'tgstars' if position=='other_gateway' else 'zarinpal',c.iid))
    for n in range(51 if position=='beyond50' else 201 if position=='beyond200' else 1):
        c.db.create_extra_invoice('zarinpal','wallet_topup',700+n,777,900,900)
    expected=[r['id'] for r in c.db.list_extra_invoices(50,'zarinpal')]
    assert c.iid not in expected;c.effects.clear()
    check(c,expected)


@pytest.mark.parametrize('kind',['wallet_topup','reseller_request'])
@pytest.mark.parametrize('status',['new','completed'])
def test_other_kind_collision_list(catalog,monkeypatch,kind,status):
    c=catalog;alias(c,monkeypatch,'global_renewal_target','composite','sqlite')
    with c.db._get_conn() as conn:conn.execute('UPDATE extra_gateway_invoices SET kind=?,status=? WHERE id=?',(kind,status,c.iid))
    before=dump(c.db);events=invoke(c,'zarinpal')
    assert len(events)==1 and events[0].text is None
    assert f'view_xgw_invoice:{c.iid}' in buttons(c)
    assert [x[0] for x in c.effects]==['expire_stale_extra_invoices','purge_old_extra_invoices','list_extra_invoices']
    assert dump(c.db)==before


def test_composite_only_list_empty(catalog,monkeypatch):
    c=catalog;alias(c,monkeypatch,'custom_product','composite','sqlite')
    with c.db._get_conn() as conn:conn.execute('DELETE FROM extra_gateway_invoices WHERE id=?',(c.decoy,))
    check(c,[])
    assert 'هیچ پرداختی ثبت نشده است.' in c.views[-1][1]
