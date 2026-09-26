#!/usr/bin/env python3
"""Reproduce the exploratory midpoint-root table in the manuscript.

Requires Python 3.9+ and mpmath (install with: python -m pip install mpmath).
Run this file without arguments to use 55 decimal digits, Euler cutoffs
2000, 8000, 32000, and Taylor prime cutoff 251.  To check Taylor stability:

    python estimate_midpoint_roots.py --check-taylor-cutoff 149

The roots are numerical roots of FINITE POLYNOMIALS.  No Euler-product tail
bound or rigorous root enclosure is computed.  These calculations do not
certify a nonzero root of the limiting entire function f(z)-f(0), and they
do not establish infinitely many such roots.  A small polynomial residual
is not an error bound for the limiting function.

All results, including this qualification and every cutoff, go to stdout
as JSON.  The script neither reads nor writes any data files.
"""

from __future__ import annotations

import argparse
import json

try:
    import mpmath as mp
except ImportError as exc:
    raise SystemExit(
        "This script requires mpmath. Install it with: python -m pip install mpmath"
    ) from exc


def primes_through(limit: int) -> list[int]:
    """Return all primes at most limit, using an integer sieve."""
    flags = bytearray(b"\x01") * (limit + 1)
    flags[:2] = b"\x00\x00"
    candidate = 2
    while candidate * candidate <= limit:
        if flags[candidate]:
            start = candidate * candidate
            flags[start : limit + 1 : candidate] = b"\x00" * (
                (limit - start) // candidate + 1
            )
        candidate += 1
    return [n for n in range(2, limit + 1) if flags[n]]


def finite_residues(primes: list[int], taylor_cutoff: int):
    """Compute 1/K_Q'(1-p) for odd primes p up to the Taylor cutoff.

    K_Q(s) = L_Q**(-s) product_{q<=Q}(1+s/(q-1)),
    L_Q = product_{q<=Q}(1-1/q)**(-1).

    Hence the reciprocal derivative at 1-p is
      (p-1) L_Q**(-(p-1)) /
          product_{q<=Q,q!=p}(1-(p-1)/(q-1)).
    We compute the logarithm of its absolute value and the exact sign.
    """
    log_scale = -mp.fsum(mp.log1p(-mp.mpf(1) / q) for q in primes)
    residues = []
    for index, p in enumerate(primes):
        if p > taylor_cutoff:
            break
        if p == 2:
            continue
        log_abs = (
            mp.log(p - 1)
            - (p - 1) * log_scale
            - mp.fsum(
                mp.log(abs(mp.mpf(q - p) / (q - 1)))
                for q in primes
                if q != p
            )
        )
        coefficient = (-1 if index % 2 else 1) * mp.exp(log_abs)
        residues.append((p, coefficient))
    return residues


def estimate_root(residues, taylor_cutoff: int):
    """Solve P_Q(z)/z in t=z**2, using fixed first-quadrant seeds."""
    terms = [
        ((p - 3) // 2, coefficient)
        for p, coefficient in residues
        if p <= taylor_cutoff
    ]

    def polynomial_in_t(t):
        return mp.fsum(coefficient * t**power for power, coefficient in terms)

    t = mp.findroot(
        polynomial_in_t,
        (mp.mpc("6", "28"), mp.mpc("6.1", "28")),
        solver="secant",
        maxsteps=100,
    )
    z = mp.sqrt(t)
    if not (mp.re(z) > 0 and mp.im(z) > 0):
        raise RuntimeError("The computed root is not in the intended first quadrant.")
    residual = abs(z * polynomial_in_t(t))
    return z, residual


def printable_root(z, residual, taylor_cutoff: int, digits: int):
    return {
        "taylor_prime_cutoff": taylor_cutoff,
        "root_real": mp.nstr(mp.re(z), digits),
        "root_imaginary": mp.nstr(mp.im(z), digits),
        "root_rounded_to_six_decimals": (
            f"{float(mp.re(z)):.6f} + {float(mp.im(z)):.6f} i"
        ),
        "absolute_finite_polynomial_residual": mp.nstr(residual, 8),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--euler-cutoffs", type=int, nargs="+", default=[2000, 8000, 32000]
    )
    parser.add_argument("--taylor-cutoff", type=int, default=251)
    parser.add_argument("--check-taylor-cutoff", type=int, default=None)
    parser.add_argument("--precision", type=int, default=55)
    args = parser.parse_args()
    taylor_cutoffs = [args.taylor_cutoff]
    if args.check_taylor_cutoff is not None:
        taylor_cutoffs.append(args.check_taylor_cutoff)
    if args.precision < 25:
        parser.error("Use at least 25 decimal digits of working precision.")
    if min(taylor_cutoffs) < 5:
        parser.error("Taylor cutoffs must be at least 5.")
    if min(args.euler_cutoffs) < max(taylor_cutoffs):
        parser.error("Every Euler cutoff must be at least every Taylor cutoff.")

    mp.mp.dps = args.precision
    output_digits = min(25, args.precision - 10)
    all_primes = primes_through(max(args.euler_cutoffs))
    rows = []
    for cutoff in args.euler_cutoffs:
        primes = [p for p in all_primes if p <= cutoff]
        residues = finite_residues(primes, max(taylor_cutoffs))
        z, residual = estimate_root(residues, args.taylor_cutoff)
        row = {
            "euler_prime_cutoff": cutoff,
            **printable_root(z, residual, args.taylor_cutoff, output_digits),
        }
        if args.check_taylor_cutoff is not None:
            z_check, residual_check = estimate_root(
                residues, args.check_taylor_cutoff
            )
            row["taylor_stability_check"] = {
                **printable_root(
                    z_check, residual_check, args.check_taylor_cutoff, output_digits
                ),
                "absolute_root_difference_at_fixed_euler_cutoff": mp.nstr(
                    abs(z_check - z), 8
                ),
            }
        rows.append(row)

    print(
        json.dumps(
            {
                "status": "exploratory_uncertified_finite_polynomial_roots",
                "warning": (
                    "No Euler-product tail bound or rigorous root enclosure is "
                    "computed. The roots and residuals concern finite polynomials "
                    "only. They do not certify roots of the limiting entire "
                    "function f(z)-f(0) or prove midpoint recurrence."
                ),
                "working_precision_decimal_digits": args.precision,
                "mpmath_version": mp.__version__,
                "polynomial": "sum_{3<=p<=P, p prime} z^(p-2)/K_Q'(1-p)",
                "solver_variable": "t=z^2, after dividing the odd polynomial by z",
                "secant_seeds_in_t": ["6+28i", "6.1+28i"],
                "results": rows,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
