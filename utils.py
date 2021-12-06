import json
import logging
from datetime import datetime, timedelta
from io import StringIO
from html.parser import HTMLParser

DEFAULT_CONFIG = {
    "favicon": "/static/images/fish.gif",
    "image": "fish.gif",
    "title": "COVID Dashboard",
    "location": "Exeter",
    "nation": "England",
    "api_key": "INSERT-API-KEY-HERE",
}
log = logging.getLogger("covid_dashboard")


def get_config(*keys):
    try:
        with open("config.json") as file:
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
    if len(result) > 1:
        result = tuple(result)
    elif len(result) == 1:
        result = str(result[0])
    return result


def time_difference(target_time):
    now = datetime.now()
    current_time = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
    return target_time - current_time


def time_until(target_time):
    now = datetime.now()
    current_time = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)

    # If target time is in the future
    if current_time < target_time:
        time_delta = target_time - current_time
    # If scheduled time is in the past, or now
    else:
        time_delta = timedelta(hours=24) + target_time - current_time
    return time_delta




def get_news_blacklist():
    try:
        with open("news-blacklist.json") as file:
            log.info("Getting news blacklist from news-blacklist.json")
            blacklist = json.load(file)
    except FileNotFoundError:
        log.warning("No news-blacklist.json found, creating a new one")
        blacklist = {"blacklist": []}
        with open("news-blacklist.json", "w") as file:
            json.dump(blacklist, file)
    return blacklist["blacklist"]


def blacklist(title):
    blacklist = list(get_news_blacklist())
    blacklist.append(title)
    log.info(f"Blacklisting {title}")
    with open("news-blacklist.json", "w") as file:
        json.dump({"blacklist": blacklist}, file)


# from https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def sanitise_input(html):
    sanitiser = MLStripper()
    sanitiser.feed(html)
    return sanitiser.get_data()
