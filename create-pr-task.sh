#!/usr/bin/env bash

set -e

WORK_LABEL_ID=2149844174
DEVELOPMENT_LABEL_ID=2149844309
REVIEW_LABEL_ID=2156922490
PROJECT_ID=2234888663
TASKS_URL="https://api.todoist.com/rest/v1/tasks"

if [[ -z "$TODOIST_API_TOKEN" ]]; then
    echo "TODOIST_API_TOKEN must be set to your API token"
    exit 1
fi

link=$1
if [[ -z "$link" ]]; then
    echo "A link to the PR must be specified."
    exit 1
fi

pr_id=$(echo "$link" | awk -F "/" '{ print $NF }')
user=$(az repos pr show --id "$pr_id" --organization https://dev.azure.com/DCFOrg | \
    jq .createdBy.displayName --raw-output)
repo_name=$(az repos pr show --id "$pr_id" --organization https://dev.azure.com/DCFOrg | \
    jq .repository.name --raw-output)
branch_name=$(az repos pr show --id "$pr_id" --organization https://dev.azure.com/DCFOrg | \
    jq .sourceRefName --raw-output | awk -F "/" '{ print $NF }')

(
cat << EOF
{
    "project_id": $PROJECT_ID,
    "content": "Review [PR]($link): $user requesting merge of \`$branch_name\` into \`$repo_name\`",
    "label_ids": [$WORK_LABEL_ID, $DEVELOPMENT_LABEL_ID, $REVIEW_LABEL_ID]
}
EOF
) | http --print HBhb POST "$TASKS_URL" \
    "Authorization: Bearer $TODOIST_API_TOKEN" \
    "Content-Type":"application/json" \
    "X-Request-Id":"$(uuidgen)"
