import pytest
from sandbox_dating_sim.core.ids import is_valid_id, normalize_id

def test_valid_id():
    assert is_valid_id("sophie_route_started")

def test_invalid_id_starts_with_number():
    assert not is_valid_id("1sophie")

def test_invalid_id_contains_chinese():
    assert not is_valid_id("蘇菲")

def test_normalize_id():
    assert normalize_id("Summer City") == "summer_city"

def test_normalize_id_with_hyphens():
    assert normalize_id("cool-place-123") == "cool_place_123"

def test_normalize_id_rejects_chinese():
    with pytest.raises(ValueError, match="contains Chinese characters"):
        normalize_id("Summer夏日")
