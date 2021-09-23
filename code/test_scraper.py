import unittest


class TestScraper(unittest.TestCase):

    def test_download(self):
        import scraper as ss
        scraper = ss.Scraper()
        scraper.download()
        self.assertLess(1609455600, scraper.ampel_download_timestamp)

if __name__ == "__main__":
    unittest.main()
