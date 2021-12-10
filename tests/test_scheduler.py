from scheduler import call_event, keep_alive, remove_event, schedule_event
from datetime import timedelta


def test_schedule_event():
    schedule_event(timedelta(hours=3), "pytest", True, True, True)


def test_call_event():
    call_event("pytest", timedelta(hours=3), True, True, True)


def test_remove_event():
    remove_event("pytest")


def test_keep_alive():
    keep_alive()
