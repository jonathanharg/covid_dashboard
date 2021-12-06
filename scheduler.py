import sched
import time
import logging
from utils import time_until, time_difference, get_config
from covid_data_handler import get_covid_data
from covid_news_handling import update_news

scheduler = sched.scheduler(time.time, time.sleep)
scheduled_events = []
log = logging.getLogger("covid_dashboard")

def schedule_event(target_time, label, repeat, data, news, new=True):
    log.info(
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
            log.info(f"Appending {label} to scheduled_events")
            scheduled_events.append(new_event)
        else:
            for index, event in enumerate(scheduled_events):
                # print(f"Target Time: {time_until(target_time)}")
                # print(f"Ith Time: {time_until(event['target_time'])}")
                # print(
                #     "Eval:"
                #     f" {time_until(target_time) < time_until(event['target_time'])}"
                # )

                if time_until(target_time) < time_until(event["target_time"]):
                    log.info(f"Inserting {label} at {index = } of scheduled_events")
                    scheduled_events.insert(index, new_event)
                    break
                elif index == len(scheduled_events) - 1:
                    log.info(f"Appending {label} to scheduled_events")
                    scheduled_events.append(new_event)
                    break
    else:
        log.warning(f"Scheduled update with {label = } already exists")


def call_event(label, target_time, repeat, data, news):
    log.info(
        f"Running scheduled event {label} with {repeat = } for {data = } and {news = }"
    )
    log.info(f"This event is running {time_difference(target_time)} schedule")

    remove_event(label)
    if data:
        location, nation = get_config("location", "nation")
        get_covid_data(location, nation, force_update=True)
    if news:
        update_news()
    if repeat:
        log.info(f"Repeating event for {target_time}")
        schedule_event(target_time, label, repeat, data, news, new=False)
    return


def remove_event(title):
    log.info(f"Removing event {title}")
    global scheduled_events
    scheduled_events[:] = [
        event for event in scheduled_events if event["title"] != title
    ]


def keep_alive():
    scheduler.enter(10, 1, keep_alive)
    # print(":)")
