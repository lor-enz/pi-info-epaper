import unittest


class TestDataprep(unittest.TestCase):

    def test_trend(self):
        import dataprep as dp
        self.assertEqual(dp.trend(100.0, 90.0), dp.Trend.DOWN_STRONG)
        self.assertEqual(dp.trend(100.0, 99.0), dp.Trend.STEADY)
        self.assertEqual(dp.trend(100.0, 97.0), dp.Trend.DOWN)
        self.assertEqual(dp.trend(100.0, 104.0), dp.Trend.UP)
        self.assertEqual(dp.trend(100.0, 110.0), dp.Trend.UP_STRONG)







if __name__ == "__main__":
    unittest.main()
