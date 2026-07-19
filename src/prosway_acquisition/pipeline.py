from __future__ import annotations

from pathlib import Path

from .api import collect_companies
from .drive import upload_as_google_sheet, verify_google_sheet_export
from .workbook import workbook_counts, write_workbook


def build_local_workbook(output: Path) -> dict[str, object]:
    companies, logs = collect_companies()
    write_workbook(output, companies, logs)
    return {
        "local_xlsx": str(output),
        "company_count": len(companies),
        "counts": workbook_counts(output),
    }


def build_and_upload(output: Path) -> dict[str, object]:
    result = build_local_workbook(output)
    file_info, drive = upload_as_google_sheet(output)
    verification = verify_google_sheet_export(drive, file_info["id"])
    return {
        **result,
        "spreadsheetUrl": file_info.get("webViewLink"),
        "id": file_info.get("id"),
        "name": file_info.get("name"),
        "drive_verification": verification,
    }
