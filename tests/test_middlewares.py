import unittest

from routes.middlewares import remove_search_hash_from_url


class TestRulesRoutes(unittest.TestCase):
    def test_remove_search_hash_from_url(self):
        main_url = "https://test.com/segment"
        full_url = main_url + "?query=value#something"
        result = remove_search_hash_from_url(full_url)
        self.assertEqual(result, main_url)
