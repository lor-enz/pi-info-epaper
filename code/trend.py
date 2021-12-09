from enum import Enum


class Trend(Enum):
    UP = "UP"
    DOWN = "DOWN"
    STEADY = "STEADY"
    UP_STRONG = "UP_STRONG"
    DOWN_STRONG = "DOWN_STRONG"
    UNKNOWN = "UNKNOWN"


def trend(previous, current):
    dif = current - previous
    percentage = round(dif / current, 2)

    if percentage < -0.05:
        t = Trend.DOWN_STRONG
    elif percentage < -0.01:
        t = Trend.DOWN
    elif percentage < 0.01:
        t = Trend.STEADY
    elif percentage < 0.05:
        t = Trend.UP
    else:
        t = Trend.UP_STRONG
    print(f'Prev: {previous}   Now: {current}  --> {t} ({percentage})')
    return t