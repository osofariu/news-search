
from dataclasses import dataclass
from typing import TypedDict, List
import requests

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

def nyt_archive_wrapper(query: ArchiveQuery) -> List[ArchiveItem]:
    '''This function wraps the nyt_archive_api function and returns the response.'''
    print(f"** nyt_archive_wrapper: query={query}")
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

def nyt_archive_api(year, month, api_key):
    '''This function returns the NYT Archive API response for a given year and month.'''
    url = f'https://api.nytimes.com/svc/archive/v1/{year}/{month}.json?api-key={api_key}'
    response = requests.get(url)
    return response.json()
  