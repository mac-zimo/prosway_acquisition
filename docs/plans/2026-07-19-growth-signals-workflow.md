# Prosway Growth Signals Workflow Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Refactor the current Prosway acquisition code into configurable workflows/pipelines, then implement a new workflow that finds 50-200 employee companies with multiple growth signals indicating likely fractional HR needs.

**Architecture:** Separate immutable domain models, workflow configuration, collectors/adapters, enrichment, rule evaluation/scoring, and exporters. Each workflow declares its filters, sources, rules, scoring weights, and output schema in config/code without hard-coding business logic inside API loops or Excel generation.

**Tech Stack:** Python 3.11+, stdlib HTTP clients initially, openpyxl, existing Google Drive upload layer. Optional future adapters may use external APIs/providers for LinkedIn, job boards, funding/news, and company enrichment.

---

## Current State Diagnosis

The current solution is a useful MVP but not ready for multiple workflows:

- `api.py` mixes source access, filter generation, business constraints, deduplication, scoring inputs, and model construction.
- `config.py` contains one hard-coded MVP: Île-de-France + selected NAFs + 100-1000 employee brackets.
- `scoring.py` is segment/taille specific, not a generic rule engine.
- `workbook.py` has fixed sheets/headers tied to the current MVP.
- `pipeline.py` only runs one implicit workflow.
- No tests exist, so refactoring risks breaking behavior silently.

Blocking constraint: before adding growth-signal logic, we need a workflow abstraction and test coverage around the current behavior.

---

## Target Design

### Core Concepts

1. **Workflow**
   - One named prospecting request.
   - Example: `rh_growth_50_200_idf`.
   - Contains: geography, company-size range, sector scope, source adapters, qualification rules, scoring weights, export columns.

2. **Source Adapter**
   - Fetches raw evidence from one source.
   - Examples:
     - `RechercheEntreprisesAdapter`: SIREN, company identity, employee tranche, NAF, location.
     - `JobsSignalAdapter`: active job postings / multiple simultaneous recruitments.
     - `FundingNewsSignalAdapter`: fundraising announcements.
     - `OfficeExpansionSignalAdapter`: new office/location announcements.
     - `LinkedInSignalAdapter`: employee-count thresholds/headcount growth, company posts, hiring signals.
   - Adapters return normalized `Evidence` objects, not final scores.

3. **Rule**
   - Small independent predicate or scoring unit.
   - Examples:
     - `EmployeeRangeRule(50, 200)`
     - `MinGrowthSignalsRule(min_count=2)`
     - `HiringVelocityRule(min_open_roles=3)`
     - `FundingRecentRule(max_age_days=365)`
     - `OfficeOpeningRecentRule(max_age_days=365)`
   - Rules can be added/removed without modifying collectors or exporters.

4. **Scorecard**
   - Aggregates rule outputs into `priority_score_0_100` and labels.
   - Keeps evidence/source URLs visible for auditability.

5. **Exporter**
   - Receives normalized `LeadResult` records.
   - Sheet schema comes from workflow/export config.
   - Existing Excel/Google Drive behavior remains.

---

## New Request: Business Interpretation

**Demand:** find companies between 50 and 200 employees, all sectors, with several growth signals.

**Lead hypothesis:** companies in growth often need HR structuring before they explicitly search for fractional HR support.

**Initial workflow scope:**

- Geography: default Île-de-France because current Prosway focus is IDF unless explicitly changed.
- Size: 50-200 employees.
- Sector: all sectors, but start with a controlled sample to avoid noisy full-market crawling.
- Required signal strength: at least 2 growth signals, or 1 very strong signal plus matching size and active hiring.
- Output: ranked account list with evidence and recommended outreach angle.

**Do not exclude LinkedIn.** Treat LinkedIn as an optional adapter requiring an access decision later. Design the interface now; implement with a stub/manual-import path first if automated access is not ready.

---

## Signal Taxonomy

### Company Fit Signals

- `employee_range_target`: company currently estimated between 50 and 200 employees.
- `employee_threshold_crossed`: company recently crossed 50, 100, 150, or 200 employees.
- `idf_or_target_geo`: headquarters or relevant office in target geography.

### Growth Signals

- `multi_hiring`: multiple active job postings at the same time.
- `fundraising_recent`: recent fundraising or capital increase announcement.
- `new_office`: new office, agency, site, or international/local expansion.
- `headcount_growth`: visible employee count growth over recent period.
- `strong_growth_claim`: public claim such as “hypercroissance”, “forte croissance”, “double ses effectifs”, “recrute X personnes”, “croissance de X%”.

### HR Need Signals

- `people_ops_gap`: no visible senior HR/People leadership despite growth.
- `hiring_pressure`: many roles across functions/locations.
- `managerial_scaling`: growth from founder-led to structured management likely.
- `training_transition_need`: job postings or news imply onboarding, internal mobility, skills development, or career path structuring.

---

## Source Strategy

### Phase 1: Public, low-friction sources

- Recherche Entreprises API: identity, SIREN, location, NAF, official employee tranche.
- Company websites/career pages: job openings, office news, press pages.
- Public web/news search: fundraising, expansion, growth announcements.
- Welcome to the Jungle / Apec / Indeed / France Travail / company ATS pages: hiring signal.
- Pappers/Societe/Annuaire pages only where public and stable.

### Phase 2: LinkedIn / enriched sources

Potential uses:

- Employee count and headcount trend.
- “Hiring” banner / active job postings.
- Company posts announcing offices, fundraising, growth.
- People/HR team presence.

Implementation stance:

- Keep `LinkedInSignalAdapter` behind a provider interface.
- Target provider for later implementation: **Apify**.
- Implement now only the interface + optional manual/import fixture path if needed for tests.
- Do not implement Apify calls in this refactor unless credentials/dataset/actor choice are explicitly provided later.
- Do not hard-code scraping into core pipeline.

---

## Persistence Strategy

A real database is relevant once we run repeated enrichments, compare historical employee/job counts, deduplicate evidence across runs, and track lead status.

Design now, implement later unless needed by the first workflow:

- Keep the first implementation file/export-compatible; do not block on DB setup.
- Add repository interfaces so persistence can switch from files to DB.
- Preferred production path: PostgreSQL.
- Optional no-code/admin layer: NocoDB on top of Postgres if Prosway needs manual review/editing.
- Avoid SQLite for long-term multi-run enrichment history except as a local cache/prototype.

Future tables/entities:

- `companies`
- `workflow_runs`
- `evidence`
- `lead_scores`
- `lead_status`
- `source_logs`
- `contacts_or_roles` without collecting unnecessary personal data.

---

## Refactor Tasks

### Task 1: Add tests around current MVP behavior

**Objective:** Protect the existing workbook flow before refactoring.

**Files:**
- Create: `tests/test_scoring.py`
- Create: `tests/test_workbook.py`
- Create: `tests/test_api_mapping.py`
- Modify: `pyproject.toml`

**Steps:**
1. Add `pytest` as a dev dependency or document running through `uv add --dev pytest`.
2. Test `segment_for`, `score_company`, `priority_label`, `roles_for`.
3. Test `Company.as_enterprise_row()` preserves current column order.
4. Test workbook generation creates expected sheets and counts from fake companies/logs.
5. Test API row-to-company mapping once extracted in Task 3.

**Verify:**

```bash
uv run pytest -q
```

Expected: tests pass.

---

### Task 2: Introduce generic domain models

**Objective:** Add reusable models without breaking existing `Company` output.

**Files:**
- Create: `src/prosway_acquisition/domain.py`
- Modify: `src/prosway_acquisition/models.py`

**Models to add:**

- `CompanyProfile`: normalized company identity and official/public metadata.
- `Evidence`: one observed fact from one source.
- `RuleResult`: output of one rule evaluation.
- `LeadResult`: final ranked result for one company.
- `WorkflowRunLog`: source and execution logs.

**Important fields:**

- company: `name`, `siren`, `website`, `naf_code`, `naf_label`, `employee_min`, `employee_max`, `employee_label`, `city`, `department`, `region`, `source_urls`.
- evidence: `signal_type`, `description`, `source_name`, `source_url`, `observed_at`, `confidence_0_100`, `raw`.
- result: `priority_score_0_100`, `priority_label`, `matched_rules`, `growth_signal_count`, `recommended_angle`, `enrichment_needed`.

**Verify:**

```bash
uv run python3 -m compileall src
uv run pytest -q
```

---

### Task 3: Extract company collection from API mapping

**Objective:** Make Recherche Entreprises reusable across workflows.

**Files:**
- Modify: `src/prosway_acquisition/api.py`
- Create: `src/prosway_acquisition/adapters/recherche_entreprises.py`
- Create: `src/prosway_acquisition/adapters/__init__.py`

**Change:**

- Move HTTP/client logic into adapter.
- Split three concerns:
  1. `iter_search_params(...)`
  2. `fetch_companies(params)`
  3. `map_row_to_company_profile(row)`
- Keep existing `collect_companies()` as compatibility wrapper until old MVP is migrated.

**Verify:**

```bash
uv run pytest -q
PYTHONPATH=src uv run python3 -m prosway_acquisition.cli --output data/exports/prosway_refactor_smoke.xlsx
```

Expected: workbook still generated.

---

### Task 4: Add workflow configuration layer

**Objective:** Let each request define filters/rules without editing core code.

**Files:**
- Create: `src/prosway_acquisition/workflows.py`
- Create: `src/prosway_acquisition/workflow_configs.py`
- Modify: `src/prosway_acquisition/cli.py`

**Add:**

- `WorkflowConfig` dataclass:
  - `name`
  - `description`
  - `departments`
  - `employee_min`, `employee_max`
  - `naf_codes` optional; `None` = all sectors / sampled sectors
  - `sample_limit`
  - `sources`
  - `rules`
  - `export_profile`
- CLI option:

```bash
--workflow rh_mvp_idf
--workflow rh_growth_50_200_idf
```

**Verify:**

```bash
PYTHONPATH=src uv run python3 -m prosway_acquisition.cli --workflow rh_mvp_idf --output data/exports/prosway_mvp_workflow_smoke.xlsx
```

Expected: same functional output as existing MVP.

---

### Task 5: Implement rule engine

**Objective:** Make rules composable and independent.

**Files:**
- Create: `src/prosway_acquisition/rules.py`
- Create: `tests/test_rules.py`

**Rules for this request:**

- `EmployeeRangeRule(50, 200)`
- `DepartmentRule(IDF_DEPARTMENTS)`
- `MinSignalsRule(min_count=2, signal_family="growth")`
- `WeightedSignalRule(signal_type="multi_hiring", weight=25)`
- `WeightedSignalRule(signal_type="fundraising_recent", weight=25)`
- `WeightedSignalRule(signal_type="new_office", weight=20)`
- `WeightedSignalRule(signal_type="headcount_growth", weight=20)`
- `WeightedSignalRule(signal_type="strong_growth_claim", weight=15)`

**Scoring proposal:**

- Base fit: 30
- Size 50-200: +20
- IDF: +10
- Multi-hiring: +25
- Fundraising recent: +25
- New office: +20
- Headcount growth: +20
- Strong growth claim: +15
- Cap: 100
- Label A: >=80 and at least 2 growth signals
- Label B: >=65 and at least 1 strong growth signal
- Label C: >=50
- Label D: otherwise

**Verify:**

```bash
uv run pytest tests/test_rules.py -q
```

---

### Task 6: Add growth workflow config

**Objective:** Define the new demand as a workflow, not as scattered code.

**Files:**
- Modify: `src/prosway_acquisition/workflow_configs.py`
- Create: `tests/test_workflow_configs.py`

**Config:**

Name: `rh_growth_50_200_idf`

Initial filters:

- departments: `75,77,78,91,92,93,94,95`
- employee range: 50-200
- all sectors: use official employee brackets that overlap 50-200
- sample: start with configurable per-department/per-sector cap

**SIRENE employee brackets to map:**

- `21`: 50-99 salariés
- `22`: 100-199 salariés

Do not include `31` because it starts at 200-249 and exceeds the requested cap except if the user later chooses a wider “around 200” interpretation.

**Verify:**

```bash
uv run pytest tests/test_workflow_configs.py -q
```

---

## New Growth-Signal Implementation Tasks

### Task 7: Implement public jobs signal adapter

**Objective:** Detect companies recruiting multiple people at once.

**Files:**
- Create: `src/prosway_acquisition/adapters/jobs.py`
- Create: `tests/test_jobs_adapter.py`

**Initial pragmatic implementation:**

- Provider interface with method `collect(company: CompanyProfile) -> list[Evidence]`.
- Start with website/career-page URL if known.
- Add fallback “manual CSV import” path for job counts:
  - columns: `siren`, `company_name`, `open_roles_count`, `source_url`, `observed_at`.
- Generate `multi_hiring` evidence when `open_roles_count >= 3`.

**Reason:** reliable job-board automation varies by source; manual/import provider lets the workflow run before LinkedIn or job board access is solved.

---

### Task 8: Implement funding/news signal adapter

**Objective:** Detect recent fundraising and strong growth announcements.

**Files:**
- Create: `src/prosway_acquisition/adapters/news.py`
- Create: `tests/test_news_adapter.py`

**Initial implementation:**

- Provider interface for search results.
- Manual JSON/CSV fixture support first.
- Parse evidence types:
  - `fundraising_recent`
  - `new_office`
  - `strong_growth_claim`
- Match with keyword rules:
  - fundraising: `levée de fonds`, `seed`, `série A`, `financement`, `tour de table`, `capital développement`
  - new office: `ouvre un bureau`, `nouvelle agence`, `s'implante`, `nouveau site`
  - strong growth: `forte croissance`, `hypercroissance`, `double ses effectifs`, `recrute`, `croissance de`

**Later provider options:** Tavily/SerpAPI/Bing API/Google CSE, RSS/news APIs, sector media scraping if legally and technically acceptable.

---

### Task 9: Add LinkedIn signal adapter interface

**Objective:** Keep LinkedIn in the design without blocking implementation.

**Files:**
- Create: `src/prosway_acquisition/adapters/linkedin.py`
- Create: `tests/test_linkedin_adapter.py`

**Implementation now:**

- `LinkedInApifyAdapter` interface/skeleton only; no real network calls yet.
- Optional `LinkedInManualCsvAdapter` for tests and interim enrichment.
- Apify implementation will be added later once actor choice, input schema, credentials, and usage limits are decided.
- Supported normalized fields:
  - `company_name`
  - `linkedin_url`
  - `employee_count_current`
  - `employee_count_previous`
  - `open_jobs_count`
  - `is_hiring`
  - `hr_leadership_found`
  - `source_url`
- Evidence emitted:
  - `headcount_growth` when current > previous by configured threshold.
  - `employee_threshold_crossed` when crossing 50/100/150/200.
  - `multi_hiring` when open jobs >= threshold.
  - `people_ops_gap` when growth/hiring exists and no HR leadership found.

**Later:** replace CSV adapter with API/provider adapter without touching rules or exporters.

---

### Task 10: Build growth pipeline orchestration

**Objective:** Run the new workflow end-to-end with adapters and rules.

**Files:**
- Modify: `src/prosway_acquisition/pipeline.py`
- Create: `src/prosway_acquisition/engine.py`
- Create: `tests/test_engine.py`

**Flow:**

1. Load workflow config.
2. Collect base companies from Recherche Entreprises.
3. Normalize employee bracket to numeric range.
4. Apply hard fit filters: size/geography/status.
5. Collect enrichment evidence from configured adapters.
6. Evaluate rules.
7. Rank results.
8. Export workbook.
9. Log all sources, missing enrichments, and skipped companies.

**Verify:**

```bash
PYTHONPATH=src uv run python3 -m prosway_acquisition.cli \
  --workflow rh_growth_50_200_idf \
  --output data/exports/prosway_growth_50_200_idf_sample.xlsx
```

Expected: workbook generated, even if some enrichment adapters only produce `enrichment_needed` logs initially.

---

### Task 11: Add growth export profile

**Objective:** Produce a workbook useful for sales action, not just raw data.

**Files:**
- Modify: `src/prosway_acquisition/workbook.py`
- Create: `src/prosway_acquisition/export_profiles.py`
- Create: `tests/test_growth_workbook.py`

**Sheets:**

1. `Entreprises`
   - company_name
   - siren
   - employee_range
   - city
   - department
   - region
   - naf_code
   - naf_label
   - website
   - source_company_url
   - priority_score_0_100
   - priority_label
   - recommended_angle
   - enrichment_needed

2. `Signaux_croissance`
   - company_name
   - siren
   - signal_type
   - signal_description
   - source_name
   - source_url
   - confidence_0_100
   - observed_at

3. `Angles_contact`
   - company_name
   - siren
   - target_roles_recommended
   - outreach_angle
   - why_now
   - contact_channel_found
   - contact_source_url
   - enrichment_needed

4. `Scoring`
   - rule
   - weight
   - rationale

5. `Sources_Logs`
   - source/API/site
   - query_or_url
   - status
   - notes

---

### Task 12: Add CLI options for async-friendly runs

**Objective:** Make implementation and future cron/async tasks controllable.

**Files:**
- Modify: `src/prosway_acquisition/cli.py`

**Add options:**

```bash
--workflow rh_growth_50_200_idf
--sample-limit 100
--max-pages-per-query 1
--enrichment-input data/input/linkedin_growth.csv
--no-upload-drive
--upload-drive
--output data/exports/prosway_growth_50_200_idf_sample.xlsx
```

**Verify:**

```bash
PYTHONPATH=src uv run python3 -m prosway_acquisition.cli --help
```

Expected: all workflow options visible.

---

### Task 13: End-to-end smoke run

**Objective:** Prove the refactor did not break the old workflow and the new workflow can generate an artifact.

**Commands:**

```bash
PYTHONPATH=src uv run python3 -m prosway_acquisition.cli \
  --workflow rh_mvp_idf \
  --output data/exports/prosway_mvp_idf_after_workflow_refactor.xlsx

PYTHONPATH=src uv run python3 -m prosway_acquisition.cli \
  --workflow rh_growth_50_200_idf \
  --sample-limit 50 \
  --output data/exports/prosway_growth_50_200_idf_sample.xlsx

uv run pytest -q
```

**Expected:**

- Both workbooks exist.
- Tests pass.
- Growth workbook has companies, logs, and explicit `enrichment_needed` where no external source was checked.

---

## Async Implementation Work Packages

### Package A — Refactor foundation

Tasks: 1-6.

Outcome: current MVP migrated to configurable workflow architecture with tests.

Can run independently after codebase inspection. Blocks all later packages.

### Package B — Public growth adapters

Tasks: 7-8.

Outcome: jobs/news/funding evidence interfaces plus manual/import provider support.

Can start after Task 2 domain models are in place.

### Package C — LinkedIn-ready adapter

Task: 9.

Outcome: LinkedIn data can be imported manually now and automated later without core changes.

Can start after Task 2 domain models are in place.

### Package D — Engine + export + CLI

Tasks: 10-13.

Outcome: end-to-end growth workflow with workbook output.

Depends on Package A; integrates B/C when available.

---

## Access Decisions Needed Later, Not Now

Do not block refactor on these. The code should support provider replacement.

1. LinkedIn access path:
   - manual export/import
   - Sales Navigator export
   - official API if available
   - Apify/PhantomBuster/Captain Data/Clay-style provider

2. News/search access path:
   - web search API
   - SerpAPI/Tavily/Bing/Google CSE
   - targeted media/source adapters

3. Job postings access path:
   - company career pages
   - Welcome to the Jungle
   - Apec
   - Indeed / France Travail where allowed
   - ATS pages: Greenhouse, Lever, Teamtailor, Workable, SmartRecruiters

---

## Recommended First Execution Order

1. Package A first. No growth feature until the old MVP is protected and workflowized.
2. Package D skeleton next, using fake/manual evidence so the full pipeline runs.
3. Package B public evidence adapters.
4. Package C LinkedIn manual CSV adapter.
5. Only then decide whether to add automated LinkedIn/job/news providers.

This avoids building brittle source-specific scraping before the pipeline is modular.
