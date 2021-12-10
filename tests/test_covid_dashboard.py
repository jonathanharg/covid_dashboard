from app import create_app
from utils import get_setting
import pytest


@pytest.fixture
def client():
    app = create_app(testing=True)

    with app.test_client() as client:
        yield client


@pytest.mark.parametrize("url", ["/", "/index"])
def test_get_url(client, url):
    response = client.get(url)
    assert response.status_code in [200, 302]


remove_nonexisting_event = {
    "update_item": "TRY TO REMOVE AN ARTICLE THAT DOES NOT EXIST"
}
remove_nonexisting_news = {"notif": "TRY TO REMOVE AN ARTICLE THAT DOES NOT EXIST"}
schedule_update_with_no_label = {
    "update": "12:30",
    "covid-data": "covid-data",
}
schedule_update_with_no_time = {
    "update": "",
    "two": "No Time",
    "covid-data": "covid-data",
}
schedule_update_with_invalid_time = {
    "update": "25:72",
    "two": "Invalid Time",
    "covid-data": "covid-data",
}
schedule_update_with_same_name = {
    "update": "12:30",
    "two": "Same Name",
    "covid-data": "covid-data",
}
remove_update_with_same_name = {"update_item": "Same Name"}
schedule_update_with_no_covid_or_news = {"update": "12:30", "two": "Label"}
requests = [
    remove_nonexisting_event,
    remove_nonexisting_news,
    schedule_update_with_no_label,
    schedule_update_with_no_time,
    schedule_update_with_invalid_time,
    schedule_update_with_no_covid_or_news,
    schedule_update_with_same_name,
    schedule_update_with_same_name,
    remove_update_with_same_name,
    remove_update_with_same_name,
]


@pytest.mark.parametrize("requests", requests)
def test_input_sequence(client, requests):
    url = "index"
    for i, arg in enumerate(requests):
        if i == 0:
            url += "?"
        else:
            url += "&"
        url += arg + "=" + requests[arg]
    response = client.get(url)
    assert response.status_code in [200, 302]


# TEST FAVICON, TEST IMAGE

def test_favicon(client):
    favicon = get_setting("favicon")
    response = client.get(favicon)
    assert response.status_code in [200, 302]

def test_image(client):
    image = get_setting("image")
    response = client.get('/static/images/' + image)