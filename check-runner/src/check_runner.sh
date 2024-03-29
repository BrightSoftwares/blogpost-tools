#!/bin/bash

echo "My current shell is $SHELL ($0)"
echo $SHELL
echo "Old fashioned way to know your shell name "
ps -p $$
echo "With the echo $0 technique"
echo $0

echo "If user forced to run on github infra, return ubuntu and exit"
if [[ $FORCE_RUNS_ON_UBUNTU == 'true' ]]; then
  echo "User forced to run on github infra. Returning ubuntu latest. FORCE_RUNS_ON_UBUNTU = $FORCE_RUNS_ON_UBUNTU"
  echo "runner-label=ubuntu-latest" >> $GITHUB_OUTPUT
  echo "Exiting..."
  exit
else
  echo "Not forced to run on github infra. We continue. FORCE_RUNS_ON_UBUNTU = $FORCE_RUNS_ON_UBUNTU"
fi

echo "User provided repo name is $GITHUB_REPOSITORY"
echo "User provided repo org is $GITHUB_REPO_OWNER"

echo "Get the repo org name env variable if the user did not provide it"
if [[ -n "$GITHUB_REPO_OWNER" || -z "$GITHUB_REPO_OWNER" ]]; then
GITHUB_REPO_OWNER=$GITHUB_REPOSITORY_OWNER
fi

echo "The repo name is $GITHUB_REPOSITORY"
echo "The repo org is $GITHUB_REPO_OWNER"
#echo "The token is $CHECK_RUNNER_TOKEN"

echo "Query runners at repo level"
curl -s -H "Accept: application/vnd.github+json" -H "Authorization: token $CHECK_RUNNER_TOKEN" "https://api.github.com/repos/$GITHUB_REPOSITORY/actions/runners"

echo "Query runners at org level"
curl -s -H "Accept: application/vnd.github+json" -H "Authorization: token $CHECK_RUNNER_TOKEN" "https://api.github.com/orgs/$GITHUB_REPO_OWNER/actions/runners"

# runners=$(curl -s -H "Accept: application/vnd.github+json" -H "Authorization: token ${{ CHECK_RUNNER_TOKEN }}" "https://api.github.com/repos/${{ github.repository }}/actions/runners")
runners=$(curl -s -H "Accept: application/vnd.github+json" -H "Authorization: token $CHECK_RUNNER_TOKEN" "https://api.github.com/orgs/$GITHUB_REPO_OWNER/actions/runners")

#if [[ -z "$runners" || -n "$runners" ]]; then 
if [[ -z "$runners" ]]; then 
  echo "NULL";
  echo "We couldn't retrieve the runners data. Got $runners"; 
  echo "Defaulting to ubuntu-latest as runner";
  echo "runner-label=ubuntu-latest" >> $GITHUB_OUTPUT
else 
  echo "Not NULL"; 
  echo "Success! Got the runners data = $runners";
  available=$(echo "$runners" | jq 'select(.runners != null) | .runners[] | select(.status == "online" and .busy == false and .labels[] .name == "self-hosted")')
  
  if [ -n "$available" ]; then
    echo "Found $available runners. Available value = $available"
    echo "Choosing self hosted"
    echo "runner-label=self-hosted" >> $GITHUB_OUTPUT
  else
    echo "No runners found. available value = $available"
    echo "Choosing ubuntu latest"
    echo "runner-label=ubuntu-latest" >> $GITHUB_OUTPUT
  fi
fi

#echo "runner-label=ubuntu-latest" >> $GITHUB_OUTPUT
echo "Final value of echo GITHUB_OUTPUT = $GITHUB_OUTPUT"
