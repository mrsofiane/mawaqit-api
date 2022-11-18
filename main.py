from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
import uvicorn

from typing import List

import script
import models



def create_app() -> FastAPI:
    app = FastAPI(title='Mawaqit Api', debug=False, read_root="/")
    return app


app = create_app()
app.router.prefix = "/api/v1"


@app.get("/", summary="Greetings",)
def read_root():
    return {"Greetings": "Hello and Welcome to this Api, this api use the mawaqit.net as data source of prayers time in more than 8000 masjid, this api can be used to fetch data in json, you can find our docs on /docs. "}


@app.get("/{masjid_id}/", status_code=200, summary="get the raw data from mawaqit website")
def get_raw_data(masjid_id: str):
    r = script.fetch_mawaqit(masjid_id)
    return {"rawdata": r}


@app.get("/{masjid_id}/prayer-times", status_code=200, summary="get the prayer times of the current day", response_model=models.PrayerTimes)
def get_prayer_times(masjid_id: str):
    prayer_times = script.get_prayer_times_of_the_day(masjid_id)
    return prayer_times


@app.get("/{masjid_id}/calendar", status_code=200, summary="get the year calendar of the prayer times")
def get_year_calendar(masjid_id: str):
    r = script.get_calendar(masjid_id)
    return {"calendar": r}


@app.get("/{masjid_id}/calendar/{month_number}", status_code=200, summary="get the month calendar of the prayer times", response_model=List[models.PrayerTimes])
def get_month_calendar(masjid_id: str, month_number: int):
    month_dict = script.get_month(masjid_id, month_number)
    return jsonable_encoder(month_dict)