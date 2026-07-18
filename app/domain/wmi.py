"""World Manufacturer Identifier (VIN positions 1-3) lookups.

The region map follows the SAE first character allocation. The manufacturer
table is a curated subset of common North American market WMIs; it is not
exhaustive, and the local structural provider only reports what it finds here.
"""

REGIONS = {
    "1": ("North America", "United States"),
    "4": ("North America", "United States"),
    "5": ("North America", "United States"),
    "7": ("North America", "United States"),
    "2": ("North America", "Canada"),
    "3": ("North America", "Mexico"),
    "6": ("Oceania", "Australia"),
    "8": ("South America", None),
    "9": ("South America", "Brazil"),
    "J": ("Asia", "Japan"),
    "K": ("Asia", "South Korea"),
    "L": ("Asia", "China"),
    "M": ("Asia", "India"),
    "N": ("Asia", "Turkey"),
    "R": ("Asia", None),
    "S": ("Europe", "United Kingdom"),
    "T": ("Europe", None),
    "V": ("Europe", None),
    "W": ("Europe", "Germany"),
    "X": ("Europe", None),
    "Y": ("Europe", "Sweden"),
    "Z": ("Europe", "Italy"),
}

MANUFACTURERS = {
    # United States
    "1C3": "Chrysler", "1C4": "Chrysler", "1C6": "Ram",
    "1D7": "Dodge", "1FA": "Ford", "1FB": "Ford", "1FC": "Ford",
    "1FD": "Ford", "1FM": "Ford", "1FT": "Ford", "1FU": "Freightliner",
    "1G1": "Chevrolet", "1G4": "Buick", "1G6": "Cadillac", "1GC": "Chevrolet",
    "1GK": "GMC", "1GM": "Pontiac", "1GT": "GMC", "1GY": "Cadillac",
    "1HD": "Harley-Davidson", "1HG": "Honda", "1J4": "Jeep", "1J8": "Jeep",
    "1LN": "Lincoln", "1ME": "Mercury", "1N4": "Nissan", "1N6": "Nissan",
    "1NX": "Toyota", "1VW": "Volkswagen", "1YV": "Mazda",
    "4F2": "Mazda", "4JG": "Mercedes-Benz", "4M2": "Mercury",
    "4S3": "Subaru", "4S4": "Subaru", "4T1": "Toyota", "4T3": "Toyota",
    "4US": "BMW", "5FN": "Honda", "5FP": "Honda", "5J6": "Honda",
    "5LM": "Lincoln", "5N1": "Nissan", "5NP": "Hyundai", "5TB": "Toyota",
    "5TD": "Toyota", "5TF": "Toyota", "5UX": "BMW", "5XX": "Kia",
    "5XY": "Kia", "5YJ": "Tesla", "7SA": "Tesla",
    # Canada
    "2C3": "Chrysler", "2C4": "Chrysler", "2D3": "Dodge", "2FA": "Ford",
    "2FM": "Ford", "2FT": "Ford", "2G1": "Chevrolet", "2G4": "Buick",
    "2G9": "General Motors", "2HG": "Honda", "2HH": "Acura", "2HJ": "Honda",
    "2HK": "Honda", "2HM": "Hyundai", "2T1": "Toyota", "2T2": "Lexus",
    "2T3": "Toyota",
    # Mexico
    "3C4": "Chrysler", "3C6": "Ram", "3FA": "Ford", "3FE": "Ford",
    "3G1": "Chevrolet", "3GN": "Chevrolet", "3GC": "Chevrolet",
    "3HG": "Honda", "3HM": "Honda", "3KP": "Kia", "3MZ": "Mazda",
    "3N1": "Nissan", "3N6": "Nissan", "3VW": "Volkswagen",
    # Japan
    "JA3": "Mitsubishi", "JA4": "Mitsubishi", "JF1": "Subaru",
    "JF2": "Subaru", "JH4": "Acura", "JHM": "Honda", "JM1": "Mazda",
    "JM3": "Mazda", "JN1": "Nissan", "JN8": "Nissan", "JT2": "Toyota",
    "JT3": "Toyota", "JT4": "Toyota", "JT6": "Lexus", "JT8": "Lexus",
    "JTD": "Toyota", "JTE": "Toyota", "JTH": "Lexus", "JTJ": "Lexus",
    "JTK": "Toyota", "JTL": "Toyota", "JTM": "Toyota", "JTN": "Toyota",
    # South Korea
    "KL4": "Buick", "KM8": "Hyundai", "KMH": "Hyundai", "KNA": "Kia",
    "KND": "Kia", "KNM": "Renault Samsung",
    # Germany
    "WA1": "Audi", "WAU": "Audi", "WBA": "BMW", "WBS": "BMW",
    "WBX": "BMW", "WBY": "BMW", "WDB": "Mercedes-Benz",
    "WDC": "Mercedes-Benz", "WDD": "Mercedes-Benz", "WMW": "Mini",
    "WP0": "Porsche", "WP1": "Porsche", "WVG": "Volkswagen",
    "WVW": "Volkswagen", "W1K": "Mercedes-Benz", "W1N": "Mercedes-Benz",
    # Other Europe
    "SAJ": "Jaguar", "SAL": "Land Rover", "SCA": "Rolls-Royce",
    "SCC": "Lotus", "SCF": "Aston Martin", "SHS": "Honda",
    "VF1": "Renault", "VF3": "Peugeot", "VF7": "Citroen",
    "YV1": "Volvo", "YV4": "Volvo", "ZAM": "Maserati",
    "ZAR": "Alfa Romeo", "ZFA": "Fiat", "ZFF": "Ferrari",
    # Brazil
    "93H": "Honda", "9BW": "Volkswagen", "9BG": "Chevrolet",
}


def region_for(vin: str) -> tuple[str | None, str | None]:
    """Return (region, country) for the first VIN character."""
    if not vin:
        return (None, None)
    return REGIONS.get(vin[0].upper(), (None, None))


def manufacturer_for(wmi: str) -> str | None:
    """Return the manufacturer for a 3 character WMI, if curated."""
    return MANUFACTURERS.get(wmi.upper())
