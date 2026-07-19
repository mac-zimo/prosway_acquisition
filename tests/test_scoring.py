from prosway_acquisition.scoring import priority_label, roles_for, score_company, segment_for


def test_segment_for_known_naf_codes():
    assert segment_for("62.01Z") == "ESN/conseil IT"
    assert segment_for("25.62B") == "Industrie"
    assert segment_for("64.19Z") == "Banque/assurance"
    assert segment_for("00.00Z") == "Autre pertinent"


def test_score_company_and_priority_label_current_mvp_behavior():
    assert score_company("ESN/conseil IT", "32") == 95
    assert score_company("Industrie", "31") == 90
    assert score_company("Banque/assurance", "22") == 77
    assert score_company("Autre pertinent", "00") == 55
    assert priority_label(85) == "A"
    assert priority_label(70) == "B"
    assert priority_label(55) == "C"
    assert priority_label(54) == "D"


def test_roles_for_segment_specific_additions():
    assert "Talent Acquisition" in roles_for("ESN/conseil IT")
    assert "Prévention/HSE" in roles_for("Industrie")
    assert "mobilité/carrières" in roles_for("Banque/assurance")
    assert "DRH" in roles_for("Autre pertinent")
