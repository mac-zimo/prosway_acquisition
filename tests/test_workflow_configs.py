from prosway_acquisition.config import IDF_DEPARTMENTS
from prosway_acquisition.workflow_configs import get_workflow


def test_rh_mvp_idf_workflow_matches_existing_scope():
    workflow = get_workflow("rh_mvp_idf")
    assert workflow.departments == IDF_DEPARTMENTS
    assert workflow.employee_brackets == ("22", "31", "32", "41")
    assert workflow.export_profile == "mvp"


def test_growth_workflow_uses_50_200_idf_brackets_without_31():
    workflow = get_workflow("rh_growth_50_200_idf")
    assert workflow.departments == ("75", "77", "78", "91", "92", "93", "94", "95")
    assert workflow.employee_min == 50
    assert workflow.employee_max == 200
    assert workflow.employee_brackets == ("21", "22")
    assert "31" not in workflow.employee_brackets
    assert workflow.naf_codes is None
    assert workflow.export_profile == "growth"
