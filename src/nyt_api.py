from cache import NewsCache
from dataclasses import dataclass
from typing import TypedDict, List
import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ArchiveQuery(TypedDict):
    '''Class for keeping track of an item in inventory.'''
    topic: str
    start_date: str
    end_date: str

class ArchiveItem(TypedDict):
    pub_date: str
    headline: str
    abstract: str
    lead_paragraph: str
    web_url: str

class ArchiveResponse(TypedDict):
    status: int
    responses: List[ArchiveItem]

 
""" PLANS 

- turn the wrapper into a class
- add a method to call the API
- cache results on each call, saving the results in a file
- add a method to read the cache on each call

"""

class NYTNews:
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.cache = NewsCache()
        print(f"NYTNews initialized with API key {api_key}")

    def get_archives(self, topic: str, start_date: str, end_date: str) -> ArchiveResponse:
        '''This function wraps the nyt_archive_api function and returns the response.
        
        Args:
            topic: a search query for in the NYT archive.
            start_date: the beginning of the date range with format YYYY.MM.
            end_date: the beginning of the date range with format YYYY.MM.            
        '''
        
        months_to_query = self.generateMonths(start_date, end_date)
        archiveItems = []
        for year, month in months_to_query:
            api_response = self.get_archive(year, month)
            archiveItems.extend(api_response)
        
        # TODO: each API returns a status code; this status should be a higher-level status
        #        maybe something like "OK" or "ERROR".. or just throw an exception.
        if not archiveItems:
            return {"status": 404, "responses": []}
        
        filtered_archive_items = self.filter_by_topic(archiveItems, topic)
        return {"status": 200, "responses": filtered_archive_items}

    def filter_by_topic(self, archive_items: List[ArchiveItem], topic: str) -> List[ArchiveItem]:
        '''This function filters the archive items by a given topic.'''
        if topic == None:
            return archive_items
        
        return [item for item in archive_items 
                if topic.lower() in item.get('headline', '').lower() 
                or topic.lower() in item.get('abstract', '').lower()]

    def get_archive(self, year, month):
        """get archive from cache if present, else call the API and cache the results
        Args:
            year (_type_): _description_
            month (_type_): _description_
        """
        cached_archive = self.cache.get_by_date(year, month)
        if cached_archive:
            return cached_archive
        api_response = self.call_archive_api(year, month)
        archive = self.map_to_archive_item(api_response)
        self.cache.put_by_date(year, month, archive)
        return archive
    
    
    def call_archive_api(self, year, month):
        '''This function returns the NYT Archive API response for a given year and month.'''
        year_int = int(year)
        month_int = int(month)
        url = f'https://api.nytimes.com/svc/archive/v1/{year_int}/{month_int}.json?api-key={self.api_key}'
        
        print(f"Calling NYT Archive API for {year}-{month}: {url}")
        response = requests.get(url)
        status_code = response.status_code
        if status_code != 200:
            raise(Exception(f"Error: {response.text}"))
        json_response = response.json()
        return json_response
  

    def map_to_archive_item(self, api_response) -> List[ArchiveItem]:
        '''This function maps the API response to an ArchiveItem.'''
        docs = api_response.get('response', {}).get('docs', [])
        if not docs:
            return []
        return [ArchiveItem(
            pub_date=doc.get('pub_date', ''),
            headline=doc.get('headline', {}).get('main', ''),
            abstract=doc.get('abstract', ''),
            web_url=doc.get('web_url', ''),
            lead_paragraph=doc.get('lead_paragraph', '')
        ) for doc in docs]

    def generateMonths(self, start_date: str, end_date: str) -> List[str]:
        """_summary_

        Args:
            start_date (str): String representing start date in format YYYY-MM
            end_date (str): String representing end date in format YYYY-MM
        """
        start_year, start_month = start_date.split("-")
        end_year, end_month = end_date.split("-")
        dates = []
        if int(start_year) > int(end_year):
            raise ValueError("Start year must be less than or equal to end year")
        
        if int(start_year) == int(end_year) and int(start_month) > int(end_month):
            raise ValueError("Start month must be less than or equal to end month")
        for year in range(int(start_year), int(end_year)+1):
            for month in range(1, 13):
                if year == int(start_year) and month < int(start_month):
                    continue
                if year == int(end_year) and month > int(end_month):
                    continue
                dates.append((str(year), str(month).zfill(2)))
        return dates

if __name__ == "__main__":
    
    start_date="2024-09"
    end_date="2024-12"
      
    start_date = input("Enter start date (YYYY-MM): ") or start_date
    end_date = input("Enter end date (YYYY-MM): ") or end_date
    topic = input("Enter topic: ") or "Romania"
    
    print(f"Searching NYT archive for {topic} from {start_date} to {end_date}")
    
    api_key = os.getenv("NYT_API_KEY")
    news_api = NYTNews(api_key)
    response = news_api.get_archives(topic, start_date, end_date)    
    print("# Response:\n")
    print(response)