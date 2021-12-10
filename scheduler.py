""" Handles scheduling of data and news updates requested from the front end.

Attributes:
    log (Logger): The logger for the covid_dashboard.
    scheduler (scheduler): The sched scheduler object.
    scheduled_events (list): A list of dictionaries of scheduled events.
"""

import sched
import time
import logging
from datetime import timedelta, datetime
from utils import time_until, get_settings
from covid_data_handler import get_covid_data
from covid_news_handling import update_news

scheduler = sched.scheduler(time.time, time.sleep)
scheduled_events: list = []
log = logging.getLogger("covid_dashboard")


def schedule_event(
    target_time: timedelta,
    label: str,
    repeat: bool,
    data: bool,
    news: bool,
    new: bool = True,
) -> None:
    """Schedule a new event to occur at a given time.

    Args:
        target_time (timedelta): The target time the scheduled event should run, as a timedelta.
        label (str): The name of the scheduled event.
        repeat (bool): If the scheduled event should repeat in 24 hours or not.
        data (bool): If the scheduled event should update the dashboards COVID data.
        news (bool): If the scheduled event should update the dashboards news data.
        new (bool, optional): If the event is new (has just been added). Defaults to True.
    """
    log.info(  # pylint: disable=logging-fstring-interpolation
        f"Scheduling {'new' if new else 'repeating'} event {label} at"
        f" {target_time} with {repeat = } for {data = } and {news = }"
    )
    label_exists = any(event["title"] == label for event in scheduled_events)
    if not label_exists:
        time_delta = time_until(target_time)
        sched_event = scheduler.enter(
            time_delta.seconds, 1, call_event, (label, target_time, repeat, data, news)
        )

        new_event = {
            "title": label,
            "target_time": target_time,
            "repeat": repeat,
            "data": data,
            "news": news,
            "sched_event": sched_event,
            "new": new,
        }

        # Insert in time order
        if not scheduled_events:
            log.info("Appending %s to scheduled_events", label)
            scheduled_events.append(new_event)
        else:
            for index, event in enumerate(scheduled_events):
                if time_until(target_time) < time_until(event["target_time"]):
                    scheduled_events.insert(index, new_event)
                    break
                if index == len(scheduled_events) - 1:
                    log.info("Appending %s to scheduled_events", label)
                    scheduled_events.append(new_event)
                    break
    else:
        log.warning("Scheduled update with label = %s already exists", label)


def call_event(
    label: str, target_time: timedelta, repeat: bool, data: bool, news: bool
) -> None:
    """Called when the time comes for a scheduled event to run. Utilises the necessary COVID and
    news function and deals with repeated events.

    Args:
        label (str): Label of event to be run.
        target_time (timedelta): The time that the event should run, as a timedelta.
        repeat (bool): If the event should repeat in 24 hours or not.
        data (bool): If the event should update the COVID data.
        news (bool): If the event should update the news.
    """
    log.info(  # pylint: disable=logging-fstring-interpolation
        f"Running scheduled event {label} with {repeat = } for {data = } and {news = }"
    )
    log.info(
        "This event was scheduled to run at %s, it is currently %s",
        target_time,
        datetime.now(),
    )

    remove_event(label)
    if data:
        location, nation = get_settings(  # pylint: disable=unbalanced-tuple-unpacking
            "location", "nation"
        )
        get_covid_data(location, nation, force_update=True)
    if news:
        update_news()
    if repeat:
        log.info("Repeating event for %s", target_time)
        schedule_event(target_time, label, repeat, data, news, new=False)


def remove_event(title: str) -> None:
    """Removes an event from the scheduler.

    Args:
        title (str): The title of the event to be removed
    """
    log.info("Removing event %s", title)
    global scheduled_events
    scheduled_events[:] = [
        event for event in scheduled_events if event["title"] != title
    ]


def keep_alive() -> None:
    """This function does nothing but print a smiley face to the console every 10 seconds. If you
    are thinking that this is completely pointless, you are correct. However without this function,
    the whole scheduling system breaks in the most spectacular ways. Indeed, even removing the
    print statement alone stops the scheduler from working at all. Its highly likely that it does
    not need to be a smiley face that is printed to the console in order for this to work, but at
    this point I am simply to scared to even begin to modify this function.
    """
    scheduler.enter(10, 1, keep_alive)
    #################
    # DO NOT REMOVE #
    #################
    print(":)")
    # This is terrible, but sched has forced my hand.
