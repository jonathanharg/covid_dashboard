""" Provides general utilities for the covid_dashboard including settings,
timing functions and storing the users blacklist.

Attributes:
    log (Logger): The logger for the covid_dashboard.
"""
import json
import logging
from datetime import datetime, timedelta
from io import StringIO
from html.parser import HTMLParser
from typing import Any

DEFAULT_CONFIG = {
    "favicon": "/static/images/fish.gif",
    "image": "fish.gif",
    "title": "COVID Dashboard",
    "location": "Exeter",
    "nation": "England",
    "api_key": "INSERT-API-KEY-HERE",
}
log = logging.getLogger("covid_dashboard")


def get_settings(*keys) -> tuple:
    """Get multiple settings from the users config.json

    Args:
        keys: The settings keys to be read from the users config.json.

    Returns:
        tuple: The values for each given settings from the users config.json
    """
    try:
        with open("config.json", encoding="utf-8") as file:
            log.info("Loading config.json")
            config = json.load(file)
    except FileNotFoundError:
        log.warning(
            "No config.json found, creating a new config.json with default values"
        )
        config = DEFAULT_CONFIG
        with open("config.json", "w", encoding="utf-8") as file:
            json.dump(config, file, ensure_ascii=False, indent=4)
    result = []
    if (config["api_key"] == "INSERT-API-KEY-HERE") or (config["api_key"] is None):
        log.warning(
            "No NewsAPI.org API key found in config, get one from"
            " https://newsapi.org/register"
        )
    for key in keys:
        result.append(config[key])
    return tuple(result)


def get_setting(key: str) -> Any:
    """Get a single setting from the users config.json

    Args:
        key (str): The setting key to be read from the users config.json

    Returns:
        Any: The value for the given setting in the users config.json
    """
    result = get_settings(key)
    return result[0]


def time_until(target_time: timedelta) -> timedelta:
    """Returns the time until a given time occurs.

    Used to calculate how long until a scheduled event will run. For example,
    if an event is scheduled to run at 14:15, the function will return the time time
    until the clock next strikes 14:15.

    Args:
        target_time (timedelta): Target time to calculate the difference between.

    Returns:
        timedelta: Resulting time difference.
    """
    now = datetime.now()
    current_time = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)

    # If target time is in the future
    if current_time < target_time:
        time_delta = target_time - current_time
    # If target time is in the past, or now
    else:
        time_delta = timedelta(hours=24) + target_time - current_time
    return time_delta


def get_news_blacklist() -> list:
    """Get the users news blacklist from news-blacklist.json.

    Returns:
        list: List of blacklisted news article titles
    """
    try:
        with open("news-blacklist.json", encoding="utf-8") as file:
            log.info("Getting news blacklist from news-blacklist.json")
            user_blacklist = json.load(file)
    except FileNotFoundError:
        log.warning("No news-blacklist.json found, creating a new one")
        user_blacklist = {"blacklist": []}
        with open("news-blacklist.json", "w", encoding="utf-8") as file:
            json.dump(user_blacklist, file)
    return user_blacklist["blacklist"]


def blacklist(title: str) -> None:
    """Blacklist a new news article, and add it to the users news-blacklist.json.

    Args:
        title (str): The title of the news article that should be blacklisted.
    """
    stored_blacklist = list(get_news_blacklist())
    stored_blacklist.append(title)
    log.info("Blacklisting %s", title)
    with open("news-blacklist.json", "w", encoding="utf-8") as file:
        json.dump({"blacklist": stored_blacklist}, file)


# from https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
class HTMLStripper(HTMLParser):
    """A HTML code stripper to remove any HTML elements from the description of news articles."""

    # pylint: disable=W0223
    def __init__(self) -> None:
        super().__init__()
        self.reset()
        self.convert_charrefs = True
        self.strict = False
        self.text = StringIO()

    def handle_data(self, data: str) -> None:
        """This is called when handling arbitrary HTML data."""
        self.text.write(data)

    def get_data(self) -> str:
        """This is called when getting sanitised HTML data"""
        return self.text.getvalue()


def sanitise_input(html: str) -> str:
    """Sanitises any string and removes any potentially malicious HTML tags.

    Args:
        html (str): A string which may contain HTML.

    Returns:
        str: A sanitised version of the input string, with all HTML removed.
    """
    sanitiser = HTMLStripper()
    sanitiser.feed(html)
    return sanitiser.get_data()
