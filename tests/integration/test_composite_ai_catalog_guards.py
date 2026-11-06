"""T050n: AI catalog discovery guard tests (tasks T050 / T053).

Refuse composite product discovery through unsupported AI catalog shortcuts,
while preserving legacy product discovery and isolated selected legacy options.
"""
import asyncio

import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings

use_synthetic_bot_settings()
import ai_support
from tests.integration.test_composite_ai_catalog_legacy import catalog, dump


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("selected", ["stock", "auto", "empty"])
@pytest.mark.parametrize("tool", ["list_products", "show_purchase_options"])
def test_composite_ai_catalog_refused(catalog, caplog, tool, selected, representation):
    c = catalog
    pid = getattr(c, selected)
    c.inject(pid, "composite", representation)
    before = dump(c.db)

    result = asyncio.run(ai_support._run_tool(c.db, 5101, tool, {"product_id": str(pid)}))

    assert isinstance(result, dict)
    assert not result.get("ok")
    refusal = result.get("reason") or result.get("error")
    assert refusal and "composite" in str(refusal).lower()
    assert "categories" not in result
    assert "products" not in result
    assert "SECRET-AI-PRODUCT" not in str(result)
    assert "SECRET-AI-PRODUCT" not in caplog.text
    assert dump(c.db) == before
    assert c.counts == []


@pytest.mark.parametrize("composite", ["auto", "empty"])
@pytest.mark.parametrize("representation", ["dict", "sqlite"])
def test_selected_legacy_ai_option_with_unrelated_composite(catalog, composite, representation):
    c = catalog
    composite_pid = getattr(c, composite)
    c.inject(composite_pid, "composite", representation)
    before = dump(c.db)

    result = asyncio.run(
        ai_support._run_tool(c.db, 5101, "show_purchase_options", {"product_id": str(c.stock)})
    )

    assert result == {"ok": True, "product_id": c.stock, "name": "Stock"}
    assert dump(c.db) == before
    assert c.counts == []
