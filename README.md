# Prosway — Acquisition prospects

Projet local pour industrialiser le MVP de recherche de prospects Prosway.

## Objectif

Construire un pipeline évolutif qui :

1. collecte des entreprises cibles depuis des sources publiques ;
2. qualifie les comptes selon le fit Prosway ;
3. produit un fichier Excel / Google Sheet exploitable ;
4. garde des logs de sources et d'exécution ;
5. prépare l'ajout futur d'enrichissements LinkedIn / Apify ou autres sources.

## Périmètre actuel

- Focus géographique : Île-de-France.
- Départements : 75, 77, 78, 91, 92, 93, 94, 95.
- Pas de scoring par département.
- Pas de collecte d'emails personnels.
- Pas d'automatisation de contact.
- Données issues de sources publiques uniquement pour le MVP actuel.

## Arborescence

```text
src/prosway_acquisition/
  api.py        # client Recherche Entreprises
  cli.py        # point d'entrée CLI
  config.py     # constantes métier
  drive.py      # upload / vérification Google Drive
  models.py     # modèles de données
  pipeline.py   # orchestration
  scoring.py    # scoring compte / signaux
  workbook.py   # génération XLSX

data/exports/   # exports existants et fichiers générés
docs/           # notes projet
```

## Utilisation

Générer un fichier XLSX local :

```bash
python3 -m prosway_acquisition.cli --output data/exports/prosway_mvp_prospection_rh_idf.xlsx
```

Depuis le dépôt, sans installation :

```bash
PYTHONPATH=src python3 -m prosway_acquisition.cli --output data/exports/prosway_mvp_prospection_rh_idf.xlsx
```

Avec upload Google Drive :

```bash
PYTHONPATH=src python3 -m prosway_acquisition.cli --upload-drive
```

L'upload dépend des credentials Google déjà configurés dans Hermes.

## Prochaine évolution prévue

Ajouter les enrichissements demandés plus tard sous forme de nouveaux adapters dans `src/prosway_acquisition/`, sans mélanger la collecte publique, la normalisation, le scoring et la génération de livrables.
