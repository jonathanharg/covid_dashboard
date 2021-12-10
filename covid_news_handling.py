""" Deals with the dashboard news and all of its related API requests.

Attributes:
    news (list): A list of all the current dashboard news.
    log (Logger): The logger for the covid_dashboard.
"""
import logging
import requests
from utils import get_setting, get_news_blacklist, blacklist, sanitise_input

news: list = []
log = logging.getLogger("covid_dashboard")


def news_API_request(covid_terms: str = "Covid COVID-19 coronavirus") -> list:
    """Sends an API request to NewsAPI.org for news articles that include covid_terms.

    Args:
        covid_terms (str, optional): News article search terms.
            Defaults to "Covid COVID-19 coronavirus".

    Returns:
        List[dict]: A list of news article dictionaries. Read the full documentation on NewsAPI.org
    """
    # pylint: disable=invalid-name
    log.info("Making NewsAPI.org request")
    api_key = get_setting("api_key")
    url = (
        f"https://newsapi.org/v2/everything?q={covid_terms}"
        f"&apiKey={api_key}&sortBy=PublishedAt&pageSize=100&language=en"
    )
    try:
        response = requests.get(url)
        if response.status_code == 200:
            log.info("Received response from NewsAPI.org")
            articles = response.json()["articles"]
        else:
            log.error(
                "NewsAPI.org request failed, %s - %s", response.status_code, response.reason
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


def get_news(
    covid_terms: str = "Covid COVID-19 coronavirus", force_update: bool = False
) -> list:
    """Gets the internal cached news, and if that does not exist or an update is forced, makes a
    request to NewsAPI.org.

    Args:
        covid_terms (str, optional): News article search terms.
            Defaults to "Covid COVID-19 coronavirus".
        force_update (bool, optional): Force an update to the news articles. Defaults to False.

    Returns:
        list: A list of news article dictionaries.
    """
    global news
    log.info("Reqest to get news with covid_terms = %s", covid_terms)
    if not news:
        log.info("No cached news exists")
    elif force_update:
        log.info("Forcing NewsAPI update")
    else:
        log.info("Using cached news data")
        return news
    news = update_news(covid_terms)
    return news


def update_news(covid_terms: str = "Covid COVID-19 coronavirus") -> list:
    """Parses the NewsAPI.org response for useful data such as the title, description and
    time of publishing.

    Args:
        covid_terms (str, optional): News article search terms.
            Defaults to "Covid COVID-19 coronavirus".

    Returns:
        list:  A list of news article dictionaries.
    """
    result = []
    users_blacklist = get_news_blacklist()
    new_news = news_API_request(covid_terms)
    if new_news is not None:
        for article in new_news:
            if article["title"] not in users_blacklist:
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


def remove_article(title: str) -> None:
    """Remove an article and blacklist its title.

    Args:
        title (str): The article title.
    """
    log.info("Removing article title = %s", title)
    global news
    news[:] = [article for article in news if article["title"] != title]
    blacklist(title)
