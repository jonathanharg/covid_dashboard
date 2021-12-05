import json
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


def get_config(*keys):
    try:
        with open("config.json") as file:
            config = json.load(file)
    except FileNotFoundError:
        config = DEFAULT_CONFIG
        with open("config.json", "w", encoding="utf-8") as file:
            json.dump(config, file, ensure_ascii=False, indent=4)
    result = []
    if len(keys) == 1:
        result = config[keys[0]]
    else:
        for key in keys:
            result.append(config[key])
    return result


def time_until(target_time):
    # target_time = timedelta(hours=target.hour, minutes=target.minute, seconds=target.second)
    now = datetime.now()
    current_time = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)

    # If target time is in the future
    if current_time < target_time:
        time_delta = target_time - current_time
    # If scheduled time is in the past, or now
    else:
        time_delta = timedelta(hours=24) + target_time - current_time
    return time_delta


def format_string(string):
    if string is None:
        return None
    return f"{string:,}"


def get_news_blacklist():
    try:
        with open("news-blacklist.json") as file:
            blacklist = json.load(file)
    except FileNotFoundError:
        blacklist = {"blacklist": []}
        with open("news-blacklist.json", "w") as file:
            json.dump(blacklist, file)
    return blacklist["blacklist"]


def blacklist(title):
    blacklist = list(get_news_blacklist())
    blacklist.append(title)
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
