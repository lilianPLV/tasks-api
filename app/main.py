"""Petite API de gestion de tâches : le fil rouge du cours GitOps & CI/CD."""

import os

from flask import Flask, jsonify, request

from app.logic import is_valid_title, normalize_title


def create_app() -> Flask:
    app = Flask(__name__)
    tasks: list[dict] = []

    @app.get("/")
    def index():
        return jsonify(message="Bienvenue sur l'API du cours GitOps & CI/CD")

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.get("/version")
    def version():
        # La version est injectée par le pipeline (variable d'environnement).
        return jsonify(version=os.getenv("APP_VERSION", "dev"))

    @app.get("/tasks")
    def list_tasks():
        return jsonify(tasks)

    @app.post("/tasks")
    def add_task():
        payload = request.get_json(silent=True) or {}
        title = payload.get("title", "")
        if not isinstance(title, str) or not is_valid_title(title):
            return jsonify(error="titre invalide"), 400
        task = {"id": len(tasks) + 1, "title": normalize_title(title)}
        tasks.append(task)
        return jsonify(task), 201

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
