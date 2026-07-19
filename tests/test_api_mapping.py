from prosway_acquisition.api import city_from_siege, department_from_siege, map_row_to_company_profile, region_from_siege


def test_current_api_mapping_helpers_for_siege_location():
    siege = {"libelle_commune": "Paris", "departement": "75"}
    assert city_from_siege(siege) == "Paris"
    assert department_from_siege(siege) == "75"
    assert region_from_siege(siege) == "Île-de-France"


def test_city_falls_back_to_commune():
    assert city_from_siege({"commune": "Nanterre"}) == "Nanterre"


def test_map_row_to_company_profile_normalizes_recherche_entreprises_row():
    profile = map_row_to_company_profile(
        {
            "siren": "123456789",
            "nom_complet": "ACME SAS",
            "activite_principale": "62.01Z",
            "tranche_effectif_salarie": "22",
            "siege": {"libelle_commune": "Paris", "departement": "75", "etat_administratif": "A"},
        }
    )
    assert profile is not None
    assert profile.name == "ACME SAS"
    assert profile.siren == "123456789"
    assert profile.employee_min == 100
    assert profile.employee_max == 199
    assert profile.employee_label == "100-199 salariés"
    assert profile.department == "75"
    assert profile.source_urls == ("https://annuaire-entreprises.data.gouv.fr/entreprise/123456789",)
