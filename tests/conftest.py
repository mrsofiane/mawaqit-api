"""Shared fixtures: all tests stay offline (no live mawaqit.net calls)."""
from datetime import datetime

import pytest


def _day_adhan(fajr="05:30", shuruq="07:00", dohr="13:00", asr="16:00", maghreb="19:00", icha="20:30"):
    return [fajr, shuruq, dohr, asr, maghreb, icha]


def _day_iqama(fajr="05:45", dohr="13:15", asr="16:15", maghreb="19:05", icha="20:45"):
    return [fajr, dohr, asr, maghreb, icha]


def build_mock_conf_data(
    name="Assalam Argenteuil",
    timezone="Europe/Paris",
    include_feb_29=False,
):
    """Minimal confData shaped like mawaqit.net scrape output."""
    calendar = []
    iqama_calendar = []
    days_per_month = [31, 29 if include_feb_29 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    for month_idx, num_days in enumerate(days_per_month):
        month = {}
        iqama_month = {}
        for day in range(1, num_days + 1):
            key = str(day)
            # Distinct times so DST / UID tests can assert specifics for day 1 of January
            if month_idx == 0 and day == 1:
                month[key] = _day_adhan(
                    fajr="05:30",
                    shuruq="07:00",
                    dohr="13:00",
                    asr="16:00",
                    maghreb="19:00",
                    icha="20:30",
                )
                iqama_month[key] = ["+15", "+10", "16:20", "+5", "+15"]
            elif month_idx == 1 and day == 29 and include_feb_29:
                # Caller may still force a 29 entry for leap-year skip tests
                month[key] = _day_adhan()
                iqama_month[key] = _day_iqama()
            else:
                month[key] = _day_adhan()
                iqama_month[key] = _day_iqama()
        calendar.append(month)
        iqama_calendar.append(iqama_month)

    return {
        "name": name,
        "timezone": timezone,
        "times": ["05:31", "13:02", "16:22", "19:13", "20:24"],
        "shuruq": "06:45",
        "calendar": calendar,
        "iqamaCalendar": iqama_calendar,
        "announcements": [
            {
                "id": 1,
                "uuid": "test-uuid",
                "title": "Test announcement",
                "content": "Hello",
                "image": None,
                "video": None,
                "startDate": None,
                "endDate": None,
                "updated": datetime(2024, 1, 1, 12, 0, 0),
                "duration": 10,
                "isMobile": True,
                "isDesktop": True,
            }
        ],
        "womenSpace": True,
        "janazaPrayer": False,
        "aidPrayer": True,
        "childrenCourses": False,
        "adultCourses": True,
        "ramadanMeal": False,
        "handicapAccessibility": True,
        "ablutions": True,
        "parking": False,
    }


@pytest.fixture
def mock_conf_data():
    return build_mock_conf_data()


@pytest.fixture(autouse=True)
def _patch_fetch_mawaqit(monkeypatch, mock_conf_data):
    """Prevent every test from hitting the live network."""
    monkeypatch.setattr(
        "scraping.script.fetch_mawaqit",
        lambda masjid_id: mock_conf_data,
    )
