import pprint
import pytest
from nyt_api import NYTNews
import responses
import requests

@pytest.fixture
def nytimes():
    return NYTNews(api_key="1234567890") 


@responses.activate
def test_loading_yaml_works():
    test_url="https://api.nytimes.com/svc/archive/v1/2024/11.json?api-key=1234567890"
    responses._add_from_file(file_path="tests/data/nyt_api_responses.yaml")
    api_response = requests.get(test_url)
    assert api_response.status_code == 200
    
    json = api_response.json()
    assert json["copyright"] == 'Copyright (c) 2024 The New York Times Company. All Rights Reserved.'
    docs = json["response"]["docs"]
    assert len(docs) == 5
    assert docs[0]["headline"]["main"] == "Vance Tells Rogan: Teens Become Trans to Get Into Ivy League"

@responses.activate
def test_get_archives(nytimes):
    test_url="https://api.nytimes.com/svc/archive/v1/2024/11.json?api-key=1234567890"
    responses._add_from_file(file_path="tests/data/nyt_api_responses.yaml")
    
    ny_times_response = nytimes.get_archives("junk", "2024-11", "2024-11")
    assert ny_times_response["status"] == 200
    
    archive_items = ny_times_response["responses"]
    assert len(archive_items) == 5
    
    first_doc = archive_items[0]
    assert first_doc["headline"] == "Vance Tells Rogan: Teens Become Trans to Get Into Ivy League"
