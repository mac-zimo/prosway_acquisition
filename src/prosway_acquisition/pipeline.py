from __future__ import annotations

from pathlib import Path

from .api import collect_companies
from .drive import upload_as_google_sheet, verify_google_sheet_export
from .workflow_configs import get_workflow
from .workbook import workbook_counts, write_workbook


def build_local_workbook(
    output: Path,
    workflow_name: str = "rh_mvp_idf",
    sample_limit: int | None = None,
    max_pages_per_query: int = 2,
    enrichment_input: Path | None = None,
) -> dict[str, object]:
    workflow = get_workflow(workflow_name)
    companies, logs = collect_companies(
        max_pages_per_query=max_pages_per_query,
        naf_codes=workflow.naf_codes,
        employee_brackets=workflow.employee_brackets,
        departments=workflow.departments,
        target_per_naf=workflow.target_per_naf or None,
        sample_limit=sample_limit if sample_limit is not None else workflow.sample_limit,
    )
    write_workbook(output, companies, logs)
    return {
        "workflow": workflow.name,
        "local_xlsx": str(output),
        "company_count": len(companies),
        "counts": workbook_counts(output),
        "enrichment_input": str(enrichment_input) if enrichment_input else None,
    }


def build_and_upload(output: Path, **kwargs) -> dict[str, object]:
    result = build_local_workbook(output, **kwargs)
    file_info, drive = upload_as_google_sheet(output)
    verification = verify_google_sheet_export(drive, file_info["id"])
    return {
        **result,
        "spreadsheetUrl": file_info.get("webViewLink"),
        "id": file_info.get("id"),
        "name": file_info.get("name"),
        "drive_verification": verification,
    }
