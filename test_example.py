from pickle import FALSE

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
