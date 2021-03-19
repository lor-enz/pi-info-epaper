import unittest

class TestTimeTool(unittest.TestCase):

    def test_paper_demo(self):
        from paper_demo import Paper
        paper = Paper()
        paper.demo()

    def test_paper_init(self):
        from paper import Paper
        paper = Paper()
        print(paper)
