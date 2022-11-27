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

    def test_get_temp(self):
        from databook import Databook
        db = Databook(False)
        # MIN
        self.assertEqual("23.4°", db.get_temp_min_string(234))
        self.assertEqual("-23.4°", db.get_temp_min_string(-234))
        self.assertEqual("2.2°", db.get_temp_min_string(22))
        self.assertEqual("-2.2°", db.get_temp_min_string(-22))
        self.assertEqual("0.6°", db.get_temp_min_string(6))
        self.assertEqual("-0.6°", db.get_temp_min_string(-6))
        self.assertEqual("0.0°", db.get_temp_min_string(0))

        # MAX
        self.assertEqual("23.4°", db.get_temp_max_string(234))
        self.assertEqual("-23.4°", db.get_temp_max_string(-234))
        self.assertEqual("2.2°", db.get_temp_max_string(22))
        self.assertEqual("-2.2°", db.get_temp_max_string(-22))
        self.assertEqual("0.6°", db.get_temp_max_string(6))
        self.assertEqual("-0.6°", db.get_temp_max_string(-6))
        self.assertEqual("0.0°", db.get_temp_max_string(0))


if __name__ == "__main__":
    unittest.main()
