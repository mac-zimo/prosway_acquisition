from __future__ import annotations

from pathlib import Path

TITLE = "Prosway - MVP Prospection RH"
DEFAULT_OUTPUT = Path("data/exports/prosway_mvp_prospection_rh_idf.xlsx")

IDF_DEPARTMENTS = ("75", "77", "78", "91", "92", "93", "94", "95")

NAF_LABELS = {
    "62.01Z": "Programmation informatique",
    "62.02A": "Conseil en systèmes et logiciels informatiques",
    "62.02B": "Tierce maintenance de systèmes et applications informatiques",
    "62.03Z": "Gestion d’installations informatiques",
    "62.09Z": "Autres activités informatiques",
    "63.11Z": "Traitement de données, hébergement et activités connexes",
    "70.22Z": "Conseil pour les affaires et autres conseils de gestion",
    "10.89Z": "Fabrication d’autres produits alimentaires n.c.a.",
    "20.14Z": "Fabrication d’autres produits chimiques organiques de base",
    "20.59Z": "Fabrication d’autres produits chimiques n.c.a.",
    "22.29A": "Fabrication de pièces techniques à base de matières plastiques",
    "25.62B": "Mécanique industrielle",
    "26.51A": "Fabrication d’équipements d’aide à la navigation",
    "27.12Z": "Fabrication de matériel de distribution et de commande électrique",
    "28.29B": "Fabrication d’autres machines d’usage général",
    "29.32Z": "Fabrication d’autres équipements automobiles",
    "30.30Z": "Construction aéronautique et spatiale",
    "33.12Z": "Réparation de machines et équipements mécaniques",
    "64.19Z": "Autres intermédiations monétaires",
    "65.11Z": "Assurance vie",
    "65.12Z": "Autres assurances",
    "66.22Z": "Activités des agents et courtiers d’assurances",
}

ESN_NAF = ("62.01Z", "62.02A", "62.02B", "62.03Z", "62.09Z", "63.11Z", "70.22Z")
INDUSTRY_NAF = (
    "10.89Z",
    "20.14Z",
    "20.59Z",
    "22.29A",
    "25.62B",
    "26.51A",
    "27.12Z",
    "28.29B",
    "29.32Z",
    "30.30Z",
    "33.12Z",
)
FINANCE_NAF = ("64.19Z", "65.11Z", "65.12Z", "66.22Z")
ALL_TARGET_NAF = ESN_NAF + INDUSTRY_NAF + FINANCE_NAF

TARGET_EMPLOYEE_BRACKETS = ("22", "31", "32", "41")
EMPLOYEE_BRACKET_LABELS = {
    "22": "100-199 salariés",
    "31": "200-249 salariés",
    "32": "250-499 salariés",
    "41": "500-999 salariés",
}

TARGET_PER_NAF = {naf: 10 for naf in ESN_NAF} | {naf: 6 for naf in INDUSTRY_NAF} | {naf: 3 for naf in FINANCE_NAF}

REGION_BY_DEPARTMENT = {
    **{department: "Île-de-France" for department in IDF_DEPARTMENTS},
    **{department: "Auvergne-Rhône-Alpes" for department in ("01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74")},
    **{department: "Bourgogne-Franche-Comté" for department in ("21", "25", "39", "58", "70", "71", "89", "90")},
    **{department: "Bretagne" for department in ("22", "29", "35", "56")},
    **{department: "Centre-Val de Loire" for department in ("18", "28", "36", "37", "41", "45")},
    **{department: "Corse" for department in ("2A", "2B")},
    **{department: "Grand Est" for department in ("08", "10", "51", "52", "54", "55", "57", "67", "68", "88")},
    **{department: "Hauts-de-France" for department in ("02", "59", "60", "62", "80")},
    **{department: "Normandie" for department in ("14", "27", "50", "61", "76")},
    **{department: "Nouvelle-Aquitaine" for department in ("16", "17", "19", "23", "24", "33", "40", "47", "64", "79", "86", "87")},
    **{department: "Occitanie" for department in ("09", "11", "12", "30", "31", "32", "34", "46", "48", "65", "66", "81", "82")},
    **{department: "Pays de la Loire" for department in ("44", "49", "53", "72", "85")},
    **{department: "Provence-Alpes-Côte d’Azur" for department in ("04", "05", "06", "13", "83", "84")},
}
