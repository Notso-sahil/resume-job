import pytest
from finder.stipend_parser import extract_stipend, is_above_threshold

def test_extract_stipend_monthly_inr():
    assert extract_stipend("₹25,000/month") == 25000
    assert extract_stipend("25000 per month") == 25000
    assert extract_stipend("25k p.m.") == 25000

def test_extract_stipend_lpa():
    assert extract_stipend("3 LPA") == 25000
    assert extract_stipend("3.6 LPA") == 30000

def test_extract_stipend_usd():
    assert extract_stipend("$300/mo") == 25200
    assert extract_stipend("$3000/month") == 252000

def test_extract_stipend_ranges():
    assert extract_stipend("20k - 30k") == 20000
    assert extract_stipend("25000-35000") == 25000

def test_extract_stipend_edge_cases():
    assert extract_stipend("Not disclosed") == 0
    assert extract_stipend("Unpaid") == 0
    assert extract_stipend("") == 0
    assert extract_stipend(None) == 0  # type: ignore

def test_is_above_threshold():
    assert is_above_threshold(25000) is True
    assert is_above_threshold(15000) is False
    assert is_above_threshold(20000) is True
    assert is_above_threshold(25000, threshold=30000) is False
