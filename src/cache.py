from datetime import datetime
import json
import os

from utils import file_is_expired


class NewsCache:
    """
    NewsCache is a class responsible for caching news archive items. It provides methods
    to store and retrieve cached items based on a date key in the format "YYYY-MM".
    The cache has a maximum age limit, after which cached items are considered expired
    and are not returned.

    Attributes:
        cache_path (str): The directory path where cache files are stored.
        max_cache_age_days (int): The maximum age of cache items in days before they
        are considered expired.
    """

    def __init__(self, max_cache_age_days=5):
        self.cache_path = "cache"
        self.max_cache_age_days = max_cache_age_days
        os.makedirs(self.cache_path, exist_ok=True)

    def get_by_date(self, year, month):
        """
        Retrieve cached items based on the provided year and month.

        Args:
            year (str): The year in "YYYY" format.
            month (str): The month in "MM" format.

        Returns:
            - None if the cache item is not found or is expired.
            - List[ArchiveItem]: A list of ArchiveItem objects if the cache item is found and is not expired.
        """

        key = f"{year}-{month}"
        return self.get(key, self.max_cache_age_days)

    def put_by_date(self, year, month, value):
        """add item to cache if not already present
        Args:
            key (str): "YYYY-MM" formatted date
            value (List[ArchiveItem]:): archive items matching the key
        """
        key = f"{year}-{month}"
        self.put(key, value)

    def get(self, key, max_cache_age_days):
        try:
            file_path = f"{self.cache_path}/{key}.json"
            if file_is_expired(file_path, key, max_cache_age_days):
                return None
            else:
                with open(file_path, "r") as f:
                    return json.load(f)

        except FileNotFoundError:
            return None

    def put(self, key, value):
        with open(f"{self.cache_path}/{key}.json", "w") as f:
            json.dump(value, f)

    def get_path(self, key):
        return f"{self.cache_path}/{key}.json"
