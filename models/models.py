from pydantic import BaseModel

class PrayerTimes(BaseModel):
    fajr: str
    sunset: str
    dohr: str
    asr: str
    maghreb: str
    icha: str

