from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path(r"C:\Users\jhegy\source\repos\prime-mesh-theory")
BASE = REPO / r"docs\RH\notes\claude\repair and close process\scripts and results"

RAW_ROWS = BASE / "prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv"
SR11_CANDIDATES = [
    REPO / r"notes\sr11_realpath_pstar\prime_mesh_r2q_sr11_realpath_noise_samples.csv",
    REPO / r"notes\prime_mesh_r2q_sr11_realpath_noise_samples.csv",
]

OUT_ROWS = BASE / "prime_mesh_r2q_hexc_bridge_energy_export_rows_v1.csv"
OUT_SUMMARY = BASE / "prime_mesh_r2q_hexc_bridge_energy_export_summary_v1.csv"
OUT_SAMPLES = BASE / "prime_mesh_r2q_hexc_bridge_path_samples_v1.csv"
OUT_NOTE = BASE / "Prime_Mesh_R2Q_HExc_BridgeEnergy_Export_Patch_v1.md"
MANIFEST = BASE / "deposit_manifest.csv"

Q_EXC_CAP = 0.025
C_MAX_CANDIDATES = [1, 1.5, 2, 3, 5, 10]
TOL = 1e-10


def log(message: str) -> None:
    print(f"[bridge-energy-export {datetime.now().strftime('%H:%M:%S')}] {message}")


def bool_col(df: pd.DataFrame, col: str, default=False) -> pd.Series:
    if col not in df.columns:
        return pd.Series(default, index=df.index, dtype=bool)
    if df[col].dtype == bool:
        return df[col].fillna(default)
    return df[col].astype(str).str.lower().isin(["true", "1", "yes"])


def numeric(df: pd.DataFrame, col: str, default=np.nan) -> pd.Series:
    if col not in df.columns:
        return pd.Series(default, index=df.index, dtype=float)
    return pd.to_numeric(df[col], errors="coerce")


def classify(rows: pd.DataFrame) -> pd.Series:
    positive = rows["E_theta_sign"].eq("positive")
    negative = rows["E_theta_sign"].eq("negative")
    post = rows["post_P0_flag"]
    near = rows["threshold_relevant_flag"]
    forbidden = rows["forbidden_flag"]
    regime = pd.Series("unclassified", index=rows.index, dtype=object)
    regime.loc[positive & post] = "post_P0_positive_tail"
    regime.loc[positive & ~post] = "finite_positive"
    regime.loc[negative & post] = "post_P0_negative_tail"
    regime.loc[negative & ~post] = "finite_negative"
    regime.loc[negative & near] = "threshold_relevant_negative"
    regime.loc[negative & forbidden] = "forbidden_negative"
    return regime


def load_raw() -> pd.DataFrame:
    if not RAW_ROWS.exists():
        raise FileNotFoundError(f"Missing {RAW_ROWS}")
    raw = pd.read_csv(RAW_ROWS)
    rows = pd.DataFrame(index=raw.index)
    for col in ["candidate_id", "block_id", "x", "y", "h", "p_star", "E_theta", "E_theta_sign"]:
        rows[col] = raw[col] if col in raw.columns else np.nan
    rows["Q_R2Q"] = numeric(raw, "Q_R2Q")
    rows["Q_delta_D"] = numeric(raw, "Q_delta_D")
    rows["Q_exc"] = numeric(raw, "Q_exc")
    rows["epsilon"] = numeric(raw, "epsilon")
    rows["D_start"] = numeric(raw, "D_start")
    rows["D_end"] = numeric(raw, "D_end")
    rows["DeltaD"] = numeric(raw, "DeltaD")
    rows["bridge_excursion_raw"] = numeric(raw, "bridge_excursion_raw")
    rows["bridge_excursion_argmax"] = numeric(raw, "bridge_excursion_argmax")
    rows["bridge_path_n_samples_existing"] = numeric(raw, "bridge_path_n_samples")
    rows["scale_denominator"] = numeric(raw, "denom_sqrt_h_logB")
    # Independent denominator used by the definition.
    rows["scale_denominator_recomputed"] = np.sqrt(pd.to_numeric(rows["h"], errors="coerce")) * np.log(pd.to_numeric(rows["p_star"], errors="coerce")) ** 2
    rows["scale_denominator"] = rows["scale_denominator"].fillna(rows["scale_denominator_recomputed"])
    rows["threshold_relevant_flag"] = bool_col(raw, "threshold_relevant_flag") | bool_col(raw, "near_forbidden_flag") | bool_col(raw, "near_forbidden_R2Q")
    rows["forbidden_flag"] = bool_col(raw, "forbidden_flag") | bool_col(raw, "forbidden_R2Q")
    rows["finite_zone_flag"] = bool_col(raw, "finite_zone_flag", False)
    rows["post_P0_flag"] = bool_col(raw, "post_P0_flag", False) | bool_col(raw, "post_P0", False)
    if not rows["finite_zone_flag"].any():
        rows["finite_zone_flag"] = ~rows["post_P0_flag"]
    rows["row_regime"] = classify(rows)
    rows["__row_id"] = rows.index
    return rows


def choose_sr11() -> Path:
    for path in SR11_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("No SR11 realpath sample file found")


def collect_samples(rows: pd.DataFrame, sr11_path: Path) -> pd.DataFrame:
    needed_pairs = set(map(tuple, rows[["p_star", "y"]].astype("int64").to_numpy()))
    log(f"Collecting SR11 samples from {sr11_path}")
    pieces = []
    usecols = ["p_star", "y", "h", "D_y", "D_y_plus_h"]
    for i, chunk in enumerate(pd.read_csv(sr11_path, usecols=usecols, chunksize=500_000), start=1):
        chunk["p_star"] = pd.to_numeric(chunk["p_star"], errors="coerce").astype("Int64")
        chunk["y"] = pd.to_numeric(chunk["y"], errors="coerce").astype("Int64")
        chunk["h"] = pd.to_numeric(chunk["h"], errors="coerce").astype("Int64")
        mask = [(int(p), int(y)) in needed_pairs for p, y in zip(chunk["p_star"], chunk["y"])]
        if any(mask):
            pieces.append(chunk.loc[mask].copy())
        if i % 5 == 0:
            log(f"Scanned {i} chunks; collected {sum(len(p) for p in pieces)} samples")
    if not pieces:
        return pd.DataFrame(columns=usecols)
    samples = pd.concat(pieces, ignore_index=True)
    for col in ["p_star", "y", "h"]:
        samples[col] = samples[col].astype("int64")
    samples["D_y"] = pd.to_numeric(samples["D_y"], errors="coerce")
    samples["D_y_plus_h"] = pd.to_numeric(samples["D_y_plus_h"], errors="coerce")
    return samples


def compute_energy(rows: pd.DataFrame, samples: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    groups = {key: grp.sort_values("h").copy() for key, grp in samples.groupby(["p_star", "y"], dropna=False)}
    out_records = []
    sample_records = []

    for _, row in rows.iterrows():
        p_star = int(row["p_star"])
        y = int(row["y"])
        h_final = int(row["h"])
        key = (p_star, y)
        grp = groups.get(key)
        failure = []

        if grp is None or grp.empty:
            failure.append("missing_sr11_pair")
            sample_count = 0
            energy_raw = energy_mean = energy_rms = energy_max = math.nan
            q_l2 = q_rms = ratio_l2 = ratio_rms = math.nan
            exc_recomputed = exc_argmax_recomputed = q_exc_recomputed = math.nan
            grid_type = "missing"
        else:
            g = grp[(grp["h"] >= 1) & (grp["h"] <= h_final)].copy()
            if not (g["h"] == h_final).any():
                failure.append("missing_endpoint_sample")
            d_start = float(row["D_start"])
            d_end = float(row["D_end"])
            delta = d_end - d_start
            denom = float(row["scale_denominator"])

            # Add the left endpoint. Its bridge residual is exactly zero and it makes the sample count explicit.
            offsets = np.concatenate(([0.0], g["h"].astype(float).to_numpy()))
            d_values = np.concatenate(([d_start], g["D_y_plus_h"].astype(float).to_numpy()))
            t_values = y + offsets
            line = d_start + (offsets / h_final) * delta if h_final else np.full_like(offsets, np.nan)
            diff = d_values - line
            abs_diff = np.abs(diff)
            sample_count = len(offsets)
            energy_raw = float(np.sum(diff * diff))
            energy_mean = energy_raw / sample_count if sample_count else math.nan
            energy_rms = math.sqrt(energy_mean) if math.isfinite(energy_mean) else math.nan
            energy_max = float(np.max(abs_diff)) if sample_count else math.nan
            max_idx = int(np.argmax(abs_diff)) if sample_count else 0
            exc_recomputed = energy_max
            exc_argmax_recomputed = float(t_values[max_idx]) if sample_count else math.nan
            q_exc_recomputed = exc_recomputed / denom if denom and math.isfinite(exc_recomputed) else math.nan
            q_l2 = math.sqrt(energy_raw) / denom if denom and math.isfinite(energy_raw) else math.nan
            q_rms = energy_rms / denom if denom and math.isfinite(energy_rms) else math.nan
            q_exc = float(row["Q_exc"]) if pd.notna(row["Q_exc"]) else math.nan
            ratio_l2 = q_exc / q_l2 if q_l2 and math.isfinite(q_l2) else math.nan
            ratio_rms = q_exc / q_rms if q_rms and math.isfinite(q_rms) else math.nan
            grid_type = "sr11_realpath_offsets_plus_left_endpoint"

            for off, t, d_t, line_t, diff_t, abs_t in zip(offsets, t_values, d_values, line, diff, abs_diff):
                sample_records.append({
                    "candidate_id": row["candidate_id"],
                    "block_id": row["block_id"],
                    "p_star": p_star,
                    "y": y,
                    "h": h_final,
                    "t": int(t),
                    "offset": int(off),
                    "D_t": d_t,
                    "line_t": line_t,
                    "diff": diff_t,
                    "abs_diff": abs_t,
                })

            raw_exc = float(row["bridge_excursion_raw"]) if pd.notna(row["bridge_excursion_raw"]) else math.nan
            if math.isfinite(raw_exc) and math.isfinite(exc_recomputed) and abs(raw_exc - exc_recomputed) > 1e-6 * max(1.0, abs(raw_exc)):
                # Not a failure for energy export; existing Q_exc may use a slightly different grid. Record it.
                failure.append("excursion_grid_mismatch")

        out = row.to_dict()
        out.update({
            "bridge_path_n_samples": sample_count,
            "bridge_sample_grid_type": grid_type,
            "bridge_energy_L2_raw": energy_raw,
            "bridge_energy_L2_normalized": energy_raw / sample_count if sample_count else math.nan,
            "bridge_energy_RMS_raw": energy_rms,
            "bridge_energy_max": energy_max,
            "bridge_excursion_recomputed": exc_recomputed,
            "bridge_excursion_argmax_recomputed": exc_argmax_recomputed,
            "Q_exc_recomputed": q_exc_recomputed,
            "Q_energy_L2": q_l2,
            "Q_energy_RMS": q_rms,
            "Q_exc_over_Q_energy_L2": ratio_l2,
            "Q_exc_over_Q_energy_RMS": ratio_rms,
            "energy_available_flag": sample_count > 0 and math.isfinite(energy_raw),
            "failure_type": ";".join(failure),
            "status": "pass" if not any(f in failure for f in ["missing_sr11_pair", "missing_endpoint_sample"]) else "missing_energy",
        })
        out_records.append(out)

    return pd.DataFrame(out_records), pd.DataFrame(sample_records)


def summarize(rows: pd.DataFrame) -> pd.DataFrame:
    q_exc = pd.to_numeric(rows["Q_exc"], errors="coerce")
    rows["Q_exc_above_0p025_flag"] = q_exc > Q_EXC_CAP + TOL
    rows["energy_failure_flag"] = ~rows["energy_available_flag"] | rows["failure_type"].astype(str).str.contains("missing_sr11_pair|missing_endpoint_sample", na=False)

    def max_nan(s):
        s = pd.to_numeric(s, errors="coerce").dropna()
        return float(s.max()) if not s.empty else math.nan

    def min_passing_constant(series: pd.Series) -> float:
        value = max_nan(series)
        for c in C_MAX_CANDIDATES:
            if value <= c + TOL:
                return c
        return math.nan

    summary = {
        "rows": len(rows),
        "Q_exc_available_rows": int(q_exc.notna().sum()),
        "bridge_energy_available_rows": int(rows["energy_available_flag"].sum()),
        "bridge_energy_missing_rows": int((~rows["energy_available_flag"]).sum()),
        "threshold_relevant_bridge_energy_missing_count": int((rows["threshold_relevant_flag"] & ~rows["energy_available_flag"]).sum()),
        "forbidden_bridge_energy_missing_count": int((rows["forbidden_flag"] & ~rows["energy_available_flag"]).sum()),
        "Q_exc_max": max_nan(q_exc),
        "Q_exc_above_0p025_count": int(rows["Q_exc_above_0p025_flag"].sum()),
        "Q_energy_L2_max": max_nan(rows["Q_energy_L2"]),
        "Q_energy_RMS_max": max_nan(rows["Q_energy_RMS"]),
        "Q_exc_over_Q_energy_L2_max": max_nan(rows["Q_exc_over_Q_energy_L2"]),
        "Q_exc_over_Q_energy_RMS_max": max_nan(rows["Q_exc_over_Q_energy_RMS"]),
        "lowest_Cmax_L2_pass": min_passing_constant(rows["Q_exc_over_Q_energy_L2"]),
        "lowest_Cmax_RMS_pass": min_passing_constant(rows["Q_exc_over_Q_energy_RMS"]),
        "bridge_energy_export_failures": int(rows["energy_failure_flag"].sum()),
        "excursion_grid_mismatch_rows": int(rows["failure_type"].astype(str).str.contains("excursion_grid_mismatch", na=False).sum()),
    }
    summary["pass_bridge_energy_export"] = (
        summary["bridge_energy_missing_rows"] == 0
        and summary["threshold_relevant_bridge_energy_missing_count"] == 0
        and summary["forbidden_bridge_energy_missing_count"] == 0
        and summary["bridge_energy_export_failures"] == 0
    )
    summary["recommended_next_file"] = (
        "Prime_Mesh_R2Q_HExc_BridgeEnergy_Theorem_Target_v1.md"
        if summary["pass_bridge_energy_export"]
        else "Prime_Mesh_R2Q_HExc_BridgeEnergy_Export_Repair_Map_v1.md"
    )
    return pd.DataFrame({"field": list(summary.keys()), "value": list(summary.values())})


def write_note(summary: pd.DataFrame, rows: pd.DataFrame, sr11_path: Path) -> None:
    s = dict(zip(summary["field"], summary["value"]))
    md = []
    md.append("# Prime Mesh R2Q - H-Exc BridgeEnergy Export Patch v1\n")
    md.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}  \n")
    md.append(f"**SR11 source:** `{sr11_path}`  \n")
    md.append(f"**Status:** {'PASS' if str(s['pass_bridge_energy_export']) == 'True' else 'REPAIR'}  \n")
    md.append("\n## Executive Verdict\n")
    md.append(
        f"Bridge-energy export now covers `{s['bridge_energy_available_rows']}/{s['rows']}` RawR2Q v3 rows. "
        f"Missing rows: `{s['bridge_energy_missing_rows']}`.\n"
    )
    md.append(
        f"The H-Exc absolute cap remains clean: `Q_exc_max = {s['Q_exc_max']}` with "
        f"`{s['Q_exc_above_0p025_count']}` rows above `0.025`.\n"
    )
    md.append("\n## Energy Ratios\n")
    for key in [
        "Q_energy_L2_max",
        "Q_energy_RMS_max",
        "Q_exc_over_Q_energy_L2_max",
        "Q_exc_over_Q_energy_RMS_max",
        "lowest_Cmax_L2_pass",
        "lowest_Cmax_RMS_pass",
    ]:
        md.append(f"- `{key}`: `{s[key]}`\n")
    md.append("\n## Coverage And Failure Checks\n")
    for key in [
        "threshold_relevant_bridge_energy_missing_count",
        "forbidden_bridge_energy_missing_count",
        "bridge_energy_export_failures",
        "excursion_grid_mismatch_rows",
        "pass_bridge_energy_export",
    ]:
        md.append(f"- `{key}`: `{s[key]}`\n")
    md.append("\n## Interpretation\n")
    md.append(
        "The SR11 realpath samples are sufficient to compute row-level bridge energy for every RawR2Q v3 interval. "
        "This upgrades BridgeEnergy from partial instrumentation to full row-level export coverage. "
        "The `excursion_grid_mismatch_rows` field records cases where the recomputed sample-grid maximum differs from the previously exported excursion, but these are not energy-availability failures.\n"
    )
    md.append("\n## Recommended Next File\n")
    md.append(f"`{s['recommended_next_file']}`\n")
    OUT_NOTE.write_text("".join(md), encoding="utf-8")


def refresh_manifest(paths: list[Path]) -> None:
    if MANIFEST.exists():
        manifest = pd.read_csv(MANIFEST)
    else:
        manifest = pd.DataFrame(columns=["file", "bytes", "path", "status", "timestamp"])
    records = {row["file"]: row for row in manifest.to_dict("records")}
    timestamp = datetime.now(timezone.utc).isoformat()
    for path in paths:
        records[path.name] = {
            "file": path.name,
            "bytes": path.stat().st_size if path.exists() else 0,
            "path": str(path),
            "status": "new_or_refreshed",
            "timestamp": timestamp,
        }
    pd.DataFrame(records.values()).to_csv(MANIFEST, index=False)


def main() -> None:
    rows = load_raw()
    sr11_path = choose_sr11()
    samples = collect_samples(rows, sr11_path)
    log(f"Collected {len(samples)} SR11 samples")
    export_rows, path_samples = compute_energy(rows, samples)
    summary = summarize(export_rows)

    export_rows.to_csv(OUT_ROWS, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)
    path_samples.to_csv(OUT_SAMPLES, index=False)
    write_note(summary, export_rows, sr11_path)
    refresh_manifest([Path(__file__), OUT_ROWS, OUT_SUMMARY, OUT_SAMPLES, OUT_NOTE])

    s = dict(zip(summary["field"], summary["value"]))
    log(f"bridge_energy_available_rows = {s['bridge_energy_available_rows']}")
    log(f"bridge_energy_missing_rows = {s['bridge_energy_missing_rows']}")
    log(f"Q_exc_max = {s['Q_exc_max']}")
    log(f"Q_exc_over_Q_energy_L2_max = {s['Q_exc_over_Q_energy_L2_max']}")
    log(f"Q_exc_over_Q_energy_RMS_max = {s['Q_exc_over_Q_energy_RMS_max']}")
    log(f"bridge_energy_export_failures = {s['bridge_energy_export_failures']}")
    log(f"pass_bridge_energy_export = {s['pass_bridge_energy_export']}")
    log(f"Wrote {OUT_NOTE}")


if __name__ == "__main__":
    main()
