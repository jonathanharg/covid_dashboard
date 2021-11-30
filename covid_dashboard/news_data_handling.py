import requests
from dashboard_utilities import get_config
import json
import sched

news = None


def news_API_request(covid_terms="Covid COVID-19 coronavirus"):
    # TODO: Get api key from config, do not hard code
    # TODO: Handle Error
    api_key = get_config("api_key")
    url = (
        f"https://newsapi.org/v2/everything?q={covid_terms}&apiKey={api_key}&pageSize=5"
    )
    try:
        response = requests.get(url)
        articles = response.json()["articles"]
    except requests.exceptions.RequestException:
        print("NEWS REQUEST ERROR")
        articles = None
    return articles


def get_news(covid_terms="Covid COVID-19 coronavirus"):
    global news
    if news is None:
        news = update_news(covid_terms)
    return news


def update_news(covid_terms="Covid COVID-19 coronavirus"):
    # use news_API_request() within function
    # update a data structure containing news articles.
    # integrate this with scheduled updates
    # NOTE: news should be update on a different interval than covid data
    # NOTE: There is a way to remove articles that you have seen from the interface, which should not reappear
    result = []
    new_news = news_API_request(covid_terms)
    if new_news is not None:
        for article in new_news:
            result.append(
                {"title": article["title"], "description": article["description"], "url": article["url"]}
            )
    return result


def remove_article(title):
    global news
    news[:] = [article for article in news if article["title"] != title]
