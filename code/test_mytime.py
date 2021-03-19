import unittest


class TestTimeTool(unittest.TestCase):

    def test_timezones_and_stuff(self):
        import mytime as tt
        self.assertEqual(1615359000, tt.dt2ts("2021-03-10_07:50"))
        self.assertEqual(1329498733, tt.dt2ts("2012-02-17_18:12:13", time_format="%Y-%m-%d_%H:%M:%S"))
        self.assertNotEqual(
            tt.dt2ts("2021-03-01_15:00", timezone_name="America/New_York"),
            tt.dt2ts("2021-03-01_15:00", timezone_name="Europe/Vienna"))
        self.assertEqual(1614628800, tt.dt2ts("2021-03-01_15:00", timezone_name="America/New_York"))

    def test_is_business_hours(self):
        import mytime as tt
        self.assertEqual(True, tt.is_business_hours(1616057856))
        self.assertEqual(False, tt.is_business_hours(1616043400))
        self.assertEqual(False, tt.is_business_hours(1616045400))

    def test_current_time(self):
        import mytime as tt
        tt.current_time()

    def test_seconds2delta(self):
        import mytime as tt
        self.assertEqual("0:01:00", str(tt.seconds2delta(60)))
        self.assertEqual("1:01:00", str(tt.seconds2delta(60*60 + 60)))

    def test_business_time_since(self):
        from mytime import business_time_since
        import mytime as tt
        result = business_time_since(1615791600, 1615885200)
        self.assertEqual(12 * 60 * 60, result)

        result = business_time_since(1615791600, 1615874400)
        self.assertEqual(10 * 60 * 60, result)

        result = business_time_since(1615791600, 1615806000)
        self.assertEqual(4 * 60 * 60, result)

        result = business_time_since(1615791600, 1615964405)
        self.assertEqual(20 * 60 * 60 + 5, result)

        result = business_time_since(tt.dt2ts("2021-03-10_07:50"), tt.dt2ts("2021-03-10_07:51"))
        self.assertEqual(0, result)

        result = business_time_since(tt.dt2ts("2021-03-10_17:55"), tt.dt2ts("2021-03-10_18:05"))
        self.assertEqual(5*60, result)
