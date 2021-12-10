from covid_data_handler import (
    get_covid_data,
    parse_csv_data,
    process_covid_csv_data,
    covid_api_request,
    schedule_covid_updates,
    update_covid_data,
)


def test_parse_csv_data():
    data = parse_csv_data("nation_2021-10-28.csv")
    assert len(data) == 639


def test_process_covid_csv_data():
    last7days_cases, current_hospital_cases, total_deaths = process_covid_csv_data(
        parse_csv_data("nation_2021-10-28.csv")
    )
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544


def test_covid_api_request():
    data = covid_api_request()
    assert isinstance(data, dict)


def test_schedule_covid_updates():
    schedule_covid_updates(update_interval=10, update_name="update test")


def test_get_covid_data():
    assert get_covid_data("Exeter", "England")


def test_update_covid_data():
    assert update_covid_data("Exeter", "England")
