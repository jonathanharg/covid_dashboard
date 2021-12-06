import requests
from utils import get_config, get_news_blacklist, blacklist, sanitise_input
import logging

news = []
log = logging.getLogger("covid_dashboard")

def news_API_request(covid_terms="Covid COVID-19 coronavirus"):
    log.info("Making NewsAPI.org request")
    api_key = get_config("api_key")
    url = f"https://newsapi.org/v2/everything?q={covid_terms}&apiKey={api_key}&sortBy=PublishedAt&pageSize=100&language=en"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            log.info("Recieved response from NewsAPI.org")
            articles = response.json()["articles"]
        else:
            log.error(
                f"NewsAPI.org request failed, {response.status_code} -"
                f" {response.reason}"
            )
            if response.status_code == 401:
                log.warning(
                    "Have you supplied a valid NewsAPI.org API key in config.json?"
                )
            articles = []

    except requests.exceptions.RequestException:
        log.error("RequestException for NewsAPI.org request")
        articles = []
    return articles


def get_news(covid_terms="Covid COVID-19 coronavirus", force_update=False):
    global news
    log.info(f"Reqest to get news with {covid_terms = }")
    if news == []:
        log.info("No cached news exists")
    elif force_update:
        log.info("Forcing NewsAPI update")
    else:
        log.info("Using cached news data")
        return news
    news = update_news(covid_terms)
    return news


def update_news(covid_terms="Covid COVID-19 coronavirus"):
    result = []
    blacklist = get_news_blacklist()
    new_news = news_API_request(covid_terms)
    if new_news is not None:
        for article in new_news:
            if article["title"] not in blacklist:
                if article["title"] is not None:
                    title = sanitise_input(article["title"])
                if article["description"] is not None:
                    description = sanitise_input(article["description"])
                result.append(
                    {
                        "title": title,
                        "description": description,
                        "url": article["url"],
                        "publishedAt": article["publishedAt"],
                    }
                )
    return result


def remove_article(title):
    log.info(f"Removing article {title = }")
    global news
    news[:] = [article for article in news if article["title"] != title]
    blacklist(title)
