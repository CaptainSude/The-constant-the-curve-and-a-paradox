"""Numerical illustration of the positive entropy-moment recursion.

The series remainder bound is rigorous. Quadrature is numerical, without an
interval error certificate; agreement of the two grids is a consistency check.
"""
import json
import math
import numpy as np
from numpy.polynomial.legendre import leggauss


def estimate(points, terms=32):
    nodes, weights = leggauss(points)
    u, weights = (nodes + 1) / 2, weights / 2
    h = -u * np.log(u) - (1 - u) * np.log1p(-u)
    a = [1.0]
    for r in range(1, terms + 1):
        value = sum(a[j] * np.dot(weights, h ** (r-j) * (1-u) ** j)
                    / math.factorial(r-j) for j in range(r))
        a.append((r + 1) * value / r)
    return float(sum(a))


if __name__ == "__main__":
    print(json.dumps({
        "quadrature_320_nodes": estimate(320),
        "quadrature_640_nodes": estimate(640),
        "series_remainder_bound": 81 * 2 ** (-33),
        "scope": "Numerical quadrature, not a certified interval computation."
    }, indent=2))
