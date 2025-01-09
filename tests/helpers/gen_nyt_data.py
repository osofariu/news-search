import requests
from responses import _recorder
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("NYT_API_KEY")

@_recorder.record(file_path="tests/data/nyt_api_responses.yaml")
def test_recorder(year:int, month:int):
    rsp = requests.get(f"https://api.nytimes.com/svc/archive/v1/{year}/{month}.json?api-key={api_key}")
    
test_recorder(2024, 11)