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
        checker.get_average_daily_vaccs_of_last_days(7)
        self.assertEqual('foo'.upper(), 'FOO')

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


if __name__ == '__main__':
    unittest.main()
