import logging
import unittest




class TestPaperController(unittest.TestCase):




    def test_basics(self):
        logging.basicConfig(level=logging.INFO)
        logging.info("Hi logged")
        from piinfoepaper import mytime
        import paper_controller as pc
        from paper_layout import Orientation, PaperLayout
        from paper_elements import PaperTextElement, PaperImageElement
        from paper_enums import Alignment, Fill
        # from piinfoepaper.paper_elements import PaperTextPartialElement, PaperImagePartialElement

        text_elements = [
            PaperTextElement(480, 280, Alignment.BOTTOM_RIGHT, Fill.GRAY4, "Hi, World in bottom right", 30),
            PaperTextElement(240, 140, Alignment.CENTERED, Fill.GRAY4, "Center", 30),
            PaperTextElement(480, 0, Alignment.TOP_RIGHT, Fill.GRAY4, f'{mytime.current_time_hr("%d %b %H:%M")}', 12)
        ]

        image_elements = [
            PaperImageElement(0, 60, Alignment.TOP_LEFT, Fill.GRAY4, 'ampel-green-small.bmp')
        ]

        layout = PaperLayout(Orientation.LANDSCAPE_FLIPPED, text_elements, image_elements, None, None)
        controller = pc.PaperController(layout)


if __name__ == "__main__":
    unittest.main()
