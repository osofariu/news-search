import requests
from responses import _recorder
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    
    load_dotenv()
    api_key = os.getenv("NYT_API_KEY")
    
    year = "2024"
    month = "9"
    year =  input(f"Year: (default {year}) > ") or year
    month = input(f"Month: (default {month}) > ") or month

    @_recorder.record(file_path=f"tests/data/nyt_api_responses_{year}-{month}.yaml")
    def test_recorder(year:int, month:int):
        requests.get(f"https://api.nytimes.com/svc/archive/v1/{year}/{month}.json?api-key={api_key}")
        
    test_recorder(year, month)