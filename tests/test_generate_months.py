import pytest
from nyt_api import NYTNewsApi

@pytest.fixture
def nytimes():
    return NYTNewsApi("fake_key") 

@pytest.mark.parametrize("start_date, end_date, expected", [
    ("2020-01", "2020-01", [("2020", "01")]), 
    ("2020-01", "2020-02", [("2020", "01"), ("2020", "02")]), 
    ("1905-12", "1906-02", [("1905", "12"), ("1906", "01"), ("1906", "02")]),
    ])
def test_good_date_range_generation(nytimes, start_date, end_date, expected):
    print(f"start_date: {start_date}, end_date: {end_date}, expected: {expected}")
    assert nytimes.generateMonths(start_date, end_date) == expected
    
def test_bad_year_range_generation(nytimes):
    with pytest.raises(ValueError):
        nytimes.generateMonths("2020-01", "2019-01")

def test_bad_month_range_generation(nytimes):
    with pytest.raises(ValueError):
        nytimes.generateMonths("2020-02", "2020-01")