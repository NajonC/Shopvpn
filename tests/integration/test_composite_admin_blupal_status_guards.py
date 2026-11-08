"""T050bp/bq: actual BluPal admin status, claim competition and SQL effects."""
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog
from tests.integration.test_composite_admin_abangateway_status_guards import composite,legacy,opaque,topup

@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('scenario',['pending','expired','paid_success','completed'])
def test_composite_admin_blupal_refused(catalog,monkeypatch,representation,marker,scenario,caplog):
    composite(catalog,monkeypatch,representation,marker,scenario,'blupal',caplog)

@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('scenario',['pending','partially_paid','expired','cancelled','completed','remote_error','claim_lost','no_key','paid_prior','paid_missing_server','paid_provider_error','paid_success'])
def test_legacy_admin_blupal_exact(catalog,monkeypatch,representation,kind,scenario):
    legacy(catalog,monkeypatch,representation,kind,scenario,'blupal')

@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('failure',['malformed','missing','unauthorized'])
def test_admin_blupal_opaque(catalog,monkeypatch,representation,failure):opaque(catalog,monkeypatch,representation,failure,'blupal')

@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_admin_blupal_topup(catalog,monkeypatch,representation):topup(catalog,monkeypatch,representation,'blupal')
