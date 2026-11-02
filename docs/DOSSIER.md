# Dossier de rendu : GitOps & CI/CD

## L'évaluation en bref

| Élément | Poids |
|---|---|
| Dossier de TP (ce document) | **10 points sur 20** (50 %) : dossier complet et correct = 10/10 |
| QCM (20 questions, 30 minutes, jeudi 5 novembre, en fin de journée) | **10 points sur 20** (50 %) |

Le dossier rassemble **tous les TP de la semaine**, avec des captures d'écran et vos explications.
Vous le construisez **au fil des jours** : ne gardez pas tout pour le jeudi soir !

- **À rendre :** le **vendredi 6 novembre à 17 h**, dernier délai · envoi du lien de votre dépôt GitHub dans le tableur Excel fourni par le formateur (voir ci-dessous)
- **Qui rend quoi :** le dossier est **individuel** : vous pouvez travailler à deux pendant les TP, mais chacun rend son propre dossier, avec ses propres captures et ses propres mots.
- **Format :** un seul fichier **PDF**, nommé `NOM_Prenom_GitOps-CICD.pdf`.
  Rédigez-le dans l'outil de votre choix (Word, Google Docs, LibreOffice…) puis exportez en PDF.
- **Lien :** indiquez en première page l'adresse de votre dépôt GitHub (il doit être **public**).
- **Dépôt et tableur :** publiez votre projet `tasks-api` sur GitHub (dépôt **public**, avec le code, les workflows et vos modifications), puis remplissez le **tableur fourni par le formateur** : nom, prénom, adresse e-mail, lien du dépôt. Un dépôt absent, privé ou incorrect fait perdre des points au dossier.

## Structure du dossier

1. **Page de garde** : nom(s), prénom(s), date, lien vers votre dépôt GitHub.
2. **TP1** : première CI avec GitHub Actions.
3. **TP2** : une CI solide.
4. **TP3** : Docker et livraison continue.
5. **TP4** : GitOps.
6. **Bilan** : 10 lignes maximum : ce que vous avez retenu, ce qui vous a posé problème, ce que vous referiez autrement.

Pour **chaque TP**, trois choses :

- **Objectif** : 2 ou 3 phrases avec vos mots (pas une copie de l'énoncé).
- **Captures d'écran** numérotées, chacune avec une **légende** d'une phrase qui explique ce que l'on voit.
- **Réponses** aux questions posées dans l'énoncé du TP, et **difficultés rencontrées** (ce qui a bloqué, comment vous avez trouvé la solution).

## TP1 : captures et questions

| N° | Capture à fournir |
|---|---|
| TP1-1 | Le run « Hello » réussi, étape « branche / auteur » dépliée |
| TP1-2 | Le run `ci.yml` réussi, avec la liste des étapes |
| TP1-3 | Le run rouge, étape `pytest` dépliée avec le message d'erreur |
| TP1-4 | Le run vert après la correction |
| TP1-5 | La pull request avec les vérifications vertes, avant fusion |
| TP1-6 | La pull request fusionnée |
| TP1-7 | Le `README.md` sur GitHub avec le badge affiché |

Questions à traiter :

1. Combien de temps a duré le run « Hello » ? Où voit-on les logs de chaque étape ?
2. Quel test a échoué dans la partie 3, et à quelle ligne ? Qu'est-ce qui a permis de le trouver rapidement ?
3. Pourquoi attend-on que la CI soit verte avant de fusionner une pull request ?

## TP2 : captures

| N° | Capture à fournir |
|---|---|
| TP2-1 | un run vert montrant les deux jobs `lint` et `test`. |
| TP2-2 | le job `lint` rouge, avec le message de flake8 lisible. |
| TP2-3 | la liste des 3 jobs de la matrice (`test (3.11)`, `test (3.12)`, `test (3.13)`). |
| TP2-4 | l'étape setup-python du 2ᵉ run, avec la mention du cache restauré, et la section « Artifacts » de la page du run. |
| TP2-5 | la page de la règle de protection avec les vérifications obligatoires. |
| TP2-6 | une PR dont la fusion est bloquée par une vérification en échec. |
| TP2-7 | la PR de B avec le message de conflit. |
| TP2-8 | le fichier `CHANGELOG.md` final sur `main` contenant les deux lignes. |
| TP2-9 | les logs où la valeur du secret apparaît masquée par `***`. |
| TP2-10 | le run en échec de chaque pipeline (une capture par pipeline, nommées TP2-10A, TP2-10B, TP2-10C). |
| TP2-11 | la liste des runs montrant vos trois pipelines réparés au vert. |

## TP3 : captures

| N° | Capture à fournir |
|---|---|
| TP3-1 | le `docker build` réussi, puis `curl` sur `/health` qui répond `{"status":"ok"}`. |
| TP3-2 | `docker compose up` en cours et le `curl` sur `/version`. |
| TP3-3 | le run avec `test` puis `build` au vert. |
| TP3-4 | la page du package `tasks-api` avec son tag `sha-…`. |
| TP3-5 | la liste des tags du package (`0.1.0` et `sha-…`). |
| TP3-6 | `docker run` de l'image **téléchargée depuis GHCR** et `curl /version` qui répond `0.1.0`. |
| TP3-7 | le run en attente d'approbation (« Waiting » / « Review deployments »), puis le run terminé. |
| TP3-8 | la sortie de la commande `id` dans le conteneur. |

## TP4 : captures

| N° | Capture à fournir |
|---|---|
| TP4-1 | `kubectl get nodes` (un nœud `Ready`). |
| TP4-2 | `kubectl get pods -n argocd` (tous `Running`) et la page de connexion d'Argo CD. |
| TP4-3 | l'application dans Argo CD, état Synced et Healthy, avec ses 2 pods. |
| TP4-4 | la réponse de `/version` obtenue dans le cluster. |
| TP4-5 | le commit sur `replicas: 3` et les 3 pods dans Argo CD. |
| TP4-6 | les pods juste après le `kubectl scale` à 5, puis après la correction automatique (deux captures). |
| TP4-7 | l'historique des commits de `tasks-config` avec le `revert`, et le retour à 2 pods. |
| TP4-8 | le run complet avec tous les jobs au vert, `update-config` compris. |
| TP4-9 | le commit automatique dans `tasks-config` et Argo CD synchronisé sur `0.2.0`. |
| TP4-10 | `/version` qui répond `0.2.0`. |

Les **questions à traiter** sont dans l'énoncé de chaque TP (lignes « Question(s) »). Répondez-y avec vos mots dans le dossier.

## Conseils de présentation

- Des captures **lisibles** : recadrez sur la partie utile, pas l'écran entier.
- **Aucun secret visible** : ne montrez jamais un mot de passe, un jeton (token) ou une clé. Floutez-les si besoin.
- Numérotez et légendez **toutes** les captures, dans l'ordre des TP.
- Écrivez avec vos mots : un dossier copié-collé de l'énoncé ne sera pas valorisé.
