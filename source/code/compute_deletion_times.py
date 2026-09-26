#!/usr/bin/env python3
"""Compute exact first-deletion rounds for the delete-seven experiment.

Requires Python 3.10+ and NumPy (install with: python -m pip install numpy).

Examples:
    python compute_deletion_times.py
    python compute_deletion_times.py --cutoff 1000000 --output deletion_times.json

The default JSON output reproduces the table and round counts in
"The constant, the curve and a paradox".

Rule:
    B_0 = all primes except 7;
    p_i remains in B_{k+1} precisely when p_i is in B_k and
    2(i+1) = q+r for primes q,r in B_k, with p_1=2.

The primes 2,3,5 survive forever. For every p_i >= 11, all prime
summands of its assigned target are smaller than p_i. Consequently
one pass in increasing prime order gives exact deletion times:
    tau(p_i) = 1 + max_{q+r=2(i+1)} min(tau(q), tau(r)).
The maximum for an empty set of certificates is defined as zero.
This is an exact finite-window computation; larger primes cannot
provide a missing certificate for a smaller prime. No floating-point
arithmetic or assumed Goldbach assertion is used.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    import numpy as np
except ImportError as exc:
    raise SystemExit(
        "NumPy is required. Install it with: python -m pip install numpy"
    ) from exc


def deletion_times(cutoff: int) -> tuple[np.ndarray, np.ndarray]:
    """Return all primes through cutoff and a value-indexed time array.

    Composite array entries remain -1. The permanent survivors have
    sentinel len(primes)+1, larger than every possible finite time.
    """
    if cutoff < 7:
        raise ValueError("cutoff must be at least 7")

    is_prime = np.ones(cutoff + 1, dtype=np.bool_)
    is_prime[:2] = False
    # Integer arithmetic keeps the sieve boundary exact.
    from math import isqrt

    for prime in range(2, isqrt(cutoff) + 1):
        if is_prime[prime]:
            is_prime[prime * prime :: prime] = False

    primes = np.flatnonzero(is_prime)
    times = np.full(cutoff + 1, -1, dtype=np.int64)
    infinity = len(primes) + 1
    times[primes[:3]] = infinity
    times[7] = 0

    # index is zero-based, so p_i has i=index+1 and target=2(index+2).
    for index in range(4, len(primes)):
        target = 2 * (index + 2)
        # All relevant summands are odd. Taking q <= r counts each
        # certificate once, which leaves its maximum lifetime unchanged.
        end = np.searchsorted(primes, target // 2, side="right")
        left = primes[1:end]
        left = left[is_prime[target - left]]
        right = target - left
        if np.any(times[left] < 0) or np.any(times[right] < 0):
            raise AssertionError("A certificate used an uncomputed dependency")
        certificate_times = np.minimum(times[left], times[right])
        last_certificate = int(certificate_times.max(initial=0))
        if last_certificate >= infinity:
            raise AssertionError("An unexpected certificate uses only survivors")
        times[primes[index]] = last_certificate + 1

    return primes, times


def summarize(cutoff: int) -> dict:
    primes, times = deletion_times(cutoff)
    finite_primes = primes[primes > 5]
    finite_times = times[finite_primes]
    last_round = int(finite_times.max())

    thresholds = []
    value = 100
    while value <= cutoff:
        thresholds.append(value)
        value *= 10
    if cutoff not in thresholds:
        thresholds.append(cutoff)
    thresholds.sort()

    clock_table = []
    for threshold in thresholds:
        chosen = finite_primes[finite_primes <= threshold]
        clock_table.append(
            {
                "cutoff": threshold,
                "prime_count_excluding_survivors": int(len(chosen)),
                "maximum_deletion_round": int(times[chosen].max()),
            }
        )

    round_counts = []
    for round_number in range(last_round + 1):
        chosen = finite_primes[finite_times == round_number]
        if len(chosen):
            round_counts.append(
                {
                    "round": round_number,
                    "count": int(len(chosen)),
                    "first_prime": int(chosen[0]),
                    "last_prime": int(chosen[-1]),
                }
            )

    # q -> p_{q-1}; all listed terms lie within the computed window.
    witness_chain = []
    prime = 7
    while prime <= cutoff:
        witness_chain.append(
            {"prime": prime, "deletion_round": int(times[prime])}
        )
        next_index = prime - 2
        if next_index >= len(primes):
            break
        prime = int(primes[next_index])

    lower_round = max(0, last_round - 2)
    last_three_count = int(np.count_nonzero(finite_times >= lower_round))

    return {
        "cutoff": cutoff,
        "method": "integer sieve and increasing-prime certificate recurrence",
        "permanent_survivors": [2, 3, 5],
        "initial_deleted_prime": 7,
        "prime_count": int(len(primes)),
        "prime_count_excluding_survivors": int(len(finite_primes)),
        "clock_table": clock_table,
        "round_counts": round_counts,
        "witness_chain": witness_chain,
        "last_three_rounds": {
            "rounds": list(range(lower_round, last_round + 1)),
            "count": last_three_count,
            "denominator": int(len(finite_primes)),
            "proportion": last_three_count / len(finite_primes),
        },
        "notes": [
            "All counts and deletion rounds are exact.",
            "The final proportion is a floating-point display of an exact ratio.",
            "No asymptotic approximation is used by the computation.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cutoff",
        type=int,
        default=1_000_000,
        help="largest integer in the prime window (default: 1000000)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="optional JSON destination; stdout is used when omitted",
    )
    args = parser.parse_args()
    if args.cutoff < 7:
        parser.error("--cutoff must be at least 7")
    result = summarize(args.cutoff)
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
