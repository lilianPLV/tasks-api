# TP3 : Docker et livraison continue

**Durée : environ 3 h 30** · Jour 3, après-midi

## Objectif

Mettre l'application dans une image Docker, publier automatiquement cette image à chaque changement,
créer une version (release) par un tag Git, et déployer avec une approbation avant la production.

> 📸 Ce TP contient 8 captures pour le dossier (TP3-1 à TP3-8).

## Avant de commencer

- [ ] **Docker Desktop est lancé** (icône verte). Test : `docker run --rm hello-world`
- [ ] `main` à jour : `git switch main && git pull`, puis `git switch -c tp3`
- [ ] Le TP2 est terminé (CI avec `lint` et `test`)

### Les commandes qui changent selon votre système

| Action | macOS / Linux | Windows (PowerShell) |
|---|---|---|
| Appeler l'API | `curl http://localhost:8000/health` | `curl.exe http://localhost:8000/health` |
| Définir une variable pour une commande | `GITHUB_OWNER=moi IMAGE_TAG=0.1.0 docker compose …` | `$env:GITHUB_OWNER="moi"; $env:IMAGE_TAG="0.1.0"; docker compose …` |

---

## Partie 1 : Votre Dockerfile (40 min)

Ouvrez le `Dockerfile` : il contient 6 `TODO`. Complétez-le (aidez-vous du cours), puis :

```bash
docker build -t tasks-api:local .
docker run --rm -p 8000:8000 tasks-api:local
```

Dans un autre terminal : appelez `/health` et `/version`. Arrêtez avec `Ctrl + C`.

Contrôles :
- `docker images tasks-api` : notez la taille de l'image ;
- modifiez un fichier de `app/`, reconstruisez : quelles étapes sont « CACHED » ? Pourquoi `requirements.txt` est-il copié **avant** le code ?

> 📸 **TP3-1 :** le `docker build` réussi, puis `curl` sur `/health` qui répond `{"status":"ok"}`.

**Questions :** Différence entre une image et un conteneur ? À quoi sert le `.dockerignore` ?

---

## Partie 2 : Docker Compose (20 min)

Créez `docker-compose.yml` avec un service `api` qui :
- construit l'image du dossier courant ;
- publie le port 8000 ;
- définit la variable d'environnement `APP_VERSION` à `local`.

```bash
docker compose up --build
```

Vérifiez que `/version` répond `local`, puis `docker compose down`.

> 📸 **TP3-2 :** `docker compose up` en cours et le `curl` sur `/version`.

**Question :** Que gagne-t-on à décrire le lancement dans un fichier plutôt que dans une longue commande ?

---

## Partie 3 : Publier l'image depuis le pipeline (45 min)

Créez `.github/workflows/docker.yml` avec **deux jobs** :

1. `test` : checkout, Python, `pip install -r requirements-dev.txt`, `pytest` ;
2. `build` (après `test`, avec `needs: test`) : se connecte à GHCR, construit l'image et la **pousse**.

Aide, étape par étape :
- déclencheurs : `push` sur `main`, `push` de tags `v*`, et `workflow_dispatch` ;
- le job `build` demande la permission `packages: write` ;
- actions à utiliser : `docker/setup-buildx-action@v4`, `docker/login-action@v4` (registre `ghcr.io`,
  utilisateur `${{ github.actor }}`, mot de passe `${{ secrets.GITHUB_TOKEN }}`), `docker/metadata-action@v6`, `docker/build-push-action@v7` ;
- tags voulus : `type=sha,format=short` (ex. `sha-1a2b3c4`) et `type=semver,pattern={{version}}` pour les tags Git ;
- **version de l'application :** pour que `/version` réponde `0.1.0` dans l'image publiée, passez la version à la construction avec `build-args: APP_VERSION=…` dans `docker/build-push-action`.
  Calculez-la dans une étape : pour un tag `v0.1.0`, `${GITHUB_REF_NAME#v}` donne `0.1.0` ; pour un push sur `main`, utilisez par exemple `dev`.
  (Cela suppose que votre Dockerfile déclare `ARG APP_VERSION` et `ENV APP_VERSION`, voir le TODO 6.)
- **piège :** le nom d'une image GHCR doit être en **minuscules**. Calculez-le dans une étape : `${GITHUB_REPOSITORY_OWNER,,}`.

Poussez sur `main`, puis allez voir votre profil GitHub → **Packages**.

> 📸 **TP3-3 :** le run avec `test` puis `build` au vert.
> 📸 **TP3-4 :** la page du package `tasks-api` avec son tag `sha-…`.

**Questions :** Pourquoi `build` attend-il `test` ? Pourquoi éviter le tag `latest` en production ?

---

## Partie 4 : Une release par un tag Git (30 min)

1. Sur GitHub, ouvrez votre package → **Package settings** → **Change visibility** → **Public** (nécessaire pour le jour 4).
2. Créez la version 0.1.0 :

```bash
git switch main && git pull
git tag v0.1.0
git push origin v0.1.0
```

3. Le pipeline se lance : l'image `0.1.0` doit apparaître dans vos packages.
4. Testez comme un utilisateur : **supprimez votre image locale**, puis lancez l'image publiée :

```bash
docker run --rm -p 8000:8000 ghcr.io/<votre-compte-minuscules>/tasks-api:0.1.0
```


> 📸 **TP3-5 :** la liste des tags du package (`0.1.0` et `sha-…`).
> 📸 **TP3-6 :** `docker run` de l'image **téléchargée depuis GHCR** et `curl /version` qui répond `0.1.0`.

**Question :** Quel est l'avantage d'une image versionnée par rapport à « le code de ma machine » ?

---

## Partie 5 : Environnements et approbation (25 min)

Ajoutez à `docker.yml` deux jobs de **déploiement simulé** :

- `deploy-staging` (après `build`, `environment: staging`) : se connecte à GHCR, lance l'image du commit
  (`docker run -d -p 8000:8000 …`), puis fait un **test de fumée** : `curl -f` sur `/health` et `/version` (avec quelques essais, le démarrage prend du temps) ;
- `deploy-production` (après `deploy-staging`, `environment: production`, **uniquement sur un tag** : `if: startsWith(github.ref, 'refs/tags/v')`) : même test de fumée avec l'image de la release.

Sur GitHub : **Settings → Environments → production** → cochez **Required reviewers** et ajoutez-vous.

Créez `v0.1.1` (nouveau tag) : le pipeline passe sur staging, puis **attend votre approbation** avant la production. Approuvez-le.

> 📸 **TP3-7 :** le run en attente d'approbation (« Waiting » / « Review deployments »), puis le run terminé.

**Questions :** À quoi sert un test de fumée ? Pourquoi demander une approbation humaine avant la production ?

---

## Partie 6 : Sécurité de l'image (10 min)

1. Vérifiez que votre conteneur n'est **pas root** : `docker run --rm tasks-api:local id` (vous devez voir un uid différent de 0).
2. Lisez ensemble le **cas d'étude** présenté par le formateur : en mars 2026, l'action de scan Trivy a été compromise.
   Quelles bonnes pratiques en tirer ? (épingler les versions, limiter les permissions, ne jamais exposer de secrets inutiles)

> 📸 **TP3-8 :** la sortie de la commande `id` dans le conteneur.

**Question :** Pourquoi ne pas exécuter une application en root dans un conteneur ?

---

## Préparer demain (10 min)

Créez dès maintenant le mini-cluster du jour 4 pour gagner du temps (téléchargement long) : `kind create cluster --name gitops`, puis `kubectl get nodes`.
Si la commande échoue, notez l'erreur : on la réglera demain.

## Checklist de fin de TP

- [ ] Dockerfile complet, image construite et testée
- [ ] `docker-compose.yml` fonctionnel
- [ ] Image publiée sur GHCR par le pipeline, package public
- [ ] Release `v0.1.0` publiée et testée depuis GHCR
- [ ] Environnement `production` avec approbation
- [ ] Mes 8 captures et mes réponses sont dans le dossier
