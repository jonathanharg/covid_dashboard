from app import create_app
import pytest


@pytest.fixture
def client():
    app = create_app(testing=True)

    with app.test_client() as client:
        yield client


# def test_config():
#     """Test create_app without passing test config."""
#     assert not create_app().testing
#     assert create_app(testing=True).testing


@pytest.mark.parametrize("url", ["/", "/index"])
def test_get_url(client, url):
    response = client.get(url)
    assert response.status_code in [200, 302]


# # Remove event/news title name, time string hh:mm, label update title, repeat=repeat, etc.
# @pytest.mark.parametrize("remove_event,remove_news,time,label,repeat,covid_data,news",[('','','','','','','')])
# def test_input(client, remove_event, remove_news, time, label, repeat, covid_data, news):
#     client.get(f"index?update_item={remove_event}&notif={remove_news}&update={time}&two={label}&repeat={repeat}&covid-data={covid_data}&news={news}")
#     url='index'

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
remove_update_with_same_name = {
    "update_item": "Same Name"
}
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
    remove_update_with_same_name
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
    client.get(url)


# TEST FAVICON, TEST IMAGE
