"""ISO 3779 check digit computation (VIN position 9, North America mandatory)."""

TRANSLITERATION = {
    "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8,
    "J": 1, "K": 2, "L": 3, "M": 4, "N": 5, "P": 7, "R": 9,
    "S": 2, "T": 3, "U": 4, "V": 5, "W": 6, "X": 7, "Y": 8, "Z": 9,
    "0": 0, "1": 1, "2": 2, "3": 3, "4": 4,
    "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
}

WEIGHTS = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]


def compute_check_digit(vin: str) -> str:
    """Return the expected check digit character for a 17 character VIN."""
    if len(vin) != 17:
        raise ValueError("VIN must be exactly 17 characters")
    total = 0
    for ch, weight in zip(vin.upper(), WEIGHTS):
        if ch not in TRANSLITERATION:
            raise ValueError(f"Character {ch!r} is not allowed in a VIN")
        total += TRANSLITERATION[ch] * weight
    remainder = total % 11
    return "X" if remainder == 10 else str(remainder)


def check_digit_valid(vin: str) -> bool:
    """True when position 9 matches the ISO 3779 computed check digit."""
    try:
        return vin[8].upper() == compute_check_digit(vin)
    except (ValueError, IndexError):
        return False
