""" Handles front-end web requests, scheduling, and makes calles to back end data/news handlers"""

# TODO: TEST INVALID VALUES, e.g. "location": "Wimbledon", "nation": "Kazakhstan",
# TODO: LOGGING
# TODO: Clean up code
# TODO: readme
# TODO: default updates in config
# TODO: repeating update not moving to end of list after repeat
# TODO: MAKE SURE NO REPEATING UPDATES ARE REMOVED
# TODO: ANNOTATE ALL FUNCTIONS e.g. def func(var: str)

# ? News Behaviour on Removal
# ? Threading
# ? news data handler name & general file structure, main app name
# ? covid_data_handler schedule_covid_update

from flask import Flask, render_template, Markup, request, redirect
from datetime import datetime, timedelta
import threading
from scheduler import (
    scheduler,
    scheduled_events,
    schedule_event,
    remove_event,
    keep_alive,
)
from covid_data_handler import get_covid_data
from covid_news_handling import get_news, update_news, remove_article
from utils import get_config, time_until


CLOCK_ICON = "<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' class='bi bi-clock' viewBox='0 0 16 16'><path d='M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z'/><path d='M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z'/></svg>"
HOSPITAL_ICON = "<svg xmlns='http://www.w3.org/2000/svg' width='32' height='32' fill='currentColor' class='bi bi-thermometer-half' viewBox='0 0 16 16'><path d='M9.5 12.5a1.5 1.5 0 1 1-2-1.415V6.5a.5.5 0 0 1 1 0v4.585a1.5 1.5 0 0 1 1 1.415z'/><path d='M5.5 2.5a2.5 2.5 0 0 1 5 0v7.55a3.5 3.5 0 1 1-5 0V2.5zM8 1a1.5 1.5 0 0 0-1.5 1.5v7.987l-.167.15a2.5 2.5 0 1 0 3.333 0l-.166-.15V2.5A1.5 1.5 0 0 0 8 1z'/></svg>"
# DEATHS_ICON = "<svg xmlns='http://www.w3.org/2000/svg' width='32' height='32' fill='currentColor' class='bi bi-emoji-dizzy' viewBox='0 0 16 16'><path d='M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z'/><path d='M9.146 5.146a.5.5 0 0 1 .708 0l.646.647.646-.647a.5.5 0 0 1 .708.708l-.647.646.647.646a.5.5 0 0 1-.708.708l-.646-.647-.646.647a.5.5 0 1 1-.708-.708l.647-.646-.647-.646a.5.5 0 0 1 0-.708zm-5 0a.5.5 0 0 1 .708 0l.646.647.646-.647a.5.5 0 1 1 .708.708l-.647.646.647.646a.5.5 0 1 1-.708.708L5.5 7.207l-.646.647a.5.5 0 1 1-.708-.708l.647-.646-.647-.646a.5.5 0 0 1 0-.708zM10 11a2 2 0 1 1-4 0 2 2 0 0 1 4 0z'/></svg>"
DEATHS_ICON = "<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' class='bi bi-activity' viewBox='0 0 16 16'><path fill-rule='evenodd' d='M6 2a.5.5 0 0 1 .47.33L10 12.036l1.53-4.208A.5.5 0 0 1 12 7.5h3.5a.5.5 0 0 1 0 1h-3.15l-1.88 5.17a.5.5 0 0 1-.94 0L6 3.964 4.47 8.171A.5.5 0 0 1 4 8.5H.5a.5.5 0 0 1 0-1h3.15l1.88-5.17A.5.5 0 0 1 6 2Z'/></svg>"
NEW_ICON = "<span class='badge badge-primary'>New</span>"


def create_app(testing=False):
    app = Flask(__name__)
    app.testing = testing

    location, nation = get_config("location", "nation")

    update_news()
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

    thread = threading.Thread(target=scheduler.run)
    thread.start()
    keep_alive()

    @app.route("/")
    def main():
        """Handles input requests if any, otherwise renders the COVID dashboard"""
        # scheduler.run(blocking=False)
        # GET PAGE VARIABLES & CONTENT
        favicon, image, title, location, nation = get_config(
            "favicon", "image", "title", "location", "nation"
        )

        # TODO: Format news article titles?? (might mess with deletion function) and descriptions to include link to read more
        news_articles = get_news()

        (
            local_7day_infections,
            national_7day_infections,
            hospital_cases,
            deaths_total,
        ) = get_covid_data(location, nation)

        # Format Strings
        title = Markup(f"<strong>{title}</strong>")
        location = Markup(f"<strong>{location}</strong>")
        nation_location = Markup(f"<strong>{nation}</strong>")
        local_7day_infections = (
            f"{local_7day_infections if local_7day_infections is not None else 0:,}"
        )
        national_7day_infections = f"{national_7day_infections if national_7day_infections is not None else 0:,}"
        hospital_cases = Markup(
            f"{HOSPITAL_ICON} {hospital_cases if hospital_cases is not None else 0:,} hospital cases"
        )
        deaths_total = Markup(
            f"{DEATHS_ICON} {deaths_total if deaths_total is not None else 0:,} total deaths "
        )

        for article in news_articles:
            time = datetime.strptime(article['publishedAt'],"%Y-%m-%dT%H:%M:%S%z")
            article["content"] = Markup(
                f"<u>{time.strftime('%I:%M %p %d/%m/%y')}</u><br>{article['description']} <a href='{article['url']}' target='_blank'>Read More</a>"
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
            updating = (
                " and ".join(types) if types != [] else "<strong>nothing</strong>"
            )
            time = update["target_time"]
            time_to = str(time_until(time))
            new = ""
            if update["new"] is True:
                update["new"] = False
                new = "<br>" + NEW_ICON
            update["content"] = Markup(
                f"{CLOCK_ICON} <u>{time.seconds//3600:02d}:{(time.seconds//60)%60:02d}</u><br>{repeating} for {updating} in {time_to} {new}"
                ""
            )

        # Render data with ./templates/index.html

        # TODO: MAke this into templateVariables dict and then call with render_template("index.html", **templateVariables)
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

    @app.route("/index")
    def index():
        # Handle Inputs
        # TODO: Verify all inputs are valid and sane
        # Handle Remove Scheduled Event Request
        if "update_item" in request.args:
            title = request.args.get("update_item")
            remove_event(title)
            for event in scheduled_events:
                if event["title"] == title:
                    scheduler.cancel(event["sched_event"])

        # Handle Remove News Article Request
        if "notif" in request.args:
            title = request.args.get("notif")
            remove_article(title)

        # Handle Request to Schedule New Event
        # TODO: Handle missing data, e.g. no title, update, name etc.
        # TODO: Validate time string
        if "update" in request.args:
            label = request.args.get("two")
            # Change request arguments to booleans
            repeat = "repeat" in request.args
            data = "covid-data" in request.args
            news = "news" in request.args
            # Make sure an event with the same title does not exist and either data or news is being updated
            if (not any(event["title"] == label for event in scheduled_events)) and (
                data or news
            ):
                try:
                    # Converts time string time into datetime
                    time_offset = datetime(1900, 1, 1, 0, 0)
                    time = (
                        datetime.strptime(request.args.get("update"), "%H:%M")
                        - time_offset
                    )

                    schedule_event(time, label, repeat, data, news)
                except ValueError:
                    print("Date can not be read")

        # Redirect user back to root URL to stop form being submitted again on a page reload
        return redirect("/", code=302)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
