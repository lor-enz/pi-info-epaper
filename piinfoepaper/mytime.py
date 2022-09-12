import logging
from datetime import datetime as dt
import datetime as datetime
import time
import pytz

TZ_GERMANY = "Europe/Berlin"

# timestamp in seconds
def current_time() -> float:
    return time.time()


def current_time_hr(str_format="%Y-%m-%d_%H:%M:%S"):
    return ts2dt(current_time()).strftime(str_format)


def ts2dt(timestamp, timezone_name=TZ_GERMANY) -> datetime.datetime:
    tz = pytz.timezone(timezone_name)
    # To convert the timestamp to an aware datetime object in the given timezone directly:
    return dt.fromtimestamp(timestamp, tz)


def string2timestamp(time_string, time_format="%Y-%m-%d_%H:%M", timezone_name=TZ_GERMANY):
    logging.debug(f'time_string {time_string} time_format {time_format} timezone_name {timezone_name}')
    try:

        dt_obj = datetime.datetime.strptime(time_string, time_format)
        timezone_obj = pytz.timezone(timezone_name)
        dt_obj = timezone_obj.localize(dt_obj)
        return dt.timestamp(dt_obj)
    except Exception as e:
        logging.error(f'Error in mytime. time_string is {time_string} time_format is {time_format} error message is {e} ')


def weekday_to_german_short(number):
    options = {0: "Mo",
               1: "Di",
               2: "Mi",
               3: "Do",
               4: "Fr",
               5: "Sa",
               6: "So"}
    return options[number]



def string2datetime(time_string, time_format="%Y-%m-%d_%H:%M", timezone_name=TZ_GERMANY):
    return ts2dt(string2timestamp(time_string, time_format, timezone_name))


def seconds2delta(seconds):
    return datetime.timedelta(seconds=seconds)


# Human readable delta, without milliseconds (/microseconds?)
def seconds2delta_hr(seconds):
    return str(datetime.timedelta(seconds=seconds)).split(".")[0]


def is_business_hours(given_timestamp=0, timezone_name=TZ_GERMANY):
    if given_timestamp < 1:
        dt_object = dt.now()
        logging.debug(f'is_business_hours() created dt_object: {dt_object}')
    else:
        dt_object = dt.fromtimestamp(given_timestamp)

    tz = pytz.timezone(timezone_name)
    # Careful, this requires the raspi to be set to the German timezone
    dt_object = tz.normalize(tz.localize(dt_object))
    if dt_object.hour == 18 and dt_object.minute < 9:
        return True
    if dt_object.hour == 7 and dt_object.minute > 30:
        return True
    if dt_object.hour == 6 and dt_object.minute > 30:
        return True
    return 7 < dt_object.hour < 18


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

    logging.debug(
        f"Input time from {dt_a}  to  {dt_b} -> full days: {full_days} + seconds of remaning day {partial_day} = {result} secs or {datetime.timedelta(seconds=result)}")
    return result


def daily_business_time_seconds(business_time_start=8, business_time_end=18):
    return (business_time_end - business_time_start) * 60 * 60
