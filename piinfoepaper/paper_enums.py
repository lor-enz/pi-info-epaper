from enum import Enum


class Alignment(Enum):
    TOP_LEFT = 0,
    TOP_CENTER = 2
    TOP_RIGHT = 3,
    RIGHT_CENTER = 4,
    BOTTOM_RIGHT = 5,
    BOTTOM_CENTER = 6,
    BOTTOM_LEFT = 7,
    LEFT_CENTER = 8,
    CENTERED = 9,


class Fill(Enum):
    GRAY1 = 1,
    GRAY2 = 2,
    GRAY3 = 3,
    GRAY4 = 4,
    # 4 is black


class Orientation(Enum):
    LANDSCAPE = 1,
    PORTRAIT = 2,
    LANDSCAPE_FLIPPED = -1,
    PORTRAIT_FLIPPED = -2,
