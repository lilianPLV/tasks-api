# ---------------------------------------------------------------
# Dockerfile À COMPLÉTER : TP3 (jour 3)
# Ne pas toucher avant le jour 3 !
# ---------------------------------------------------------------

# TODO 1 : choisir une image de base Python légère (python:3.12-slim)
FROM ???

# TODO 2 : définir le dossier de travail /app
WORKDIR ???

# TODO 3 : copier requirements.txt AVANT le code (pour profiter du cache),
#          puis installer les dépendances avec pip (--no-cache-dir)

# TODO 4 : copier le code de l'application

# TODO 5 : créer un utilisateur non-root et basculer dessus (USER)

# TODO 6 : embarquer la version et lancer l'app
#          - déclarer ARG APP_VERSION=dev puis ENV APP_VERSION=${APP_VERSION}
#            (c'est ce qui permet à /version de répondre 0.1.0 dans l'image publiée)
#          - exposer le port 8000 (EXPOSE)
#          - lancer l'app avec gunicorn :
#            gunicorn --bind 0.0.0.0:8000 app.main:app
