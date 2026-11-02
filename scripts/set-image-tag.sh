#!/usr/bin/env bash
# Met à jour le tag de l'image (et APP_VERSION) dans un manifeste Kubernetes.
# Usage : bash scripts/set-image-tag.sh k8s/deployment.yaml 0.2.0
# Utilisé au jour 4 par le pipeline pour modifier le dépôt de configuration.
set -euo pipefail

file="${1:?usage: set-image-tag.sh <fichier> <version>}"
version="${2:?usage: set-image-tag.sh <fichier> <version>}"

if ! [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Version invalide : '$version' (attendu : 1.2.3)" >&2
  exit 1
fi
if [ ! -f "$file" ]; then
  echo "Fichier introuvable : $file" >&2
  exit 1
fi

sed -i.bak -E "s|(image: ghcr\.io/[^:]+/tasks-api:).*|\1${version}|" "$file"
sed -i.bak -E "/name: APP_VERSION/{n;s|value: .*|value: \"${version}\"|;}" "$file"
rm -f "$file.bak"
echo "Image et APP_VERSION mis à jour : ${version}"
