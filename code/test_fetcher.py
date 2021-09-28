import unittest


class TestFetcher(unittest.TestCase):



    def test_download(self):
        import fetcher as ff
        fetcher = ff.Fetcher()
        fetcher.download_all_data()

        fetcher.save_storage()
        another_fetcher = ff.Fetcher()
        another_fetcher.load_storage()
        self.assertEqual(9, int(fetcher.bl_id))
        self.assertEqual(9, int(another_fetcher.bl_id))


if __name__ == "__main__":
    unittest.main()
