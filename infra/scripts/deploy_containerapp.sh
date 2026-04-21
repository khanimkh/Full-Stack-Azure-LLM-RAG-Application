#!/usr/bin/env bash
set -euo pipefail

: "${AZURE_SUBSCRIPTION_ID:?Missing AZURE_SUBSCRIPTION_ID}"
: "${RESOURCE_GROUP:?Missing RESOURCE_GROUP}"
: "${CONTAINER_APP_NAME:?Missing CONTAINER_APP_NAME}"
: "${IMAGE_NAME:?Missing IMAGE_NAME}"
: "${IMAGE_TAG:?Missing IMAGE_TAG}"

az config set extension.use_dynamic_install=yes_without_prompt >/dev/null
az account set --subscription "${AZURE_SUBSCRIPTION_ID}"

if [[ -n "${GHCR_TOKEN:-}" ]]; then
  az containerapp registry set \
    --name "${CONTAINER_APP_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --server ghcr.io \
    --username "${GHCR_USERNAME:-github}" \
    --password "${GHCR_TOKEN}"
fi

az containerapp update \
  --name "${CONTAINER_APP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --image "${IMAGE_NAME}:${IMAGE_TAG}" \
  --min-replicas "${MIN_REPLICAS:-1}" \
  --max-replicas "${MAX_REPLICAS:-3}" \
  --scale-rule-name "http-${DEPLOYMENT_ENV:-env}" \
  --scale-rule-type http \
  --scale-rule-http-concurrency "${HTTP_CONCURRENCY:-25}" \
  --set-env-vars \
    AZURE_OPENAI_ENDPOINT="${AZURE_OPENAI_ENDPOINT:-}" \
    AZURE_OPENAI_CHAT_DEPLOYMENT="${AZURE_OPENAI_CHAT_DEPLOYMENT:-}" \
    AZURE_SEARCH_ENDPOINT="${SEARCH_ENDPOINT:-}" \
    AZURE_SEARCH_INDEX_NAME="${SEARCH_INDEX_NAME:-rag-docs-index}"

new_revision=$(az containerapp revision list \
  --name "${CONTAINER_APP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --query "sort_by(@, &properties.createdTime)[-1].name" \
  --output tsv)

if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  echo "new_revision=${new_revision}" >> "${GITHUB_OUTPUT}"
fi
