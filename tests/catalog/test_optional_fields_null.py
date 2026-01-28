from app.schemas.catalog import ProductResponse

def test_optional_fields_are_null():
    product = ProductResponse(id=1, name="Test Product", price=None)
    data = product.model_dump()
    assert "old_price" in data
    assert data["old_price"] is None
    assert "unit" in data
    assert data["unit"] is None
    assert "nutritional_info" in data
    assert data["nutritional_info"] is None
