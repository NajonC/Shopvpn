"""T050bt/bu: upstream BluPal catalog dispatch and conditional SQL claim."""
import pytest
from tests.integration.test_composite_admin_aban_catalog_status_guards import (
    catalog, auto_catalog, BRANCHES, composite, legacy, opaque,
)

@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('branch',BRANCHES)
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('scenario',['pending','expired','paid','completed'])
def test_composite_blupal_catalog(auto_catalog,monkeypatch,representation,branch,marker,scenario,caplog):
    composite(auto_catalog,monkeypatch,'blupal',representation,branch,marker,scenario,caplog)

@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('branch',BRANCHES)
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('scenario',['paid','prior','fulfillment_failure','pending','expired','cancelled','remote_error','completed','claim_lost'])
def test_legacy_blupal_catalog(auto_catalog,monkeypatch,representation,branch,kind,scenario):
    legacy(auto_catalog,monkeypatch,'blupal',representation,branch,kind,scenario)

@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('branch',BRANCHES)
@pytest.mark.parametrize('failure',['unauthorized','malformed','missing'])
def test_blupal_catalog_opaque(auto_catalog,monkeypatch,representation,branch,failure):
    opaque(auto_catalog,monkeypatch,'blupal',representation,branch,failure)
