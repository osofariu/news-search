import requests
from responses import _recorder
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    
    load_dotenv()
    api_key = os.getenv("NYT_API_KEY")
    
    year = input("Enter year: ") or 2024
    month = input("Enter month: ") or 9

    @_recorder.record(file_path=f"tests/data/nyt_api_responses_{year}-{month}.yaml")
    def test_recorder(year:int, month:int):
        rsp = requests.get(f"https://api.nytimes.com/svc/archive/v1/{year}/{month}.json?api-key={api_key}")
        
    test_recorder(year, month)