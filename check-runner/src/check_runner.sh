#!/bin/bash

echo "The repo name is ${{ github.repository }}"
echo "The repo org is ${{ github.repository_owner }}"
echo "Query runners at repo level"
curl -s -H "Accept: application/vnd.github+json" -H "Authorization: token ${{ CHECK_RUNNER_TOKEN }}" "https://api.github.com/repos/${{ github.repository }}/actions/runners"

echo "Query runners at org level"
curl -s -H "Accept: application/vnd.github+json" -H "Authorization: token ${{ CHECK_RUNNER_TOKEN }}" "https://api.github.com/orgs/${{ github.repository_owner }}/actions/runners"

# runners=$(curl -s -H "Accept: application/vnd.github+json" -H "Authorization: token ${{ CHECK_RUNNER_TOKEN }}" "https://api.github.com/repos/${{ github.repository }}/actions/runners")
runners=$(curl -s -H "Accept: application/vnd.github+json" -H "Authorization: token ${{ CHECK_RUNNER_TOKEN }}" "https://api.github.com/orgs/${{ github.repository_owner }}/actions/runners")
available=$(echo "$runners" | jq '.runners[] | select(.status == "online" and .busy == false and .labels[] .name == "self-hosted")')
if [ -n "$available" ]; then
echo "runner-label=self-hosted" >> $GITHUB_OUTPUT
else
echo "runner-label=ubuntu-latest" >> $GITHUB_OUTPUT
fi
