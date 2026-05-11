# Prime Mesh R2Q — RawR2Q Full Primitive Export Patch Spec

**Document:** `Prime_Mesh_R2Q_RawR2Q_FullPrimitiveExport_Patch_Spec_v1.md`  
**Project:** Prime Mesh Theory — RH Programme  
**Date:** 2026-05-08  
**Status:** Specification — not yet implemented  
**Purpose:** Specify what must be exported from the bridge computation to close the 1302 instrumentation-gap rows and make Q_R2Q proof-grade globally.

---

## 1. Background

The primitive decomposition export patch (v2) confirmed:

\[
Q_{\rm R2Q}(J) = Q_{\Delta D}(J) + Q_{\rm exc}(J) + \epsilon(J)
\]

on **166 of 1468 rows** where `D_left`, `D_right`, and `bridge_excursion_raw` are available.

The remaining **1302 rows** are in the instrumentation gap: `Q_R2Q` is computed, but the underlying `D_N` endpoint values and interior bridge data were not exported from the original computation.

Until these are exported, neither of the following can be confirmed globally:

- PositiveHarmlessness: $E_\theta > 0 \Rightarrow Q_{\Delta D} \le \tfrac{1}{4}$
- NegativeTransfer: $Q_{\Delta D} > \tfrac{3}{4} \Rightarrow E_\theta < 0$
- The one-directional sign claim: $\Delta D < 0 \Rightarrow E_\theta < 0$

---

## 2. Required Data

For each of the 1302 gap rows (block_id identified in `prime_mesh_r2q_rawr2q_primitive_decomposition_gap_rows_v2.csv`), the export must provide:

### 2.1 Endpoint values

| Field | Definition |
|---|---|
| `D_start` | $D_N(y)$ — bridge value at block left endpoint |
| `D_end` | $D_N(y+h)$ — bridge value at block right endpoint |
| `DeltaD` | $D_N(y+h) - D_N(y)$ — signed endpoint change |
| `DeltaD_sign` | sign(DeltaD): +1, 0, or -1 |

From these, compute:

\[
Q_{\Delta D}(J) = \frac{|\Delta D(J)|}{\sqrt{h} \cdot \log^2(p^*)}
\]

### 2.2 Bridge interior

| Field | Definition |
|---|---|
| `bridge_excursion_raw` | $\sup_{t \in J} \|B_J(t)\|$ — max absolute bridge deviation from linear interpolation |
| `bridge_excursion_argmax` | $t^* = \arg\sup \|B_J(t)\|$ — location of maximum excursion |
| `bridge_path_n_samples` | number of interior sample points used |

From these, compute:

\[
Q_{\rm exc}(J) = \frac{\text{bridge\_excursion\_raw}}{\sqrt{h} \cdot \log^2(p^*)}
\]

### 2.3 Optional (for sign analysis)

| Field | Definition |
|---|---|
| `endpoint_exclusion_flag` | True if block uses endpoint exclusion mechanism |
| `endpoint_exclusion_Q` | excluded endpoint contribution to Q_R2Q |
| `finite_zone_flag` | True if block is in finite zone (y < P0) |
| `post_P0_flag` | True if block extends past P0 |

---

## 3. Approach Options

### Option A — Re-run with full export flag

Re-execute the existing blocksystem computation with an added export flag that writes `D_left`, `D_right`, and `bridge_excursion_raw` for all 1468 blocks to a supplementary CSV.

**Advantages:** exact, uses original computation  
**Cost:** full re-run of the bridge computation

Suggested output file:
```text
prime_mesh_r2q_bridge_primitive_export_all_blocks.csv
```

### Option B — Targeted re-computation for gap rows only

Load the gap row block IDs from:
```text
prime_mesh_r2q_rawr2q_primitive_decomposition_gap_rows_v2.csv
```

Re-run only those 1302 blocks' bridge computation and export the required fields.

**Advantages:** cheaper than full re-run  
**Cost:** requires reproducible bridge computation that can be re-entered at arbitrary blocks

### Option C — Extend the existing H-Exc and endpoint repayment scripts

The current exports only covered 166 blocks. Extend both scripts to output all 1468 blocks:

- `prime_mesh_r2q_hexc_bridge_rigidity_audit.py` → add all-block export
- `prime_mesh_r2q_endpoint_repayment_compatibility_audit.py` → add all-block export

**Advantages:** least invasive — extends existing scripts  
**Cost:** requires checking whether all 1468 blocks are within scope of those audits

---

## 4. Pass Criteria

The full primitive export is complete when:

| Condition | Value |
|---|---|
| `primitive_unavailable` | 0 |
| `pos_harm_instrumentation_gap_count` | 0 |
| `pos_harm_antecedent_prim_available` | = total E_theta > 0 rows |
| `pos_harm_prim_pass` | True |
| `neg_transfer_prim_pass` | True |
| `global_proof_grade` | `proof_grade_global` |

Then the primitive decomposition note should be updated to:

```text
Prime_Mesh_R2Q_RawR2Q_Primitive_Decomposition_v3.md
status: proof_grade_global
```

---

## 5. Sign Inconsistency Resolution

The 18 sign-inconsistent rows (DeltaD and E_theta disagree in sign, all positive-harmless) must be classified in the full export. For each:

Determine whether the sign disagreement arises from:

1. **Endpoint exclusion** — the endpoint contribution is excluded from Q_R2Q for this block, so DeltaD is not the dominant term
2. **Finite zone** — the block is in the finite zone where the theta deviation is small and the sign of DeltaD is not constrained by E_theta
3. **Channel modulation** — a channel-specific correction shifts the effective DeltaD
4. **Residual** — the sign disagreement is absorbed entirely into the ε residual

The classification must be recorded per row so that the one-directional claim:

\[
\Delta D(J) < 0 \;\Rightarrow\; E_\theta(J) < 0
\]

can either be proved or limited to a subcategory of blocks.

---

## 6. Script to Create

```text
prime_mesh_r2q_rawr2q_full_primitive_export_patch.py
```

This script should:

1. Load the gap row list from `prime_mesh_r2q_rawr2q_primitive_decomposition_gap_rows_v2.csv`
2. Execute Option A, B, or C (as chosen) to obtain D_left, D_right, bridge_excursion_raw for all gap rows
3. Merge with the existing 166-row primitive data
4. Re-run the full primitive decomposition logic (from export patch v2) on all 1468 rows
5. Write:
   - `prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv`
   - `prime_mesh_r2q_rawr2q_primitive_decomposition_summary_v3.csv`
   - `prime_mesh_r2q_rawr2q_primitive_decomposition_sign_checks_v3.csv`
   - `Prime_Mesh_R2Q_RawR2Q_Primitive_Decomposition_v3.md`

---

## 7. What This Unlocks

Once the full primitive export is complete:

| Proof obligation | Status after full export |
|---|---|
| Q_R2Q formula validated globally | closeable if residual < threshold |
| PositiveHarmlessness from primitives | closeable (all antecedent rows evaluated) |
| NegativeTransfer from primitives | closeable (already has low antecedent count) |
| DeltaD sign → E_theta sign (one direction) | closeable if no new counterexample |
| Route A alpha bound | still needs analytic proof |
| H-Exc BridgeMaximal bound | still needs analytic proof |

---

*Prime Mesh Theory — RH Programme*
