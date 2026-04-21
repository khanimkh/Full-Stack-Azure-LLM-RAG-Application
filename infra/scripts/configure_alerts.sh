#!/usr/bin/env bash
set -euo pipefail

: "${AZURE_SUBSCRIPTION_ID:?Missing AZURE_SUBSCRIPTION_ID}"
: "${RESOURCE_GROUP:?Missing RESOURCE_GROUP}"
: "${CONTAINER_APP_NAME:?Missing CONTAINER_APP_NAME}"

az config set extension.use_dynamic_install=yes_without_prompt >/dev/null
az account set --subscription "${AZURE_SUBSCRIPTION_ID}"

app_id=$(az containerapp show \
  --name "${CONTAINER_APP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --query id \
  --output tsv)

az monitor metrics alert create \
  --name "${CONTAINER_APP_NAME}-${DEPLOYMENT_ENV:-env}-cpu" \
  --resource-group "${RESOURCE_GROUP}" \
  --scopes "${app_id}" \
  --condition "avg CpuUsage > ${CPU_ALERT_THRESHOLD:-75}" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 2 \
  --auto-mitigate true \
  --only-show-errors >/dev/null
