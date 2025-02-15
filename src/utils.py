from datetime import datetime
import logging
import os
import time

logger = logging.getLogger(__name__)


def file_is_expired(file_path, key, max_cache_age_days):
    """news items get created every day in the archive, so to stay fresh we want to refresh
    the cache periodically, but we don't want to do it all the time -- this max_cache_age_days
    is used to find a balance between freshness and not refreshing too often
    """
    max_cache_age_milliseconds = max_cache_age_days * 24 * 60 * 60 * 1000
    is_expired = file_is_for_current_month(key) and file_created_before_max_age(
        file_path, max_cache_age_milliseconds
    )
    logger.debug(f"file_path: {file_path} is_expired: {is_expired}")
    return is_expired


def file_created_before_max_age(file_path, max_cache_age_milliseconds):
    file_creation_time = os.path.getctime(file_path)
    current_time = time.time()
    age_in_milliseconds = (current_time - file_creation_time) * 1000
    age_in_days = age_in_milliseconds / (24 * 60 * 60 * 1000)
    logger.debug(
        f"file_path: {file_path} age in days: {age_in_days} expired: {age_in_milliseconds > max_cache_age_milliseconds}"
    )
    return age_in_milliseconds > max_cache_age_milliseconds


def file_is_for_current_month(file_key):
    this_year = str(datetime.now().year)
    this_month = f"{datetime.now().month:02d}"
    current_date_key = f"{this_year}-{this_month}"
    logger.debug(f"file is for current month: {file_key == current_date_key}")

    return file_key == current_date_key
