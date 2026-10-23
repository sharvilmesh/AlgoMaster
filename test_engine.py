
import ctypes
from ctypes import c_int, c_size_t, c_longlong, POINTER, Structure

dll = ctypes.CDLL("./algo_engine.dll")


class SortStats(Structure):
    _fields_ = [
        ("comparisons", c_size_t),
        ("swaps", c_size_t),
    ]


# Test the C engine version
dll.algo_master_version.restype = ctypes.c_char_p
print("Engine:", dll.algo_master_version().decode())

# Test insertion sort
dll.insertion_sort.argtypes = [
    POINTER(c_int),
    c_size_t,
    POINTER(SortStats),
]
dll.insertion_sort.restype = c_int

values = (c_int * 6)(9, 3, 7, 1, 5, 2)
stats = SortStats()

success = dll.insertion_sort(values, 6, ctypes.byref(stats))

print("Sort successful:", bool(success))
print("Sorted array:", list(values))
print("Comparisons:", stats.comparisons)
print("Element shifts:", stats.swaps)

assert list(values) == [1, 2, 3, 5, 7, 9]
assert success == 1

print("\nAll insertion-sort tests passed!")
