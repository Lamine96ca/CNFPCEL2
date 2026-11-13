# CNFPCEL2

Plateforme du **CNFPATEL** (Centre National de Formation et de Perfectionnement des Cadres et des Élus Locaux) : site public, espace de gestion, espace formateur et espace participant.

## Espaces

| Espace | Accès | Rôle |
|---|---|---|
| Site public | `/` | Présentation, catalogue des formations, actualités, événements, galerie |
| Gestion | `/gestion/` | Personnel : formations, formateurs, participants, évaluations, contenus du site |
| Formateur | `/espace-formateur/` | Formateurs : proposer des formations, gérer sections, ressources et évaluations, suivre les participants |
| Participant | `/formation-etudiant/` | Participants : suivre leurs formations et passer les évaluations |

La connexion se fait sur `/login/` ; chaque compte est redirigé vers son espace.

## Installation (développement)

```bash
python -m venv env
env\Scripts\activate            # Windows
pip install -r requirements.txt
copy config\local_settings.example.py config\local_settings.py   # puis renseigner les valeurs
python manage.py migrate
python manage.py runserver
```

La base de données est MySQL (`cnfpcel` sur `localhost:3306` par défaut, modifiable dans `config/local_settings.py`).

## Secrets

`config/local_settings.py` (clé secrète, mots de passe SMTP, `DEBUG`…) et `credentials.json` ne sont **jamais versionnés**. Partez de `config/local_settings.example.py`.

## Mise en production

Voir [DEPLOIEMENT.md](DEPLOIEMENT.md) (o2switch, domaine principal `cnfpcel.gov.gn`).

## Tests

```bash
python manage.py test cnfpcel
```

## Structure

- `cnfpcel/views/` : vues regroupées par thème (public, comptes, formations, participants, évaluations, formateurs, espace formateur…)
- `cnfpcel/roles.py` : rôles et contrôle d'accès centralisé (middleware)
- `cnfpcel/templates/accueil/` : site public · `gestion/` : espace de gestion · `formateur/` : espace formateur
- `cnfpcel/static/gestion/css/cnf-gestion.css` : thème des espaces de gestion et formateur
