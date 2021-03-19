import unittest


class TestDatabook(unittest.TestCase):

    def test_basics(self):
        import databook as db
        book = db.Databook()
