# tasks-api : fil rouge du cours GitOps & CI/CD

Petite API Flask de gestion de tâches. On ne travaille pas sur l'application elle-même :
c'est un **prétexte** pour apprendre à automatiser les tests, la construction et le déploiement.

## Démarrage

### 1. Créer votre dépôt

Sur la page GitHub de ce dépôt, cliquez sur **Use this template**, puis **Create a new repository**.
Nommez-le `tasks-api` et laissez-le **Public** (GitHub Actions est gratuit sur les dépôts publics).

> Préférez le modèle (*template*) au *fork* : avec un fork, GitHub désactive les workflows
> jusqu'à ce que vous cliquiez sur « I understand my workflows, go ahead and enable them » dans l'onglet Actions.

### 2. Cloner votre dépôt

```bash
gh repo clone <votre-compte>/tasks-api
cd tasks-api
```

### 3. Créer l'environnement Python et installer les dépendances

| | macOS | Linux | Windows (PowerShell) |
|---|---|---|---|
| Créer | `python3.12 -m venv .venv` | `python3 -m venv .venv` | `py -3.12 -m venv .venv` |
| Activer | `source .venv/bin/activate` | `source .venv/bin/activate` | `.venv\Scripts\Activate.ps1` |

Une fois l'environnement activé (votre terminal affiche `(.venv)`), c'est identique partout :

```bash
pip install -r requirements-dev.txt
```

### 4. Lancer les tests

```bash
pytest
```

Vous devez voir `10 passed`.

### 5. Lancer l'application

```bash
python -m app.main
```

Dans un **second terminal** :

| macOS / Linux | Windows (PowerShell) |
|---|---|
| `curl http://localhost:8000/health` | `curl.exe http://localhost:8000/health` |

Vous devez lire `{"status":"ok"}`. Arrêtez l'application avec `Ctrl + C`.

> Sous Windows PowerShell, écrivez bien `curl.exe` : `curl` seul est un alias d'une autre commande.

## Structure

| Chemin | Rôle | Quand on y touche |
|---|---|---|
| `app/` | Le code de l'API | Jamais (sauf pour casser un test volontairement) |
| `tests/` | Les tests pytest | J1, J2 |
| `.github/workflows/` | Vos workflows GitHub Actions | **J1 à J3** |
| `Dockerfile` | À compléter | J3 |
| `pipelines-a-reparer/` | Trois pipelines cassés à réparer | Fin du J2 |
| `config-repo/` | Modèle du dépôt de configuration Kubernetes | J4 |
| `argocd/` | Déclaration de l'application pour Argo CD | J4 |
| `scripts/` | Script utilisé par le pipeline au J4 | Ne pas toucher |
| `docs/` | Énoncés des TP (TP1 à TP4) et modèle de dossier | Tous les jours |

## Endpoints

- `GET /` : message de bienvenue
- `GET /health` : état de santé (`{"status": "ok"}`)
- `GET /version` : version déployée (variable d'environnement `APP_VERSION`)
- `GET /tasks` et `POST /tasks` : liste et création de tâches

## Commandes utiles

```bash
pytest --cov=app --cov-fail-under=80   # tests + couverture
flake8 .                                # qualité du code (linter)
black --check .                         # formatage du code
```

## Évaluation

Votre note finale = **10/20 pour le dossier de TP** (complet et correct, dépôt GitHub public + tableur du formateur) + **10/20 pour le QCM**.
Le modèle du dossier est dans `docs/DOSSIER.md` : gardez vos captures d'écran **au fil des TP**.
