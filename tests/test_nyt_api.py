import pytest
from nyt_api import NYTNewsApi
import responses
import requests


@pytest.fixture
def nytimes():
    return NYTNewsApi(api_key="1234567890")


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
def test_get_archives(nytimes):
    test_url = "https://api.nytimes.com/svc/archive/v1/2024/11.json?api-key=1234567890"
    responses._add_from_file(file_path="tests/data/nyt_api_responses_2024-11.yaml")

    ny_times_response = nytimes.get_archives(None, "2024-11", "2024-11")
    assert ny_times_response["status"] == 200

    archive_items = ny_times_response["responses"]
    assert len(archive_items) == 4602

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
