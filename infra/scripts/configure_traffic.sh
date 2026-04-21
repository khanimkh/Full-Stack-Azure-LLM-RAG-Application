#!/usr/bin/env bash
set -euo pipefail

: "${AZURE_SUBSCRIPTION_ID:?Missing AZURE_SUBSCRIPTION_ID}"
: "${RESOURCE_GROUP:?Missing RESOURCE_GROUP}"
: "${CONTAINER_APP_NAME:?Missing CONTAINER_APP_NAME}"

az config set extension.use_dynamic_install=yes_without_prompt >/dev/null
az account set --subscription "${AZURE_SUBSCRIPTION_ID}"

new_revision="${NEW_REVISION:-}"
if [[ -z "${new_revision}" ]]; then
  new_revision=$(az containerapp revision list \
    --name "${CONTAINER_APP_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --query "sort_by(@, &properties.createdTime)[-1].name" \
    --output tsv)
fi

if [[ "${TRAFFIC_MODE:-latest}" == "latest" ]]; then
  az containerapp ingress traffic set \
    --name "${CONTAINER_APP_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --revision-weight "${new_revision}=100"
  exit 0
fi

current_revision=$(az containerapp ingress traffic show \
  --name "${CONTAINER_APP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --query "[?weight > \`0\` && revisionName != null][0].revisionName" \
  --output tsv)

stable_weight=$((100 - ${CANARY_WEIGHT:-20}))

az containerapp ingress traffic set \
  --name "${CONTAINER_APP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --revision-weight "${current_revision}=${stable_weight}" "${new_revision}=${CANARY_WEIGHT:-20}"
