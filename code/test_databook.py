import unittest


class TestDatabook(unittest.TestCase):

    def test_basics(self):
        import databook as db
        book = db.Databook()

    def test_inz(self):
        import databook as db
        book = db.Databook()
        inz_bav = book.get_inz_bavaria()
        inz_muc = book.get_inz_munich()
        print(f'Bavaria Incidence: {inz_bav}')
        print(f'Munich  Incidence: {inz_muc}')
        self.assertGreater(float(inz_bav[0]), 0)
        self.assertGreater(float(inz_muc[0]), 0)

    def test_vac_official(self):
        import databook as db
        book = db.Databook()
        official_doses = book.get_official_abs_doses()
        print(f'Official Doses in bavaria: {official_doses}')
        self.assertGreater(official_doses, 1700000)
        self.assertLess(official_doses, 30 * 1000000)

    def test_vac_extrapo(self):
        import databook as db
        book = db.Databook()
        all_doses = book.get_extrapolated_abs_doses()
        print(f'All Doses in bavaria: {all_doses}')
        self.assertGreater(float(all_doses[0].replace('.','')), 1700000)
        self.assertLess(float(all_doses[0].replace('.','')), 30 * 1000000)