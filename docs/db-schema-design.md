# Persistence design: Postgres / NocoDB-ready

Initial workflow runs remain file/export based. Persistence is introduced through repository contracts, not a concrete DB dependency, so the pipeline can later swap file memory for Postgres without changing adapters, rules, or exporters.

## Target entities

- companies
  - siren primary key
  - name, website, naf_code, naf_label
  - employee_min, employee_max, employee_label
  - city, department, region
  - source_urls jsonb
  - raw jsonb
  - created_at, updated_at

- workflow_runs
  - id uuid primary key
  - workflow_name
  - started_at, finished_at
  - status
  - parameters jsonb

- evidence
  - id uuid primary key
  - workflow_run_id foreign key
  - siren foreign key
  - signal_type, signal_family
  - description
  - source_name, source_url
  - observed_at
  - confidence_0_100
  - raw jsonb

- lead_scores
  - id uuid primary key
  - workflow_run_id foreign key
  - siren foreign key
  - priority_score_0_100
  - priority_label
  - matched_rules jsonb
  - growth_signal_count
  - recommended_angle
  - enrichment_needed

- lead_status
  - siren foreign key
  - owner/status/stage
  - last_contacted_at
  - notes
  - no personal email collection by default

- source_logs
  - id uuid primary key
  - workflow_run_id foreign key
  - source
  - query_or_url
  - status
  - notes
  - created_at

## NocoDB path

NocoDB can sit on top of the same Postgres schema for manual review/editing of lead status and notes. Do not put source credentials or personal emails into NocoDB tables unless a later compliance decision explicitly allows it.
