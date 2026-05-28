"""Utilities for checking and extending the #287 good-prime chain.

The key point is that entries below 2^64 are checked by deterministic
Miller-Rabin.  The new entries above 2^64 are chosen as safe primes
`p = 2q + 1`; once `q` is certified prime, Pocklington certifies `p`.

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

from dataclasses import dataclass
from decimal import Decimal, getcontext
from fractions import Fraction
from math import gcd


U64_LIMIT = 2**64
MR_U64_BASES = [2, 325, 9375, 28178, 450775, 9780504, 1795265022]
POCKLINGTON_BASES = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
    53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107,
    109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167,
    173, 179, 181, 191, 193, 197, 199,
]
SMALL_TRIAL_PRIMES = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
    53, 59, 61, 67, 71, 73, 79,
]
SERIES_TERMS = 90


CATFLOWERS_CHAIN = [
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
]

U64_EXTENSION_CHAIN = [
    3279511452685958219,
    6559022905371915361,
    13118045810743829821,
    18446744073709550147,
]

# These are safe-prime style extensions found and certified here.
POCKLINGTON_EXTENSION_CHAIN = [
    36893488147419100019,
    73786976294837987927,
    147573952589666836319,
]

KNOWN_CERTIFIED_CHAIN = (
    CATFLOWERS_CHAIN + U64_EXTENSION_CHAIN + POCKLINGTON_EXTENSION_CHAIN
)


@dataclass(frozen=True)
class PocklingtonStep:
    n: int
    q: int
    witness: int


def is_prime_u64(n: int) -> bool:
    if n < 2:
        return False
    for p in SMALL_TRIAL_PRIMES:
        if n % p == 0:
            return n == p

    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    for a in MR_U64_BASES:
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


def pocklington_witness_for_safe_prime(n: int, q: int) -> int | None:
    """Return a Pocklington witness proving n prime from n = 2q+1.

    Pocklington applies because q divides n-1 and q > sqrt(n) for q > 2.
    """
    if n != 2 * q + 1:
        return None
    for a in POCKLINGTON_BASES:
        if pow(a, n - 1, n) != 1:
            continue
        if gcd(pow(a, (n - 1) // q, n) - 1, n) == 1:
            return a
    return None


def certify_prime(n: int, max_depth: int = 8) -> list[PocklingtonStep] | None:
    """Certify primality for the primes used here.

    Below 2^64 this uses deterministic Miller-Rabin.  Above 2^64 it only
    certifies safe-prime towers n = 2q+1, recursively.
    """
    if n < U64_LIMIT:
        return [] if is_prime_u64(n) else None
    if max_depth <= 0 or n % 2 == 0:
        return None

    q = (n - 1) // 2
    child = certify_prime(q, max_depth - 1)
    if child is None:
        return None

    witness = pocklington_witness_for_safe_prime(n, q)
    if witness is None:
        return None
    return child + [PocklingtonStep(n=n, q=q, witness=witness)]


def is_certified_prime(n: int) -> bool:
    return certify_prime(n) is not None


def is_good_prime_certified(p: int) -> bool:
    if certify_prime(p) is None:
        return False
    return certify_prime((p - 1) // 2) is not None or certify_prime((p + 1) // 2) is not None


def verify_chain(chain: list[int]) -> None:
    for p in chain:
        if not is_good_prime_certified(p):
            raise RuntimeError(f"not a certified good prime: {p}")
    for a, b in zip(chain, chain[1:]):
        if b > 2 * a - 3:
            raise RuntimeError(f"chain condition failed: {a}, {b}")


def exp_partial_sum(x: int, n: int) -> Fraction:
    total = Fraction(1, 1)
    term = Fraction(1, 1)
    for j in range(1, n + 1):
        term *= Fraction(x, j)
        total += term
    return total


def exp_bounds(x: int, n: int = SERIES_TERMS) -> tuple[Fraction, Fraction]:
    lower = exp_partial_sum(x, n)
    next_term = Fraction(x, n + 1)
    for j in range(1, n + 1):
        next_term *= Fraction(x, j)
    ratio_bound = Fraction(x, n + 2)
    upper = lower + next_term / (1 - ratio_bound)
    return lower, upper


def exp_minus_one_bounds(n: int = SERIES_TERMS) -> tuple[Fraction, Fraction]:
    lower_e, upper_e = exp_bounds(1, n)
    return lower_e - 1, upper_e - 1


def decimal_values_for_p(p: int) -> tuple[Decimal, int, Decimal, int]:
    getcontext().prec = 120
    e2 = Decimal(2).exp()
    em1 = Decimal(1).exp() - Decimal(1)
    n1_value = Decimal(2 * p) / e2
    n1_floor = int(n1_value)
    k_value = em1 * Decimal(n1_floor)
    k_lower = int(k_value) + 1
    return n1_value, n1_floor, k_value, k_lower


def prove_floor_div_by_e2(p: int, expected_floor: int) -> None:
    lower_e2, upper_e2 = exp_bounds(2)
    numerator = 2 * p
    q = expected_floor
    if not (q * upper_e2 < numerator):
        raise RuntimeError(f"could not prove {q} <= 2p/e^2 for p={p}")
    if not (numerator < (q + 1) * lower_e2):
        raise RuntimeError(f"could not prove 2p/e^2 < {q + 1} for p={p}")


def prove_harmonic_k_lower(n1_floor: int, expected_k_lower: int) -> None:
    lower_em1, upper_em1 = exp_minus_one_bounds()
    if not (expected_k_lower - 1 < n1_floor * lower_em1):
        raise RuntimeError("could not prove lower side of k bound")
    if not (n1_floor * upper_em1 < expected_k_lower):
        raise RuntimeError("could not prove upper side of k bound")
