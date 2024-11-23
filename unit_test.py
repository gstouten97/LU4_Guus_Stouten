import pytest

import main_biker_app
from main_biker_app import *

@pytest.mark.parametrize("input,expected", [
    ("guus", False),
    ("guus@guus", False),
    ("guus.com", False),
    ("guus@guus.com", True)
])

def test_valid_email(input, expected):
    assert main_biker_app.BikeRentalApp.is_valid_email(BikeRentalApp,input) == expected;


@pytest.mark.parametrize("input,expected", [
    ("Bike", True),
    ("Electric Bike", True),
    ("Car", False),
    ("", False)
])
def test_valid_rental_type(input, expected):
    is_valid = input in ["Bike", "Electric Bike"]
    assert is_valid == expected
