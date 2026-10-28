from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response

from hashlib import sha256
from typing import List

import scraping.script as script
import models.models as models
from config.auth import verify_token, verify_token_or_query
from services.ical_service import build_calendar_ics


router = APIRouter(prefix="/api/v1")

_ICS_RESPONSE = {
    200: {
        "content": {"text/calendar": {}},
        "description": "RFC 5545 iCalendar feed",
    }
}


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

@router.get("/{masjid_id}/next-prayer-times", status_code=200, summary="Get the next prayer time once the time prayer is passed")#,  #response_model=models.PrayerTimes)
def get_next_prayer_times(masjid_id: str, _: str = Depends(verify_token)):
    prayer_times = script.get_next_prayer_times_of_the_day(masjid_id)
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


@router.get(
    "/{masjid_id}/calendar.ics",
    status_code=200,
    summary="Subscribe to the year prayer calendar as an iCalendar feed (adhan)",
    responses=_ICS_RESPONSE,
)
def get_calendar_ics(
    masjid_id: str,
    duration: int = Query(default=15, ge=1, le=180),
    include_shuruk: bool = Query(default=False),
    _: str = Depends(verify_token_or_query),
):
    return _ics_response(
        masjid_id=masjid_id,
        kind="adhan",
        duration_minutes=duration,
        include_shuruk=include_shuruk,
    )


@router.get(
    "/{masjid_id}/calendar-iqama.ics",
    status_code=200,
    summary="Subscribe to the year iqama calendar as an iCalendar feed",
    responses=_ICS_RESPONSE,
)
def get_calendar_iqama_ics(
    masjid_id: str,
    duration: int = Query(default=15, ge=1, le=180),
    _: str = Depends(verify_token_or_query),
):
    return _ics_response(
        masjid_id=masjid_id,
        kind="iqama",
        duration_minutes=duration,
        include_shuruk=False,
    )


def _ics_response(
    masjid_id: str,
    kind: str,
    duration_minutes: int,
    include_shuruk: bool,
) -> Response:
    mosque = script.get_mosque_calendar(masjid_id)
    timezone = mosque.get("timezone")
    if not timezone:
        raise HTTPException(status_code=502, detail=f"Timezone missing for {masjid_id}")

    calendar = mosque["calendar"] if kind == "adhan" else mosque.get("iqamaCalendar", [])
    try:
        body = build_calendar_ics(
            masjid_id=masjid_id,
            name=mosque.get("name") or masjid_id,
            timezone=timezone,
            calendar=calendar,
            kind=kind,
            duration_minutes=duration_minutes,
            include_shuruk=include_shuruk,
            adhan_calendar=mosque["calendar"] if kind == "iqama" else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    safe_name = (
        masjid_id.replace('"', "")
        .replace("\r", "")
        .replace("\n", "")
    )
    etag = sha256(body.encode("utf-8")).hexdigest()
    return Response(
        content=body,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f'inline; filename="{safe_name}.ics"',
            "Cache-Control": "public, max-age=3600",
            "ETag": f'"{etag}"',
        },
    )
