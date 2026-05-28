# Erdos Problem #287: improving the lower bound on `k`

This repository is about improving the known finite lower bound on `k` for a
possible counterexample to Erdős Problem #287.

The verified conclusion here is conditional on the good-prime-chain framework:

```text
any counterexample must have k >= 68634921076157089631.
```

The repository contains Python verifiers/search scripts for the
good-prime-chain finite certificate behind this improvement.  See Reference 1
for the discussion thread.

The starting point is the good-prime-chain certificate posted by
catsflowers5544 at 09:30 on 27 May 2026; see Reference 2.  That certificate
gives a finite lower bound on `n_1` for any counterexample.

This repository verifies two improvements to that certificate.

1. The conversion from chain coverage to an `n_1` lower bound is sharpened
   from the older `M <= 8n_1` estimate to `M + 2 < e^2 n_1`.
2. The good-prime chain is extended beyond the previously listed endpoint,
   using additional safe-prime/Pocklington-certified primes.

Together these improvements give the lower bound stated above.

## What is being checked

There are two independent checks, corresponding to the two improvements.

### Improvement 1: sharper conversion from chain coverage to `n_1`

Corresponding scripts:

- `verify_e2_sharpening.py`
- `verify_pm_chain.py`

Let `M = n_k`.  In a putative counterexample with gaps at most `2`,

```text
n_i <= n_1 + 2(i-1).
```

Therefore

```text
1 = sum_i 1/n_i
  >= sum_{i=0}^{k-1} 1/(n_1+2i)
  > 1/2 log(1+2k/n_1).
```

Since `M <= n_1 + 2(k-1)`, we have `n_1 + 2k >= M+2`, hence

```text
M + 2 < e^2 n_1.
```

So if a good-prime chain rules out all `M <= T = 2p_m-3`, then it rules out

```text
n_1 <= floor(2p_m/e^2).
```

This improves the older conversion using `M <= 8n_1`.

Using the existing endpoint from catsflowers5544's certificate,

```text
p_m = 1639755726342979307,
```

this sharper conversion gives

```text
n_1 > 443833611326969352
k >= 762631229202486109
```

### Improvement 2: certified extension of the good-prime chain

Corresponding scripts:

- `verify_pm_chain.py`
- `search_pm_extension.py`
- shared helper code: `pm_tools.py`

The second check extends the good-prime chain itself.  A valid next chain entry
must be a good prime and must satisfy

```text
p_next <= 2p_m - 3.
```

The repository verifies the four extension primes below `2^64`, then verifies
three further primes with Pocklington primality certificates:

```text
36893488147419100019
73786976294837987927
147573952589666836319
```

With the final endpoint

```text
p_m = 147573952589666836319,
```

the same `e^2` conversion gives

```text
n_1 > 39943925344138028689
k >= 68634921076157089631
```

## Scripts

### `verify_e2_sharpening.py`

This is the original `e^2` sharpening verifier.  It checks catsflowers5544's
listed chain and the four proposed extension primes below `2^64`.

### `verify_pm_chain.py`

This is the stronger endpoint verifier.  It checks:

1. catsflowers5544's original endpoint
   `p_m = 1639755726342979307`;
2. the four `2^64`-range extension primes;
3. three additional safe-prime/Pocklington-certified extensions, giving the
   larger endpoint

```text
p_m = 147573952589666836319.
```

### `search_pm_extension.py`

This searches for certificate-friendly safe-prime extensions of the current
endpoint.  It looks for

```text
p_next = 2q + 1 <= 2p_m - 3
```

where `q` is itself certified prime.  Then `p_next` is a good prime, and
Pocklington certifies `p_next` from `q`.

This is not an exhaustive search for all possible good primes; it is a fast
search for extensions that come with short certificates.

## Verified data

The scripts verify:

1. the full listed good-prime chain, including the four proposed extension
   primes and the three Pocklington extensions;
2. primality of every `p`;
3. primality of at least one of `(p-1)/2`, `(p+1)/2`;
4. the chain condition `p_next <= 2p - 3`;
5. the numerical floors involving `e^2` and `e-1`, with rational interval
   checks from the exponential series.

The four proposed extension primes are

```text
3279511452685958219
6559022905371915361
13118045810743829821
18446744073709550147
```

All are below `2^64`.

The three additional Pocklington-certified extension primes are

```text
36893488147419100019
73786976294837987927
147573952589666836319
```

The last of these gives

```text
T = 2p_m - 3 = 295147905179333672635.
```

## Run the verifiers

```sh
python3 verify_e2_sharpening.py
python3 verify_pm_chain.py
```

Expected key conclusions:

```text
existing chain with e^2 sharpening:
  certified n_1 lower bound: n_1 > 443833611326969352
  certified k lower bound: k >= 762631229202486109

four-prime extension with e^2 sharpening:
  certified n_1 lower bound: n_1 > 4992990668017577201
  certified k lower bound: k >= 8579365134520192266

new certified endpoint found here:
  p_m = 147573952589666836319
  coverage endpoint T = 2*p_m - 3 = 295147905179333672635
  certified n_1 lower bound: n_1 > 39943925344138028689
  certified k lower bound: k >= 68634921076157089631
```

## Re-run the extension search

To replay the three certified extensions:

```sh
python3 search_pm_extension.py --demo-known --limit 10000000
```

The search finds:

```text
18446744073709550147
  -> 36893488147419100019
  -> 73786976294837987927
  -> 147573952589666836319
```

## AI usage disclosure
The solution and code were made with assistance from Codex 5.5 using xhigh reasoning, and ChatGPT 5.5 pro.


## References

1. Erdős Problems, #287 discussion thread:
   https://www.erdosproblems.com/forum/thread/287
2. Good-prime-chain certificate posted by catsflowers5544 at 09:30 on
   27 May 2026 in the #287 discussion thread:
   https://www.erdosproblems.com/forum/thread/287
