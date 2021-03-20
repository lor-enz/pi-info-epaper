import unittest

class TestTimeTool(unittest.TestCase):

    def test_paper_demo(self):
        from paper_demo import Paper
        paper = Paper()
        paper.demo()

    def test_paper_init(self):
        import databook as db
        import paper as pap
        book = db.Databook()
        paper = pap.Paper(book)
        print(paper)
