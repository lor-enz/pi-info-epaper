
from typing import List

from piinfoepaper.paper_elements import PaperImageElement, PaperTextElement, PaperTextPartialElement, PaperImagePartialElement
from piinfoepaper.paper_enums import Orientation


class PaperLayout:

    def __init__(self, orientation: Orientation, font_path: str, text_elements: List[PaperTextElement], image_elements: List[PaperImageElement],
                 partial_text_element: PaperTextPartialElement, partial_image_element: PaperImagePartialElement):
        self.orientation = orientation
        self.font_path = font_path
        self.text_elements = text_elements
        self.image_elements = image_elements
        self.partial_text_element = partial_text_element
        self.partial_image_element = partial_image_element

        
