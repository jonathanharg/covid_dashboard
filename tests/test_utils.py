from datetime import timedelta
from utils import (
    blacklist,
    get_news_blacklist,
    get_setting,
    get_settings,
    sanitise_input,
    time_until,
)


def test_get_settings():
    assert get_settings("image", "title", "location")


def test_get_setting():
    assert get_setting("nation")


def test_time_until():
    assert time_until(timedelta(hours=5))


def test_get_news_blacklist():
    get_news_blacklist()


def test_sanitise_input():
    assert sanitise_input("Test<script>alert(1)</script>Test") == "Testalert(1)Test"
