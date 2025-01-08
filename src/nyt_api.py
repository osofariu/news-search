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
    
@dataclass
class ArchiveResponse:
    '''Class for keeping track of an item in inventory.'''
    response: List[ArchiveItem]
    
  
""" PLANS 

- turn the wrapper into a class
- add a method to call the API
- cache results on each call, saving the results in a file
- add a method to read the cache on each call

"""

class NYTimesArchive:
    
    def __init__(self):
        self.api_key = os.getenv("NYT_API_KEY")

    def nyt_archive_wrapper(topic: str, start_date: str, end_date: str) -> str: # List[ArchiveItem]:
        '''This function wraps the nyt_archive_api function and returns the response.
        
        Args:
            topic: a search query for in the NYT archive.
            start_date: the beginning of the date range with format YYYY.MM.
            end_date: the beginning of the date range with format YYYY.MM.            
        '''
        
        months_to_query = generateMonths(start_date, end_date)
        
        return [
            {
                "name": "Test",
                "pub_date": "2022-01-01",
                "headline": "Test Headline",
                "abstract": "Test Abstract",
                "web_url": "https://www.nytimes.com",
                "snippet": "Test Snippet",
                "lead_paragraph": "Test Lead Paragraph"
            }
        ]


    def nyt_archive_api(year, month):
        '''This function returns the NYT Archive API response for a given year and month.'''
        url = f'https://api.nytimes.com/svc/archive/v1/{year}/{month}.json?api-key={self.api_key}'
        response = requests.get(url)
        return response.json()
  

    def generateMonths(self, start_date, end_date):
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