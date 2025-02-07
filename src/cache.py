import json
import os
import time


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

    def get_by_date(self, year, month):
        key = f"{year}-{month}"
        max_cache_age_milliseconds = self.max_cache_age_days * 24 * 60 * 60 * 1000
        return self.get(key, max_cache_age_milliseconds)

    def get(self, key, max_cache_age_milliseconds):
        """get item from cache
        Args:
            - key (str): "YYYY-MM" formatted date
        Returns:
            - None if cache item not found or was created more than max_cache_age_milliseconds ago
            - List[ArchiveItem]: a list of ArchiveItem objects
        """
        try:
            file_path = f"{self.cache_path}/{key}.json"
            with open(file_path, "r") as f:
                file_creation_time = os.path.getctime(file_path)
                current_time = time.time()
                age_in_milliseconds = (current_time - file_creation_time) * 1000
                return (
                    None
                    if age_in_milliseconds > max_cache_age_milliseconds
                    else json.load(f)
                )
        except FileNotFoundError:
            return None

    def put_by_date(self, year, month, value):
        key = f"{year}-{month}"
        self.put(key, value)

    def put(self, key, value):
        """add item to cache if not already present
        Args:
            key (str): "YYYY-MM" formatted date
            value (List[ArchiveItem]:): archive items matching the key
        """

        with open(f"{self.cache_path}/{key}.json", "w") as f:
            json.dump(value, f)
