#!/usr/bin/env bash
# Build the image, load it into a local kind cluster and install the chart.
set -euo pipefail

CLUSTER="${CLUSTER:-demo}"
IMAGE_REPO="demo-api"
TAG="local"

command -v kind >/dev/null || { echo "kind is required: https://kind.sigs.k8s.io"; exit 1; }
command -v helm >/dev/null || { echo "helm is required: https://helm.sh"; exit 1; }

kind get clusters | grep -qx "$CLUSTER" || kind create cluster --name "$CLUSTER"

docker build -t "$IMAGE_REPO:$TAG" .
kind load docker-image "$IMAGE_REPO:$TAG" --name "$CLUSTER"

helm upgrade --install demo charts/demo-api \
  --namespace demo --create-namespace \
  --set image.repository="$IMAGE_REPO" \
  --set image.tag="$TAG" \
  --set autoscaling.enabled=false \
  --wait

echo "Deployed. Try: kubectl -n demo port-forward svc/demo-demo-api 8080:80 && curl localhost:8080/healthz"
