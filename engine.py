"""Python port of the C recommender (2.c). Algorithm catalog + cost factors live in algorithms.json."""
import json, math
from collections import Counter
from pathlib import Path

CFG = json.loads(Path(__file__).with_name("algorithms.json").read_text(encoding="utf-8"))
A, F = CFG["algorithms"], CFG["factors"]
INS, BUB, SEL, MRG, QCK, HEP = range(6)
nm = lambda i: A[i]["name"]

def _merge_count(a):                       # merge sort that also counts inversions
    if len(a) < 2: return a, 0
    m = len(a) // 2
    l, x = _merge_count(a[:m]); r, y = _merge_count(a[m:])
    out, i, j, c = [], 0, 0, x + y
    while i < len(l) and j < len(r):
        if l[i] <= r[j]: out.append(l[i]); i += 1
        else: out.append(r[j]); j += 1; c += len(l) - i
    return out + l[i:] + r[j:], c

def profile(a):                            # = compute_metrics()
    if not a:
        raise ValueError("Input array must contain at least one integer.")

    n = len(a)
    asc = sum(a[i] <= a[i + 1] for i in range(n - 1)); desc = sum(a[i] >= a[i + 1] for i in range(n - 1))
    s, inv = _merge_count(a); cnt = Counter(s)
    return {"n": n, "min": s[0], "max": s[-1], "asc_pct": 100 * asc / (n - 1) if n > 1 else 100.0,
            "desc_pct": 100 * desc / (n - 1) if n > 1 else 100.0, "inversions": inv,
            "max_inversions": n * (n - 1) / 2, "distinct": len(cnt), "dup_pct": 100 * (n - len(cnt)) / n,
            "equal_pairs": sum(k * (k - 1) / 2 for k in cnt.values()), "sorted": inv == 0}

def cost(p, i):                            # = estimate_cost()
    n = p["n"]; L = n * math.log2(n); q = n * (n - 1) / 2
    if i == INS: return (n - 1) + 2 * p["inversions"]
    if i == BUB: return n - 1 if p["inversions"] == 0 else q + p["inversions"]
    if i == SEL: return q + n
    if i == MRG: return F["merge"] * L
    if i == QCK: return F["quick"] * L + p["equal_pairs"]
    return F["heap"] * L

def eligible(is_list, stable, mem, worst):  # = check_eligible()
    ok, why = [True] * 6, [""] * 6
    for i in range(6):
        if is_list and i in (HEP, QCK): ok[i], why[i] = False, "needs index access, a linked list allows only node by node walk"
        if ok[i] and stable and not A[i]["stable"]: ok[i], why[i] = False, "not stable (equal elements may change order)"
        if ok[i] and mem and not is_list and i == MRG: ok[i], why[i] = False, "needs an extra O(n) array, but memory is tight"
        if ok[i] and worst and not A[i]["worst_nlogn"]: ok[i], why[i] = False, "worst case is O(n^2), no O(n log n) guarantee"
    return ok, why

def _row(i): return {"Algorithm": nm(i), "Best Ω": A[i]["best"], "Average Θ": A[i]["avg"], "Worst O": A[i]["worst"], "Extra space": A[i]["space"]}

def _why_sort(p, win, c, ok, is_list, stable, worst, mem, allowed):
    n, inv, w = p["n"], p["inversions"], []
    w.append(f"Estimated work: about {c[win]:.0f} steps for n = {n}, the lowest of the {allowed} allowed algorithms.")
    nl = [i for i in (MRG, QCK, HEP) if ok[i]]; bn = min(nl, key=lambda i: c[i]) if nl else None
    if win == INS:
        w.append(f"Insertion Sort needs about (n - 1) + 2 x inversions steps. Here inversions are only {inv}, so it stays cheap.")
        if p["sorted"]: w.append("The data is already sorted: one pass just confirms it.")
        if bn is not None and c[bn] > c[win]: w.append(f"The best O(n log n) sort ({nm(bn)}) would need about {c[bn]:.0f} steps, {c[bn]/c[win]:.1f} times more.")
        if n <= 30: w.append(f"With only {n} elements, an n log n algorithm saves very little.")
    elif win == QCK:
        w += ["Among the O(n log n) sorts it is the fastest in practice: in place, cache-friendly.",
              f"The simple O(n^2) sorts need far more (Insertion Sort: about {c[INS]:.0f} steps) because the data has {inv} inversions.",
              f"Repeated values are limited ({p['equal_pairs']:.0f} equal pairs), so Quick Sort's weakness with duplicates does not hurt.",
              "Its O(n^2) worst case is unlikely because the pivot is the middle element."]
    elif win == MRG:
        if is_list: w.append("On a linked list, Merge Sort needs no extra array and only walks node by node.")
        if stable: w.append("It is stable: equal elements keep their order (you asked for this).")
        if worst: w.append("It guarantees O(n log n) even in the worst case (you asked for this).")
        if ok[QCK] and c[QCK] > c[MRG]: w.append(f"Quick Sort would cost about {c[QCK]:.0f} steps: {p['equal_pairs']:.0f} equal pairs slow its partitioning.")
        if not is_list: w.append(f"Price to pay: an extra array of {n} ints (about {n*4/1048576:.2f} MB).")
    elif win == HEP:
        w.append("Its worst case is O(n log n) and it needs only O(1) extra memory.")
        if mem and worst: w.append("Exactly what you asked for (tight memory + guaranteed worst case).")
    elif win == SEL:
        w += [f"The data is heavily out of order ({100*inv/p['max_inversions']:.1f}% of pairs inverted) and n is small, so Insertion Sort would shift many elements.",
              f"Selection Sort does at most n - 1 = {n-1} swaps, so it moves very little data."]
    else:
        w.append(f"The data is tiny (n = {n}), so all algorithms cost almost the same; Bubble Sort's early exit needs only about {c[win]:.0f} steps.")
    return w

def recommend_sort(p, is_list=False, stable=False, worst=False, mem=False):
    c = [cost(p, i) for i in range(6)]
    s0, w0, m0 = stable, worst, mem
    ok, why = eligible(is_list, stable, mem, worst); relaxed = []
    if not any(ok) and mem:   mem = False;   ok, why = eligible(is_list, stable, mem, worst); relaxed.append("memory tight")
    if not any(ok) and worst: worst = False; ok, why = eligible(is_list, stable, mem, worst); relaxed.append("worst-case guarantee")
    if not any(ok) and stable: stable = False; ok, why = eligible(is_list, stable, mem, worst); relaxed.append("stability")
    allowed = sum(ok); win = min((i for i in range(6) if ok[i]), key=lambda i: c[i])
    order = sorted(range(6), key=lambda i: (not ok[i], c[i]))
    fok, _ = eligible(is_list, False, False, False); fbest = min((i for i in range(6) if fok[i]), key=lambda i: c[i])
    alts = [
        {
            "algorithm": nm(t),
            "times_work": round(c[t] / c[win], 1) if c[win] > 0 else (1.0 if c[t] == 0 else float("inf")),
            "trade_off": A[t]["trade_off"],
        }
        for t in order[1:3]
        if ok[t] and allowed > 1
    ]
    return {"kind": "Sorting", "title": f"Sorting | n={p['n']} | {nm(win)}",
            "constraints": f"storage = {'linked list' if is_list else 'array'} | stable = {s0} | memory tight = {m0} | worst-case guarantee = {w0}",
            "note": ("Your constraints contradict each other. Relaxed: " + ", ".join(relaxed)) if relaxed else "",
            "warning": f"Constraints leave only slow options: {nm(win)} needs about {c[win]:.0f} steps vs {nm(fbest)} about {c[fbest]:.0f} without them." if c[win] > 3 * c[fbest] else "",
            "recommended": nm(win), "data_structure": "Linked list (as chosen)" if is_list else "Array",
            "why": _why_sort(p, win, c, ok, is_list, stable, worst, mem, allowed),
            "complexity": [_row(win)], "properties": f"Stable: {'Yes' if A[win]['stable'] else 'No'} | In-place: {'Yes' if A[win]['inplace'] else 'No'}",
            "ranking": [{"Algorithm": nm(t), "Est. steps": round(c[t]), "Status": "allowed" if ok[t] else "ELIMINATED: " + why[t]} for t in order],
            "alternatives": alts, "alt_note": "" if alts else "None: every other algorithm was eliminated by your constraints."}

def recommend_search(p, is_list, Q, U=0):
    n = p["n"]; per_lin = (n + 1) / 2; per_bin = math.log2(n + 1); lin = Q * per_lin
    c = [cost(p, i) for i in range(6)]; best = min(range(6), key=lambda i: c[i])
    sc = 0 if p["sorted"] else c[best]; upkeep = U * n / 2; binary = sc + Q * per_bin + upkeep
    use_bin = (not is_list) and binary < lin; w = []
    if is_list: w.append("Binary Search must jump to the middle element; a linked list cannot do that, so every step would still walk node by node.")
    elif use_bin:
        w.append(f"Estimated comparisons: Binary about {binary:.0f} vs Linear about {lin:.0f} ({lin/binary:.1f} times fewer).")
        w.append("The data is already sorted, so Binary Search costs nothing extra." if p["sorted"] else f"Sorting once with {nm(best)} costs about {sc:.0f} steps, repaid because you will search {Q} times.")
        if U > 0: w.append(f"Keeping the array sorted through {U} updates adds about {upkeep:.0f} shifts, and Binary Search still wins.")
    else:
        w.append(f"Estimated comparisons: Linear about {lin:.0f} vs Binary about {binary:.0f}.")
        if not p["sorted"] and sc > 0: w.append(f"The data is not sorted, and sorting first would cost about {sc:.0f} steps, more than the searches save.")
        if U > 0: w.append(f"Keeping a sorted array up to date through {U} updates would cost about {upkeep:.0f} shifts.")
        if p["sorted"]: w.append(f"Only {Q} search(es) on this data: the difference is too small to matter.")
    if not is_list and (not p["sorted"] or U > 0) and per_lin - per_bin > 0:
        w.append(f"Break-even: Binary Search overtakes Linear Search after about {(sc + upkeep)/(per_lin - per_bin):.0f} searches (you plan {Q}).")
    if use_bin and p["dup_pct"] > 0: w.append(f"Note: {p['dup_pct']:.1f}% of values repeat. Binary Search finds ONE match; scan neighbours for all.")
    if Q >= 1000 and U >= 1000 and n >= 1000: w.append("With many searches AND many updates, a Hash Table or BST would be worth considering (outside this version).")
    name = "Binary Search" if use_bin else "Linear Search"
    ds = "Sorted array" if use_bin else ("Linked list (as chosen)" if is_list else "Array (no need to keep it sorted)")
    other = "Linear Search" if use_bin else "Binary Search"
    alt_ratio = (
        (lin / binary if use_bin else binary / lin)
        if (binary if use_bin else lin) > 0
        else 1.0
    )
    return {"kind": "Searching", "title": f"Searching | n={n} | {name}",
            "constraints": f"n = {n} | storage = {'linked list' if is_list else 'array'} | sorted now = {p['sorted']} | searches = {Q} | updates = {U}",
            "note": "", "warning": "", "recommended": name + ("" if p["sorted"] or not use_bin else f" (after sorting with {nm(best)})"),
            "data_structure": ds, "why": w,
            "complexity": [{"Algorithm": "Linear Search", "Best Ω": "1", "Average Θ": "n", "Worst O": "n", "Extra space": "1"},
                           {"Algorithm": "Binary Search (sorted array only)", "Best Ω": "1", "Average Θ": "log n", "Worst O": "log n", "Extra space": "1"}],
            "properties": f"For n = {n}: Linear about {per_lin:.0f} comparisons/search, Binary about {per_bin:.1f}",
            "ranking": [{"Algorithm": "Linear Search", "Est. steps": round(lin), "Status": "chosen" if not use_bin else "allowed"},
                        {"Algorithm": "Binary Search", "Est. steps": round(binary), "Status": "chosen" if use_bin else ("not possible on linked list" if is_list else "allowed")}],
            "alternatives": [{"algorithm": other, "times_work": round(alt_ratio, 1),
                              "trade_off": "simple, works on unsorted data and linked lists, but O(n) per search" if use_bin else "O(log n) per search, but needs a sorted array plus sorting/upkeep cost"}],
            "alt_note": ""}
