#!/usr/bin/env python3
"""Verify the good-prime-chain endpoint p_m and certified extensions.

This script answers two questions:

1. Does the catsflowers5544 chain really end at
   p_m = 1639755726342979307 and satisfy the good-prime-chain checks?
2. Can we certify a larger endpoint using additional safe-prime/Pocklington
   extensions?

No external packages are required.

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

from pm_tools import (
    CATFLOWERS_CHAIN,
    KNOWN_CERTIFIED_CHAIN,
    POCKLINGTON_EXTENSION_CHAIN,
    U64_EXTENSION_CHAIN,
    certify_prime,
    decimal_values_for_p,
    is_good_prime_certified,
    prove_floor_div_by_e2,
    prove_harmonic_k_lower,
    verify_chain,
)


def report_endpoint(label: str, chain: list[int]) -> None:
    p = chain[-1]
    n1_value, n1_floor, k_value, k_lower = decimal_values_for_p(p)
    prove_floor_div_by_e2(p, n1_floor)
    prove_harmonic_k_lower(n1_floor, k_lower)

    print(f"{label}:")
    print(f"  chain length = {len(chain)}")
    print(f"  p_m = {p}")
    print(f"  coverage endpoint T = 2*p_m - 3 = {2 * p - 3}")
    print(f"  2*p_m/e^2 = {n1_value}")
    print(f"  certified n_1 lower bound: n_1 > {n1_floor}")
    print(f"  (e-1)*{n1_floor} = {k_value}")
    print(f"  certified k lower bound: k >= {k_lower}")
    print()


def report_pocklington_steps() -> None:
    print("Pocklington-certified extension primes:")
    for p in POCKLINGTON_EXTENSION_CHAIN:
        proof = certify_prime(p)
        if proof is None:
            raise RuntimeError(f"could not certify extension prime: {p}")
        print(f"  p = {p}")
        for step in proof:
            print(
                "    Pocklington step: "
                f"n = {step.n}, q = {step.q}, witness = {step.witness}"
            )
    print()


def main() -> int:
    print("Checking catsflowers5544 chain...")
    verify_chain(CATFLOWERS_CHAIN)
    print("  all entries are certified good primes")
    print("  all adjacent pairs satisfy p_next <= 2*p - 3")
    print()

    full_u64_chain = CATFLOWERS_CHAIN + U64_EXTENSION_CHAIN
    print("Checking chain with 64-bit extension primes...")
    verify_chain(full_u64_chain)
    print("  all entries are certified good primes")
    print("  all adjacent pairs satisfy p_next <= 2*p - 3")
    print()

    print("Checking chain with Pocklington-certified extension primes...")
    verify_chain(KNOWN_CERTIFIED_CHAIN)
    print("  all entries are certified good primes")
    print("  all adjacent pairs satisfy p_next <= 2*p - 3")
    print()

    # A few explicit checks make failures easier to read if someone edits data.
    for p in KNOWN_CERTIFIED_CHAIN:
        if not is_good_prime_certified(p):
            raise RuntimeError(f"not a certified good prime: {p}")

    report_endpoint("catsflowers5544 endpoint", CATFLOWERS_CHAIN)
    report_endpoint("previous 64-bit extension endpoint", full_u64_chain)
    report_endpoint("new certified endpoint found here", KNOWN_CERTIFIED_CHAIN)
    report_pocklington_steps()
    print("VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
