# tasks-config : dépôt de configuration (jour 4, GitOps)

Ce dossier est le **modèle** du dépôt de configuration. Au jour 4, vous le copierez dans un
**nouveau dépôt GitHub public** nommé `tasks-config` : c'est lui qu'Argo CD surveillera.

Ne le modifiez pas avant le jour 4 !

```
k8s/
  deployment.yaml   les pods de l'application et l'image à utiliser
  service.yaml      l'exposition de l'application dans le cluster
```

Dans `k8s/deployment.yaml`, remplacez `<votre-compte-github>` par votre identifiant GitHub **en minuscules**.

Règle d'or du GitOps : on ne modifie jamais le cluster à la main, on modifie ce dépôt.
