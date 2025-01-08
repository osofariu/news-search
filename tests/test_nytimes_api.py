import pytest
from nyt_api import NYTimesArchive

@pytest.fixture
def nyt_archive():
    return NYTimesArchive() 

@pytest.mark.parametrize("start_date, end_date, expected", [
    ("2020-01", "2020-01", [("2020", "01")]), 
    ("2020-01", "2020-02", [("2020", "01"), ("2020", "02")]), 
    ])
def test_good_date_range_generation(nyt_archive, start_date, end_date, expected):
    print(f"start_date: {start_date}, end_date: {end_date}, expected: {expected}")
    assert nyt_archive.generateMonths(start_date, end_date) == expected
    
def test_bad_year_range_generation(nyt_archive):
    with pytest.raises(ValueError):
        nyt_archive.generateMonths("2020-01", "2019-01")

def test_bad_month_range_generation(nyt_archive):
    with pytest.raises(ValueError):
        nyt_archive.generateMonths("2020-02", "2020-01")