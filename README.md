# RWE Methods Demo: GLP-1 RA vs DPP-4 Inhibitors

This repository contains a reproducible **real-world evidence (RWE) methods demonstration** for an epidemiologist evaluating the question:

> Among adults with type 2 diabetes, compare new users of GLP-1 receptor agonists versus DPP-4 inhibitors and estimate 12-month all-cause hospitalization risk.

The analysis uses a clearly labeled synthetic Medicare-claims-like cohort generated locally. Results are for methodology demonstration only and are **not clinical evidence**.

## Contents

- `docs/evidence_methods_packet.md` — normalized terminology, clinical/translational evidence context, confounders, target-trial emulation risks, protocol, and demo results.
- `docs/target_trial_protocol.md` — concise target-trial-style protocol.
- `src/rwe_demo.py` — dependency-free Python pipeline that generates synthetic source claims, constructs cohorts, estimates propensity scores, checks balance, and estimates treatment effects.
- `dashboard/index.html` — local static dashboard with methods, cohort counts, balance diagnostics, and effect estimates.
- `output/` — generated CSV/JSON artifacts from the reproducible demo run.

## Quick start

```bash
python src/rwe_demo.py
python -m http.server 8000 --directory dashboard
```

Open <http://localhost:8000> to view the dashboard.

## Reproducibility

The script uses only the Python standard library and a fixed random seed. It regenerates all synthetic data and output artifacts from scratch.

## Important limitation

This is a methods demo built from synthetic/public-demo-style data. It is suitable for demonstrating study design and analytic workflow, not for inference about GLP-1 receptor agonists, DPP-4 inhibitors, or hospitalization risk in real patients.
