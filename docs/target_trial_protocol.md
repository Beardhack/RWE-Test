# Target Trial Protocol: Synthetic RWE Methods Demo

## Research question

Among adults with type 2 diabetes mellitus (T2DM), what is the 12-month risk of all-cause hospitalization after initiating a glucagon-like peptide-1 receptor agonist (GLP-1 RA) compared with initiating a dipeptidyl peptidase-4 inhibitor (DPP-4 inhibitor)?

## Eligibility criteria

Eligible patients are synthetic beneficiaries who meet all criteria at treatment initiation:

1. Age 18 years or older.
2. At least one diagnosis code consistent with T2DM during the 365-day baseline period.
3. Continuous medical and pharmacy enrollment during baseline.
4. No dispensing for either comparator class during baseline, operationalizing a new-user design.
5. No inpatient hospitalization on the index date.

## Treatment strategies

- Strategy A: initiate a GLP-1 RA, represented by semaglutide, liraglutide, dulaglutide, or exenatide ingredient labels in the synthetic pharmacy file.
- Strategy B: initiate a DPP-4 inhibitor, represented by sitagliptin, saxagliptin, linagliptin, or alogliptin ingredient labels in the synthetic pharmacy file.

## Assignment and index date

The index date is the first eligible dispensing for either comparator class during the accrual window. Patients are assigned to the class dispensed on the index date. Patients initiating both classes on the same date are excluded.

## Baseline covariates

Baseline covariates are measured during the 365 days before index and include demographics, dual-eligibility proxy, calendar quarter, diabetes complications, obesity, chronic kidney disease, heart failure, atherosclerotic cardiovascular disease, prior inpatient use, emergency department use, endocrinology visit proxy, and baseline use of metformin, insulin, sulfonylureas, SGLT2 inhibitors, statins, ACE inhibitors or ARBs, beta blockers, and loop diuretics.

## Follow-up

Follow-up begins the day after index and continues until the earliest of outcome occurrence, disenrollment, death proxy, treatment discontinuation proxy, treatment switch or augmentation with the comparator class, 365 days, or end of available data. The primary estimand in this simplified demo is the 12-month intention-to-treat-style risk difference using complete 365-day synthetic follow-up; censoring indicators are still generated for protocol transparency.

## Outcome

The outcome is all-cause inpatient hospitalization within 365 days after index, defined by at least one synthetic inpatient admission claim after index and on or before day 365.

## Causal contrast and analysis

The primary contrast is the average treatment effect comparing GLP-1 RA initiation with DPP-4 inhibitor initiation. The demo estimates propensity scores with a dependency-free logistic model, applies inverse-probability-of-treatment weights with propensity-score truncation, reports standardized mean differences before and after weighting, and estimates weighted 12-month risks, risk difference, risk ratio, and a bootstrap confidence interval.

## Interpretation

All outputs are generated from synthetic data and are intended only to demonstrate reproducible RWE methodology.
