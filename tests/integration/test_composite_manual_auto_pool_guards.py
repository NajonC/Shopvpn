"""T050bx/by: manual AUTO/pool-renewal success, failure and selected aliases."""
import pytest
from tests.integration.test_composite_manual_catalog_guards import (
    catalog, auto_catalog, refused, legacy, opaque,
)

@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('branch,marker',[
    ('auto','order'),('auto','product'),
    ('renewal','order'),('renewal','product'),('renewal','target'),
])
@pytest.mark.parametrize('scenario',['success','failure','prior'])
def test_composite_manual_auto_pool(auto_catalog,monkeypatch,representation,branch,marker,scenario,caplog):
    refused(auto_catalog,monkeypatch,representation,branch,marker,scenario,caplog)

@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('branch,quantity',[('auto',0),('auto',2),('renewal',2)])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('scenario',['success','failure','prior','lost_claim','delivery'])
def test_legacy_manual_auto_pool(auto_catalog,monkeypatch,representation,branch,quantity,kind,scenario):
    if scenario=='failure' and quantity==0:quantity=2
    legacy(auto_catalog,monkeypatch,representation,branch,kind,scenario,quantity)

@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('branch',['auto','renewal'])
@pytest.mark.parametrize('failure',['unauthorized','malformed','missing'])
def test_manual_auto_pool_opaque(auto_catalog,monkeypatch,representation,branch,failure):
    opaque(auto_catalog,monkeypatch,representation,branch,failure)
