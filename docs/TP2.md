# TP2 : Une CI solide

**Durée : environ 3 h 30** · Jour 2, après-midi

## Objectif

Transformer la CI minimale du jour 1 en CI de qualité : analyse du code, couverture, plusieurs versions de Python,
cache, protection de la branche `main`, travail à deux sur un même dépôt et gestion d'un secret.

> 📸 Ce TP contient 11 captures pour le dossier (TP2-1 à TP2-11). La liste et les questions sont dans `docs/DOSSIER.md`.

## Avant de commencer

- [ ] Votre TP1 est terminé : `ci.yml` fonctionne et `main` est à jour (`git switch main && git pull`)
- [ ] Environnement `.venv` activé, puis `pip install -r requirements-dev.txt` (ajoute `black`)
- [ ] Travaillez sur une branche : `git switch -c tp2`
- [ ] Vous avez un **binôme** pour la partie 4 (sinon, voir « Si vous êtes seul »)

---

## Partie 1 : Qualité automatique (35 min)

1. En local, lancez `flake8 .` puis `black --check .` : les deux doivent réussir.
2. Séparez votre CI en **deux jobs** dans `ci.yml` : `lint` (flake8 + `black --check`) et `test` (pytest).
3. Ajoutez un **seuil de couverture** au job `test` : `pytest --cov=app --cov-fail-under=80`.
4. Cassez volontairement le linter (ajoutez un `import os` inutilisé dans `app/logic.py`), poussez : le job `lint` doit devenir rouge.
5. Corrigez, poussez : retour au vert.

> 📸 **TP2-1 :** un run vert montrant les deux jobs `lint` et `test`.
> 📸 **TP2-2 :** le job `lint` rouge, avec le message de flake8 lisible.

**Questions :** Quelle différence entre un linter (flake8) et un formateur (black) ? Pourquoi séparer `lint` et `test` en deux jobs ?

---

## Partie 2 : Matrix, cache et artefact (35 min)

1. Transformez le job `test` pour qu'il tourne sur **Python 3.11, 3.12 et 3.13** avec une `matrix`.
   Attention : écrivez les versions **entre guillemets** (`"3.11"`).
2. Activez le **cache** de pip : dans `actions/setup-python`, ajoutez `cache: pip`.
3. Poussez deux fois de suite. Au 2ᵉ run, ouvrez l'étape setup-python : vous devez lire que le cache a été restauré.
4. Générez un rapport de couverture (`--cov-report=xml`) et publiez-le comme **artefact** avec `actions/upload-artifact@v7`
   (uniquement pour la version 3.12 : `if: matrix.python-version == '3.12'`).
5. Téléchargez l'artefact depuis la page du run.

> 📸 **TP2-3 :** la liste des 3 jobs de la matrice (`test (3.11)`, `test (3.12)`, `test (3.13)`).
> 📸 **TP2-4 :** l'étape setup-python du 2ᵉ run, avec la mention du cache restauré, et la section « Artifacts » de la page du run.

**Questions :** Pourquoi tester sur plusieurs versions de Python ? Que gagne-t-on avec le cache ? Un artefact, c'est quoi ?

---

## Partie 3 : Protéger la branche main (15 min)

1. Sur GitHub : **Settings → Branches** (ou **Rules → Rulesets**) → créez une règle pour la branche `main`.
2. Cochez : *Require a pull request before merging* et *Require status checks to pass before merging*.
3. Choisissez comme vérifications obligatoires : `lint` et `test (3.12)`.
   (Un contrôle n'apparaît dans la liste que s'il a tourné récemment : lancez la CI avant.)
4. Ouvrez une PR depuis `tp2` qui fait échouer volontairement un test, et constatez que la fusion est **bloquée**.
5. Corrigez : le bouton de fusion se débloque.

> 📸 **TP2-5 :** la page de la règle de protection avec les vérifications obligatoires.
> 📸 **TP2-6 :** une PR dont la fusion est bloquée par une vérification en échec.

**Question :** Pourquoi interdire de pousser directement sur `main` ?

---

## Partie 4 : Pull request croisée et conflit (45 min)

**Binôme A et binôme B travaillent sur le dépôt de A.** A ajoute B comme collaborateur
(Settings → Collaborators), B accepte l'invitation, puis clone le dépôt de A.

1. A et B partent **tous les deux** de `main` à jour et créent chacun une branche (`entree-a`, `entree-b`).
2. Chacun ajoute **une ligne différente** sous « Non publié » dans `CHANGELOG.md`, au **même endroit** (juste sous la première ligne).
3. Chacun pousse sa branche et ouvre une pull request vers `main`.
4. **A fusionne** sa PR (CI verte). La PR de B affiche maintenant : *This branch has conflicts*.
5. **B résout le conflit** dans son terminal :

```bash
git fetch origin
git merge origin/main        # Git signale un conflit dans CHANGELOG.md
# ouvrez CHANGELOG.md : gardez LES DEUX lignes, supprimez les marqueurs <<<<<<<, =======, >>>>>>>
git add CHANGELOG.md
git commit -m "Résout le conflit sur CHANGELOG"
git push
```

6. La CI repasse au vert sur la PR de B ; B fusionne.

> 📸 **TP2-7 :** la PR de B avec le message de conflit.
> 📸 **TP2-8 :** le fichier `CHANGELOG.md` final sur `main` contenant les deux lignes.

**Si vous êtes seul :** créez vous-même deux branches depuis `main`, modifiez la même ligne de `CHANGELOG.md` sur chacune, fusionnez la première puis résolvez le conflit sur la seconde.

**Questions :** Pourquoi Git ne peut-il pas résoudre ce conflit seul ? Qu'est-ce qui a vérifié le code après la résolution ?

---

## Partie 5 : Un secret dans le pipeline (20 min)

1. Sur GitHub : **Settings → Secrets and variables → Actions** : créez un **secret** `DEMO_TOKEN` (valeur de votre choix, par exemple `abc123`).
   Dans l'onglet **Variables**, créez une variable `APP_ENV` = `staging`.
2. Créez `.github/workflows/secret-demo.yml`, déclenché **à la demande** (`workflow_dispatch`), avec un job qui :
   - lit le secret via `${{ secrets.DEMO_TOKEN }}` placé dans une variable d'environnement ;
   - échoue (`exit 1`) s'il est vide ;
   - affiche la longueur du secret (`${#DEMO_TOKEN}`) ;
   - essaie d'afficher sa valeur avec `echo` ;
   - affiche la variable `${{ vars.APP_ENV }}`.
3. Lancez le workflow depuis l'onglet Actions (**Run workflow**) et ouvrez les logs.

> 📸 **TP2-9 :** les logs où la valeur du secret apparaît masquée par `***`.
> ⚠️ Ne mettez **jamais** un vrai secret dans une capture ou dans le code.

**Questions :** Pourquoi GitHub masque-t-il le secret ? Que se passe-t-il si on le commite dans le dépôt ? Secret ou variable : comment choisir ?

---

## Partie 6 : Trois pipelines à réparer (30 min)

Dans le dossier `pipelines-a-reparer/` : trois workflows (A, B, C) avec **un bug chacun**. Suivez `pipelines-a-reparer/LISEZMOI.md`.

> 📸 **TP2-10 :** le run en échec de chaque pipeline (une capture par pipeline, nommées TP2-10A, TP2-10B, TP2-10C).
> 📸 **TP2-11 :** la liste des runs montrant vos trois pipelines réparés au vert.

**Questions :** Pour chaque pipeline : quel était le bug, comment l'avez-vous trouvé, comment l'éviter à l'avenir ?

---

## Checklist de fin de TP

- [ ] `ci.yml` : jobs `lint` et `test` (matrix, cache, couverture ≥ 80 %, artefact)
- [ ] `main` protégée : PR et vérifications obligatoires
- [ ] Conflit résolu dans une PR croisée
- [ ] Secret utilisé sans jamais être affiché
- [ ] Les trois pipelines A, B, C sont réparés
- [ ] Mes 11 captures et mes réponses sont dans le dossier
