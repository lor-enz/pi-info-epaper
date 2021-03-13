import unittest


class TestChecker(unittest.TestCase):

    def test_get_extrapolated_abs_doses(self):
        from covid import Checker
        checker = Checker()
        total_vaccs = checker.get_extrapolated_abs_doses()
        print(f"total_vaccs {total_vaccs}")
        self.assertGreater(total_vaccs, int(checker.get_current_abs_doses()[
                           "vaccinated_abs"]))

    def test_get_average_daily_vaccs_of_last_days(self):
        from covid import Checker
        checker = Checker()
        mean = checker.get_average_daily_vaccs_of_last_days(7)
        print(f"mean: {mean}")
        self.assertGreater(mean, 30000)
        self.assertLess(mean, 70000)

    def test_extrapolate(self):
        from covid import Checker
        checker = Checker()

        self.assertEqual(checker.extrapolate(50000, 360000), 50000)
        self.assertEqual(checker.extrapolate(50000, 36000), 50000)
        self.assertEqual(checker.extrapolate(50000, 18000), 25000)


if __name__ == '__main__':
    unittest.main()
