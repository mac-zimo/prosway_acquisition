from prosway_acquisition.api import city_from_siege, department_from_siege, region_from_siege


def test_current_api_mapping_helpers_for_siege_location():
    siege = {"libelle_commune": "Paris", "departement": "75"}
    assert city_from_siege(siege) == "Paris"
    assert department_from_siege(siege) == "75"
    assert region_from_siege(siege) == "Île-de-France"


def test_city_falls_back_to_commune():
    assert city_from_siege({"commune": "Nanterre"}) == "Nanterre"
