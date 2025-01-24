from cache import NewsCache
from index import Index
from dataclasses import dataclass
from typing import Literal, TypedDict, List
import requests
import os
import logging
from datetime import datetime
import numpy as np
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ArchiveItem(TypedDict):
    """This class represents an item in the NYT Archive API response."""

    archive_date: str
    pub_date: str
    headline: str
    abstract: str
    lead_paragraph: str
    web_url: str


class ArchiveResponse(TypedDict):
    status: Literal["Ok", "RangeError"]
    message: str
    responses: List[ArchiveItem]


class NYTApi:
    def __init__(
        self,
        api_key: str,
        max_range: int = 12,
        cache: NewsCache = None,
        index: Index = None,
    ):
        self.api_key = api_key
        self.cache = cache or NewsCache()
        self.index = index or Index()
        self.max_range = max_range

    def get_archives(
        self, topic: str, start_date: str, end_date: str
    ) -> ArchiveResponse:
        """Given a topic and date range, get all the appropriate archive items and filter
        them by the topic.  If spanning more than one month make multiple calls.

        Args:
            topic: a search query for in the NYT archive.
            start_date: the beginning of the date range with format YYYY.MM.
            end_date: the beginning of the date range with format YYYY.MM.
        """

        months_to_query = self.generate_months(start_date, end_date)
        if len(months_to_query) > self.max_range:
            month = "month" if self.max_range == 1 else "months"
            return {
                "status": "RangeError",
                "responses": [],
                "message": f"Your time range is too large. Choose a time range no longer than {self.max_range} {month}.",
            }

        archive_items_by_month = []
        for year, month in months_to_query:
            api_response = self.get_monthly_archive(year, month)
            archive_item_date = f"{year}-{month}"
            self.index.create_vector_store(archive_item_date)
            archive_items_by_month.append(api_response)

        filtered_archive_items = self.filter_by_topic(archive_items_by_month, topic)

        return {"status": "Ok", "responses": filtered_archive_items}

    def filter_by_topic(
        self, archive_items_by_month: List[List[ArchiveItem]], topic: str
    ) -> List[ArchiveItem]:
        """This function filters the archive items by a given topic."""
        if topic == None:
            return [
                archive_item
                for archive_items in archive_items_by_month
                for archive_item in archive_items
            ]

        response = []
        for archive_items in archive_items_by_month:
            archive_date = archive_items[0].get("archive_date")
            matched_items = self.index.search_index(archive_date, topic)

            for archive_item in archive_items:
                headline = archive_item.get("headline")
                if headline in matched_items:
                    response.append(archive_item)
        return response

    def get_monthly_archive(self, year, month) -> List[ArchiveItem]:
        """get archive from cache if present, else call the API and cache the results
        Args:
            year (_type_): _description_
            month (_type_): _description_
        """
        if cached_archive := self.cache.get_by_date(year, month):
            logger.info(f"Using cached archive for {year}-{month}")
            return cached_archive
        archive = self.call_archive_api(year, month)
        self.cache.put_by_date(year, month, archive)
        return archive

    def call_archive_api(self, year: str, month: str) -> List[ArchiveItem]:
        """This function returns the NYT Archive API response for a given year and month."""
        base_url = "https://api.nytimes.com/svc/archive/v1"
        url = f"{base_url}/{int(year)}/{int(month)}.json?api-key={self.api_key}"

        logger.info(f"Calling NYT Archive API for {year}-{month}")
        response = requests.get(url)
        status_code = response.status_code
        if status_code != 200:
            logger.error(f"API error: {response.text}")
            raise (Exception(f"Error: {response.text}"))
        json_response = response.json()
        return self.map_to_archive_item(json_response, f"{year}-{month}")

    def map_to_archive_item(self, api_response, archive_date) -> List[ArchiveItem]:
        """This function maps each doc in the API response to an ArchiveItem."""
        docs = api_response.get("response", {}).get("docs", [])
        if not docs:
            return []
        return [
            ArchiveItem(
                archive_date=archive_date,
                pub_date=doc.get("pub_date", ""),
                headline=doc.get("headline", {}).get("main", ""),
                abstract=doc.get("abstract", ""),
                web_url=doc.get("web_url", ""),
                lead_paragraph=doc.get("lead_paragraph", ""),
            )
            for doc in docs
        ]

    def generate_months(self, start_date: str, end_date: str) -> List[str]:
        """Given the range of months, generate a list of (year, month) tuples
        to make it easy to call the NYT Archive API for each month in the range.

        Args:
            - start_date (str): String representing start date in format YYYY-MM
            - end_date (str): String representing end date in format YYYY-MM
        """
        start_year, start_month = start_date.split("-")
        end_year, end_month = end_date.split("-")
        dates = []
        if int(start_year) > int(end_year):
            raise ValueError("Start year must be less than or equal to end year")

        if int(start_year) == int(end_year) and int(start_month) > int(end_month):
            raise ValueError("Start month must be less than or equal to end month")
        for year in range(int(start_year), int(end_year) + 1):
            for month in range(1, 13):
                if year == int(start_year) and month < int(start_month):
                    continue
                if year == int(end_year) and month > int(end_month):
                    continue
                dates.append((str(year), str(month).zfill(2)))
        return dates


def main():
    logging.basicConfig(filename="logs/nyt_api.log", level=logging.INFO)

    today = datetime.today().strftime("%Y-%m-%d")
    three_months_ago = np.datetime64(today) - np.timedelta64(90, "D")
    start_date = str(three_months_ago)[:7]  # keey YYYY-MM

    end_date = datetime.today().strftime("%Y-%m")
    topic = "COVID"

    start_date = input(f"Start date (default {start_date}) > ") or start_date
    end_date = input(f"  End date (default {end_date}) > ") or end_date
    topic = input(f"   Topic: (default {topic}) > ") or topic
    logger.info(f"Searching NYT archive for {topic} from {start_date} to {end_date}.")

    api_key = os.getenv("NYT_API_KEY")
    news_api = NYTApi(api_key)
    response = news_api.get_archives(topic, start_date, end_date)


if __name__ == "__main__":
    main()
