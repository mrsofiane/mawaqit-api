"""Unit tests for the native RFC 5545 iCalendar generator."""
from services.ical_service import build_calendar_ics
from tests.conftest import build_mock_conf_data


def _events(ics: str):
    return [block for block in ics.split("BEGIN:VEVENT") if "END:VEVENT" in block]


def test_crlf_and_required_calendar_fields():
    conf = build_mock_conf_data()
    ics = build_calendar_ics(
        masjid_id="assalam-argenteuil",
        name=conf["name"],
        timezone=conf["timezone"],
        calendar=conf["calendar"],
        kind="adhan",
        duration_minutes=15,
        year=2025,
    )
    assert ics.endswith("\r\n")
    assert "\r\n" in ics
    assert "BEGIN:VCALENDAR" in ics
    assert "VERSION:2.0" in ics
    assert "PRODID:-//Mawaqit API//Prayer Times//EN" in ics
    assert "CALSCALE:GREGORIAN" in ics
    assert "METHOD:PUBLISH" in ics
    assert "X-WR-TIMEZONE:Europe/Paris" in ics
    assert "END:VCALENDAR" in ics


def test_summary_uses_ascii_hyphen_not_em_dash():
    conf = build_mock_conf_data()
    ics = build_calendar_ics(
        masjid_id="assalam-argenteuil",
        name=conf["name"],
        timezone=conf["timezone"],
        calendar=conf["calendar"],
        kind="adhan",
        year=2025,
    )
    assert "SUMMARY:Fajr (Adhan) - Assalam Argenteuil" in ics
    assert "—" not in ics


def test_duration_affects_dtend():
    conf = build_mock_conf_data()
    # Jan 1 Fajr 05:30 Europe/Paris in winter = 04:30 UTC; +10 min => 04:40Z
    ics = build_calendar_ics(
        masjid_id="assalam-argenteuil",
        name=conf["name"],
        timezone=conf["timezone"],
        calendar=conf["calendar"],
        kind="adhan",
        duration_minutes=10,
        year=2025,
    )
    assert "UID:assalam-argenteuil-adhan-fajr-20250101@mawaqit-api" in ics
    assert "DTSTART:20250101T043000Z" in ics
    assert "DTEND:20250101T044000Z" in ics


def test_shuruk_excluded_by_default_and_included_when_flagged():
    conf = build_mock_conf_data()
    without = build_calendar_ics(
        masjid_id="m",
        name="M",
        timezone=conf["timezone"],
        calendar=conf["calendar"],
        kind="adhan",
        include_shuruk=False,
        year=2025,
    )
    with_shuruk = build_calendar_ics(
        masjid_id="m",
        name="M",
        timezone=conf["timezone"],
        calendar=conf["calendar"],
        kind="adhan",
        include_shuruk=True,
        year=2025,
    )
    assert "shuruk" not in without
    assert "SUMMARY:Shuruk (Adhan) - M" in with_shuruk
    assert "UID:m-adhan-shuruk-20250101@mawaqit-api" in with_shuruk


def test_iqama_has_no_shuruk_and_supports_plus_offset():
    conf = build_mock_conf_data()
    ics = build_calendar_ics(
        masjid_id="assalam-argenteuil",
        name=conf["name"],
        timezone=conf["timezone"],
        calendar=conf["iqamaCalendar"],
        kind="iqama",
        include_shuruk=True,
        year=2025,
        adhan_calendar=conf["calendar"],
    )
    assert "shuruk" not in ics
    assert "SUMMARY:Fajr (Iqama) - Assalam Argenteuil" in ics
    # Adhan fajr 05:30 +15 => 05:45 local = 04:45 UTC in January
    assert "DTSTART:20250101T044500Z" in ics
    # Absolute iqama asr 16:20 local = 15:20 UTC
    assert "UID:assalam-argenteuil-iqama-asr-20250101@mawaqit-api" in ics
    assert "DTSTART:20250101T152000Z" in ics


def test_stable_uid_when_time_changes():
    conf = build_mock_conf_data()
    calendar_a = conf["calendar"]
    calendar_b = build_mock_conf_data()["calendar"]
    calendar_b[0]["1"] = ["06:00", "07:30", "13:30", "16:30", "19:30", "21:00"]

    ics_a = build_calendar_ics(
        masjid_id="m",
        name="M",
        timezone="Europe/Paris",
        calendar=calendar_a,
        year=2025,
    )
    ics_b = build_calendar_ics(
        masjid_id="m",
        name="M",
        timezone="Europe/Paris",
        calendar=calendar_b,
        year=2025,
    )
    uid = "UID:m-adhan-fajr-20250101@mawaqit-api"
    assert uid in ics_a and uid in ics_b
    assert "DTSTART:20250101T043000Z" in ics_a
    assert "DTSTART:20250101T050000Z" in ics_b


def test_invalid_time_skipped():
    conf = build_mock_conf_data()
    conf["calendar"][0]["1"][0] = "--:--"
    ics = build_calendar_ics(
        masjid_id="m",
        name="M",
        timezone="Europe/Paris",
        calendar=conf["calendar"],
        year=2025,
    )
    assert "UID:m-adhan-fajr-20250101@mawaqit-api" not in ics
    assert "UID:m-adhan-dohr-20250101@mawaqit-api" in ics


def test_feb_29_skipped_in_non_leap_year():
    conf = build_mock_conf_data(include_feb_29=False)
    # Force an invalid Feb 29 entry into a non-leap year calendar
    conf["calendar"][1]["29"] = ["05:00", "07:00", "13:00", "16:00", "19:00", "20:30"]
    ics = build_calendar_ics(
        masjid_id="m",
        name="M",
        timezone="Europe/Paris",
        calendar=conf["calendar"],
        year=2025,  # not a leap year
    )
    assert "20250229" not in ics
    assert "UID:m-adhan-fajr-20250228@mawaqit-api" in ics
    assert "UID:m-adhan-fajr-20250301@mawaqit-api" in ics


def test_text_escaping_and_folding():
    long_name = "Mosque; Name, With\\Special " + ("X" * 80)
    calendar = [{"1": ["05:30", "07:00", "13:00", "16:00", "19:00", "20:30"]}] + [{}] * 11
    ics = build_calendar_ics(
        masjid_id="m",
        name=long_name,
        timezone="Europe/Paris",
        calendar=calendar,
        year=2025,
    )
    assert "Mosque\\; Name\\, With\\\\Special" in ics
    # Folded continuation lines start with a space after CRLF
    assert "\r\n " in ics


def test_dst_summer_utc_conversion():
    # July 1 Fajr 05:30 Europe/Paris (CEST, UTC+2) => 03:30Z
    conf = build_mock_conf_data()
    conf["calendar"][6]["1"] = ["05:30", "07:00", "13:00", "16:00", "19:00", "20:30"]
    ics = build_calendar_ics(
        masjid_id="m",
        name="M",
        timezone="Europe/Paris",
        calendar=conf["calendar"],
        year=2025,
    )
    assert "DTSTART:20250701T033000Z" in ics
