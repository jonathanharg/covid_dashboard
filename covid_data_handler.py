from uk_covid19 import Cov19API
import requests
import uk_covid19

internal_covid_data = {"location": None, "nation": None, "data": None}


def parse_csv_data(csv_filename: str) -> list:
    """Parses csv file into list of row strings.

    Args:
        csv_filename (str): name or path of csv file to parse

    Returns:
        rows (list[str]): list of csv row strings
    """
    rows = []
    with open(csv_filename, encoding="utf-8") as data:
        file = data.read()
        for line in file.split("\n"):
            if line != "":
                rows.append(line)
    return rows


def process_covid_csv_data(covid_csv_data):
    """Proccess COVID csv data and calculate 7 day case total, current hospital cases, and total deaths.

    Args:
        covid_csv_data (list[str]): List of csv row strings from the GOV.UK Coronavirus API

    Returns:
        (tuple): containing
            cases_in_seven_days(int): Total cases in the last 7 days
            current_hospitcal_cases(int): Current number of hospital cases
            cumulative_deaths(int): Total deaths
    """

    # Assign each csv row title its corresponding list index
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


def sum_7days(days, key, skip_first=True) -> int:
    """Iterate over and sum 7 days worth of a specified value.

    Args:
        days (list): List of days, where each day contains "indexable" data
        key: Index of data that should be summed, can be either an int for a list or a string for a dictionary
        skip_first (bool, optional): If the first valid data value should be skipeed. Defaults to True.

    Returns:
        int: Summed total of specified data key over 7 days
    """
    total = 0
    limit = 8 if skip_first else 7
    index = 0
    for day in days:
        # Stop if we reach the limit
        if index == limit:
            break
        # Otherwise, skip if the value is not valid AND we have not started summing yet
        elif (day[key] in [None, ""]) & (index == 0):
            continue
        # Otherwise, skip the first valid value
        elif index == 0 & skip_first:
            index += 1
        # Sum the value, even if it's not valid. This avoids a bug that would occur if one of the values included in the 7 day total is ""
        else:
            total += int(day[key])
            index += 1
    return total


def first_value(rows, column):
    """Get the first valid value in a row.

    Args:
        rows (list): Rows of data, where one of the rows has leading values are not valid
        column: Index of column that should be verified, can be either an int for a list or a string for a dictionary

    Returns:
        any: First valid value in row
    """
    result = None
    for row in rows:
        if row[column] not in [None, ""]:
            result = int(row[column])
            break
    return result


def covid_API_request(location="Exeter", location_type="ltla"):
    """Returns latest COVID data from GOV.UK Coronavirus API as a dictionary

    For more info see https://publichealthengland.github.io/coronavirus-dashboard-api-python-sdk/

    Args:
        location(str): Location name, see https://coronavirus.data.gov.uk/details/developers-guide/main-api#params-filters.
        location_type(str): Location type either "overview", "nation", "region", "nhsRegion", "utla", or "ltla", for more information see https://coronavirus.data.gov.uk/details/developers-guide/main-api#params-filters.

    Returns:
        dict: Response data
    """

    location_filter = ["areaType=" + location_type, "areaName=" + location]

    data_structure = {
        "date": "date",
        "newCasesBySpecimenDate": "newCasesBySpecimenDate",
        "hospitalCases": "hospitalCases",
        "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
    }

    try:
        api = Cov19API(filters=location_filter, structure=data_structure)
        response = api.get_json()
        return response
    except uk_covid19.exceptions.FailedRequestError:
        return None
    except requests.exceptions.RequestException:
        return None


def get_covid_data(location, nation, location_type="ltla", force_update=False):
    # IF LOCATION/NATION HAS CHANGED OR DATA IS NONE UPDATE_COVID_DATA
    if (
        (internal_covid_data["location"] != location)
        | (internal_covid_data["nation"] != nation)
        | (internal_covid_data["data"] is None)
        | force_update
    ):
        internal_covid_data["location"] = location
        internal_covid_data["nation"] = nation
        internal_covid_data["data"] = update_covid_data(location, nation, location_type)
    return internal_covid_data["data"]


def update_covid_data(location, nation, location_type="ltla"):
    """Get local and national COVID data

    Args:
        location (str): Location name, see https://coronavirus.data.gov.uk/details/developers-guide/main-api#params-filters.
        nation (str): Nation name, see https://coronavirus.data.gov.uk/details/developers-guide/main-api#params-filters.
        location_type (str, optional): Location type either "overview", "nation", "region", "nhsRegion", "utla", or "ltla", for more information see https://coronavirus.data.gov.uk/details/developers-guide/main-api#params-filters. Defaults to "ltla".

    Returns:
        int: Local 7-day infections
        int: National 7-day infections
        int: National hospital cases
        int: National total deaths
    """
    local = covid_API_request(location, location_type)
    national = covid_API_request(nation, "Nation")

    # try:
    local_7day = sum_7days(local["data"], "newCasesBySpecimenDate")
    # except ValueError:
    #     local_7day = None

    # try:
    national_7day = sum_7days(national["data"], "newCasesBySpecimenDate")
    hospital = first_value(national["data"], "hospitalCases")
    deaths = first_value(national["data"], "cumDailyNsoDeathsByDeathDate")
    # except ValueError:
    #     national_7day = None
    #     hospital = None
    #     deaths = None

    covid_data = {
        "local_7day": local_7day,
        "national_7day": national_7day,
        "hospital": hospital,
        "deaths": deaths,
    }
    return covid_data


# schedule = sched.scheduler(time.time, time.sleep)
def schedule_covid_updates(update_interval, update_name):
    # Use `sched` module to schedule updates to the covid data at the given time interval
    # schedule.enter(time.time + , 1, )
    return


process_covid_csv_data(parse_csv_data("nation_2021-10-28.csv"))
