from paper_enums import Alignment, Fill


class PaperElement:

    def __init__(self, x_pos: int, y_pos: int, alignment: Alignment, fill: Fill):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.xy = (x_pos, y_pos)
        self.alignment = alignment
        self.fill = fill

    def __str__(self):
        return f"Paperelement ({self.x_pos}, {self.y_pos}) Aligned {self.alignment}"


class PaperTextElement(PaperElement):

    def __init__(self, x_pos: int, y_pos: int, alignment: Alignment, fill: Fill, text: str, font_size: int):
        super().__init__(x_pos, y_pos, alignment, fill)
        self.text = text
        self.font_size = font_size

    def __str__(self):
        return f"{super(PaperTextElement, self).__str__()} text (fontsize {self.font_size}): {self.text}"

class PaperTextPartialElement(PaperTextElement):
    pass
    # TODO init
    # use superclass text field for default text


class PaperImageElement(PaperElement):

    def __init__(self, x_pos, y_pos, alignment: Alignment, image_path: str):
        super().__init__(x_pos, y_pos, alignment, Fill.GRAY4)
        self.image_path = image_path

    def __str__(self):
        return f"{super(PaperImageElement, self).__str__()} image {self.image_path}"

class PaperImagePartialElement(PaperImageElement):
    pass
    # TODO init
    # use superclass image field for default image
