# Prime Mesh R2Q — H-Exc HighWeightRayleighCollapse ClusterFactor Audit v1

**Date:** 2026-05-10

## 1. Scope

This audit analyzes only the sampled-grid bridge energy on `T_J`. It does not assert or use a full-grid lifting theorem.

Target regime:

```text
post_P0_flag = True, W > 1040
K_prime = rho * W <= 65
C_cluster = K_prime / (log(p_star) * S_T)
```

## 2. Summary

- Rows: `22`.
- `K_prime_max = 64.2498859117` with margin `0.750114088289`.
- `K_prime_above_65_count = 0`.
- `C_cluster_median = 0.358679148756`, `C_cluster_max = 1.10266938872`.
- `C_cluster > 1`: `2` rows; `>1.05`: `1`; `>1.10`: `1`; `>1.12`: `0`.
- Empirical pass: `True`.

## 3. Binding Rows

| candidate | h | k | K_prime | C_cluster | S_T | prime_u_mean | sample_u_mean | sample_left_mass |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| hexc_00453 | 767 | 35 | 64.249886 | 1.1026694 | 2.8817775 | 0.44645185 | 0.16445259 | 0.78378378 |
| hexc_00442 | 771 | 34 | 59.236033 | 1.0179619 | 2.8778466 | 0.47211414 | 0.16430049 | 0.78378378 |
| hexc_00303 | 1710 | 75 | 45.488076 | 0.91873013 | 2.4485961 | 0.46361014 | 0.14837557 | 0.80555556 |
| hexc_00431 | 1557 | 72 | 34.362879 | 0.6796301 | 2.5004981 | 0.46503247 | 0.1466264 | 0.81081081 |
| hexc_00222 | 4791 | 80 | 34.179265 | 0.80652909 | 2.0958057 | 0.20049572 | 0.11755375 | 0.85 |
| hexc_00462 | 503 | 24 | 33.768732 | 0.55766311 | 2.9948421 | 0.5545063 | 0.18430593 | 0.73529412 |

## 4. Exception Family

`C_cluster > 1` rows: `hexc_00453,hexc_00442`.

| candidate | h | K_prime | C_cluster | prime_u_mean | sample_u_mean | sample_left_mass | bridge_peak_u |
|---:|---:|---:|---:|---:|---:|---:|---:|
| hexc_00453 | 767 | 64.249886 | 1.1026694 | 0.44645185 | 0.16445259 | 0.78378378 | 0.32073012 |
| hexc_00442 | 771 | 59.236033 | 1.0179619 | 0.47211414 | 0.16430049 | 0.78378378 | 0.10246433 |

## 5. Correlations

| metric | Pearson | Spearman |
|---|---:|---:|
| KS statistic | -0.44557353 | -0.38678713 |
| u_mean | 0.44471723 | 0.39130435 |
| left_mass_frac | -0.40911732 |  |
| sample_u_mean | 0.50047091 |  |
| sample_left_mass_frac | -0.46251042 |  |
| h | -0.39118344 |  |
| S_T | 0.50982962 |  |

## 6. Short-Block Isolation

| threshold | rows_inside | Cmax_inside | Cmax_outside | Kmax_inside | Kmax_outside |
|---|---:|---:|---:|---:|---:|
| h < 500 | 0 | nan | 1.1026694 | nan | 64.249886 |
| h < 800 | 4 | 1.1026694 | 0.91873013 | 64.249886 | 45.488076 |
| h < 1000 | 4 | 1.1026694 | 0.91873013 | 64.249886 | 45.488076 |
| h < 1500 | 5 | 1.1026694 | 0.91873013 | 64.249886 | 45.488076 |
| h < 2000 | 8 | 1.1026694 | 0.80652909 | 64.249886 | 34.179265 |

## 7. Recommended Theorem Form

`short_block_cluster_lemma`.

All C_cluster>1 rows are few and have h<1000; the binding rows are short-block cases. The left-skew signal is strongest in the sampled grid rather than the reconstructed prime-event offsets.

Recommended next file: `Prime_Mesh_R2Q_HExc_HighWeightRayleighCollapse_ShortBlockCluster_Theorem_Target_v1.md`.

## 8. Outputs

```text
prime_mesh_r2q_hexc_highweight_clusterfactor_audit.py
prime_mesh_r2q_hexc_highweight_clusterfactor_summary.csv
prime_mesh_r2q_hexc_highweight_clusterfactor_rows.csv
prime_mesh_r2q_hexc_highweight_clusterfactor_by_regime.csv
prime_mesh_r2q_hexc_highweight_clusterfactor_extremes.csv
prime_mesh_r2q_hexc_highweight_clusterfactor_failures.csv
prime_mesh_r2q_hexc_highweight_clusterfactor_comparison_453_442.csv
prime_mesh_r2q_hexc_highweight_clusterfactor_exceptions.csv
```

*AI documentation pass: GPT-5.5*