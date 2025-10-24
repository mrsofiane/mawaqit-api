import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
from config.redisClient import redisClient
from redis.exceptions import RedisError
from typing import List

import json
import re
import models.models as models


def fetch_mawaqit(masjid_id:str):
    WEEK_IN_SECONDS = 604800
    retrieved_data = None

    # Check if Redis client is initialized
    if redisClient is not None:
        try:
            retrieved_data = redisClient.get(masjid_id)
        except RedisError:
            print("Error when reading from cache")

        if retrieved_data:
            return json.loads(retrieved_data)

    url = f"https://mawaqit.net/fr/m/{masjid_id}"
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        searchString = r'(?:var|let)\s+confData\s*=\s*(.*?);'
        script = soup.find('script', string=re.compile(searchString, re.DOTALL))
        if script:
            mawaqit = re.search(searchString, script.string, re.DOTALL)
            if mawaqit:
                conf_data_json = mawaqit.group(1)
                conf_data = json.loads(conf_data_json)
                # Store data in Redis if client is initialized
                if redisClient is not None:
                    redisClient.set(masjid_id, json.dumps(conf_data), ex=WEEK_IN_SECONDS)
                return conf_data
            else:
                raise HTTPException(status_code=500, detail=f"Failed to extract confData JSON for {masjid_id}")
        else:
            print("Script containing confData not found.")
            raise HTTPException(status_code=500, detail=f"Script containing confData not found for {masjid_id}")
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail=f"{masjid_id} not found")  
    if r.status_code == 500:
        raise HTTPException(status_code=502, detail=f"something went wrong fetching {url}") 

def get_prayer_times_of_the_day(masjid_id):
    confData = fetch_mawaqit(masjid_id)
    times = confData["times"]
    sunrise = confData["shuruq"]
    prayer_time = models.PrayerTimes(fajr=times[0], sunrise=sunrise, dohr=times[1], asr=times[2], maghreb=times[3], icha=times[4])
    prayer_dict = prayer_time.model_dump()
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
            sunrise=prayer[1],
            dohr=prayer[2],
            asr=prayer[3],
            maghreb=prayer[4],
            icha=prayer[5]
        )
        for prayer in month.values()
    ]
    return prayer_times_list

def get_month_iqama(masjid_id, month_number):
    if month_number < 1 or month_number > 12:
        raise HTTPException(status_code=400, detail=f"Month number should be between 1 and 12")
    confData = fetch_mawaqit(masjid_id)
    month = confData["iqamaCalendar"][month_number - 1]
    iqama_times_list = [
        models.IqamaPrayerTimes( 
            fajr=iqama[0],
            dohr=iqama[1],
            asr=iqama[2],
            maghreb=iqama[3],
            icha=iqama[4]
        )
        for iqama in month.values()
    ]

    return iqama_times_list

def get_announcements(masjid_id: int) -> List[models.Announcement]:
    confData = fetch_mawaqit(masjid_id)
    announcements = confData.get("announcements", [])
    return [models.Announcement(**a) for a in announcements]

def get_services(masjid_id: int) -> models.MosqueServices:
    confData = fetch_mawaqit(masjid_id)
    mosque_services = models.MosqueServices(**confData)
    return mosque_services