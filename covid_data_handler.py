""" Caches and request COVID data from the GOV.UK Covid19 API

Attributes:
    internal_covid_data (dict): An internal cache for the latest
        API request and its associated location and nation
    log (Logger): The logger for the covid_dashboard.
"""
from typing import Optional, Union
from datetime import timedelta
import logging
import requests
import uk_covid19
# from scheduler import schedule_event

log = logging.getLogger("covid_dashboard")
log.info("Initialising empty internal covid data")
internal_covid_data: dict = {"location": None, "nation": None, "data": None}


def parse_csv_data(csv_filename: str) -> list:
    """Parses csv file into list of row strings.

    Args:
        csv_filename (str): name of or path to csv file to parse.

    Returns:
        list[str]: list of csv row strings.
    """
    log.info("Parsing csv data in %s", csv_filename)
    rows = []
    with open(csv_filename, encoding="utf-8") as data:
        file = data.read()
        for line in file.split("\n"):
            if line != "":
                rows.append(line)
    return rows


def process_covid_csv_data(covid_csv_data: list) -> tuple:
    """Calculate the 7 day case total, current hospital cases, and total deaths.

    Args:
        covid_csv_data (list): List of csv row strings from the GOV.UK COVID19 API.

    Returns:
        tuple: containing,
            cases_in_seven_days(int): Total cases in the last 7 days.
            current_hospitcal_cases(int): Current number of hospital cases.
            cumulative_deaths(int): Total deaths.
    """
    # Assign each csv row title its corresponding list index
    log.info("Processing csv data")
    column_titles = covid_csv_data[0].split(",")
    deaths_column = column_titles.index("cumDailyNsoDeathsByDeathDate")
    hospital_cases_column = column_titles.index("hospitalCases")
    new_cases_column = column_titles.index("newCasesBySpecimenDate")

    # Split each line after the first by ","
    data = []
    for line in covid_csv_data[1:]:
        data.append(line.split(","))

    cases_in_seven_days = sum_7days(data, new_cases_column)
    current_hospital_cases = first_value(data, hospital_cases_column)
    cumulative_deaths = first_value(data, deaths_column)

    return (cases_in_seven_days, current_hospital_cases, cumulative_deaths)


def sum_7days(days: list, key: Union[str, int], skip_first: bool = True) -> int:
    """Iterates over and sums the first 7 days worth of a specified value.

    Args:
        days (list): List of days, where each day contains indexable data.
        key (str | int): Index of data that should be summed.
        skip_first (bool, optional): If first valid data value should be skipped. Defaults to True.

    Returns:
        int: Summed total of specified data key over 7 days.
    """
    total = 0
    limit = 8 if skip_first else 7
    index = 0
    for day in days:
        # Stop if we reach the limit
        if index == limit:
            break
        # Otherwise, skip if the value is not valid AND we have not started summing yet
        if (day[key] in [None, ""]) & (index == 0):
            continue
        # Otherwise, skip the first valid value
        if index == 0 & skip_first:
            index += 1
        # Sum the value, even if it's not valid. This avoids a bug that would occur if one of the
        # values included in the 7 day total is an empty string
        else:
            total += int(day[key])
            index += 1
    return total


def first_value(rows: list, column: Union[str, int]) -> Optional[int]:
    """Get the first valid value in a row.

    Args:
        rows (list): Rows of data, where one of the rows has invalid leading values.
        column (str | int): Index of column that should be verified.

    Returns:
        Optional[int]: First valid value in row.
    """
    result = None
    for row in rows:
        if row[column] not in [None, ""]:
            result = int(row[column])
            break
    return result


def covid_api_request(
    location: str = "Exeter", location_type: str = "ltla"
) -> Optional[dict]:
    """Makes a request to the GOV.UK COVID API.

    Args:
        location (str, optional): Location name. See API developer guide for possible values.
            Defaults to "Exeter".
        location_type (str, optional): Location type. See API developer guide for possible values.
            Defaults to "ltla".

    Returns:
        Optional[dict]: Response data.
    """
    log.info(
        "Making COVID19 API request for location = %s and location_type = %s",
        location,
        location_type,
    )
    location_filter = ["areaType=" + location_type, "areaName=" + location]

    data_structure = {
        "date": "date",
        "newCasesBySpecimenDate": "newCasesBySpecimenDate",
        "hospitalCases": "hospitalCases",
        "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
    }

    try:
        api = uk_covid19.Cov19API(filters=location_filter, structure=data_structure)
        response = api.get_json()
        log.info("Received COVID19 API response")
        return response
    except uk_covid19.exceptions.FailedRequestError:
        log.error("FailedRequestError from COVID19 API request")
        return None
    except requests.exceptions.RequestException:
        log.error("RequestException from COVID19 API request")
        return None


def get_covid_data(
    location: str, nation: str, location_type: str = "ltla", force_update: bool = False
) -> Optional[dict]:
    """Gets internal cached COVID data based on the GOV.UK COVID API.

    Args:
        location (str): Location name. See API developer guide for possible values.
        nation (str): Nation name. See API developer guide for possible values.
        location_type (str, optional): Location type. See API developer guide for possible values.
            Defaults to "ltla".
        force_update (bool, optional): Ignore the cached values and force and update.
            Defaults to False.

    Returns:
        dict: COVID data.
    """
    # IF LOCATION/NATION HAS CHANGED OR DATA IS NONE UPDATE_COVID_DATA
    log.info("Getting COVID data")
    if internal_covid_data["location"] != location:
        log.info(
            "Cached location %s does not match" " requested location %s",
            internal_covid_data["location"],
            location,
        )
    elif internal_covid_data["nation"] != nation:
        log.info(
            "Cached nation %s does not match requested" " nation %s",
            internal_covid_data["nation"],
            nation,
        )
    elif not internal_covid_data["data"]:
        log.info("No cached data exists for %s, %s", location, nation)
    elif force_update:
        log.info("Forcing an update of COVID data")
    else:
        log.info("Using cached COVID data for %s, %s", location, nation)
        return internal_covid_data["data"]
    internal_covid_data["location"] = location
    internal_covid_data["nation"] = nation
    internal_covid_data["data"] = update_covid_data(location, nation, location_type)
    return internal_covid_data["data"]


def update_covid_data(location: str, nation: str, location_type: str = "ltla") -> dict:
    """Update the cached COVID data with new values from the API.

    Args:
        location (str): Location name. See API developer guide for possible values.
        nation (str): Nation name. See API developer guide for possible values.
        location_type (str, optional): Location type. See API developer guide for possible values.
            Defaults to "ltla".

    Returns:
        dict: COVID data.
    """
    local = covid_api_request(location, location_type)
    national = covid_api_request(nation, "Nation")

    try:
        local_7day = sum_7days(local["data"], "newCasesBySpecimenDate")
    except TypeError:
        local_7day = None

    try:
        national_7day = sum_7days(national["data"], "newCasesBySpecimenDate")
        hospital = first_value(national["data"], "hospitalCases")
        deaths = first_value(national["data"], "cumDailyNsoDeathsByDeathDate")
    except TypeError:
        national_7day = hospital = deaths = None

    covid_data = {
        "local_7day": local_7day,
        "national_7day": national_7day,
        "hospital": hospital,
        "deaths": deaths,
    }
    return covid_data


def schedule_covid_updates(update_interval: int, update_name: str) -> None:
    """Wrapper function for scheduler module to schedule update.

    Args:
        update_interval (int): time until update, in seconds.
        update_name (str): name of the update.
    """
    from scheduler import schedule_event # pylint: disable=import-outside-toplevel
    schedule_event(timedelta(seconds=update_interval), update_name, False, True, False)
    return True
