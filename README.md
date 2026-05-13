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

## Hosting on GitHub Pages

This repo includes a GitHub Actions workflow at `.github/workflows/deploy-pages.yml` that publishes the static dashboard in `dashboard/` to GitHub Pages. The workflow regenerates the deterministic demo artifacts with `python src/rwe_demo.py`, copies the dashboard plus selected `output/` and `docs/` files into a Pages artifact, and deploys it.

To enable hosting:

1. Push this repository to GitHub on a `main` branch.
2. In GitHub, open **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to **GitHub Actions**.
4. Push to `main` or run the **Deploy RWE demo dashboard to GitHub Pages** workflow manually from the **Actions** tab.
5. After the workflow completes, the site will be available at `https://<owner>.github.io/<repo>/`.

For local preview before publishing, run:

```bash
python src/rwe_demo.py
python -m http.server 8000 --directory dashboard
```

Then open <http://localhost:8000>.

## Reproducibility

The script uses only the Python standard library and a fixed random seed. It regenerates all synthetic data and output artifacts from scratch.

## Important limitation

This is a methods demo built from synthetic/public-demo-style data. It is suitable for demonstrating study design and analytic workflow, not for inference about GLP-1 receptor agonists, DPP-4 inhibitors, or hospitalization risk in real patients.
