import requests
from utils import get_config, get_news_blacklist, blacklist, sanitise_input

news = None


def news_API_request(covid_terms="Covid COVID-19 coronavirus"):
    # TODO: Handle Error
    api_key = get_config("api_key")
    url = f"https://newsapi.org/v2/everything?q={covid_terms}&apiKey={api_key}&sortBy=PublishedAt&pageSize=100&language=en"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            articles = response.json()["articles"]
        else:
            print(f"Error, {response.status_code} - {response.reason}")
            if response.status_code == 401:
                print("Have you supplied a valid NewsAPI.org API key in config.json?")
            articles = None

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
    blacklist = get_news_blacklist()
    new_news = news_API_request(covid_terms)
    if new_news is not None:
        for article in new_news:
            if article["title"] not in blacklist:
                result.append(
                    {
                        "title": sanitise_input(article["title"]),
                        "description": sanitise_input(article["description"]),
                        "url": article["url"],
                        "publishedAt": article["publishedAt"],
                    }
                )
    return result


def remove_article(title):
    global news
    news[:] = [article for article in news if article["title"] != title]
    blacklist(title)
