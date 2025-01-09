from dataclasses import dataclass
from typing import TypedDict, List
import requests
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ArchiveQuery(TypedDict):
    '''Class for keeping track of an item in inventory.'''
    topic: str
    start_date: str
    end_date: str

class ArchiveItem(TypedDict):
    name: str
    pub_date: str
    headline: str
    abstract: str
    web_url: str
    snippet: str
    lead_paragraph: str
    
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
            api_response = self.call_archive_api(year, month)
            
            archiveItems.extend(self.map_to_archive_item(api_response))
        
        # TODO: each API returns a status code; this status should be a higher-level status
        #        maybe something like "OK" or "ERROR".. or just throw an exception.
        return {"status": 200, "responses": archiveItems}


    def call_archive_api(self, year, month):
        '''This function returns the NYT Archive API response for a given year and month.'''
        url = f'https://api.nytimes.com/svc/archive/v1/{year}/{month}.json?api-key={self.api_key}'
        response = requests.get(url)
        json_response = response.json()
        return json_response
  

    def map_to_archive_item(self, api_response) -> List[ArchiveItem]:
        '''This function maps the API response to an ArchiveItem.'''
        docs = api_response.get('response', {}).get('docs', [])
        if not docs:
            return []
        return [ArchiveItem(
            name=doc.get('source', ''),
            pub_date=doc.get('pub_date', ''),
            headline=doc.get('headline', {}).get('main', ''),
            abstract=doc.get('abstract', ''),
            web_url=doc.get('web_url', ''),
            snippet=doc.get('snippet', ''),
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