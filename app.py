""" Handles front-end web requests, scheduling, and makes calles to back end data/news handlers"""
# TODO: fix scheduling ???? -> Scheduling multiple events, log time delay
# TODO: clean up code
# TODO: type hinting
# TODO: docstrings
# TODO: readme
# TODO: default updates in config [low priority]
# TODO: tests

from datetime import datetime, timedelta
import threading
import logging
from flask import Flask, render_template, Markup, request, redirect
from scheduler import (
    scheduler,
    scheduled_events,
    schedule_event,
    remove_event,
    keep_alive,
)
from covid_data_handler import get_covid_data
from covid_news_handling import get_news, remove_article
from utils import get_config, time_until

LOG_FORMAT = (
    "%(asctime)s (%(thread)d) [%(levelname)s]: %(message)s (%(funcName)s in %(module)s)"
)
CLOCK_ICON = (
    "<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor'"
    " class='bi bi-clock' viewBox='0 0 16 16'><path d='M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0"
    " 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z'/><path d='M8 16A8 8 0 1 0 8"
    " 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z'/></svg>"
)
HOSPITAL_ICON = (
    "<svg xmlns='http://www.w3.org/2000/svg' width='32' height='32' fill='currentColor'"
    " class='bi bi-thermometer-half' viewBox='0 0 16 16'><path d='M9.5 12.5a1.5 1.5 0 1"
    " 1-2-1.415V6.5a.5.5 0 0 1 1 0v4.585a1.5 1.5 0 0 1 1 1.415z'/><path d='M5.5 2.5a2.5"
    " 2.5 0 0 1 5 0v7.55a3.5 3.5 0 1 1-5 0V2.5zM8 1a1.5 1.5 0 0 0-1.5"
    " 1.5v7.987l-.167.15a2.5 2.5 0 1 0 3.333 0l-.166-.15V2.5A1.5 1.5 0 0 0 8"
    " 1z'/></svg>"
)
DEATHS_ICON = (
    "<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor'"
    " class='bi bi-activity' viewBox='0 0 16 16'><path fill-rule='evenodd' d='M6 2a.5.5"
    " 0 0 1 .47.33L10 12.036l1.53-4.208A.5.5 0 0 1 12 7.5h3.5a.5.5 0 0 1 0"
    " 1h-3.15l-1.88 5.17a.5.5 0 0 1-.94 0L6 3.964 4.47 8.171A.5.5 0 0 1 4 8.5H.5a.5.5 0"
    " 0 1 0-1h3.15l1.88-5.17A.5.5 0 0 1 6 2Z'/></svg>"
)
NEW_ICON = "<span class='badge badge-primary'>New</span>"

logging.basicConfig(
    filename="covid_dashboard.log", format=LOG_FORMAT, level=logging.DEBUG
)
log = logging.getLogger("covid_dashboard")
thread = threading.Thread(target=scheduler.run)


def create_app(testing=False):
    flask_app = Flask(__name__)
    flask_app.testing = testing
    log.info(f"Creating covid_dashboard flask app {__name__} with {testing = }")

    location, nation = get_config("location", "nation")

    # update_news()
    get_news(force_update=True)
    get_covid_data(location, nation, force_update=True)
    schedule_event(
        timedelta(hours=0, minutes=0),
        "Default COVID Update",
        True,
        True,
        False,
        new=False,
    )
    schedule_event(
        timedelta(hours=1, minutes=0),
        "Default News Update",
        True,
        False,
        True,
        new=False,
    )

    keep_alive()
    thread.start()
    log.info(f"Starting scheduler tread with ID = {thread.native_id}")

    @flask_app.route("/")
    def main():
        """Handles input requests if any, otherwise renders the COVID dashboard"""
        # scheduler.run(blocking=False)
        # GET PAGE VARIABLES & CONTENT
        log.info("Requested /")

        favicon, image, title, location, nation = get_config(
            "favicon", "image", "title", "location", "nation"
        )

        news_articles = get_news()

        covid_data = get_covid_data(location, nation)

        # Format Strings
        log.info("Formatting data")
        title = Markup(f"<strong>{title}</strong>")
        location = Markup(f"<strong>{location}</strong>")
        nation_location = Markup(f"<strong>{nation}</strong>")
        local_7day_infections = (
            None
            if covid_data["local_7day"] is None
            else f"{covid_data['local_7day']:,}"
        )
        national_7day_infections = (
            None
            if covid_data["national_7day"] is None
            else f"{covid_data['national_7day']:,}"
        )
        hospital_cases = (
            None
            if covid_data["hospital"] is None
            else Markup(f"{HOSPITAL_ICON} {covid_data['hospital']:,} hospital cases")
        )
        deaths_total = (
            None
            if covid_data["deaths"] is None
            else Markup(f"{DEATHS_ICON} {covid_data['deaths']:,} total deaths")
        )

        for article in news_articles:
            time = datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%S%z")
            article["content"] = Markup(
                f"<u>{time.strftime('%I:%M %p %d/%m/%y')}</u><br>{article['description']} <a"
                f" href='{article['url']}' target='_blank'>Read More.</a>"
            )

        for update in scheduled_events:
            repeating = (
                "Repeating scheduled update" if update["repeat"] else "Scheduled update"
            )
            types = []
            if update["data"] is True:
                types.append("<strong>COVID data</strong>")
            if update["news"] is True:
                types.append("<strong>news</strong>")
            updating = " and ".join(types) if types else "<strong>nothing</strong>"
            time = update["target_time"]
            time_hours = time.seconds // 3600
            time_minutes = (time.seconds // 60) % 60
            time_to = str(time_until(time))
            new = ""
            if update["new"] is True:
                update["new"] = False
                new = "<br>" + NEW_ICON
            update["content"] = Markup(
                f"{CLOCK_ICON} <u>{time_hours:02d}:{time_minutes:02d}</u><br>{repeating} for"
                f" {updating} in {time_to} {new}"
            )

        # Render data with ./templates/index.html
        log.info("Rendering template for /")
        return render_template(
            "index.html",
            favicon=favicon,
            updates=scheduled_events,
            image=image,
            title=title,
            location=location,
            local_7day_infections=local_7day_infections,
            nation_location=nation_location,
            national_7day_infections=national_7day_infections,
            hospital_cases=hospital_cases,
            deaths_total=deaths_total,
            news_articles=news_articles[:4],
        )

    @flask_app.route("/index")
    def index():
        # Handle Inputs
        log.info("Requested /index")

        # Handle Remove Scheduled Event Request
        if "update_item" in request.args:
            title = request.args.get("update_item")
            log.info(f"Requested removal of event {title}")
            for event in scheduled_events:
                if event["title"] == title:
                    remove_event(title)
                    scheduler.cancel(event["sched_event"])

        # Handle Remove News Article Request
        if "notif" in request.args:
            title = request.args.get("notif")
            log.info(f"Requested removal of news article {title}")
            remove_article(title)

        # Handle Request to Schedule New Event
        if "update" in request.args:
            label = request.args.get("two")
            log.info(f"Request to schedule new event {label}")
            # Change request arguments to booleans
            repeat = "repeat" in request.args
            data = "covid-data" in request.args
            news = "news" in request.args

            supplied_time = request.args.get("update")
            # Make sure an event with the same title does not exist
            if any(event["title"] == label for event in scheduled_events):
                log.warning(f"An event with the name {label} already exists! Ignoring!")
            # Make sure either data or news is being updated
            elif data or news:
                try:
                    # Converts time string time into datetime
                    time_offset = datetime(1900, 1, 1, 0, 0)
                    time = datetime.strptime(supplied_time, "%H:%M") - time_offset

                    schedule_event(time, label, repeat, data, news)
                except ValueError:
                    log.error(
                        f"Supplied time {supplied_time} does not match the format %H:%M"
                    )
            else:
                log.warning(
                    f"New event {label} either already exists or does not request a"
                    " news or data update"
                )

        # Redirect user back to root URL to stop form being submitted again on a page reload
        log.info("Redirecting user to /")
        return redirect("/", code=302)

    return flask_app


if __name__ == "__main__":
    # log.info("covid_dashboard running as main")
    app = create_app()
    app.run()
