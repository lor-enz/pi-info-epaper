import unittest


class TestFetcher(unittest.TestCase):

    def test_storage(self):
        import fetcher as ff
        fetcher = ff.Fetcher()

        fetcher.inf_download_timestamp = 133742
        fetcher.vac_download_timestamp = 1337

        fetcher.save_storage()
        another_fetcher = ff.Fetcher()
        self.assertEqual(0, another_fetcher.inf_download_timestamp)
        self.assertEqual(0, another_fetcher.vac_download_timestamp)
        another_fetcher.load_storage()
        self.assertEqual(133742, another_fetcher.inf_download_timestamp)
        self.assertEqual(1337, another_fetcher.vac_download_timestamp)

    def test_download(self):
        import fetcher as ff
        fetcher = ff.Fetcher()
        fetcher.download_all_data()
        self.assertLess(1609455600, fetcher.inf_download_timestamp)
        self.assertLess(1609455600, fetcher.vac_download_timestamp)
        fetcher.save_storage()
        another_fetcher = ff.Fetcher()
        another_fetcher.load_storage()
        self.assertEqual(fetcher.vac_download_timestamp, another_fetcher.vac_download_timestamp)
        self.assertEqual(fetcher.inf_download_timestamp, another_fetcher.inf_download_timestamp)