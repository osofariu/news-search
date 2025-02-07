from typing import List
import pytest
from cache import NewsCache
from unittest.mock import MagicMock


def test_cache_age_is_expired(tmp_path):
    cache = NewsCache(max_cache_age_days=0)
    cache.cache_path = tmp_path
    cache.put_by_date("2024", "01", "test")
    assert cache.get_by_date("2024", "01") is None


def test_cache_age_is_not_expired(tmp_path):
    cache = NewsCache(max_cache_age_days=1)
    cache.cache_path = tmp_path
    cache.put_by_date("2024", "01", "test")
    assert cache.get_by_date("2024", "01") == "test"
