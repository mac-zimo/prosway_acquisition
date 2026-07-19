# État du MVP initial

Artefacts récupérés depuis `/home/zimoza` et placés dans `data/exports/` :

- `scripts/legacy/prosway_mvp_build.py` : script historique monolithique.
- `data/exports/prosway_mvp_prospection_rh.xlsx` : export initial.
- `data/exports/prosway_mvp_prospection_rh_idf.xlsx` : export dédié Île-de-France.
- `data/exports/prosway_mvp_prospection_rh_idf_refactored.xlsx` : export régénéré depuis le code refactoré.

Le script monolithique est conservé comme référence historique. Le code actif est maintenant découpé dans `src/prosway_acquisition/`.

## Contraintes métier connues

- Tous les projets Prosway doivent être rangés sous `/media/zimoza/DATA/projects/Prosway/` côté local.
- Ce projet d'acquisition vit dans `/media/zimoza/DATA/projects/Prosway/acquisition`.
- Le dossier Drive cible historique est `Prosway/Prospection`.
- Focus MVP : comptes franciliens pertinents pour coaching professionnel, carrière, bilan de compétences, reconversion et transition professionnelle côté Prosway.
