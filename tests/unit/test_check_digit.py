import pytest

from app.domain.check_digit import check_digit_valid, compute_check_digit


class TestComputeCheckDigit:
    def test_known_valid_vin(self):
        assert compute_check_digit("1HGCM82633A004352") == "3"

    def test_x_check_digit(self):
        assert compute_check_digit("1M8GDM9AXKP042788") == "X"

    def test_all_ones_is_valid(self):
        assert compute_check_digit("11111111111111111") == "1"

    def test_wrong_length_raises(self):
        with pytest.raises(ValueError):
            compute_check_digit("1HGCM82633A00435")

    def test_illegal_character_raises(self):
        with pytest.raises(ValueError):
            compute_check_digit("1HGCM82633A00435O")


class TestCheckDigitValid:
    def test_valid(self):
        assert check_digit_valid("1HGCM82633A004352")
        assert check_digit_valid("1M8GDM9AXKP042788")

    def test_single_transposition_detected(self):
        assert not check_digit_valid("1HGCM82634A004352")

    def test_lowercase_accepted(self):
        assert check_digit_valid("1hgcm82633a004352")

    def test_garbage_is_false_not_error(self):
        assert not check_digit_valid("")
        assert not check_digit_valid("short")
        assert not check_digit_valid("IIIIIIIIIIIIIIIII")
