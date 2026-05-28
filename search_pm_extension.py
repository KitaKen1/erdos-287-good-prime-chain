#!/usr/bin/env python3
"""Search for safe-prime style extensions of a good-prime-chain endpoint.

For a current endpoint p, a valid next chain entry must satisfy

    p_next <= 2*p - 3.

This script searches for entries of the special form

    p_next = 2*q + 1,

where q is itself certified prime.  Then p_next is automatically a good prime,
and Pocklington certifies p_next from q.

This is not an exhaustive search for all possible good primes; it is a fast,
certificate-friendly search for safe-prime extensions.

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

import argparse
from time import perf_counter

from pm_tools import (
    POCKLINGTON_EXTENSION_CHAIN,
    U64_EXTENSION_CHAIN,
    certify_prime,
    decimal_values_for_p,
    pocklington_witness_for_safe_prime,
)


DEFAULT_START = U64_EXTENSION_CHAIN[-1]


def automatic_depth(q: int) -> int:
    """Depth needed if q is certified by repeatedly writing n = 2r+1."""
    return max(0, q.bit_length() - 64)


def small_prime_filter(q: int, p_next: int) -> bool:
    for ell in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79]:
        if q % ell == 0 or p_next % ell == 0:
            return False
    return True


def print_candidate(start: int, q: int, p_next: int, elapsed: float, tried: int) -> None:
    proof_q = certify_prime(q)
    witness = pocklington_witness_for_safe_prime(p_next, q)
    if proof_q is None or witness is None:
        raise RuntimeError("internal error: candidate is not certified")

    n1_value, n1_floor, k_value, k_lower = decimal_values_for_p(p_next)
    print("FOUND")
    print(f"  current endpoint p_m = {start}")
    print(f"  next endpoint p_next = {p_next}")
    print(f"  q = (p_next - 1)/2 = {q}")
    print(f"  chain check: p_next <= 2*p_m - 3 is {p_next <= 2 * start - 3}")
    print(f"  margin: (2*p_m - 3) - p_next = {2 * start - 3 - p_next}")
    print(f"  Pocklington witness for p_next from q: {witness}")
    if proof_q:
        print("  recursive proof for q:")
        for step in proof_q:
            print(
                "    "
                f"n = {step.n}, q = {step.q}, witness = {step.witness}"
            )
    else:
        print("  q is below 2^64 and is checked by deterministic Miller-Rabin")
    print(f"  coverage endpoint T = 2*p_next - 3 = {2 * p_next - 3}")
    print(f"  2*p_next/e^2 = {n1_value}")
    print(f"  n_1 lower bound from e^2 conversion: n_1 > {n1_floor}")
    print(f"  (e-1)*{n1_floor} = {k_value}")
    print(f"  harmonic k lower bound: k >= {k_lower}")
    print(f"  searched odd q values: {tried}")
    print(f"  elapsed seconds: {elapsed:.3f}")


def search_one(start: int, limit: int, depth: int | None) -> int | None:
    q_max = start - 2
    q = q_max if q_max % 2 else q_max - 1
    lower = q_max - limit
    tried = 0
    begin = perf_counter()

    while q > lower:
        tried += 1
        p_next = 2 * q + 1
        if small_prime_filter(q, p_next):
            q_depth = automatic_depth(q) if depth is None else depth
            proof_q = certify_prime(q, max_depth=q_depth)
            if proof_q is not None:
                witness = pocklington_witness_for_safe_prime(p_next, q)
                if witness is not None:
                    print_candidate(start, q, p_next, perf_counter() - begin, tried)
                    return p_next
        q -= 2

    print("NOT FOUND")
    print(f"  current endpoint p_m = {start}")
    print(f"  searched q from {q_max} down to {lower + 1}")
    print(f"  searched odd q values: {tried}")
    print(f"  elapsed seconds: {perf_counter() - begin:.3f}")
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start",
        type=int,
        default=DEFAULT_START,
        help="current endpoint p_m; default is the 64-bit extension endpoint",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10_000_000,
        help="search window for q below start-2",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=None,
        help="recursive safe-prime certification depth for q; default is automatic",
    )
    parser.add_argument(
        "--demo-known",
        action="store_true",
        help="replay the certified extensions found here",
    )
    args = parser.parse_args()

    if args.demo_known:
        start = DEFAULT_START
        for expected in POCKLINGTON_EXTENSION_CHAIN:
            found = search_one(start, args.limit, args.depth)
            if found != expected:
                raise RuntimeError(f"expected {expected}, got {found}")
            print()
            start = found
        return 0

    search_one(args.start, args.limit, args.depth)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
