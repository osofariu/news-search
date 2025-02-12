from datetime import datetime, timedelta
from typing import List
import pytest
from cache import NewsCache


def test_cache_age_is_expired(tmp_path):
    cache = NewsCache(max_cache_age_days=0)
    this_year = str(datetime.now().year)
    this_month = f"{datetime.now().month:02d}"
    cache.put_by_date(this_year, this_month, "test")
    assert cache.get_by_date(this_year, this_month) is None


def test_cache_age_is_not_expired(tmp_path):
    one_milisecond = 1 / (24 * 60 * 60 * 1000)
    cache = NewsCache(max_cache_age_days=one_milisecond)
    cache.cache_path = tmp_path
    cache.put_by_date("2024", "01", "test")
    assert cache.get_by_date("2024", "01") == "test"


def test_cache_age_is_not_expired_for_previous_month(tmp_path):
    cache = NewsCache(max_cache_age_days=0)
    cache.cache_path = tmp_path
    this_year = str(datetime.now().year)
    last_month = str(datetime.now().month - 1)
    cache.put_by_date(this_year, last_month, "test")
    assert cache.get_by_date(this_year, last_month) == "test"
