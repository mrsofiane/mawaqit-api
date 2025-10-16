from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class PrayerTimes(BaseModel):
    fajr: str
    sunrise: str
    dohr: str
    asr: str
    maghreb: str
    icha: str

class IqamaPrayerTimes(BaseModel):
    fajr: str
    dohr: str
    asr: str
    maghreb: str
    icha: str


class Announcement(BaseModel):
    id: int
    uuid: str
    title: str
    content: Optional[str] = None
    image: Optional[HttpUrl] = None
    video: Optional[HttpUrl] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    updated: datetime
    duration: Optional[int] = None
    isMobile: bool
    isDesktop: bool

class MosqueServices(BaseModel):
    womenSpace: bool
    janazaPrayer: bool
    aidPrayer: bool
    childrenCourses: bool
    adultCourses: bool
    ramadanMeal: bool
    handicapAccessibility: bool
    ablutions: bool
    parking: bool

