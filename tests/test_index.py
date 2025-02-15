from datetime import datetime
import os
from cache import NewsCache
from index import Index
from nyt_api import ArchiveItem


def test_search_index(tmp_path):
    cache = create_cache(
        tmp_path, [{"headline": "test headline", "abstract": "abstract"}]
    )
    index = Index(max_index_age_days=1)
    index.index_path = tmp_path
    index.cache = cache

    search_date = get_search_date()
    index.create_vector_store(search_date)

    assert os.path.exists(f"{index.index_path}/{search_date}.faiss_index")

    result = index.search_index(search_date, "test")
    # we concatenate heading and abstract in the index to capture embedding from both
    assert result == ["test headline abstract"]


def test_index_recreated_when_index_is_expired(tmp_path):
    cache = create_cache(
        tmp_path,
        [
            {"headline": "In Times Square, Hundreds of Thousands Ring In 2024."},
        ],
    )
    # index the contents of the cache with the Times Square headline
    index = Index(cache=cache, max_index_age_days=0)
    index.index_path = tmp_path
    index.create_vector_store(get_search_date())

    cache = create_cache(
        tmp_path,
        [
            {
                "headline": "Chill in the Housing Market Seeps Into Other Industries",
                "abstract": "bad news",
            },
        ],
    )

    # index should be recreated since max_index_age_days is 0, thus expired
    # so it should contain the Housing Market headline
    search_date = get_search_date()
    index.create_vector_store(search_date)

    result = index.search_index(search_date, "Housing Market")
    assert "Chill in the Housing Market Seeps Into Other Industries bad news" in result


def get_search_date():
    this_year = str(datetime.now().year)
    this_month = f"{datetime.now().month:02d}"
    search_date = f"{this_year}-{this_month}"
    return search_date


def create_cache(path, items):
    cache = NewsCache(max_cache_age_days=1)
    cache.cache_path = path
    this_year = str(datetime.now().year)
    this_month = f"{datetime.now().month:02d}"
    search_date = f"{this_year}-{this_month}"
    cache.put_by_date(this_year, this_month, items)
    return cache
