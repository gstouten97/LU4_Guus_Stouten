from pickle import FALSE

import pytest

import main_biker_app
from main_biker_app import *

def multiply(a, b):
    return a * b

def test_multiply_positives():
    assert multiply(2, 3) == 6  # Test case 1

def test_multiply_negative():
    assert multiply(-1, 1) == -1  # Test case 2

def test_multiply_zero():
    assert multiply(0, 5) == 0   # Test case 3

@pytest.mark.parametrize("input,expected", [
    ("guus", False),
    ("guus@guus", False),
    ("guus.com", False),
    ("guus@guus.com", True)
])

def test_valid_email(input, expected):
    assert main_biker_app.BikeRentalApp.is_valid_email(BikeRentalApp,input) == expected;
