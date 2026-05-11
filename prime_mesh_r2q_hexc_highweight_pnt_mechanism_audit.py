"""
Prime Mesh R2Q — H-Exc High-Weight Rayleigh Collapse PNT Mechanism Audit
Adapted to use actual data columns from:
  prime_mesh_r2q_hexc_primeshock_rayleighcoupling_rows.csv

Column mapping:
  W_J  -> W  (sum of log^2 weights)
  K_prime -> K  (bridge energy)
  rho_J -> rho  (Rayleigh quotient = K/W)
  p_star -> p_star
  h -> h
  sample positions -> R_offsets (prime offset positions in block)
"""

import numpy as np
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

DATA_FILE = r"C:\Users\jhegy\source\repos\prime-mesh-theory\docs\RH\notes\claude\repair and close process\scripts and results\prime_mesh_r2q_hexc_primeshock_rayleighcoupling_rows.csv"

REGIME2_THRESHOLD = 1040.0
K_PRIME_CAP = 65.0

# ── PARSE HELPERS ─────────────────────────────────────────────────────────────

def parse_list(raw):
    if pd.isna(raw):
        return None
    s = str(raw).strip()
    if s.startswith('['):
        s = s[1:]
    if s.endswith(']'):
        s = s[:-1]
    try:
        vals = [float(x) for x in s.split(',') if x.strip()]
        return np.array(vals) if vals else None
    except ValueError:
        return None


def compute_S_T(u_arr):
    return float(np.sum(u_arr * (1.0 - u_arr)))


def classify_prime_distribution(u_primes):
    if u_primes is None or len(u_primes) == 0:
        return "unknown"
    u_sorted = np.sort(u_primes)
    n = len(u_sorted)
    expected = np.arange(1, n + 1) / n
    ks = np.max(np.abs(u_sorted - expected))
    if ks < 0.1:
        return "uniform"
    elif ks < 0.25:
        return "mildly_concentrated"
    else:
        return "concentrated"


# ── MAIN ──────────────────────────────────────────────────────────────────────

def run_audit():
    df = pd.read_csv(DATA_FILE, low_memory=False)
    print(f"Loaded {len(df)} rows from rayleighcoupling export.")

    # Map columns
    w_col     = 'W'
    k_col     = 'K'
    rho_col   = 'rho'
    pstar_col = 'p_star'
    h_col     = 'h'
    ns_col    = 'sample_count'
    kp_col    = 'prime_event_count'

    # Regime 2
    regime2 = df[df[w_col] > REGIME2_THRESHOLD].copy()
    post_p0 = df[(df[w_col] > REGIME2_THRESHOLD) & (df['post_P0_flag'] == True)].copy()
    print(f"Regime 2 (W > {REGIME2_THRESHOLD}): {len(regime2)} total, {len(post_p0)} post-P0")

    # Work with post-P0 Regime 2 (the 22 rows from the theorem)
    r2 = post_p0.copy() if len(post_p0) > 0 else regime2.copy()
    print(f"Working with {len(r2)} rows for PNT audit.")

    # log(p*)
    r2['log_p_star'] = np.log(r2[pstar_col])

    # Parse R_offsets to get u_t = offset / h (prime positions normalized to [0,1])
    r2['r_arr'] = r2['R_offsets'].apply(parse_list)

    def make_u(row):
        r = row['r_arr']
        if r is None:
            return None
        h = row[h_col]
        if h <= 0:
            return None
        u = r / h
        u = u[(u >= 0) & (u <= 1)]
        return u if len(u) > 0 else None

    r2['u_arr'] = r2.apply(make_u, axis=1)
    r2['S_T'] = r2['u_arr'].apply(lambda u: compute_S_T(u) if u is not None else np.nan)
    r2['N_s'] = r2['u_arr'].apply(lambda u: len(u) if u is not None else np.nan)

    # PNT ratios
    r2['K_prime_over_logpstar']    = r2[k_col] / r2['log_p_star']
    r2['K_prime_over_ST_logpstar'] = r2[k_col] / (r2['log_p_star'] * r2['S_T'])
    r2['PNT_prediction']           = r2['log_p_star'] * r2['S_T']
    r2['PNT_residual_ratio']       = r2[k_col] / r2['PNT_prediction']

    # k/h
    r2['k_over_h']         = r2[kp_col] / r2[h_col]
    r2['pnt_density_ratio'] = r2['k_over_h'] * r2['log_p_star']

    # Flags
    r2['anomalous']    = r2[k_col] > 3.0 * r2['log_p_star']
    r2['exceeds_cap']  = r2[k_col] > K_PRIME_CAP

    # ── TABLE ────────────────────────────────────────────────────────────────
    display_cols = [
        w_col, h_col, kp_col, pstar_col, 'log_p_star',
        k_col, rho_col, 'N_s', 'S_T',
        'K_prime_over_logpstar', 'K_prime_over_ST_logpstar',
        'PNT_prediction', 'PNT_residual_ratio',
        'k_over_h', 'pnt_density_ratio',
        'anomalous', 'exceeds_cap',
    ]
    display_cols = [c for c in display_cols if c in r2.columns]
    result = r2[display_cols].sort_values(w_col, ascending=False)

    print("\n" + "="*100)
    print("REGIME 2 POST-P0 — PNT MECHANISM AUDIT TABLE (sorted by W descending)")
    print("="*100)
    pd.set_option("display.max_columns", 30)
    pd.set_option("display.width", 220)
    pd.set_option("display.float_format", "{:.5f}".format)
    print(result.to_string(index=True))

    # ── SUMMARY ──────────────────────────────────────────────────────────────
    print("\n" + "="*100)
    print("SUMMARY STATISTICS")
    print("="*100)

    def stat_row(label, series):
        s = series.dropna()
        if len(s) == 0:
            return
        print(f"  {label:45s}  n={len(s):3d}  min={s.min():.5f}  median={s.median():.5f}  "
              f"mean={s.mean():.5f}  max={s.max():.5f}")

    stat_row("W (weight_sq_sum)",                     r2[w_col])
    stat_row("K_prime",                               r2[k_col])
    stat_row("rho_J (=K/W)",                          r2[rho_col])
    stat_row("log(p*)",                               r2['log_p_star'])
    stat_row("N_s = prime count in block",            r2['N_s'])
    stat_row("S_T = sum u(1-u) over primes",          r2['S_T'])
    stat_row("K_prime / log(p*)",                     r2['K_prime_over_logpstar'])
    stat_row("K_prime / [log(p*) * S_T]  = C?",      r2['K_prime_over_ST_logpstar'])
    stat_row("PNT prediction: log(p*)*S_T",           r2['PNT_prediction'])
    stat_row("K_prime / PNT_prediction",              r2['PNT_residual_ratio'])
    stat_row("k/h (prime density)",                   r2['k_over_h'])
    stat_row("(k/h)*log(p*) — should be ~1",          r2['pnt_density_ratio'])

    # ── LOG-LOG REGRESSION ───────────────────────────────────────────────────
    print("\n" + "="*100)
    print("LOG-LOG REGRESSION: log(K_prime) ~ a*log(log(p*)) + b*log(S_T) + c")
    print("="*100)
    reg_df = r2[[k_col, 'log_p_star', 'S_T']].dropna()
    # Filter positive values
    reg_df = reg_df[(reg_df[k_col] > 0) & (reg_df['log_p_star'] > 0) & (reg_df['S_T'] > 0)]
    if len(reg_df) >= 4:
        from numpy.linalg import lstsq
        Y = np.log(reg_df[k_col].values)
        X = np.column_stack([
            np.log(reg_df['log_p_star'].values),
            np.log(reg_df['S_T'].values),
            np.ones(len(reg_df)),
        ])
        coef, _, _, _ = lstsq(X, Y, rcond=None)
        Y_hat = X @ coef
        ss_res = np.sum((Y - Y_hat)**2)
        ss_tot = np.sum((Y - Y.mean())**2)
        r2_stat = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
        a, b, c = coef
        print(f"  log(K_prime) = {a:.4f}*log(log p*) + {b:.4f}*log(S_T) + {c:.4f}")
        print(f"  R^2 = {r2_stat:.6f}   (n={len(reg_df)})")
        print(f"  e^c = {np.exp(c):.5f}  (universal constant C estimate)")
        print()
        print("  Interpretation:")
        print(f"    a={a:.3f}: exponent on log(p*).  PNT predicts a=1.")
        print(f"    b={b:.3f}: exponent on S_T.      PNT predicts b=1.")
        print(f"    If a~1, b~1: K_prime ~ {np.exp(c):.3f} * log(p*) * S_T  [PNT confirmed]")
        print(f"    If a~1, b~0: K_prime ~ {np.exp(c):.3f} * log(p*), S_T not driving scale.")
    else:
        print(f"  Too few complete rows (need 4, have {len(reg_df)})")

    # ── WORST-CASE ROW ───────────────────────────────────────────────────────
    print("\n" + "="*100)
    print("WORST-CASE ROW (highest K_prime)")
    print("="*100)
    worst_idx = r2[k_col].idxmax()
    worst = r2.loc[worst_idx]
    for col in display_cols:
        if col in worst.index:
            print(f"  {col}: {worst[col]}")
    u = worst['u_arr']
    if u is not None:
        print(f"  u_t stats: min={u.min():.4f}  max={u.max():.4f}  mean={u.mean():.4f}  std={u.std():.4f}")
        print(f"  Prime spatial distribution: {classify_prime_distribution(u)}")

    # ── THEOREM CLOSURE CHECK ────────────────────────────────────────────────
    print("\n" + "="*100)
    print("THEOREM CLOSURE CHECK: K_prime = rho * W <= 65")
    print("="*100)
    n_exceed    = r2['exceeds_cap'].sum()
    n_anomalous = r2['anomalous'].sum()
    print(f"  Rows with K_prime > {K_PRIME_CAP}: {n_exceed}")
    print(f"  Rows with K_prime > 3*log(p*): {n_anomalous}")
    print(f"  Max K_prime: {r2[k_col].max():.6f}")
    print(f"  Max rho_J:   {r2[rho_col].max():.8f}")

    valid = r2[[rho_col, w_col]].dropna()
    valid = valid[(valid[rho_col] > 0) & (valid[w_col] > 0)]
    if len(valid) >= 2:
        corr = np.corrcoef(np.log(valid[rho_col]), np.log(valid[w_col]))[0,1]
        print(f"  corr(log rho, log W): {corr:.6f}  (expected ≈ -0.97)")

    pnt_ok = (r2['K_prime_over_logpstar'].dropna() <= 4.0).all()
    print(f"  K_prime <= 4*log(p*) for all rows: {pnt_ok}")

    print("\nDONE.")
    return r2


if __name__ == "__main__":
    result = run_audit()
