import unittest
from engine import profile, recommend_sort
from c_engine import insertion_sort, version


class TestAlgorithmIntegration(unittest.TestCase):
    def test_c_engine_version(self):
        self.assertEqual(version(), "Algo Master C Engine 1.0")

    def test_c_sort_matches_python_sorted(self):
        values = [42, 7, 19, 3, 56, 28, 11]
        result = insertion_sort(values)

        self.assertEqual(result["sorted"], sorted(values))
        self.assertEqual(values, [42, 7, 19, 3, 56, 28, 11])

    def test_empty_array_rejected_by_profile(self):
        with self.assertRaisesRegex(
            ValueError, "Input array must contain at least one integer."
        ):
            profile([])

    def test_recommendation_and_c_sort(self):
        values = [42, 7, 19, 3, 56, 28, 11]
        recommendation = recommend_sort(profile(values))

        self.assertIn("recommended", recommendation)
        self.assertTrue(recommendation["recommended"])
        self.assertEqual(insertion_sort(values)["sorted"], sorted(values))


if __name__ == "__main__":
    unittest.main()

