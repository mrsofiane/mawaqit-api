"""
Native RFC 5545 iCalendar generator for mosque prayer calendars.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Adhan day row: [fajr, shuruq, dohr, asr, maghreb, icha]
ADHAN_SLOTS: Sequence[Tuple[str, str, int]] = (
    ("fajr", "Fajr", 0),
    ("shuruk", "Shuruk", 1),
    ("dohr", "Dhuhr", 2),
    ("asr", "Asr", 3),
    ("maghreb", "Maghrib", 4),
    ("icha", "Isha", 5),
)

# Iqama day row: [fajr, dohr, asr, maghreb, icha] (no shuruk)
IQAMA_SLOTS: Sequence[Tuple[str, str, int]] = (
    ("fajr", "Fajr", 0),
    ("dohr", "Dhuhr", 1),
    ("asr", "Asr", 2),
    ("maghreb", "Maghrib", 3),
    ("icha", "Isha", 4),
)


def build_calendar_ics(
    masjid_id: str,
    name: str,
    timezone: str,
    calendar: List[Dict],
    kind: str = "adhan",
    duration_minutes: int = 15,
    include_shuruk: bool = False,
    year: Optional[int] = None,
    adhan_calendar: Optional[List[Dict]] = None,
) -> str:
    """
    Build an RFC 5545 calendar string from a 12-month Mawaqit calendar.

    Datetimes are emitted in UTC (Z). Invalid days (e.g. Feb 29 in a non-leap
    year) are skipped via ValueError/OverflowError.
    """
    if kind not in ("adhan", "iqama"):
        raise ValueError(f"Unsupported kind: {kind}")

    try:
        tz = ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, TypeError, ValueError) as exc:
        raise ValueError(f"Invalid timezone: {timezone}") from exc

    if year is None:
        year = datetime.now(tz).year

    kind_label = "Adhan" if kind == "adhan" else "Iqama"
    slots = list(ADHAN_SLOTS if kind == "adhan" else IQAMA_SLOTS)
    if kind == "adhan" and not include_shuruk:
        slots = [s for s in slots if s[0] != "shuruk"]

    lines: List[str] = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Mawaqit API//Prayer Times//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{_escape_text(f'{name} Prayer Times ({kind_label})')}",
        f"X-WR-TIMEZONE:{timezone}",
    ]

    for month_index, month in enumerate(calendar):
        month_number = month_index + 1
        if not isinstance(month, dict):
            continue
        for day_key in sorted(month.keys(), key=_day_sort_key):
            try:
                day = int(day_key)
            except (TypeError, ValueError):
                continue

            times = month[day_key]
            if not isinstance(times, (list, tuple)):
                continue

            for prayer_id, prayer_label, index in slots:
                if index >= len(times):
                    continue
                raw = times[index]
                start_local = _resolve_local_datetime(
                    year=year,
                    month=month_number,
                    day=day,
                    raw_time=raw,
                    tz=tz,
                    kind=kind,
                    prayer_index=index,
                    adhan_calendar=adhan_calendar,
                )
                if start_local is None:
                    continue

                end_local = start_local + timedelta(minutes=duration_minutes)
                start_utc = start_local.astimezone(ZoneInfo("UTC"))
                end_utc = end_local.astimezone(ZoneInfo("UTC"))

                uid = f"{masjid_id}-{kind}-{prayer_id}-{year:04d}{month_number:02d}{day:02d}@mawaqit-api"
                summary = f"{prayer_label} ({kind_label}) - {name}"

                lines.extend(
                    [
                        "BEGIN:VEVENT",
                        f"UID:{uid}",
                        f"DTSTAMP:{_format_utc(start_utc)}",
                        f"DTSTART:{_format_utc(start_utc)}",
                        f"DTEND:{_format_utc(end_utc)}",
                        f"SUMMARY:{_escape_text(summary)}",
                        "SEQUENCE:0",
                        "END:VEVENT",
                    ]
                )

    lines.append("END:VCALENDAR")
    return _fold_lines(lines)


def _day_sort_key(key) -> int:
    try:
        return int(key)
    except (TypeError, ValueError):
        return 0


def _resolve_local_datetime(
    year: int,
    month: int,
    day: int,
    raw_time,
    tz: ZoneInfo,
    kind: str,
    prayer_index: int,
    adhan_calendar: Optional[List[Dict]],
) -> Optional[datetime]:
    if raw_time is None:
        return None

    text = str(raw_time).strip()
    if not text or text in ("--:--", "-", "null", "None"):
        return None

    try:
        if text.startswith("+") and kind == "iqama":
            offset_minutes = int(text[1:])
            adhan_raw = _lookup_adhan_time(adhan_calendar, month, day, prayer_index)
            if adhan_raw is None:
                return None
            base = _parse_hhmm_datetime(year, month, day, adhan_raw, tz)
            if base is None:
                return None
            return base + timedelta(minutes=offset_minutes)

        return _parse_hhmm_datetime(year, month, day, text, tz)
    except (ValueError, OverflowError, TypeError):
        return None


def _lookup_adhan_time(
    adhan_calendar: Optional[List[Dict]],
    month: int,
    day: int,
    iqama_index: int,
) -> Optional[str]:
    """Map iqama slot index to adhan row indices (skipping shuruk at index 1)."""
    if not adhan_calendar or month < 1 or month > len(adhan_calendar):
        return None
    month_data = adhan_calendar[month - 1]
    if not isinstance(month_data, dict):
        return None
    row = month_data.get(str(day), month_data.get(day))
    if not isinstance(row, (list, tuple)):
        return None
    # iqama: 0 fajr, 1 dohr, 2 asr, 3 maghreb, 4 icha
    # adhan: 0 fajr, 1 shuruq, 2 dohr, 3 asr, 4 maghreb, 5 icha
    adhan_index = iqama_index if iqama_index == 0 else iqama_index + 1
    if adhan_index >= len(row):
        return None
    return str(row[adhan_index])


def _parse_hhmm_datetime(
    year: int,
    month: int,
    day: int,
    time_text: str,
    tz: ZoneInfo,
) -> Optional[datetime]:
    try:
        hour_str, minute_str = time_text.split(":", 1)
        hour = int(hour_str)
        minute = int(minute_str)
        return datetime(year, month, day, hour, minute, tzinfo=tz)
    except (ValueError, OverflowError, TypeError):
        return None


def _format_utc(dt: datetime) -> str:
    return dt.strftime("%Y%m%dT%H%M%SZ")


def _escape_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
        .replace("\r", "\\n")
    )


def _fold_lines(lines: Iterable[str]) -> str:
    folded: List[str] = []
    for line in lines:
        encoded = line.encode("utf-8")
        if len(encoded) <= 75:
            folded.append(line)
            continue
        # Fold on octet boundaries (RFC 5545 section 3.1)
        while len(encoded) > 75:
            chunk = encoded[:75]
            # Avoid splitting a multibyte UTF-8 character
            while chunk and (chunk[-1] & 0xC0) == 0x80:
                chunk = chunk[:-1]
            if not chunk:
                chunk = encoded[:75]
            folded.append(chunk.decode("utf-8"))
            encoded = b" " + encoded[len(chunk) :]
        if encoded:
            folded.append(encoded.decode("utf-8"))
    return "\r\n".join(folded) + "\r\n"
