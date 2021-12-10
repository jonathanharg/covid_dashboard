from covid_news_handling import get_news, news_API_request, remove_article, update_news


def test_news_API_request():
    assert news_API_request()
    assert news_API_request("Covid COVID-19 coronavirus") == news_API_request()


def test_update_news():
    assert update_news("test")


def test_get_news():
    assert get_news()
