# Prime Mesh R2Q - RawR2Q Primitive Decomposition Codex Validation

**Document:** `Prime_Mesh_R2Q_RawR2Q_Primitive_Decomposition_Codex_Validation_v1.md`  
**Project:** Prime Mesh Theory - RH Programme  
**Date:** 2026-05-08  
**Status:** validation / correction note for Claude RawR2Q primitive decomposition

## 1. Verdict

The primitive decomposition is **partially validated**, but it is not yet proof-grade globally.

Validated statement:

\[
Q_{\rm R2Q}(J)
=
Q_{\Delta D}(J)+Q_{\rm exc}(J)+\epsilon(J)
\]

is checked for the **166 rows** where both primitive endpoint and bridge-excursion data are exported.

It is not checked for the remaining **1302 rows**, because those rows do not currently export the primitive \(D_N\) endpoint / bridge path terms.

## 2. Rerun Status

Codex reran:

```text
prime_mesh_r2q_rawr2q_export_patch.py
```

with UTF-8 console output enabled. The first plain Windows run failed only because box-drawing characters could not be printed under `cp1252`; the UTF-8 rerun completed.

## 3. Confirmed Numbers

| metric | value |
|---|---:|
| total rows | 1468 |
| primitive full rows (`Q_delta_D + Q_exc`) | 166 |
| primitive unavailable rows | 1302 |
| max absolute formula residual | 0.02572845 |
| max fractional formula residual | 0.305629 |
| mean absolute formula residual | 0.00998078 |
| sign consistency rows checked | 166 |
| sign consistency count | 148 |
| sign inconsistent count | 18 |
| NegativeTransfer antecedent rows | 2 |
| NegativeTransfer primitive violations | 0 |
| positive rows total | 1320 |
| positive rows with primitive `Q_delta_D` | 18 |
| PositiveHarmless primitive violations among available rows | 0 |
| positive rows missing primitive export | 1302 |

## 4. Important Correction

The generated Claude result note says:

```text
PositiveHarmlessness from primitives: PASS (0 violations / 1320 antecedent rows)
```

That wording is too strong.

The script's own rerun reports:

```text
pos_harmlessness_antecedent_count = 1320
pos_harmlessness_prim_violation_count = 1302
pos_harmlessness_prim_pass = False
```

Those `1302` are not genuine mathematical counterexamples. They are rows with missing primitive `Q_delta_D_best`; the boolean violation field counts missing primitive data as failure.

Correct proof-facing wording:

```text
PositiveHarmlessness from primitives passes on the 18 primitive-available positive rows;
1302 positive rows remain in the primitive-export instrumentation gap.
```

## 5. Sign-Inconsistent Rows

There are 18 sign-inconsistent primitive rows. All are positive-harmless rows with:

\[
E_\theta(J)>0,\qquad \Delta D(J)<0,
\]

and all have:

\[
Q_{\Delta D}(J)<0.25.
\]

Thus they do not violate the positive-harmless cap, but they do show that:

\[
\Delta D<0 \iff E_\theta<0
\]

is **false as a global biconditional**.

The safer theorem target is one-sided:

\[
Q_{\Delta D}>3/4\Rightarrow E_\theta<0,
\]

plus:

\[
E_\theta>0\Rightarrow Q_{\Delta D}\le1/4,
\]

on primitive-available rows, then extend by exporting primitives for the missing rows.

## 6. Formula Status

The two-term formula is useful:

\[
Q_{\rm R2Q}
\approx
Q_{\Delta D}+Q_{\rm exc}.
\]

But because:

- coverage is only \(166/1468\);
- residual reaches \(0.02572845\);
- fractional residual reaches \(30.56\%\) on small rows;
- 1302 rows lack primitive terms;

this is not yet a complete primitive definition of \(Q_{\rm R2Q}\).

The correct status is:

\[
\boxed{
\text{RawR2Q primitive decomposition is partially validated; full export patch still needed.}
}
\]

## 7. Recommended Next Action

Do not proceed as if RawR2Q is globally proof-grade yet.

Next best move:

```text
Prime_Mesh_R2Q_RawR2Q_FullPrimitiveExport_Patch_Spec_v1.md
```

The required export should cover all 1468 rows and include:

- `D_start`;
- `D_end`;
- `DeltaD`;
- `Q_delta_D`;
- bridge path / `Q_exc`;
- residual correction terms explaining \(\epsilon\);
- explicit missing-data reason for any row that cannot export these primitives.

After that, rerun the primitive decomposition audit and require:

\[
\text{primitive coverage}=1468/1468
\]

or a theorem-grade reason why the missing rows are outside the primitive domain.

---

*Prime Mesh Theory - RH Programme*
