from app.normalization.query_normalizer import normalize_query


def test_normalize_etch_and_cd():
    result = normalize_query("AMAT plasma etch CD")
    assert result["original"] == "AMAT plasma etch CD"
    assert "applied materials" in result["normalized"]
    assert "critical dimension" in result["normalized"]
