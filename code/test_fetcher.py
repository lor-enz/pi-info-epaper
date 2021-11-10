import time
import unittest


class TestFetcher(unittest.TestCase):

    def test_download(self):
        import fetcher as ff
        fetcher = ff.Fetcher()
        fetcher.get_relevant_data()
        fetcher.save_storage()
        time.sleep(2)
        another_fetcher = ff.Fetcher()
        result = another_fetcher.get_relevant_data_if_needed()
        self.assertEqual(False, result)


if __name__ == "__main__":
    unittest.main()
