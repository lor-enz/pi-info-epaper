import unittest


class TestWeather(unittest.TestCase):

    def test_dry_run(self):
        from databook import Databook
        db = Databook()
        self.assertIsNotNone(db.day_date)
        self.assertTrue(-200 <= db.temp_min <= 500)
        self.assertTrue(-200 <= db.temp_max <= 500)
        self.assertTrue(0 <= db.icon1 <= 31)
        self.assertTrue(0 <= db.icon2 <= 31)


if __name__ == "__main__":
    unittest.main()
