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
        script = soup.find('script', string=re.compile(r'var confData = (.*?);', re.DOTALL))
        if script:
            mawaqit = re.search(r'var confData = (.*?);', script.string, re.DOTALL)
            if mawaqit:
                conf_data_json = mawaqit.group(1)
                conf_data = json.loads(conf_data_json)
                return conf_data
            else:
                raise HTTPException(status_code=500, detail=f"Failed to extract confData JSON for {masjid_id}")
        else:
            print("Script containing confData not found.")
            raise HTTPException(status_code=500, detail=f"Script containing confData not found for {masjid_id}")
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
    if month_number < 1 or month_number > 12:
        raise HTTPException(status_code=400, detail=f"Month number should be between 1 and 12")
    confData = fetch_mawaqit(masjid_id)
    month = confData["calendar"][month_number - 1]
    prayer_times_list = [
        models.PrayerTimes( 
            fajr=prayer[0],
            sunset=prayer[1],
            dohr=prayer[2],
            asr=prayer[3],
            maghreb=prayer[4],
            icha=prayer[5]
        )
        for prayer in month.values()
    ]
    return prayer_times_list