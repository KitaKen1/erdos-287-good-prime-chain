#!/usr/bin/env python3
"""Verify the e^2 sharpening data for Erdos Problem #287.

This script checks the arithmetic behind the proposed e^2 sharpening:

1. the listed good-prime chain, including the four proposed extensions;
2. the coverage endpoint T = 2 p_m - 3;
3. the conversion n_1 > floor(2 p_m / e^2);
4. the resulting harmonic lower bound on k.

The primality test is deterministic Miller-Rabin for 64-bit integers.
The numerical floors involving e are certified by exact rational upper/lower
bounds from the exponential series.

References:
- Erdos Problems, #287 discussion thread:
  https://www.erdosproblems.com/forum/thread/287
- Good-prime-chain certificate posted by catsflowers5544 at 09:30 on
  27 May 2026 in the #287 discussion thread:
  https://www.erdosproblems.com/forum/thread/287

AI usage disclosure:
The solution and code were made with assistance from Codex 5.5 using xhigh
reasoning, and ChatGPT 5.5 pro.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
from fractions import Fraction
from math import factorial


ORIGINAL_LAST_PRIME = 1_639_755_726_342_979_307
EXTENDED_LAST_PRIME = 18_446_744_073_709_550_147

EXPECTED_ORIGINAL_N1_FLOOR = 443_833_611_326_969_352
EXPECTED_ORIGINAL_K_LOWER = 762_631_229_202_486_109
EXPECTED_EXTENDED_N1_FLOOR = 4_992_990_668_017_577_201
EXPECTED_EXTENDED_K_LOWER = 8_579_365_134_520_192_266

SERIES_TERMS = 80

GOOD_PRIME_CHAIN = [
    13,
    23,
    37,
    61,
    107,
    193,
    383,
    757,
    1487,
    2963,
    5879,
    11701,
    23399,
    46679,
    93287,
    186481,
    372901,
    745753,
    1491493,
    2982899,
    5965643,
    11930987,
    23861687,
    47723279,
    95446487,
    190892903,
    381785617,
    763571173,
    1527142237,
    3054283703,
    6108566567,
    12217132813,
    24434264783,
    48868528993,
    97737057793,
    195474115453,
    390948230557,
    781896460979,
    1563792921721,
    3127585843007,
    6255171685921,
    12510343371563,
    25020686743033,
    50041373485547,
    100082746969523,
    200165493939001,
    400330987877123,
    800661975753803,
    1601323951507417,
    3202647903014447,
    6405295806027973,
    12810591612055513,
    25621183224110701,
    51242366448219263,
    102484732896437053,
    204969465792873143,
    409938931585745593,
    819877863171490597,
    1639755726342979307,
    # Proposed extension, still below 2^64.
    3279511452685958219,
    6559022905371915361,
    13118045810743829821,
    18446744073709550147,
]


def is_prime_u64(n: int) -> bool:
    if n < 2:
        return False
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for p in small_primes:
        if n % p == 0:
            return n == p

    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    # Deterministic for n < 2^64.
    for a in [2, 325, 9375, 28178, 450775, 9780504, 1795265022]:
        a %= n
        if a == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def is_good_prime(p: int) -> bool:
    return is_prime_u64(p) and (
        is_prime_u64((p - 1) // 2) or is_prime_u64((p + 1) // 2)
    )


def exp_partial_sum(x: int, n: int) -> Fraction:
    """Return sum_{j=0}^n x^j/j! exactly."""
    total = Fraction(0, 1)
    term = Fraction(1, 1)
    total += term
    for j in range(1, n + 1):
        term *= Fraction(x, j)
        total += term
    return total


def exp_bounds(x: int, n: int) -> tuple[Fraction, Fraction]:
    """Return rational lower/upper bounds for e^x.

    For fixed positive integer x, after n terms the ratio of consecutive tail
    terms is at most x/(n+2).  With n large enough this gives a geometric tail
    bound.
    """
    lower = exp_partial_sum(x, n)
    next_term = Fraction(x, n + 1)
    for j in range(1, n + 1):
        next_term *= Fraction(x, j)
    # The above loop computes x^(n+1)/(n+1)!.
    ratio_bound = Fraction(x, n + 2)
    upper = lower + next_term / (1 - ratio_bound)
    return lower, upper


def exp_minus_one_bounds(n: int) -> tuple[Fraction, Fraction]:
    lower_e, upper_e = exp_bounds(1, n)
    return lower_e - 1, upper_e - 1


def decimal_from_fraction(x: Fraction) -> Decimal:
    return Decimal(x.numerator) / Decimal(x.denominator)


def prove_floor_div_by_e2(numerator: int, expected_floor: int) -> None:
    lower_e2, upper_e2 = exp_bounds(2, SERIES_TERMS)
    q = expected_floor
    if not (q * upper_e2 < numerator):
        raise RuntimeError("could not prove q <= numerator/e^2")
    if not (numerator < (q + 1) * lower_e2):
        raise RuntimeError("could not prove numerator/e^2 < q+1")


def prove_harmonic_floor(n1_floor: int, expected_k_lower: int) -> None:
    lower_em1, upper_em1 = exp_minus_one_bounds(SERIES_TERMS)
    expected_floor = expected_k_lower - 1
    lower_product = n1_floor * lower_em1
    upper_product = n1_floor * upper_em1
    if not (expected_floor < lower_product):
        raise RuntimeError("could not prove harmonic product exceeds floor")
    if not (upper_product < expected_k_lower):
        raise RuntimeError("could not prove harmonic product below next integer")


def verify_chain() -> None:
    if max(GOOD_PRIME_CHAIN) >= 2**64:
        raise RuntimeError("chain contains an integer outside the 64-bit range")
    for p in GOOD_PRIME_CHAIN:
        if not is_good_prime(p):
            raise RuntimeError(f"not a good prime: {p}")
    for a, b in zip(GOOD_PRIME_CHAIN, GOOD_PRIME_CHAIN[1:]):
        if b > 2 * a - 3:
            raise RuntimeError(f"chain gap failed: {a}, {b}")


def compute_decimal_values(p: int) -> tuple[Decimal, int, Decimal, int]:
    getcontext().prec = 100
    e2 = Decimal(2).exp()
    em1 = Decimal(1).exp() - Decimal(1)
    n1_value = Decimal(2 * p) / e2
    n1_floor = int(n1_value)
    k_value = em1 * Decimal(n1_floor)
    k_lower = int(k_value) + 1
    return n1_value, n1_floor, k_value, k_lower


def report_case(label: str, p: int, expected_n1_floor: int, expected_k_lower: int) -> None:
    n1_value, n1_floor, k_value, k_lower = compute_decimal_values(p)
    prove_floor_div_by_e2(2 * p, expected_n1_floor)
    prove_harmonic_floor(expected_n1_floor, expected_k_lower)
    if n1_floor != expected_n1_floor:
        raise RuntimeError(f"unexpected n1 floor for {label}: {n1_floor}")
    if k_lower != expected_k_lower:
        raise RuntimeError(f"unexpected k lower bound for {label}: {k_lower}")

    print(f"{label}:")
    print(f"  p_m = {p}")
    print(f"  coverage endpoint T = 2*p_m - 3 = {2*p - 3}")
    print(f"  2*p_m/e^2 = {n1_value}")
    print(f"  certified n_1 lower bound: n_1 > {n1_floor}")
    print(f"  (e-1)*{n1_floor} = {k_value}")
    print(f"  certified k lower bound: k >= {k_lower}")


def main() -> int:
    verify_chain()
    print(f"chain length = {len(GOOD_PRIME_CHAIN)}")
    print("all entries are good primes")
    print("all consecutive entries satisfy p_next <= 2*p - 3")
    print()

    report_case(
        "existing chain with e^2 sharpening",
        ORIGINAL_LAST_PRIME,
        EXPECTED_ORIGINAL_N1_FLOOR,
        EXPECTED_ORIGINAL_K_LOWER,
    )
    print()
    report_case(
        "four-prime extension with e^2 sharpening",
        EXTENDED_LAST_PRIME,
        EXPECTED_EXTENDED_N1_FLOOR,
        EXPECTED_EXTENDED_K_LOWER,
    )
    print()
    print("VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
