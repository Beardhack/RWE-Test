#!/usr/bin/env python3
"""Reproducible synthetic claims-like RWE methods demo.

This script intentionally uses only the Python standard library so the demo can run
in minimal environments. It creates synthetic Medicare/RIF-like source files,
constructs a new-user active-comparator cohort, estimates propensity scores,
checks covariate balance, and writes a local static dashboard.
"""

from __future__ import annotations

import csv
import json
import math
import random
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "output"
DASHBOARD = ROOT / "dashboard"
SEED = 20260513
N_BENEFICIARIES = 1800
BOOTSTRAPS = 100

GLP1_INGREDIENTS = ["semaglutide", "liraglutide", "dulaglutide", "exenatide"]
DPP4_INGREDIENTS = ["sitagliptin", "saxagliptin", "linagliptin", "alogliptin"]
OTHER_INGREDIENTS = ["metformin", "insulin", "sulfonylurea", "sglt2_inhibitor", "statin", "ace_arb", "beta_blocker", "loop_diuretic"]

COVARIATES = [
    "age", "female", "black", "hispanic", "dual_eligible", "index_year_2021", "index_year_2022",
    "obesity", "ckd", "heart_failure", "ascvd", "diabetes_complication", "prior_hosp",
    "ed_visit", "endocrinology_visit", "metformin", "insulin", "sulfonylurea", "sglt2_inhibitor",
    "statin", "ace_arb", "beta_blocker", "loop_diuretic",
]

@dataclass
class Person:
    bene_id: str
    age: int
    sex: str
    race: str
    dual_eligible: int
    t2dm: int
    obesity: int
    ckd: int
    heart_failure: int
    ascvd: int
    diabetes_complication: int
    prior_hosp: int
    ed_visit: int
    endocrinology_visit: int
    metformin: int
    insulin: int
    sulfonylurea: int
    sglt2_inhibitor: int
    statin: int
    ace_arb: int
    beta_blocker: int
    loop_diuretic: int
    index_date: str
    exposure: str
    censor_day: int
    outcome_hosp_365: int


def expit(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1 / (1 + z)
    z = math.exp(x)
    return z / (1 + z)


def bern(rng: random.Random, p: float) -> int:
    return int(rng.random() < max(0.0, min(1.0, p)))


def choice_weighted(rng: random.Random, pairs):
    total = sum(w for _, w in pairs)
    draw = rng.random() * total
    acc = 0.0
    for value, weight in pairs:
        acc += weight
        if draw <= acc:
            return value
    return pairs[-1][0]


def generate_people() -> list[Person]:
    rng = random.Random(SEED)
    people: list[Person] = []
    start = date(2020, 1, 1)
    for i in range(N_BENEFICIARIES):
        age = int(max(35, min(94, rng.gauss(72, 9))))
        female = bern(rng, 0.55)
        race = choice_weighted(rng, [("white", 0.66), ("black", 0.16), ("hispanic", 0.11), ("other", 0.07)])
        dual = bern(rng, 0.18 + 0.08 * (race in {"black", "hispanic"}))
        obesity = bern(rng, 0.36 - 0.003 * (age - 70) + 0.05 * female)
        ckd = bern(rng, 0.18 + 0.006 * (age - 65) + 0.08 * dual)
        hf = bern(rng, 0.12 + 0.007 * (age - 65) + 0.18 * ckd)
        ascvd = bern(rng, 0.20 + 0.008 * (age - 65) + 0.08 * hf)
        comp = bern(rng, 0.28 + 0.10 * ckd)
        prior_hosp = bern(rng, 0.16 + 0.12 * hf + 0.10 * ckd + 0.08 * dual)
        ed = bern(rng, 0.24 + 0.12 * prior_hosp + 0.06 * dual)
        endo = bern(rng, 0.18 + 0.10 * obesity - 0.04 * dual)
        metformin = bern(rng, 0.68 - 0.12 * ckd)
        insulin = bern(rng, 0.24 + 0.10 * comp + 0.06 * ckd)
        sulfonyl = bern(rng, 0.22 + 0.06 * dual)
        sglt2 = bern(rng, 0.14 + 0.05 * ascvd - 0.06 * ckd)
        statin = bern(rng, 0.62 + 0.14 * ascvd)
        ace = bern(rng, 0.54 + 0.14 * ckd + 0.10 * hf)
        beta = bern(rng, 0.38 + 0.18 * ascvd + 0.14 * hf)
        loop = bern(rng, 0.12 + 0.24 * hf + 0.10 * ckd)

        # Channeling: GLP-1 RA users are somewhat younger, more obese, more often seeing endocrinology,
        # and less likely to have frailty-like utilization than DPP-4 inhibitor users.
        p_glp1 = expit(-0.55 - 0.018 * (age - 70) + 0.60 * obesity + 0.42 * endo + 0.25 * sglt2 - 0.32 * ckd - 0.25 * prior_hosp - 0.18 * dual)
        exposure = "GLP1_RA" if bern(rng, p_glp1) else "DPP4_INHIBITOR"
        index_dt = start + timedelta(days=rng.randint(365, 365 * 3 - 1))

        # Synthetic true hospitalization risk. A modest protective synthetic effect is embedded so
        # the estimator has something to recover; this is not calibrated clinical evidence.
        risk = expit(-1.75 + 0.018 * (age - 70) + 0.36 * ckd + 0.60 * hf + 0.28 * ascvd + 0.42 * prior_hosp + 0.22 * ed + 0.18 * dual + 0.18 * insulin - 0.16 * (exposure == "GLP1_RA"))
        outcome = bern(rng, risk)
        censor_day = min(365, max(30, int(rng.expovariate(1 / 650))))
        if censor_day < 365 and rng.random() < 0.45:
            outcome = 0

        people.append(Person(
            bene_id=f"B{i + 1:06d}", age=age, sex="F" if female else "M", race=race, dual_eligible=dual,
            t2dm=1, obesity=obesity, ckd=ckd, heart_failure=hf, ascvd=ascvd, diabetes_complication=comp,
            prior_hosp=prior_hosp, ed_visit=ed, endocrinology_visit=endo, metformin=metformin,
            insulin=insulin, sulfonylurea=sulfonyl, sglt2_inhibitor=sglt2, statin=statin,
            ace_arb=ace, beta_blocker=beta, loop_diuretic=loop, index_date=index_dt.isoformat(),
            exposure=exposure, censor_day=censor_day, outcome_hosp_365=outcome,
        ))
    return people


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_synthetic_sources(people: list[Person]) -> None:
    rng = random.Random(SEED + 1)
    bene_rows = []
    dx_rows = []
    rx_rows = []
    ip_rows = []
    for p in people:
        idx = date.fromisoformat(p.index_date)
        bene_rows.append({"bene_id": p.bene_id, "birth_year": idx.year - p.age, "sex": p.sex, "race": p.race, "dual_eligible": p.dual_eligible, "enroll_start": (idx - timedelta(days=400)).isoformat(), "enroll_end": (idx + timedelta(days=400)).isoformat()})
        dx_rows.append({"bene_id": p.bene_id, "claim_date": (idx - timedelta(days=rng.randint(30, 360))).isoformat(), "setting": "carrier", "code": "E11.9", "label": "type 2 diabetes mellitus"})
        for name in ["obesity", "ckd", "heart_failure", "ascvd", "diabetes_complication"]:
            if getattr(p, name):
                dx_rows.append({"bene_id": p.bene_id, "claim_date": (idx - timedelta(days=rng.randint(1, 365))).isoformat(), "setting": "carrier", "code": name.upper(), "label": name.replace("_", " ")})
        ingredient = rng.choice(GLP1_INGREDIENTS if p.exposure == "GLP1_RA" else DPP4_INGREDIENTS)
        rx_rows.append({"bene_id": p.bene_id, "fill_date": p.index_date, "ingredient": ingredient, "drug_class": p.exposure, "days_supply": 30})
        for med in OTHER_INGREDIENTS:
            if getattr(p, med):
                rx_rows.append({"bene_id": p.bene_id, "fill_date": (idx - timedelta(days=rng.randint(1, 365))).isoformat(), "ingredient": med, "drug_class": "baseline_med", "days_supply": 30})
        if p.prior_hosp:
            ip_rows.append({"bene_id": p.bene_id, "admit_date": (idx - timedelta(days=rng.randint(1, 365))).isoformat(), "discharge_date": (idx - timedelta(days=rng.randint(0, 364))).isoformat(), "period": "baseline"})
        if p.outcome_hosp_365:
            admit = idx + timedelta(days=rng.randint(1, 365))
            ip_rows.append({"bene_id": p.bene_id, "admit_date": admit.isoformat(), "discharge_date": (admit + timedelta(days=rng.randint(1, 7))).isoformat(), "period": "followup"})
    write_csv(DATA / "synthetic_beneficiary_summary.csv", bene_rows, list(bene_rows[0]))
    write_csv(DATA / "synthetic_diagnosis_claims.csv", dx_rows, list(dx_rows[0]))
    write_csv(DATA / "synthetic_pharmacy_claims.csv", rx_rows, list(rx_rows[0]))
    write_csv(DATA / "synthetic_inpatient_claims.csv", ip_rows, list(ip_rows[0]))


def design_matrix(people: list[Person]) -> tuple[list[list[float]], list[int]]:
    rows = []
    y = []
    for p in people:
        idx_year = date.fromisoformat(p.index_date).year
        row = []
        for c in COVARIATES:
            if c == "female":
                row.append(1.0 if p.sex == "F" else 0.0)
            elif c == "black":
                row.append(1.0 if p.race == "black" else 0.0)
            elif c == "hispanic":
                row.append(1.0 if p.race == "hispanic" else 0.0)
            elif c == "index_year_2021":
                row.append(1.0 if idx_year == 2021 else 0.0)
            elif c == "index_year_2022":
                row.append(1.0 if idx_year == 2022 else 0.0)
            else:
                row.append(float(getattr(p, c)))
        rows.append(row)
        y.append(1 if p.exposure == "GLP1_RA" else 0)
    return rows, y


def standardize(x: list[list[float]]) -> tuple[list[list[float]], list[float], list[float]]:
    cols = list(zip(*x))
    mus = [mean(col) for col in cols]
    sds = []
    for col, mu in zip(cols, mus):
        var = sum((v - mu) ** 2 for v in col) / max(1, len(col) - 1)
        sds.append(math.sqrt(var) or 1.0)
    return [[(v - mus[j]) / sds[j] for j, v in enumerate(row)] for row in x], mus, sds


def fit_logistic(x: list[list[float]], y: list[int], lr: float = 0.05, steps: int = 450, l2: float = 0.002) -> list[float]:
    xz, _, _ = standardize(x)
    x1 = [[1.0] + row for row in xz]
    beta = [0.0] * len(x1[0])
    n = len(y)
    for _ in range(steps):
        grad = [0.0] * len(beta)
        for row, yi in zip(x1, y):
            p = expit(sum(b * v for b, v in zip(beta, row)))
            for j, v in enumerate(row):
                grad[j] += (p - yi) * v / n
        for j in range(1, len(beta)):
            grad[j] += l2 * beta[j]
        for j in range(len(beta)):
            beta[j] -= lr * grad[j]
    return beta


def predict_ps(x: list[list[float]], beta: list[float]) -> list[float]:
    xz, _, _ = standardize(x)
    ps = []
    for row in xz:
        p = expit(beta[0] + sum(b * v for b, v in zip(beta[1:], row)))
        ps.append(min(0.975, max(0.025, p)))
    return ps


def weighted_mean(vals, weights):
    return sum(v * w for v, w in zip(vals, weights)) / sum(weights)


def smd(vals, treat, weights=None):
    if weights is None:
        weights = [1.0] * len(vals)
    vt = [v for v, t in zip(vals, treat) if t == 1]
    vc = [v for v, t in zip(vals, treat) if t == 0]
    wt = [w for w, t in zip(weights, treat) if t == 1]
    wc = [w for w, t in zip(weights, treat) if t == 0]
    mt = weighted_mean(vt, wt)
    mc = weighted_mean(vc, wc)
    def wvar(vs, ws, m):
        return sum(w * (v - m) ** 2 for v, w in zip(vs, ws)) / sum(ws)
    pooled = math.sqrt(max(1e-9, (wvar(vt, wt, mt) + wvar(vc, wc, mc)) / 2))
    return (mt - mc) / pooled


def estimate(people: list[Person], ps: list[float], sample_idx=None) -> dict:
    idxs = sample_idx if sample_idx is not None else range(len(people))
    y = [people[i].outcome_hosp_365 for i in idxs]
    t = [1 if people[i].exposure == "GLP1_RA" else 0 for i in idxs]
    p = [ps[i] for i in idxs]
    weights = [(1 / pp if tt else 1 / (1 - pp)) for tt, pp in zip(t, p)]
    cap = sorted(weights)[int(0.99 * (len(weights) - 1))]
    weights = [min(w, cap) for w in weights]
    rt = weighted_mean([yy for yy, tt in zip(y, t) if tt], [ww for ww, tt in zip(weights, t) if tt])
    rc = weighted_mean([yy for yy, tt in zip(y, t) if not tt], [ww for ww, tt in zip(weights, t) if not tt])
    return {"risk_glp1": rt, "risk_dpp4": rc, "risk_difference": rt - rc, "risk_ratio": rt / rc if rc else None}


def build_outputs(people: list[Person]) -> dict:
    OUTPUT.mkdir(exist_ok=True)
    x, t = design_matrix(people)
    beta = fit_logistic(x, t)
    ps = predict_ps(x, beta)
    weights = [(1 / p if tr else 1 / (1 - p)) for p, tr in zip(ps, t)]
    cap = sorted(weights)[int(0.99 * (len(weights) - 1))]
    weights = [min(w, cap) for w in weights]

    cohort_rows = []
    for p, pp, w in zip(people, ps, weights):
        row = asdict(p)
        row["propensity_score"] = round(pp, 6)
        row["iptw"] = round(w, 6)
        cohort_rows.append(row)
    write_csv(OUTPUT / "cohort.csv", cohort_rows, list(cohort_rows[0]))

    balance_rows = []
    for j, cov in enumerate(COVARIATES):
        vals = [row[j] for row in x]
        balance_rows.append({"covariate": cov, "smd_unweighted": round(smd(vals, t), 4), "smd_weighted": round(smd(vals, t, weights), 4)})
    write_csv(OUTPUT / "balance.csv", balance_rows, ["covariate", "smd_unweighted", "smd_weighted"])

    results = estimate(people, ps)
    rng = random.Random(SEED + 2)
    boot = []
    n = len(people)
    for _ in range(BOOTSTRAPS):
        idxs = [rng.randrange(n) for _ in range(n)]
        boot.append(estimate(people, ps, idxs)["risk_difference"])
    boot.sort()
    ci = [boot[int(0.025 * BOOTSTRAPS)], boot[int(0.975 * BOOTSTRAPS) - 1]]
    counts = {
        "n_total": len(people),
        "n_glp1": sum(1 for p in people if p.exposure == "GLP1_RA"),
        "n_dpp4": sum(1 for p in people if p.exposure == "DPP4_INHIBITOR"),
        "events_glp1": sum(p.outcome_hosp_365 for p in people if p.exposure == "GLP1_RA"),
        "events_dpp4": sum(p.outcome_hosp_365 for p in people if p.exposure == "DPP4_INHIBITOR"),
    }
    max_smd_before = max(abs(r["smd_unweighted"]) for r in balance_rows)
    max_smd_after = max(abs(r["smd_weighted"]) for r in balance_rows)
    payload = {"counts": counts, "effect_estimates": results, "bootstrap_rd_ci": ci, "diagnostics": {"max_abs_smd_before": max_smd_before, "max_abs_smd_after": max_smd_after, "weight_cap_99pct": cap}, "seed": SEED, "bootstraps": BOOTSTRAPS}
    (OUTPUT / "results.json").write_text(json.dumps(payload, indent=2))
    write_dashboard(payload, balance_rows)
    return payload


def pct(x):
    return f"{100 * x:.1f}%"


def write_dashboard(results: dict, balance_rows: list[dict]) -> None:
    DASHBOARD.mkdir(exist_ok=True)
    bars = "\n".join(
        f'<div class="bar-row"><span>{r["covariate"]}</span><div class="bar"><i style="width:{min(100, abs(r["smd_weighted"])*400):.1f}%"></i></div><b>{r["smd_weighted"]:+.3f}</b></div>'
        for r in balance_rows
    )
    c = results["counts"]
    e = results["effect_estimates"]
    ci = results["bootstrap_rd_ci"]
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>RWE Methods Demo Dashboard</title><style>
body{{font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;margin:0;background:#f7f8fb;color:#172033}}header{{background:#18345a;color:white;padding:28px 40px}}main{{padding:28px 40px;max-width:1180px;margin:auto}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}}.card{{background:white;border:1px solid #e2e7f0;border-radius:14px;padding:18px;box-shadow:0 1px 8px #0000000c}}.metric{{font-size:34px;font-weight:800;color:#18345a}}.warn{{background:#fff4d6;border-color:#f3d37a}}table{{border-collapse:collapse;width:100%}}td,th{{padding:9px;border-bottom:1px solid #edf0f5;text-align:left}}.bar-row{{display:grid;grid-template-columns:190px 1fr 70px;gap:10px;align-items:center;margin:7px 0}}.bar{{height:12px;background:#e9eef6;border-radius:999px;overflow:hidden}}.bar i{{display:block;height:100%;background:#3178c6}}code{{background:#eef2f7;padding:2px 5px;border-radius:5px}}</style></head>
<body><header><h1>GLP-1 RA vs DPP-4 Inhibitor RWE Methods Demo</h1><p>12-month all-cause hospitalization risk in a synthetic new-user active-comparator cohort.</p></header><main>
<section class="card warn"><b>Methodology demonstration only.</b> Data are synthetic claims-like records generated with seed <code>{SEED}</code>; estimates are not clinical evidence.</section>
<h2>Cohort</h2><section class="grid"><div class="card"><div class="metric">{c['n_total']:,}</div><p>Eligible new users</p></div><div class="card"><div class="metric">{c['n_glp1']:,}</div><p>GLP-1 RA initiators</p></div><div class="card"><div class="metric">{c['n_dpp4']:,}</div><p>DPP-4 inhibitor initiators</p></div><div class="card"><div class="metric">{c['events_glp1'] + c['events_dpp4']:,}</div><p>12-month hospitalization events</p></div></section>
<h2>Weighted effect estimates</h2><section class="grid"><div class="card"><div class="metric">{pct(e['risk_glp1'])}</div><p>Weighted risk: GLP-1 RA</p></div><div class="card"><div class="metric">{pct(e['risk_dpp4'])}</div><p>Weighted risk: DPP-4 inhibitor</p></div><div class="card"><div class="metric">{100*e['risk_difference']:+.1f} pp</div><p>Risk difference; bootstrap 95% CI {100*ci[0]:+.1f} to {100*ci[1]:+.1f} pp</p></div><div class="card"><div class="metric">{e['risk_ratio']:.2f}</div><p>Risk ratio</p></div></section>
<h2>Balance diagnostics</h2><section class="card"><p>Maximum absolute SMD changed from {results['diagnostics']['max_abs_smd_before']:.3f} before weighting to {results['diagnostics']['max_abs_smd_after']:.3f} after IPTW.</p>{bars}</section>
<h2>Protocol snapshot</h2><section class="card"><table><tr><th>Component</th><th>Operational definition</th></tr><tr><td>Eligibility</td><td>Adults with baseline T2DM, continuous enrollment, and no baseline comparator-class use.</td></tr><tr><td>Index</td><td>First GLP-1 RA or DPP-4 inhibitor dispensing.</td></tr><tr><td>Outcome</td><td>Any all-cause inpatient admission within 365 days.</td></tr><tr><td>Adjustment</td><td>Propensity-score IPTW with demographics, comorbidities, utilization, and baseline medications.</td></tr></table></section>
</main></body></html>"""
    (DASHBOARD / "index.html").write_text(html)


def main() -> None:
    DATA.mkdir(exist_ok=True)
    people = generate_people()
    write_synthetic_sources(people)
    results = build_outputs(people)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
