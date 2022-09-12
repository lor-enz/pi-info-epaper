from enum import Enum

class Alignment(Enum):
    TOP_LEFT = 0,
    BOTTOM_LEFT = 1,
    TOP_RIGHT = 2,
    BOTTOM_RIGHT = 3,
    CENTERED = 4,
    BOTTOM_CENTER = 5,
    TOP_CENTER = 6


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