# Prime Mesh R2Q — H-Exc HighWeightRayleighCollapse ShortBlockCluster Audit v1

**Date:** 2026-05-10

## 1. Scope

This audit is sampled-grid only. It reconstructs `B_prime` on `T_J` from Lambda event offsets and weights; it does not use a full integer-grid theorem.

Regime:

```text
W > 1040, h < 800, p_star >= 500,000,000
```

## 2. Summary

- Total high-weight post-P0 rows: `22`.
- Short high-weight rows: `4`: `hexc_00453,hexc_00442,hexc_00462,hexc_00663`.
- `short_highW_K_max = 64.2498859117`.
- `short_highW_K_above_65_count = 0`.
- `short_highW_margin_min = 0.750114088289`.
- Binding reconstruction error max: `1.331e-10`.
- Best closure route: `finite_shortblock_certificate`.

## 3. Short-Block Rows

| candidate | h | K_prime | margin | C_cluster | sample_u_mean | sample_left | prime_u_mean | prime_left | peak_u | top3_energy |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| hexc_00453 | 767 | 64.249886 | 0.75011409 | 1.1026694 | 0.16445259 | 0.78378378 | 0.44645185 | 0.31428571 | 0.32073012 | 0.33773714 |
| hexc_00442 | 771 | 59.236033 | 5.7639671 | 1.0179619 | 0.16430049 | 0.78378378 | 0.47211414 | 0.32352941 | 0.10246433 | 0.26281225 |
| hexc_00462 | 503 | 33.768732 | 31.231268 | 0.55766311 | 0.18430593 | 0.73529412 | 0.5545063 | 0.16666667 | 0.32206759 | 0.45592192 |
| hexc_00663 | 626 | 8.2082512 | 56.791749 | 0.13544835 | 0.17500887 | 0.77777778 | 0.48514969 | 0.25925926 | 0.39776358 | 0.28467912 |

## 4. Interpretation

The short regime is finite in the current post-P0 export: four rows. The two near-cap rows are `hexc_00453` and `hexc_00442`; both reconstruct exactly from the Lambda event offsets and retain positive margins to 65.

The skew signal remains sample-grid driven: all four short rows have stronger sample-grid skew than reconstructed prime-event skew. This supports a finite sampled-grid certificate first, with a possible later sample-grid-shape lemma.

The simple `C_short * log(p*) * S_T` bound passes with `C_short=1.12`, but it is still empirical here and should not be presented as a proof without an analytic route.

## 5. Bound Checks

| bound | passes all short rows | max looseness |
|---|---:|---:|
| C_short_1.11 | True | 8.1950054 |
| C_short_1.12 | True | 8.2688343 |
| C_short_1.15 | True | 8.4903209 |
| C_short_1.2 | True | 8.8594653 |
| direct_K_cap_65 | True | 7.918861 |
| sampled_supremum | True | 6.0973215 |
| total_lambda_mass | True | 2088.0589 |

## 6. Recommended Next File

`Prime_Mesh_R2Q_HExc_HighWeightRayleighCollapse_ShortBlockCluster_FiniteCertificate_Target_v1.md`

Only four short high-weight post-P0 rows occur; all reconstruct from primitive offsets and all margins are positive. This is the cleanest closure unless a symbolic sampled-grid theorem is later derived.

## 7. Outputs

```text
prime_mesh_r2q_hexc_shortblock_cluster_audit.py
prime_mesh_r2q_hexc_shortblock_cluster_summary.csv
prime_mesh_r2q_hexc_shortblock_cluster_rows.csv
prime_mesh_r2q_hexc_shortblock_cluster_binding_rows.csv
prime_mesh_r2q_hexc_shortblock_cluster_certificate.csv
prime_mesh_r2q_hexc_shortblock_cluster_bounds.csv
prime_mesh_r2q_hexc_shortblock_cluster_failures.csv
prime_mesh_r2q_hexc_shortblock_cluster_bridge_values.csv
prime_mesh_r2q_hexc_shortblock_cluster_sample_prime_comparison.csv
```

*AI documentation pass: GPT-5.5*