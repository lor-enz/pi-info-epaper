import logging
from datetime import datetime as dt
import datetime as datetime
import time
import pytz

TZ_GERMANY = "Europe/Vienna"


def current_time():
    return time.time()


def ts2dt(timestamp):
    tz = pytz.timezone(TZ_GERMANY)
    # To convert the timestamp to an aware datetime object in the given timezone directly:
    return dt.fromtimestamp(timestamp, tz)


def dt2ts(time_string, time_format="%Y-%m-%d_%H:%M", timezone_name=TZ_GERMANY):
    logging.debug(f'time_string {time_string} time_format {time_format} timezone_name {timezone_name}')
    dt_obj = datetime.datetime.strptime(time_string, time_format)
    timezone_obj = pytz.timezone(timezone_name)
    dt_obj = timezone_obj.localize(dt_obj)
    return dt.timestamp(dt_obj)


def seconds2delta(seconds):
    return datetime.timedelta(seconds=seconds)


def is_business_hours(given_timestamp=0):
    if given_timestamp < 1:
        dt_object = dt.now()
    else:
        dt_object = dt.fromtimestamp(given_timestamp)

    if dt_object.hour == 18 and dt_object.minute == 00:
        return True
    return 7 <= dt_object.hour <= 18


# Returns the seconds of 'business time' that has passed between two timestamps
# week days are not taken into account, so sunday as well as mo - fr all have 10 hours of business time
# business time is time from 8:00 to 18:00
def business_time_since(timestamp_a, timestamp_b=0, business_time_start=8, business_time_end=18):
    if timestamp_b < 1:
        timestamp_b = dt.timestamp(dt.now())

    dt_a = ts2dt(timestamp_a)
    dt_b = ts2dt(timestamp_b)

    if dt_a.hour < 8:
        dt_a = dt_a.replace(hour=8)
        dt_a = dt_a.replace(minute=0)
        dt_a = dt_a.replace(second=0)

    if dt_a.hour >= 18:
        dt_a = dt_a.replace(hour=18)
        dt_a = dt_a.replace(minute=0)
        dt_a = dt_a.replace(second=0)

    if dt_b.hour < 8:
        dt_b = dt_b.replace(hour=8)
        dt_b = dt_b.replace(minute=0)
        dt_b = dt_b.replace(second=0)
    if dt_b.hour >= 18:
        dt_b = dt_b.replace(hour=18)
        dt_b = dt_b.replace(minute=0)
        dt_b = dt_b.replace(second=0)
    delta = (dt_b - dt_a)

    full_days = int(delta.total_seconds() / (60 * 60 * 24))
    partial_day = min(int(delta.total_seconds() % (60 * 60 * 24)), 60 * 60 * (business_time_end - business_time_start))

    # per full day only count 10 hours
    result = (10 * 60 * 60) * full_days + partial_day

    logging.debug(f"Input time from {dt_a}  to  {dt_b} -> full days: {full_days} + seconds of remaning day {partial_day} = {result} secs or {datetime.timedelta(seconds=result)}")
    return result


def daily_business_time_seconds(business_time_start=8, business_time_end=18):
    return (business_time_end - business_time_start) * 60 * 60