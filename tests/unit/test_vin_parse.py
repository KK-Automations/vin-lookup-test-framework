from app.domain.model_year import decode_model_year
from app.domain.vin import normalize_vin, parse_vin


class TestNormalize:
    def test_strips_spaces_hyphens_and_uppercases(self):
        assert normalize_vin(" 1hg-cm8 2633a004352 ") == "1HGCM82633A004352"


class TestParseVin:
    def test_valid_vin_parses_structure(self):
        parsed = parse_vin("1HGCM82633A004352")
        assert parsed.ok
        assert parsed.valid_format
        assert parsed.check_digit_ok
        assert parsed.wmi == "1HG"
        assert parsed.vds == "CM8263"
        assert parsed.vis == "3A004352"

    def test_short_vin_reports_length(self):
        parsed = parse_vin("1HGCM8263")
        assert not parsed.ok
        assert parsed.errors[0].code == "length"
        assert "9" in parsed.errors[0].message

    def test_illegal_letters_reported(self):
        parsed = parse_vin("1HGCM8263OA004352")
        assert not parsed.ok
        assert parsed.errors[0].code == "illegal_chars"

    def test_check_digit_failure_is_warning_by_default(self):
        parsed = parse_vin("1HGCM82634A004352")
        assert parsed.ok
        assert parsed.warnings[0].code == "check_digit"

    def test_check_digit_failure_is_error_in_strict_mode(self):
        parsed = parse_vin("1HGCM82634A004352", strict=True)
        assert not parsed.ok


class TestModelYear:
    def test_numeric_position7_selects_old_window(self):
        # 1HGCM82633A004352: position 7 is "2" (numeric), code "3" -> 2003
        decode = decode_model_year("1HGCM82633A004352")
        assert decode.year == 2003
        assert decode.rule_applied == "position7_numeric_1980_2009"

    def test_alpha_position7_selects_new_window(self):
        # Position 7 "A" alphabetic, year code "K" -> 2019
        decode = decode_model_year("5YJ3E1EAXKF000316")
        assert decode.year == 2019
        assert decode.rule_applied == "position7_alpha_2010_2039"

    def test_invalid_year_code(self):
        decode = decode_model_year("1HGCM8263UA004352")
        assert decode.year is None
        assert decode.rule_applied == "invalid_year_code"
