import pytest
from nyt_api import NYTApi
from cache import NewsCache
import responses
import requests

class FakeCache(NewsCache):
    def __init__(self):
        self.cache_path = None
    
    def get_by_date(self, _year, _month):
        return None
    
    def put_by_date(self, _year, _month, _value):
        return None

@pytest.fixture
def nyt_api():
    return NYTApi(api_key="1234567890", cache=FakeCache())


@responses.activate
def test_loading_yaml_works():
    test_url = "https://api.nytimes.com/svc/archive/v1/2024/11.json?api-key=1234567890"
    responses._add_from_file(file_path="tests/data/nyt_api_responses_2024-11.yaml")
    api_response = requests.get(test_url)
    assert api_response.status_code == 200

    json = api_response.json()
    assert (
        json["copyright"]
        == "Copyright (c) 2024 The New York Times Company. All Rights Reserved."
    )
    docs = json["response"]["docs"]
    assert len(docs) == 5
    assert (
        docs[0]["headline"]["main"]
        == "Vance Tells Rogan: Teens Become Trans to Get Into Ivy League"
    )


@responses.activate
def test_get_archives(nyt_api):
    responses._add_from_file(file_path="tests/data/nyt_api_responses_2024-11.yaml")

    ny_times_response = nyt_api.get_archives(None, "2024-11", "2024-11")
    assert ny_times_response["status"] == 200

    archive_items = ny_times_response["responses"]
    assert len(archive_items) == 5

    first_doc = archive_items[0]
    assert (
        first_doc["headline"]
        == "Vance Tells Rogan: Teens Become Trans to Get Into Ivy League"
    )
    assert first_doc["pub_date"] == "2024-11-01T00:46:06+0000"
    assert (
        first_doc["abstract"]
        == "Appearing on Joe Rogan\u2019s podcast, Senator JD Vance also said that liberal women celebrate their abortions and that \
Donald Trump would win the \u201Cnormal gay guy vote.\u201D"
    )
    assert (
        first_doc["web_url"]
        == "https://www.nytimes.com/2024/10/31/us/politics/jd-vance-joe-rogan.html"
    )
    assert (
        first_doc["lead_paragraph"]
        == "Senator JD Vance of Ohio criticized what he called \u201Cgender transition craziness,\u201D\
 spoke dismissively of women he claimed were \u201Ccelebrating\u201D their abortions and said that studies \u201Cconnect testosterone levels in young\
 men with conservative politics\u201D during a three-hour episode of \u201CThe Joe Rogan Experience\u201D that was released on Thursday."
    )
    
@responses.activate
def test_filter_with_topic_search(nyt_api):
    responses._add_from_file(file_path="tests/data/nyt_api_responses_2024-11.yaml")
    
    ny_times_response = nyt_api.get_archives("Sarah DiGregorio", "2024-11", "2024-11")
    assert ny_times_response["status"] == 200

    archive_items = ny_times_response["responses"]
    assert len(archive_items) == 1
    first_doc = archive_items[0] 
    assert (first_doc["abstract"]
        == "Sarah DiGregorio\u2019s salmon and kimchi skillet, a five-star, \
five-ingredient dinner to kick-start your taste buds."
    ) 

@responses.activate
def test_with_multiple_months(nyt_api):
    responses._add_from_file(file_path="tests/data/nyt_api_responses_2024-9.yaml")
    responses._add_from_file(file_path="tests/data/nyt_api_responses_2024-10.yaml") 
    ny_times_response = nyt_api.get_archives(None, "2024-09", "2024-10")
    assert ny_times_response["status"] == 200

    archive_items = ny_times_response["responses"]
    assert len(archive_items) == 10