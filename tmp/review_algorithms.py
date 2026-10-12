"""Read-only algorithm audit; production modules are not modified."""
import itertools
import json
import math
import random
import sys
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiment.algorithm_1.GA import GA
from experiment.algorithm_1.UDCSA_new import UDCSA_new
from experiment.algorithm_1.Qifashi import Qifashi
from experiment.algorithm_1.Brute_force import Brute_force
from experiment.algorithm_2.Lyapunov import Lyapunov
from experiment.algorithm_2.GAP import GAP
from utils.KM import KM


def emit(label, **data):
    print(json.dumps({"case": label, **data}, ensure_ascii=False), flush=True)


def uavs(specs):
    return [
        SimpleNamespace(name=i, E_i=e, Q_i=q, work_time=w, travel_time=t)
        for i, (e, q, w, t) in enumerate(specs)
    ]


def chargers(specs):
    return [
        SimpleNamespace(name=i, charge_power=p, charge_pricie=c)
        for i, (p, c) in enumerate(specs)
    ]


def all_matchings(V, L):
    for choice in itertools.product(range(-1, len(L)), repeat=len(V)):
        used = [k for k in choice if k >= 0]
        if len(used) == len(set(used)):
            yield tuple((i, k) for i, k in enumerate(choice) if k >= 0)


def durations(v, l):
    charge = math.ceil(v.E_i / l.charge_power)
    return charge, charge + v.work_time + 2 * v.travel_time


def exact_schedule(T, V, L):
    matchings = list(all_matchings(V, L))

    @lru_cache(None)
    def solve(q, vu, lu):
        if q > T:
            return 0, ()
        best = (0, ())
        for pairs in matchings:
            new_v, new_l = list(vu), list(lu)
            reward = 0
            for i, k in pairs:
                charge, cycle = durations(V[i], L[k])
                gain = V[i].Q_i - charge * L[k].charge_pricie
                if vu[i] > q or lu[k] > q or q + cycle - 1 > T or gain <= 0:
                    break
                new_v[i], new_l[k] = q + cycle, q + charge
                reward += gain
            else:
                future, schedule = solve(q + 1, tuple(new_v), tuple(new_l))
                if reward + future > best[0]:
                    best = (reward + future, tuple((q, i, k) for i, k in pairs) + schedule)
        return best

    return solve(1, (1,) * len(V), (1,) * len(L))


def validate(T, V, L, obj):
    decisions = obj.decisons[T] if obj.decisons.ndim == 4 else obj.decisons
    vu = np.zeros((T + 1, len(V)), dtype=int)
    lu = np.zeros((T + 1, len(L)), dtype=int)
    total = 0
    issues, schedule = [], []
    for q, i, k in np.argwhere(decisions):
        q, i, k = int(q), int(i), int(k)
        charge, cycle = durations(V[i], L[k])
        schedule.append((q, i, k))
        if q < 1 or q + cycle - 1 > T:
            issues.append("outside_horizon")
        vu[q:min(T + 1, q + cycle), i] += 1
        lu[q:min(T + 1, q + charge), k] += 1
        total += V[i].Q_i - charge * L[k].charge_pricie
    if vu.max(initial=0) > 1:
        issues.append("uav_overlap")
    if lu.max(initial=0) > 1:
        issues.append("charger_overlap")
    if not np.isclose(total, obj.U_arr[T]):
        issues.append("reported_utility_mismatch")
    return {"reported": float(obj.U_arr[T]), "recomputed": total,
            "issues": issues, "schedule": schedule}


def paper_dp(T, V, L):
    cycles = [durations(v, l)[1] for v in V for l in L]
    mu, phi = min(cycles), max(cycles)
    values = [0] * (T + 1)
    for b in range(mu + 1, T + 1):
        for t in range(1, min(phi, b) + 1):
            best_match = 0
            for pairs in all_matchings(V, L):
                gain = 0
                for i, k in pairs:
                    charge, cycle = durations(V[i], L[k])
                    gain += max(V[i].Q_i - charge * L[k].charge_pricie, 0) if t >= cycle else 0
                best_match = max(best_match, gain)
            values[b] = max(values[b], values[b - t] + best_match)
    return values


def basic():
    V = uavs([(1, 0, 1, 0)] * 10 + [(1, 20, 1, 0)])
    L = chargers([(1, 1)])
    for cls in (GA, UDCSA_new, Qifashi, Brute_force):
        obj = cls(4, V, L)
        emit("two_digit_uav", algorithm=cls.__name__, **validate(4, V, L, obj))
    V = uavs([(1, 20, 1, 0)])
    L = chargers([(1, 100)] * 10 + [(1, 1)])
    for cls in (GA, UDCSA_new, Qifashi):
        obj = cls(4, V, L)
        emit("two_digit_charger", algorithm=cls.__name__, **validate(4, V, L, obj))
    V, L = uavs([(1, 10, 1, 1)]), chargers([(1, 1)])
    for cls in (GA, UDCSA_new, Qifashi, Brute_force):
        obj = cls(4, V, L)
        emit("horizon_equals_mu", algorithm=cls.__name__, paper=paper_dp(4, V, L)[4],
             **validate(4, V, L, obj))
    rng = random.Random(4811)
    counts = {cls.__name__: 0 for cls in (GA, UDCSA_new, Qifashi, Brute_force)}
    first_gap, first_dp_difference, first_invalid = set(), False, set()
    for trial in range(200):
        specs = [(rng.randint(1, 4), rng.randint(5, 15), rng.randint(1, 3),
                  rng.randint(0, 1)) for _ in range(rng.randint(1, 3))]
        charger_specs = [(rng.randint(1, 3), rng.randint(1, 3))
                         for _ in range(rng.randint(1, 2))]
        V, L = uavs(specs), chargers(charger_specs)
        T = rng.randint(4, 10)
        optimal, optimal_schedule = exact_schedule(T, V, L)
        for cls in (GA, UDCSA_new, Qifashi, Brute_force):
            obj = cls(T, V, L)
            checked = validate(T, V, L, obj)
            if checked["issues"]:
                counts[cls.__name__] += 1
                if cls.__name__ not in first_invalid:
                    first_invalid.add(cls.__name__)
                    emit("invalid_small_case", algorithm=cls.__name__, trial=trial,
                         T=T, V=specs, L=charger_specs, **checked)
            if checked["reported"] < optimal and cls.__name__ not in first_gap:
                first_gap.add(cls.__name__)
                emit("suboptimal_small_case", algorithm=cls.__name__, trial=trial,
                     T=T, V=specs, L=charger_specs, optimum=optimal,
                     optimal_schedule=optimal_schedule, **checked)
            if cls is UDCSA_new and not first_dp_difference:
                p = paper_dp(T, V, L)[T]
                if p != checked["reported"] and T > min(durations(v, l)[1] for v in V for l in L):
                    first_dp_difference = True
                    emit("paper_dp_difference", T=T, V=specs, L=charger_specs,
                         paper=p, **checked)
    emit("random_small_case_validation", cases=200, invalid_counts=counts)


class KMIterationLimit(RuntimeError):
    pass


class BoundedKM(KM):
    def __init__(self):
        super().__init__()
        self.calls = 0

    def find_path(self, x):
        self.calls += 1
        if self.calls > 10000:
            raise KMIterationLimit
        return super().find_path(x)


def matching():
    rng = np.random.default_rng(1037)
    integer_pass = 0
    for trial in range(500):
        shape = (int(rng.integers(1, 6)), int(rng.integers(1, 6)))
        a = rng.integers(0, 100, size=shape).astype(float)
        match = BoundedKM().compute(a.copy())
        value = sum(a[i, j] for i, j in match if j >= 0)
        n = max(shape)
        padded = np.zeros((n, n))
        padded[:shape[0], :shape[1]] = a
        best = max(sum(padded[i, j] for i, j in enumerate(p))
                   for p in itertools.permutations(range(n)))
        if value != best:
            emit("km_integer_wrong", matrix=a.tolist(), actual=value, expected=best)
            break
        integer_pass += 1
    emit("km_integer_checks", passed=integer_pass)
    for trial in range(5000):
        a = rng.integers(0, 10000, size=(3, 3)) / 100
        km = BoundedKM()
        try:
            km.compute(a.copy())
        except KMIterationLimit:
            emit("km_fractional_iteration_limit", trial=trial, matrix=a.tolist(),
                 lx=km.lx.tolist(), ly=km.ly.tolist(), slack=km.slack.tolist())
            return
    emit("km_fractional_checks", passed=5000)


def long_term():
    V, L = uavs([(1, 10, 1, 0)] * 3), chargers([(1, 1)])
    with patch("experiment.algorithm_2.Lyapunov.random.randint", return_value=1), \
         patch("experiment.algorithm_2.Lyapunov.random.sample", return_value=[V[2]]):
        result = Lyapunov(1, V, L, 1, 1, 2)
        emit("long_term_row_index", decisions=result.decisons[1].tolist())
    V, L = uavs([(3, 10, 1, 0)] * 3), chargers([(1, 1), (3, 1)])
    with patch("experiment.algorithm_2.Lyapunov.random.randint", return_value=3), \
         patch("experiment.algorithm_2.Lyapunov.random.sample", return_value=V):
        result = Lyapunov(1, V, L, 1, 1, 3)
        emit("long_term_reversed_bins", decisions=result.decisons[1].tolist(),
             time_used=(result.decisons[1] * [3, 1]).sum(axis=0).tolist(), capacity=3)
    gap = GAP([0], [0, 1], np.array([[0.9, 0.1]]), 1, np.array([[1, 1]]))
    result = list(reversed(gap.next_bin()))
    value = sum(gap.profit[i, k] for k, selected in enumerate(result) for i in selected)
    emit("gap_fractional_profit", natural_order=[sorted(s) for s in result],
         actual=value, optimum=0.9)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    {"basic": basic, "matching": matching, "long_term": long_term}[sys.argv[1]]()
