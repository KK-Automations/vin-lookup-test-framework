from app.domain.check_digit import check_digit_valid
from app.domain.suggestions import suggest_corrections


class TestIllegalCharacterSuggestions:
    def test_letter_o_suggests_zero(self):
        suggestions = suggest_corrections("1HGCM8263OA004352")
        assert suggestions
        top = suggestions[0]
        assert top.vin == "1HGCM82630A004352"
        assert "O to 0" in top.description

    def test_check_digit_validated_suggestion_marked_high(self):
        # 1HGCM82633A004352 is valid; corrupt position 4 C -> I is not a
        # confusion we model, so use O at a position where 0 restores validity.
        suggestions = suggest_corrections("1HGCM82633A0O4352")
        assert any(s.vin == "1HGCM82633A004352" and s.confidence == "high"
                   for s in suggestions)


class TestConfusionPairSuggestions:
    def test_single_swap_restoring_check_digit(self):
        # Corrupt the valid VIN by S-for-5 confusion at position 16.
        suggestions = suggest_corrections("1HGCM82633A0043S2")
        assert any(s.vin == "1HGCM82633A004352" for s in suggestions)
        for s in suggestions:
            assert check_digit_valid(s.vin)

    def test_valid_vin_needs_no_suggestions(self):
        assert suggest_corrections("1HGCM82633A004352") == []

    def test_wrong_length_returns_empty(self):
        assert suggest_corrections("1HGCM8263") == []
