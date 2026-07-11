#!/usr/bin/env bash
# Builds and pushes all 5 images to Docker Hub under your username, then
# rewrites the k8s manifests to reference them. Automates the manual
# loop from docs/03-push-dockerhub.md — read that doc first if you want
# to understand each step before running this.
#
# Usage: ./scripts/push-to-dockerhub.sh <dockerhub-username> [tag]
set -euo pipefail

USERNAME="${1:?Usage: $0 <dockerhub-username> [tag]}"
TAG="${2:-v1}"

SERVICES=(smile-service glasses-service eyes-service gateway frontend)

echo "Logging in to Docker Hub..."
docker login

for svc in "${SERVICES[@]}"; do
  if [ -d "models/$svc" ]; then
    context="models/$svc"
  else
    context="$svc"
  fi
  echo "Building and pushing $USERNAME/$svc:$TAG ..."
  docker build -t "$USERNAME/$svc:$TAG" "$context"
  docker push "$USERNAME/$svc:$TAG"
done

echo
echo "Updating k8s manifests to reference $USERNAME/*:$TAG ..."
sed -i.bak -E "s#REPLACE_WITH_YOUR_DOCKERHUB_USERNAME/([a-z-]+):v1#$USERNAME/\1:$TAG#g" k8s/*.yaml
find k8s -name "*.bak" -delete

echo
echo "Done. Pushed images:"
for svc in "${SERVICES[@]}"; do
  echo "  $USERNAME/$svc:$TAG"
done
echo
echo "k8s/*.yaml now point at your images. Continue at docs/04-local-k8s-setup.md."
