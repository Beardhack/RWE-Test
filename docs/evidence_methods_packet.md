# Evidence and Methods Packet

## Scope and data-status note

The requested Life Science Research plugin was checked first through the local MCP/plugin resource interfaces, but no Life Science Research resources were configured in this container. I therefore used public ClinicalTrials.gov and literature sources for the evidence context and implemented the requested local methods demo in code. No CMS Synthetic Medicare RIF files were present in the repository, so the analysis generates a clearly labeled synthetic Medicare-claims-like cohort.

All analytic estimates below are a methodology demonstration using synthetic data and must not be interpreted as clinical evidence.

## 1. Normalized terminology

| Concept | Normalized term | Common synonyms and operational labels |
|---|---|---|
| Disease | Type 2 diabetes mellitus (T2DM) | Type 2 diabetes; diabetes mellitus, type 2; synthetic ICD label `E11.9` |
| Exposure 1 | Glucagon-like peptide-1 receptor agonist (GLP-1 RA) initiation | GLP-1 receptor agonists; GLP-1RA; semaglutide, liraglutide, dulaglutide, exenatide |
| Exposure 2 | Dipeptidyl peptidase-4 inhibitor (DPP-4 inhibitor) initiation | DPP-4i; DPP-IV inhibitor; sitagliptin, saxagliptin, linagliptin, alogliptin |
| Outcome | 12-month all-cause hospitalization | Any inpatient admission within 365 days after treatment initiation |
| Design | New-user, active-comparator target trial emulation | First eligible dispensing defines index date and treatment assignment |

## 2. Clinical and translational evidence context

ClinicalTrials.gov includes head-to-head glycemic efficacy trials and comparative diabetes medication trials that inform the plausibility and comparator choice for a GLP-1 RA versus DPP-4 inhibitor emulation. The SUSTAIN Japan study compared once-weekly semaglutide with sitagliptin in Japanese participants with type 2 diabetes (NCT02254291). GRADE compared major glucose-lowering medications added to metformin and included sitagliptin as the DPP-4 inhibitor arm (NCT01794143). A dulaglutide/sitagliptin study (NCT01408888) evaluated pharmacokinetic and safety questions relevant to the two incretin-based classes.

The translational context is that GLP-1 RAs and DPP-4 inhibitors both affect incretin biology, but they differ in route of administration, weight effects, cardio-renal evidence, contraindications, prescribing channeling, adherence patterns, and patient selection. Observational comparative effectiveness literature therefore commonly uses an active comparator, new-user design and propensity-score methods.

A 2020 Cardiovascular Diabetology cohort study from North-East Italy directly compared new initiators of GLP-1 RAs versus DPP-4 inhibitors in routine care. It used propensity-score matching, defined the first GLP-1 RA or DPP-4 inhibitor prescription as index date, and reported lower rates of major cardiovascular outcomes among GLP-1 RA initiators after balancing. The article explicitly noted that cardiovascular outcome trials had shown benefits for some GLP-1 RAs but not DPP-4 inhibitors, and that no trial had directly compared the two classes for cardiovascular outcomes.

A multinational LEGEND-T2DM analysis and more recent U.S. semaglutide-versus-DPP-4 inhibitor observational work further support the relevance of active-comparator RWE designs for second-line diabetes therapies, health-care utilization, cardiovascular outcomes, and hospitalization-related endpoints. These sources are used only to motivate design choices; this repository does not reproduce their clinical findings.

Key sources consulted:

- ClinicalTrials.gov NCT02254291, semaglutide versus sitagliptin in type 2 diabetes: https://clinicaltrials.gov/study/NCT02254291
- ClinicalTrials.gov NCT01794143, GRADE comparative diabetes medication trial: https://clinicaltrials.gov/study/NCT01794143
- ClinicalTrials.gov NCT01408888, dulaglutide and sitagliptin study: https://clinicaltrials.gov/study/NCT01408888
- Longato et al., Cardiovascular Diabetology 2020: https://link.springer.com/article/10.1186/s12933-020-01049-w
- LEGEND-T2DM comparative effectiveness analysis: https://pmc.ncbi.nlm.nih.gov/articles/PMC12045554/
- U.S. semaglutide versus DPP-4 inhibitor observational study record: https://pubmed.ncbi.nlm.nih.gov/39688779/

## 3. Confounders an epidemiologist would expect

The demo measures or proxies the following confounding domains:

- Demographics: age, sex, race/ethnicity proxy, dual-eligibility proxy, calendar year.
- Diabetes severity and treatment history: diabetes complications, insulin, metformin, sulfonylureas, SGLT2 inhibitor use.
- Cardiometabolic risk: obesity, ASCVD, heart failure, chronic kidney disease, statins, ACE inhibitor/ARB, beta blockers, loop diuretics.
- Health-care utilization and access: prior hospitalization, emergency department use, endocrinology visit proxy.
- Prescribing-channeling risks: GLP-1 RA users may be younger, more obese, more likely to see endocrinology, and less frail; DPP-4 inhibitor users may have more kidney disease, frailty, or simpler oral-medication preference.

Important unmeasured confounders in many claims-only settings include HbA1c, BMI values, smoking, diabetes duration, eGFR lab values, blood pressure, socioeconomic status beyond dual eligibility, formulary restrictions, contraindications, patient preference, and prescriber preference.

## 4. Target trial emulation design risks

- Immortal time bias if follow-up starts before the dispensing that defines treatment assignment.
- Prevalent-user bias if baseline users of either class are included.
- Depletion of susceptibles if long-term tolerated users are mixed with initiators.
- Confounding by indication, frailty, obesity, cardio-renal risk, access, and prescriber preference.
- Misclassification from samples, inpatient administrations, pharmacy reversals, or incomplete capture outside coverage.
- Treatment switching, augmentation, discontinuation, and nonadherence.
- Informative censoring from disenrollment, death, long-term care, or Medicare Advantage enrollment in real CMS data.
- Positivity violations if one treatment is rare in subgroups such as advanced CKD or very frail patients.
- Outcome ascertainment concerns if observation windows are incomplete or if hospitalization definitions differ across data sources.
- Competing risk of death when estimating hospitalization risk in older populations.

## 5. Local reproducible methods implementation

The script `src/rwe_demo.py` performs the following steps with no third-party dependencies:

1. Generates synthetic beneficiary summary, diagnosis, pharmacy, and inpatient claims-like files.
2. Applies a new-user active-comparator cohort definition.
3. Assigns index date from the first eligible GLP-1 RA or DPP-4 inhibitor dispensing.
4. Measures baseline covariates in a 365-day lookback period.
5. Defines 365-day all-cause hospitalization as the outcome.
6. Fits a logistic propensity-score model for GLP-1 RA initiation.
7. Applies inverse-probability-of-treatment weighting with propensity-score truncation and 99th-percentile weight capping.
8. Reports standardized mean differences before and after weighting.
9. Estimates weighted 12-month risks, risk difference, risk ratio, and bootstrap risk-difference interval.
10. Writes local dashboard and output artifacts.

## 6. Demo results from the synthetic cohort

| Quantity | Value |
|---|---:|
| Eligible new users | 1,800 |
| GLP-1 RA initiators | 714 |
| DPP-4 inhibitor initiators | 1,086 |
| GLP-1 RA hospitalization events | 125 |
| DPP-4 inhibitor hospitalization events | 213 |
| Weighted GLP-1 RA risk | 18.2% |
| Weighted DPP-4 inhibitor risk | 18.6% |
| Weighted risk difference | -0.4 percentage points |
| Bootstrap 95% interval for risk difference | -3.5 to +3.3 percentage points |
| Weighted risk ratio | 0.98 |
| Maximum absolute SMD before weighting | 0.320 |
| Maximum absolute SMD after weighting | 0.017 |

These results reflect only the synthetic data-generating process embedded in the demo.

## 7. Reproducible outputs

- `data/synthetic_beneficiary_summary.csv`
- `data/synthetic_diagnosis_claims.csv`
- `data/synthetic_pharmacy_claims.csv`
- `data/synthetic_inpatient_claims.csv`
- `output/cohort.csv`
- `output/balance.csv`
- `output/results.json`
- `dashboard/index.html`

Run `python src/rwe_demo.py` from the repository root to regenerate all artifacts.
