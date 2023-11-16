#!/bin/bash

echo "My current shell is $SHELL ($0)"
echo $SHELL
echo "Old fashioned way to know your shell name "
ps -p $$
echo "With the echo $0 technique"
echo $0

echo "The repo name is $GITHUB_REPOSITORY"
echo "The repo org is $GITHUB_REPO_OWNER"
echo "Query runners at repo level"
curl -s -H "Accept: application/vnd.github+json" -H "Authorization: token $CHECK_RUNNER_TOKEN" "https://api.github.com/repos/$GITHUB_REPOSITORY/actions/runners"

echo "Query runners at org level"
curl -s -H "Accept: application/vnd.github+json" -H "Authorization: token $CHECK_RUNNER_TOKEN" "https://api.github.com/orgs/$GITHUB_REPO_OWNER/actions/runners"

# runners=$(curl -s -H "Accept: application/vnd.github+json" -H "Authorization: token ${{ CHECK_RUNNER_TOKEN }}" "https://api.github.com/repos/${{ github.repository }}/actions/runners")
runners=$(curl -s -H "Accept: application/vnd.github+json" -H "Authorization: token $CHECK_RUNNER_TOKEN" "https://api.github.com/orgs/$GITHUB_REPO_OWNER/actions/runners")
available=$(echo "$runners" | jq '.runners[] | select(.status == "online" and .busy == false and .labels[] .name == "self-hosted")')
if [ -n "$available" ]; then
echo "runner-label=self-hosted" >> $GITHUB_OUTPUT
else
echo "runner-label=ubuntu-latest" >> $GITHUB_OUTPUT
fi
