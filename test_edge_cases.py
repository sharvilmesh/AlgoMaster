import unittest
from engine import profile, recommend_sort, recommend_search

class TestEdgeCases(unittest.TestCase):
    def test_single_element_sort_recommendation(self):
        result = recommend_sort(profile([7]))
        self.assertTrue(result["recommended"])
        self.assertIsInstance(result["alternatives"], list)

    def test_single_element_search_recommendation(self):
        result = recommend_search(profile([7]), False, 1, 0)
        self.assertIn(result["recommended"].split(" (")[0], ["Linear Search", "Binary Search"])

    def test_search_recommendation_with_repeated_values(self):
        result = recommend_search(profile([2, 2, 2, 2]), False, 100, 0)
        self.assertIn(result["recommended"].split(" (")[0], ["Linear Search", "Binary Search"])

if __name__ == "__main__":
    unittest.main()
