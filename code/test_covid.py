import unittest


class TestChecker(unittest.TestCase):

    def test_fix(self):
        from covid import Databook
        databook = Databook()
        databook.fix_comma_in_csv("infe.csv")
        self.assertLess(1, 70000)

    def test_get_inz_munich(self):
        from covid import Databook
        databook = Databook()
        inz = databook.get_inz_munich()

    def test_get_inz_bavaria(self):
        from covid import Databook
        databook = Databook()
        inz = databook.get_inz_bavaria()
        print(f'got inz: {(inz)}')

    def test_get_current_abs_doses(self):
        from covid import Databook
        databook = Databook()
        doses = databook.get_current_abs_doses()
        self.assertGreater(doses, 1500000)

    def test_get_extrapolated_abs_doses(self):
        from covid import Databook
        databook = Databook()
        total_vaccs = databook.get_extrapolated_abs_doses()
        print(f"total_vaccs {total_vaccs}")
        self.assertGreater(total_vaccs, int(databook.get_current_abs_doses()))

    def test_get_average_daily_vaccs_of_last_days(self):
        from covid import Databook
        databook = Databook()
        mean = databook.get_average_daily_vaccs_of_last_days(7)
        print(f"mean: {mean}")
        self.assertGreater(mean, 30000)
        self.assertLess(mean, 70000)

    def test_extrapolate(self):
        from covid import Databook
        databook = Databook()

        self.assertEqual(databook.extrapolate(50000, 360000), 50000)
        self.assertEqual(databook.extrapolate(50000, 36000), 50000)
        self.assertEqual(databook.extrapolate(50000, 18000), 25000)


if __name__ == '__main__':
    unittest.main()
