import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException

import json
import re
import models


def fetch_mawaqit(masjid_id):
    r = requests.get(f"https://mawaqit.net/fr/{masjid_id}")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        script = soup.script
        m = re.search(r'var confData = (.*?);', script.string)
        confData = json.loads(m.group(1))
        return confData
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail=f"{masjid_id} not found") 

def get_prayer_times_of_the_day(masjid_id):
    confData = fetch_mawaqit(masjid_id)
    times = confData["times"]
    sunset = confData["shuruq"]
    prayer_time = models.PrayerTimes(fajr=times[0], sunset=sunset, dohr=times[1], asr=times[2], maghreb=times[3], icha=times[4])
    prayer_dict = prayer_time.dict()
    return prayer_dict

def get_calendar(masjid_id):
    confData = fetch_mawaqit(masjid_id)
    return confData["calendar"]

def get_month(masjid_id, month_number):
    confData = fetch_mawaqit(masjid_id)
    month = confData["calendar"][month_number - 1]
    month_dict = []
    for i in range(1, len(month)+1):
        key = str(i)
        month_dict.append(models.PrayerTimes(fajr=month[key][0], sunset=month[key][1], dohr=month[key][2], asr=month[key][3], maghreb=month[key][4], icha=month[key][5]))

    return month_dict