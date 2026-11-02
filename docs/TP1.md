# TP1 : Votre première CI avec GitHub Actions

**Durée : environ 3 h 30** · Jour 1, après-midi

## Objectif

À la fin de ce TP, chaque `git push` sur votre dépôt lance automatiquement les tests,
et vous savez lire un run GitHub Actions, y compris quand il échoue.

> 📸 **Pour votre dossier :** ce TP contient 7 captures d'écran à garder, repérées par « 📸 TP1-n ».
> La liste complète et les questions à traiter sont dans `docs/DOSSIER.md`.

## Avant de commencer

- [ ] Le script de vérification affiche « 0 en échec »
- [ ] Vous avez créé **votre** dépôt `tasks-api` depuis le modèle et vous l'avez cloné
- [ ] `pytest` est vert en local (10 tests réussis), dans l'environnement `.venv` activé
- [ ] Vous êtes sur une branche `tp1` : `git switch -c tp1`

### Les commandes qui changent selon votre système

| Action | macOS | Linux | Windows (PowerShell) |
|---|---|---|---|
| Créer l'environnement | `python3.12 -m venv .venv` | `python3 -m venv .venv` | `py -3.12 -m venv .venv` |
| L'activer | `source .venv/bin/activate` | `source .venv/bin/activate` | `.venv\Scripts\Activate.ps1` |
| Appeler l'API | `curl http://localhost:8000/health` | `curl http://localhost:8000/health` | `curl.exe http://localhost:8000/health` |

Tout le reste (`git`, `gh`, `pytest`, `pip`) est identique sur les trois systèmes.

### Pousser votre travail

```bash
git add .
git commit -m "Ajoute le workflow hello"
git push -u origin tp1
```

**Si GitHub refuse le push** avec un message contenant `refusing to allow an OAuth App to create or update workflow … without workflow scope` :
votre connexion n'a pas le droit « workflow ». Exécutez `gh auth refresh -s workflow`, suivez les instructions,
puis recommencez le `git push`.

**Si l'onglet Actions** affiche un bouton « I understand my workflows, go ahead and enable them » (cas d'un fork), cliquez dessus.

---

## Partie 1 : Hello Actions (30 min)

1. Créez le fichier `.github/workflows/hello.yml` (le dossier existe déjà).
2. Il doit se déclencher sur chaque `push`.
3. Il contient un job `hello` qui tourne sur `ubuntu-latest` et affiche :
   - un message de votre choix (`echo`) ;
   - le nom de la branche (variable `github.ref_name`) ;
   - l'auteur du commit (variable `github.actor`).
4. Poussez, puis ouvrez l'onglet **Actions** de votre dépôt.

> 📸 **TP1-1 :** le run « Hello » réussi, avec l'étape qui affiche la branche et l'auteur **dépliée**.

**Questions (à traiter dans le dossier) :** Combien de temps a duré le run ? Où voit-on les logs de chaque étape ?

> Indice : la structure minimale est `name`, `on`, `jobs`, puis `runs-on` et `steps`.

---

## Partie 2 : Lancer les tests automatiquement (45 min)

1. Créez `.github/workflows/ci.yml` avec un job `test`.
2. Étapes attendues, dans l'ordre :
   1. récupérer le code : action `actions/checkout@v6` ;
   2. installer Python 3.12 : action `actions/setup-python@v7`, avec `python-version: "3.12"` ;
   3. installer les dépendances : `pip install -r requirements-dev.txt` ;
   4. lancer les tests : `pytest`.
3. Poussez et vérifiez que le run est vert.

> 📸 **TP1-2 :** le run `ci.yml` réussi, avec la liste des étapes visible.

> Rappel : un workflow démarre sur une machine **vide**. Si une étape manque (checkout, Python, dépendances), les suivantes échouent.

---

## Partie 3 : Casser, observer, réparer (45 min)

1. Dans `app/logic.py`, modifiez volontairement `MAX_TITLE_LENGTH` (par exemple 5).
2. Poussez : le run doit devenir **rouge**.
3. Dans les logs, retrouvez :
   - le test qui échoue ;
   - le message d'erreur ;
   - la ligne exacte du fichier.
4. Corrigez, poussez : retour au vert.

> 📸 **TP1-3 :** le run rouge, avec l'étape `pytest` dépliée et le message d'erreur lisible.
> 📸 **TP1-4 :** le run vert qui suit la correction.

**Questions (à traiter dans le dossier) :** Quel test a échoué ? À quelle ligne ? Qu'est-ce qui a permis de le trouver rapidement ?

---

## Partie 4 : Pull request et badge (45 min)

1. Poussez votre branche `tp1` et ouvrez une **pull request** vers `main` sur votre dépôt.
2. Vérifiez que le résultat de la CI apparaît dans la PR.
3. Fusionnez la PR **uniquement si la CI est verte**.
4. Ajoutez le badge de statut en haut du `README.md` :

```markdown
![CI](https://github.com/<votre-compte>/tasks-api/actions/workflows/ci.yml/badge.svg)
```

> 📸 **TP1-5 :** la pull request avec les vérifications (checks) vertes, avant la fusion.
> 📸 **TP1-6 :** la pull request fusionnée.
> 📸 **TP1-7 :** le `README.md` sur GitHub avec le badge affiché.

**Question (à traiter dans le dossier) :** Pourquoi attend-on que la CI soit verte avant de fusionner ?

---

## Partie 5 : Aller plus loin (si vous avez fini)

- Faites tourner le workflow aussi sur les `pull_request`.
- Ajoutez une étape qui affiche la version de Python utilisée.
- Faites échouer volontairement le workflow avec `exit 1` : que se passe-t-il pour les étapes suivantes ?

---

## Checklist de fin de TP

- [ ] `hello.yml` et `ci.yml` existent et fonctionnent
- [ ] J'ai provoqué et corrigé un échec de CI
- [ ] Ma PR a été fusionnée avec la CI verte
- [ ] Le badge s'affiche dans mon README
- [ ] J'ai mes 7 captures TP1-1 à TP1-7 et mes réponses aux questions
