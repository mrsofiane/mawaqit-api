from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from typing import List

import scraping.script as script
import models.models as models
from config.auth import verify_token

router = APIRouter(prefix="/api/v1")

@router.get("/", summary="Greetings")
def read_root():
    return {"Greetings": "Hello and Welcome to this Api, this api use the mawaqit.net as data source of prayers time in more than 8000 masjid, this api can be used to fetch data in json, you can find our docs on /docs. "}

@router.get("/{masjid_id}/", status_code=200, summary="get the raw data from mawaqit website")
def get_raw_data(masjid_id: str, _: str = Depends(verify_token)):
    r = script.fetch_mawaqit(masjid_id)
    return {"rawdata": r}

@router.get("/{masjid_id}/announcements", status_code=200, summary="get the announcements of a specific mosque", response_model=List[models.Announcement])
def get_announcements(masjid_id: str, _: str = Depends(verify_token)):
    r = script.get_announcements(masjid_id)
    return r

@router.get("/{masjid_id}/services", status_code=200, summary="Get the services of a specific mosque", response_model=models.MosqueServices)
def get_services(masjid_id: str, _: str = Depends(verify_token)):
    services = script.get_services(masjid_id)
    return services

@router.get("/{masjid_id}/prayer-times", status_code=200, summary="get the prayer times of the current day", response_model=models.PrayerTimes)
def get_prayer_times(masjid_id: str, _: str = Depends(verify_token)):
    prayer_times = script.get_prayer_times_of_the_day(masjid_id)
    return prayer_times


@router.get("/{masjid_id}/calendar", status_code=200, summary="get the year calendar of the prayer times")
def get_year_calendar(masjid_id: str, _: str = Depends(verify_token)):
    r = script.get_calendar(masjid_id)
    return {"calendar": r}


@router.get("/{masjid_id}/calendar/{month_number}", status_code=200, summary="get the month calendar of the prayer times", response_model=List[models.PrayerTimes])
def get_month_calendar(masjid_id: str, month_number: int, _: str = Depends(verify_token)):
    month_dict = script.get_month(masjid_id, month_number)
    return jsonable_encoder(month_dict)

@router.get("/{masjid_id}/calendar-iqama/{month_number}", status_code=200, summary="get the month calendar iqama of the prayer times", response_model=List[models.IqamaPrayerTimes])
def get_month_calendar_iqama(masjid_id: str, month_number: int, _: str = Depends(verify_token)):
    month_dict = script.get_month_iqama(masjid_id, month_number)
    return jsonable_encoder(month_dict)
