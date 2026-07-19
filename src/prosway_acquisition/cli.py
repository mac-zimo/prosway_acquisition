from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import DEFAULT_OUTPUT
from .pipeline import build_and_upload, build_local_workbook
from .workflow_configs import WORKFLOWS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Prosway acquisition workbook")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="XLSX output path")
    parser.add_argument("--workflow", choices=sorted(WORKFLOWS), default="rh_mvp_idf", help="Workflow to execute")
    parser.add_argument("--sample-limit", type=int, default=None, help="Maximum companies to include")
    parser.add_argument("--max-pages-per-query", type=int, default=2, help="Recherche Entreprises pages per query")
    parser.add_argument("--enrichment-input", type=Path, default=None, help="Manual CSV/JSON enrichment input for growth signals")
    parser.add_argument("--upload-drive", action="store_true", help="Upload and convert the XLSX to Google Sheets")
    parser.add_argument("--no-upload-drive", action="store_true", help="Force local-only output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    kwargs = {
        "workflow_name": args.workflow,
        "sample_limit": args.sample_limit,
        "max_pages_per_query": args.max_pages_per_query,
        "enrichment_input": args.enrichment_input,
    }
    result = build_and_upload(args.output, **kwargs) if args.upload_drive and not args.no_upload_drive else build_local_workbook(args.output, **kwargs)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
