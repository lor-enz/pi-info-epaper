import unittest


class TestPaper(unittest.TestCase):

    def test_paper_init(self):
        import databook as db
        import paper as pap
        book = db.Databook()
        paper = pap.Paper(book)
        print(paper)

    def test_paper_demo(self):
        from paper_demo import Paper
        paper = Paper()
        paper.demo()

    def test_paper_covid_once(self):
        import databook as db
        from paper import Paper
        book = db.Databook()
        paper = Paper(book)
        paper.maybe_refresh_all_covid_data()

    def test_paper_covid_continuous(self):
        import databook as db
        from paper import Paper
        book = db.Databook()
        paper = Paper(book)
        paper.maybe_refresh_all_covid_data()
        paper.partial_refresh_vacc_for_minutes(2)

    def test_paper_clear(self):
        from paper_demo import Paper
        paper = Paper()
        paper.clear()


if __name__ == "__main__":
    unittest.main()
