
import ctypes
from ctypes import c_int, c_size_t, c_longlong, POINTER, Structure
from pathlib import Path


class SortStats(Structure):
    _fields_ = [
        ("comparisons", c_size_t),
        ("swaps", c_size_t),
    ]


_dll_path = Path(__file__).with_name("algo_engine.dll")
_dll = ctypes.CDLL(str(_dll_path))

_dll.algo_master_version.restype = ctypes.c_char_p

_dll.insertion_sort.argtypes = [
    POINTER(c_int),
    c_size_t,
    POINTER(SortStats),
]
_dll.insertion_sort.restype = c_int


def version():
    return _dll.algo_master_version().decode("utf-8")


def insertion_sort(values):
    """Sort integers using the C implementation."""
    values = list(values)

    if not values:
        return {
            "sorted": [],
            "comparisons": 0,
            "shifts": 0,
        }

    if any(not isinstance(x, int) for x in values):
        raise TypeError("All values must be integers.")

    array_type = c_int * len(values)
    c_array = array_type(*values)
    stats = SortStats()

    success = _dll.insertion_sort(
        c_array,
        len(values),
        ctypes.byref(stats),
    )

    if not success:
        raise RuntimeError("C insertion sort failed.")

    return {
        "sorted": list(c_array),
        "comparisons": stats.comparisons,
        "shifts": stats.swaps,
    }
