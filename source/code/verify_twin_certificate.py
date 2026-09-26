"""Exact certificate: the infinite normalized H_15 has >= 4 negative eigenvalues.

Uses only Python's standard library and exact rational arithmetic.
See the manuscript appendix 'A finite certificate for an infinite matrix'
for the infinite-tail argument.
Floating point is used solely to display already-proved rational bounds.
Run: python code/verify_twin_certificate.py
"""
from fractions import Fraction as Q
from math import comb, isqrt
import json


def primes_through(y):
    flags = bytearray(b'\1') * (y + 1)
    flags[:2] = b'\0\0'
    for n in range(2, isqrt(y) + 1):
        if flags[n]:
            flags[n*n:y+1:n] = b'\0' * ((y-n*n)//n + 1)
    return [n for n in range(3, y+1, 2) if flags[n]]


def multiply(a, b):
    result = [Q(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i+j] += x*y
    return result


def evaluate(poly, x):
    value = Q(0)
    for coefficient in reversed(poly):
        value = value*x + coefficient
    return value


def finite_coefficients(primes, nmax):
    d = [Q(0)] + [sum((Q(1, p**k) - Q(1, (p+3)**k)
                       for p in primes), Q(0))
                    for k in range(1, nmax+1)]
    c = [Q(1)]
    for n in range(1, nmax+1):
        c.append(sum((d[k]*c[n-k] for k in range(1, n+1)), Q(0))/n)
    return c


def gram(c, polynomials, shift=0):
    return [[sum((weight*c[n+2-shift]
                  for n, weight in enumerate(multiply(a, b))
                  if n+2 >= shift), Q(0))
             for b in polynomials] for a in polynomials]


def is_negative_definite(matrix):
    """Exact symmetric elimination: all pivots must be strictly negative."""
    a = [list(row) for row in matrix]
    for i in range(len(a)):
        pivot = a[i][i]
        if pivot >= 0:
            return False
        for j in range(i+1, len(a)):
            for k in range(i+1, len(a)):
                a[j][k] -= a[j][i]*a[i][k]/pivot
    return True


def verify():
    cutoff = 100
    order = 15
    targets = [5, 7, 13, 19]
    support = [3, 5, 7, 11, 13, 17, 19, 23]
    prime_list = primes_through(cutoff)
    assert prime_list == [3,5,7,11,13,17,19,23,29,31,37,41,
                          43,47,53,59,61,67,71,73,79,83,89,97]
    polynomials = []
    for target in targets:
        poly = [Q(0)]*7 + [Q(1)]
        for p in support:
            if p != target:
                poly = multiply(poly, [-Q(1,p), Q(1)])
        normalization = evaluate(poly, Q(1,target))
        assert normalization != 0
        polynomials.append([v/normalization for v in poly])
    assert all(len(poly) == order for poly in polynomials)
    for i, target in enumerate(targets):
        for j, poly in enumerate(polynomials):
            assert evaluate(poly, Q(1,target)) == (1 if i == j else 0)

    c = finite_coefficients(prime_list, 2*order)
    assert is_negative_definite(gram(c, polynomials))

    # Rational Gram-Schmidt for the negative finite-prefix form.
    orthogonal = []
    for poly in polynomials:
        v = list(poly)
        for b in orthogonal:
            g = gram(c, [v, b])
            ratio = g[0][1]/g[1][1]
            v = [x-ratio*y for x, y in zip(v, b)]
        orthogonal.append(v)
    base = gram(c, orthogonal)
    size = len(targets)
    assert all(base[i][i] < 0 for i in range(size))
    assert all(base[i][j] == 0 for i in range(size)
               for j in range(size) if i != j)

    error = [[Q(0) for _ in range(size)] for _ in range(size)]
    discarded_shifts = []
    retained_shifts = []
    for shift in range(1, 2*order+1):
        matrix = gram(c, orthogonal, shift)
        if is_negative_definite(matrix):
            discarded_shifts.append(shift)
            continue
        retained_shifts.append(shift)
        coefficient_upper = Q(comb(shift+2, 2), cutoff**shift)
        for i in range(size):
            for j in range(size):
                error[i][j] += coefficient_upper*abs(matrix[i][j])

    # These strict rational inequalities are the decisive certificate.
    row_ratios = []
    for i in range(size):
        row_error = sum(error[i], Q(0))
        assert 7*row_error < -base[i][i]
        row_ratios.append(row_error/(-base[i][i]))
    return {
        'verified': True,
        'infinite_matrix_size': order,
        'certified_negative_dimension': size,
        'prime_cutoff': cutoff,
        'exact_row_bound': 'each row error < one seventh of its negative diagonal magnitude',
        'row_ratios_for_display_only': [float(r) for r in row_ratios],
        'negative_tail_shifts_discarded': discarded_shifts,
        'tail_shifts_bounded_absolutely': retained_shifts,
        'scope': 'Actual infinite matrix, but only a rediscovery of known twin pairs; no new twin-count bound.'
    }


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
