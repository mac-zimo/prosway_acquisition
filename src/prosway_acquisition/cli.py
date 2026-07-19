from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import DEFAULT_OUTPUT
from .pipeline import build_and_upload, build_local_workbook


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Prosway acquisition workbook")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="XLSX output path")
    parser.add_argument("--upload-drive", action="store_true", help="Upload and convert the XLSX to Google Sheets")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_and_upload(args.output) if args.upload_drive else build_local_workbook(args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
