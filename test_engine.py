import ctypes
import unittest
from ctypes import c_int, c_size_t, POINTER, Structure


class SortStats(Structure):
    _fields_ = [
        ("comparisons", c_size_t),
        ("swaps", c_size_t),
    ]


class TestCEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dll = ctypes.CDLL("./algo_engine.dll")
        cls.dll.algo_master_version.restype = ctypes.c_char_p
        cls.dll.insertion_sort.argtypes = [
            POINTER(c_int),
            c_size_t,
            POINTER(SortStats),
        ]
        cls.dll.insertion_sort.restype = c_int

    def test_engine_version(self):
        self.assertEqual(
            self.dll.algo_master_version().decode(),
            "Algo Master C Engine 1.0",
        )

    def test_insertion_sort(self):
        values = (c_int * 6)(9, 3, 7, 1, 5, 2)
        stats = SortStats()

        success = self.dll.insertion_sort(
            values, 6, ctypes.byref(stats)
        )

        self.assertEqual(success, 1)
        self.assertEqual(list(values), [1, 2, 3, 5, 7, 9])
        self.assertGreater(stats.comparisons, 0)
        self.assertGreater(stats.swaps, 0)

    def test_empty_array_rejected(self):
        values = (c_int * 1)(0)
        stats = SortStats()

        success = self.dll.insertion_sort(
            values, 0, ctypes.byref(stats)
        )

        self.assertEqual(success, 0)


if __name__ == "__main__":
    unittest.main()
