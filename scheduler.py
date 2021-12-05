import sched
import time
from utils import time_until, get_config
from covid_data_handler import get_covid_data
from covid_news_handling import update_news

scheduler = sched.scheduler(time.time, time.sleep)
scheduled_events = []


def schedule_event(target_time, label, repeat, data, news, new=True):
    label_exists = any(event["title"] == label for event in scheduled_events)
    if not label_exists:
        time_delta = time_until(target_time)
        print(
            f"SCHED: New event {label} at {target_time} (in {time_delta})"
            f" [{'repeat' if repeat else ''} {'data' if data else ''} {'news' if news else ''}]"
        )
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

        print("-----------")
        print(scheduled_events)
        # Insert in time order
        if not scheduled_events:
            scheduled_events.append(new_event)
        else:
            for index, event in enumerate(scheduled_events):
                print(f"Target Time: {time_until(target_time)}")
                print(f"Ith Time: {time_until(event['target_time'])}")
                print(
                    "Eval:"
                    f" {time_until(target_time) < time_until(event['target_time'])}"
                )

                if time_until(target_time) < time_until(event["target_time"]):
                    scheduled_events.insert(index, new_event)
                    break
                elif index == len(scheduled_events) - 1:
                    scheduled_events.append(new_event)
                    break


def call_event(label, target_time, repeat, data, news):
    print(f"SCHED: Running {label}")
    remove_event(label)
    if data:
        location, nation = get_config("location", "nation")
        get_covid_data(location, nation, force_update=True)
    if news:
        update_news()
    if repeat:
        print(f"SCHED: Repeat event for {target_time}")

        schedule_event(target_time, label, repeat, data, news, new=False)
    return


def remove_event(title):
    global scheduled_events
    scheduled_events[:] = [
        event for event in scheduled_events if event["title"] != title
    ]


def keep_alive():
    scheduler.enter(10, 1, keep_alive)
