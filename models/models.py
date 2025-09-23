from pydantic import BaseModel

class PrayerTimes(BaseModel):
    fajr: str
    sunrise: str
    dohr: str
    asr: str
    maghreb: str
    icha: str

