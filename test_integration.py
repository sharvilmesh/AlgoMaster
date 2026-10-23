from engine import profile, recommend_sort
from c_engine import insertion_sort, version

values = [42, 7, 19, 3, 56, 28, 11]

# Existing Python recommendation logic
p = profile(values)
recommendation = recommend_sort(p)

# Native C implementation
result = insertion_sort(values)

print("C engine:", version())
print("Recommendation:", recommendation["recommended"])
print("Original data:", values)
print("C sorted data:", result["sorted"])
print("Comparisons:", result["comparisons"])
print("Element shifts:", result["shifts"])

assert result["sorted"] == sorted(values)
assert values == [42, 7, 19, 3, 56, 28, 11]

print("\nIntegration test passed!")