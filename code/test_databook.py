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



if __name__ == "__main__":
    unittest.main()
