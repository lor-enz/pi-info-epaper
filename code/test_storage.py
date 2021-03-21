import unittest


class TestTimeTool(unittest.TestCase):
    filename = "pi-paper-test-storage.json"

    def test_store(self):
        import os
        from storage import store
        penguin = {
            'name': 'Flake',
            'height': 80,
            'timestamp': 1616061456,
        }
        filename = self.filename
        store(filename, penguin)

        exists = os.path.isfile(filename)
        self.assertEqual(exists, True)
        os.remove(filename)

    def test_store_and_load(self):
        import os
        from storage import store, retrieve
        penguin = {
            'name': 'Flake',
            'height': 80,
            'timestamp': 1616061456,
        }
        filename = self.filename
        store(filename, penguin)

        exists = os.path.isfile(filename)
        self.assertEqual(exists, True)

        retrieved = retrieve(filename)

        self.assertEqual(retrieved['name'], penguin['name'])
        self.assertEqual(retrieved['height'], penguin['height'])
        self.assertEqual(retrieved['timestamp'], penguin['timestamp'])

        os.remove(filename)

    def test_overwrite(self):
        from storage import store, retrieve
        filename = self.filename
        penguin1 = {
            'name': 'Flake',
            'height': 80,
            'timestamp': 1616061456,
        }
        store(filename, penguin1)
        penguin2 = {
            'name': 'Rico',
            'height': 90,
            'timestamp': 1616061500,
        }
        store(filename, penguin2)

        retrieved = retrieve(filename)

        self.assertEqual(retrieved['name'], penguin2['name'])
        self.assertEqual(retrieved['height'], penguin2['height'])
        self.assertEqual(retrieved['timestamp'], penguin2['timestamp'])

        import os
        os.remove(filename)


if __name__ == "__main__":
    unittest.main()
