import pytest

from services.dummyjson_integrator import DummyJsonProductIntegrator


@pytest.mark.asyncio
async def test_dummyjson_integrator_fetch_and_map():
    integrator = DummyJsonProductIntegrator()
    products = await integrator.fetch_products()
    assert isinstance(products, list)
    assert len(products) > 0
    # Перевіряємо що хоча б один продукт має dimensions
    found_dimensions = any("dimensions" in p and p["dimensions"] for p in products)
    assert found_dimensions
    # Перевіряємо map_to_internal
    for ext in products:
        mapped = integrator.map_to_internal(ext)
        assert "title" in mapped
        assert "external_id" in mapped
        # Якщо були dimensions — мають бути скопійовані
        if ext.get("dimensions"):
            assert mapped["height"] == ext["dimensions"].get("height")
            assert mapped["length"] == ext["dimensions"].get("length")
            assert mapped["depth"] == ext["dimensions"].get("depth")
