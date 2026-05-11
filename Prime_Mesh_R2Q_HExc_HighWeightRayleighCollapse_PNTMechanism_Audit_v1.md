# Prime Mesh R2Q — H-Exc High-Weight Rayleigh Collapse: PNT Mechanism Audit
**Spec:** Prime_Mesh_R2Q_HExc_HighWeightRayleighCollapse_PNTMechanism_Audit_Spec_v1  
**Date:** 2026-05-10  
**Status:** Complete — all 22 rows verified, theorem cap holds

---

## 1. Data Source

**File:** `prime_mesh_r2q_hexc_primeshock_rayleighcoupling_rows.csv`  
**Filter:** `W > 1040` AND `post_P0_flag == True`  
**Rows matched:** 22 (exactly the expected Regime 2 post-P0 set)

Column mapping used:
- `W_J` → `W` (sum of (log p_i)^2 for primes in block J)
- `K_prime` → `K` (bridge energy = (1/h) * sum_T B_prime(t)^2)
- `rho_J` → `rho` (= K/W, Rayleigh quotient)
- `p_star` → `p_star` (largest prime in block)
- `h` → `h` (block length)
- `R_offsets` → parsed to `u_t = offset/h` (normalized prime positions in [0,1])
- `prime_event_count` → `k` (number of primes in block)

---

## 2. Theorem Setup

**Target:** K_prime = rho_J * W_J <= 65 for all Regime 2 rows.

**Two-regime split:**
- Regime 1: W_J <= 1040 → rho_J <= 1/16 (proven separately)
- Regime 2: W_J > 1040 → 22 post-P0 rows, verified here

**PNT hypothesis:** K_prime ≈ log(p*) * S_T(J)  
where S_T(J) = sum_{t in T_J} u_t * (1 - u_t), u_t = (t - y) / h.

---

## 3. Full 22-Row Table

Sorted by W descending.

| idx | W | h | k | p_star | log(p*) | K_prime | rho_J | N_s | S_T | K/log(p*) | K/[log(p*)·S_T] | PNT_pred | anomalous | >65 |
|-----|---|---|---|--------|---------|---------|-------|-----|-----|-----------|-----------------|----------|-----------|-----|
| 40 | 3,033,677 | 151,650 | 7,420 | 604,672,261 | 20.220 | 2.150 | 0.0000007 | 41 | 1.441 | 0.106 | 0.074 | 29.13 | No | No |
| 63 | 1,051,189 | 53,021 | 2,571 | 604,810,421 | 20.220 | 2.142 | 0.0000020 | 41 | 1.588 | 0.106 | 0.067 | 32.10 | No | No |
| 104 | 434,188 | 22,162 | 1,062 | 604,432,601 | 20.220 | 8.954 | 0.0000206 | 41 | 1.736 | 0.443 | 0.255 | 35.11 | No | No |
| 183 | 410,879 | 20,686 | 1,005 | 604,356,173 | 20.220 | 10.343 | 0.0000252 | 40 | 1.749 | 0.512 | 0.292 | 35.37 | No | No |
| 218 | 118,559 | 6,250 | 290 | 604,167,899 | 20.219 | 20.089 | 0.0001695 | 40 | 2.019 | 0.994 | 0.492 | 40.82 | No | No |
| 296 | 103,850 | 5,423 | 254 | 604,724,143 | 20.220 | 7.676 | 0.0000739 | 41 | 2.061 | 0.380 | 0.184 | 41.67 | No | No |
| 222 | 89,133 | 4,791 | 218 | 604,848,841 | 20.220 | 34.179 | 0.0003835 | 40 | 2.096 | 1.690 | 0.807 | 42.38 | No | No |
| 227 | 78,910 | 4,338 | 193 | 604,708,931 | 20.220 | 17.213 | 0.0002181 | 40 | 2.126 | 0.851 | 0.400 | 42.98 | No | No |
| 214 | 76,459 | 4,200 | 187 | 604,883,911 | 20.221 | 19.386 | 0.0002535 | 40 | 2.136 | 0.959 | 0.449 | 43.19 | No | No |
| 334 | 49,063 | 2,559 | 120 | 604,685,377 | 20.220 | 23.952 | 0.0004882 | 39 | 2.303 | 1.185 | 0.514 | 46.57 | No | No |
| 378 | 48,245 | 2,583 | 118 | 604,681,513 | 20.220 | 9.352 | 0.0001938 | 39 | 2.299 | 0.463 | 0.201 | 46.49 | No | No |
| 207 | 46,611 | 2,762 | 114 | 604,822,567 | 20.220 | 14.554 | 0.0003122 | 38 | 2.271 | 0.720 | 0.317 | 45.93 | No | No |
| 319 | 38,433 | 2,150 | 94 | 604,702,619 | 20.220 | 11.316 | 0.0002945 | 39 | 2.345 | 0.560 | 0.239 | 47.41 | No | No |
| 300 | 37,204 | 2,075 | 91 | 604,360,789 | 20.220 | 10.640 | 0.0002860 | 40 | 2.389 | 0.526 | 0.220 | 48.30 | No | No |
| 381 | 33,525 | 1,803 | 82 | 604,365,031 | 20.220 | 29.497 | 0.0008797 | 39 | 2.441 | 1.459 | 0.598 | 49.35 | No | No |
| 303 | 30,665 | 1,710 | 75 | 604,870,961 | 20.221 | 45.488 | 0.0014832 | 36 | 2.449 | 2.250 | 0.919 | 49.51 | No | No |
| 431 | 29,438 | 1,557 | 72 | 604,813,747 | 20.220 | 34.363 | 0.0011673 | 37 | 2.501 | 1.699 | 0.680 | 50.56 | No | No |
| 315 | 19,624 | 1,183 | 48 | 604,434,563 | 20.220 | 11.891 | 0.0006060 | 37 | 2.546 | 0.588 | 0.231 | 51.48 | No | No |
| **453** | **14,309** | **767** | **35** | **604,143,557** | **20.219** | **64.250** | **0.00449** | **37** | **2.882** | **3.178** | **1.103** | **58.27** | **YES** | **No** |
| 442 | 13,901 | 771 | 34 | 604,711,937 | 20.220 | 59.236 | 0.00426 | 37 | 2.878 | 2.930 | 1.018 | 58.19 | No | No |
| 663 | 11,038 | 626 | 27 | 604,206,971 | 20.219 | 8.208 | 0.00074 | 36 | 2.997 | 0.406 | 0.135 | 60.60 | No | No |
| 462 | 9,812 | 503 | 24 | 604,208,581 | 20.219 | 33.769 | 0.00344 | 34 | 2.995 | 1.670 | 0.558 | 60.55 | No | No |

---

## 4. Summary Statistics

| Quantity | Min | Median | Mean | Max |
|---|---|---|---|---|
| W (weight sq sum) | 9,812 | 47,428 | 262,669 | 3,033,677 |
| K_prime | 2.142 | 15.883 | 21.757 | **64.250** |
| rho_J | ~0 | 0.00030 | 0.00090 | **0.00449** |
| log(p*) | 20.2193 | 20.2202 | 20.2200 | 20.2206 |
| N_s (prime count in block) | 34 | 39 | 38.7 | 41 |
| S_T = sum u(1-u) | 1.441 | 2.301 | 2.284 | 2.997 |
| K / log(p*) | 0.106 | 0.786 | 1.076 | **3.178** |
| **C_cluster = K / [log(p*)·S_T]** | **0.067** | **0.359** | **0.443** | **1.103** |
| PNT prediction: log(p*)·S_T | 29.13 | 46.53 | 46.18 | 60.60 |
| K / PNT_prediction | 0.067 | 0.359 | 0.443 | 1.103 |
| k/h (prime density) | 0.041 | 0.046 | 0.045 | 0.049 |
| (k/h)·log(p*) [should ≈ 1] | 0.820 | 0.921 | 0.919 | 0.989 |

**corr(log rho, log W) = -0.9599** (expected ≈ -0.97 from full Regime 2 — close; post-P0 subset explains the small gap).

---

## 5. Log-Log Regression

Attempted: `log(K_prime) = a·log(log p*) + b·log(S_T) + c`

**Result: degenerate.** All 22 rows share log(p*) ≈ 20.22 (blocks contain primes near 6.04×10⁸). The coefficient on log(log p*) is numerically unstable (a = 5719, not informative). R² = 0.516 driven almost entirely by S_T variation.

**Meaningful restricted regression:** `log(K_prime) ~ b·log(S_T) + c` alone.

The key quantitative result is the directly observed C_cluster distribution:
- min = 0.067, median = 0.359, max = **1.103**
- Row 453 is the binding constraint: C_cluster = 1.103.

---

## 6. PNT Mechanism Assessment

### 6a. Prime density law: CONFIRMED
(k/h)·log(p*) = 0.919 median (range 0.82–0.99). PNT density 1/log(p*) holds to within ~8% across all 22 blocks. This explains why W and K are anti-correlated: larger blocks have more primes but lower rho because the bridge energy is diluted.

### 6b. K_prime ≈ log(p*)·S_T: NOT a universal constant
The ratio C_cluster = K / [log(p*)·S_T] varies from 0.067 to 1.103 — a 16× range. PNT sets the scale but does not pin the constant. The within-block spatial distribution of primes (deviation from uniform) controls C_cluster.

### 6c. What drives high C_cluster?
Row 453 (worst case): 35 primes in h=767, u_mean = 0.165, u_std = 0.244. Primes are **heavily left-clustered** (concentrated near the block start). The KS statistic indicates strong non-uniformity. This clustering concentrates bridge energy in a narrow region, driving K_prime to 64.25 despite W being relatively modest (14,309 — lowest among the high-K rows).

### 6d. Flag: K > 3·log(p*)
Only 1 row (row 453): K/log(p*) = 3.178. All others satisfy K ≤ 3·log(p*).

---

## 7. Theorem Closure Check

| Check | Result |
|---|---|
| Rows with K_prime > 65 | **0** |
| Rows with K_prime > 3·log(p*) | 1 (row 453, K=64.25) |
| Max K_prime observed | **64.2499** |
| Max rho_J observed | **0.004490** |
| corr(log rho, log W) | **-0.9599** |
| K_prime ≤ 4·log(p*) for all rows | **True** |
| K_prime ≤ 65 for all rows | **True** — theorem cap holds |

---

## 8. Worst-Case Row Detail: Row 453 (candidate_id 453)

```
h          = 767
k (primes) = 35
p_star     = 604,143,557
log(p*)    = 20.2193
W          = 14,308.73
K_prime    = 64.2499    [near-miss: 0.75 below cap of 65]
rho_J      = 0.004490
N_s        = 37
S_T        = 2.8818
C_cluster  = K / [log(p*) * S_T] = 1.103
PNT_pred   = log(p*)*S_T = 58.27
k_over_h   = 0.04563
(k/h)*log(p*) = 0.923 [PNT density holds]
u_mean     = 0.165  [primes cluster left]
u_std      = 0.244
KS_stat    = large  [concentrated distribution]
Prime distribution: concentrated (left-skewed)
```

This row is not extreme in W (it is among the smallest W in Regime 2). Its high K_prime comes from:
1. Short block (h=767) → small S_T denominator relative to within-block concentration
2. Left-clustered primes → bridge accumulates energy near the block start, not spread across T_J
3. C_cluster = 1.103 exceeds 1, meaning the actual K exceeds the naive PNT prediction — spatial concentration is the key mechanism

---

## 9. Conclusions

1. **Theorem target K_prime ≤ 65 holds for all 22 rows.** The near-miss is row 453 at K=64.25.

2. **PNT explains the density scale:** (k/h)·log(p*) ≈ 0.92, confirming primes obey PNT density.

3. **PNT does NOT pin the bound.** C_cluster = K / [log(p*)·S_T] ranges 0.067–1.103. The bound requires a separate clustering argument.

4. **Empirical safe constant:** C_cluster ≤ 1.103 for all audited rows. A theorem target of C_cluster ≤ 1.12 (with 1.5% margin) would be conservative.

5. **Proposed refined theorem target:**
   ```
   K_prime <= C_cluster * log(p*) * S_T(J)  with  C_cluster <= 1.12
   ```
   Combined with S_T_max ≈ 2.997 and log(p*) ≈ 20.22:
   ```
   K_prime <= 1.12 * 20.22 * 2.997 ≈ 67.9
   ```
   This is marginally above 65. To close to exactly 65, need C_cluster ≤ 1.074:
   ```
   1.074 * 20.22 * 2.997 ≈ 65.0
   ```
   Row 453 has C_cluster = 1.103, so this requires tightening the S_T bound or using a sharper clustering argument. The binding row determines the theorem constant.

---

## 10. Output Files

| File | Description |
|---|---|
| `prime_mesh_r2q_hexc_highweight_pnt_mechanism_rows.csv` | All 22 rows with computed PNT columns |
| `prime_mesh_r2q_hexc_highweight_pnt_mechanism_extremes.csv` | 4 extreme rows (max K, max W, max rho, min C_cluster) |
| `prime_mesh_r2q_hexc_highweight_pnt_mechanism_summary.csv` | Scalar summary statistics |
| `prime_mesh_r2q_hexc_highweight_pnt_mechanism_audit.py` | Full audit script |

**Primary data source:**  
`prime_mesh_r2q_hexc_primeshock_rayleighcoupling_rows.csv`  
(1,468 total rows; 22 matching post-P0 Regime 2 filter)
