import unittest


class TestDatabook(unittest.TestCase):

    def test_basics(self):
        import databook as db
        db.Databook()

    def test_inz(self):
        import databook as db
        book = db.Databook()

        inz = book.get_munich_inc()
        print(f'Munich Incidence: {inz}')
        self.assertGreater(inz[0], 0)

        inz = book.get_miesbach_inc()
        print(f'Miesbach Incidence: {inz}')
        self.assertGreater(inz[0], 0)

        inz = book.get_bavaria_inc()
        print(f'Bavaria Incidence: {inz}')
        self.assertGreater(inz[0], 0)

    def test_hosp_and_icu(self):
        import databook as db
        book = db.Databook()

        icu = book.get_bavaria_icu()
        hosp = book.get_bavaria_hospital()

    def test_vax(self):
        import databook as db
        book = db.Databook()

        vax = book.get_bavaria_vax()

    def test_evaluate_freshness(self):
        import databook as db
        book = db.Databook()
        district_ts = '2021-11-17T00:00:00.000Z'
        print(book.evaluate_freshness(district_ts))

if __name__ == "__main__":
    unittest.main()
