    
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>

#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API
#endif

typedef struct {
    size_t comparisons;
    size_t swaps;
} SortStats;

API const char *algo_master_version(void) {
    return "Algo Master C Engine 1.0";
}

API int profile_array(
    const int *arr,
    size_t n,
    long long *inversions,
    size_t *distinct_count,
    int *is_sorted
) {
    if (arr == NULL || n == 0 ||
        inversions == NULL ||
        distinct_count == NULL ||
        is_sorted == NULL) {
        return 0;
    }

    int *copy = malloc(n * sizeof(int));
    int *temp = malloc(n * sizeof(int));

    if (copy == NULL || temp == NULL) {
        free(copy);
        free(temp);
        return 0;
    }

    for (size_t i = 0; i < n; i++) {
        copy[i] = arr[i];
        temp[i] = arr[i];
    }

    long long inv = 0;
    size_t distinct = 0;
    int sorted = 1;

    for (size_t i = 1; i < n; i++) {
        if (arr[i - 1] > arr[i]) {
            sorted = 0;
        }
    }

    /* Count inversions using merge sort. */
    for (size_t width = 1; width < n; ) {
        for (size_t left = 0; left < n; left += 2 * width) {
            size_t mid = left + width;
            size_t right = left + 2 * width;

            if (mid > n) mid = n;
            if (right > n) right = n;

            size_t i = left, j = mid, k = left;

            while (i < mid && j < right) {
                if (copy[i] <= copy[j]) {
                    temp[k++] = copy[i++];
                } else {
                    temp[k++] = copy[j++];
                    inv += (long long)(mid - i);
                }
            }

            while (i < mid) temp[k++] = copy[i++];
            while (j < right) temp[k++] = copy[j++];
        }

        int *swap_buffer = copy;
        copy = temp;
        temp = swap_buffer;

        if (width > n / 2) break;
        width *= 2;
    }

    /* Count distinct values from the sorted copy. */
    distinct = 1;
    for (size_t i = 1; i < n; i++) {
        if (copy[i] != copy[i - 1]) {
            distinct++;
        }
    }

    *inversions = inv;
    *distinct_count = distinct;
    *is_sorted = sorted;

    free(copy);
    free(temp);
    return 1;
}

API int insertion_sort(int *arr, size_t n, SortStats *stats) {
    if (arr == NULL || n == 0 || stats == NULL) {
        return 0;
    }

    stats->comparisons = 0;
    stats->swaps = 0;

    for (size_t i = 1; i < n; i++) {
        int key = arr[i];
        size_t j = i;

        while (j > 0) {
            stats->comparisons++;

            if (arr[j - 1] <= key) {
                break;
            }

            arr[j] = arr[j - 1];
            stats->swaps++;
            j--;
        }

        arr[j] = key;
    }

    return 1;
}
