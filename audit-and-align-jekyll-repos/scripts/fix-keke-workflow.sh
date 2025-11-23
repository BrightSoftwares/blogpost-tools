#!/bin/bash

GITHUB_TOKEN="$1"
BRANCH="migration/standardize-jekyll-20251123_182523"
REPO="BrightSoftwares/keke.li"

WORKFLOW='name: GitHub Pages publication

on:
  push:
    branches:
      - main
      - master
      - migration/*
  workflow_dispatch:

jobs:
  jekyll:
    runs-on: ubuntu-latest
    steps:

    - name: clone the repo without submodules
      uses: actions/checkout@v4

    - name: clone submodules
      uses: actions/checkout@v4
      with:
        repository: BrightSoftwares/jekyll-theme-common-includes
        path: _includes/common
        ssh-key: ${{ secrets.SUBMODULE_SSH_PRIVATE_KEY }}
        persist-credentials: false

    - uses: actions/cache@v4
      with:
        path: vendor/bundle
        key: ${{ runner.os }}-gems-${{ hashFiles('\''**/Gemfile'\'') }}
        restore-keys: |
          ${{ runner.os }}-gems-

    - uses:  BrightSoftwares/blogpost-tools/jekyll-action@main
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        target_branch: '\''prod'\''
        build_dir: ./build
        ALGOLIA_API_KEY: '\''${{ secrets.ALGOLIA_API_KEY }}'\''

    - uses: BrightSoftwares/blogpost-tools/action-netlify-deploy@main
      with:
        BUILD_DIRECTORY: '\''build'\''
        FUNCTIONS_DIRECTORY: '\'''\''
      env:
        NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
        NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
        NETLIFY_DEPLOY_MESSAGE: "Prod deploy v${{ github.ref }}"
        NETLIFY_DEPLOY_TO_PROD: true
        BUILD_COMMAND: "echo Skipping build the dependencies"
        INSTALL_COMMAND: "echo Skipping installing the dependencies"
'

CONTENT=$(echo -n "$WORKFLOW" | base64 -w 0)

# Get SHA
SHA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/contents/.github/workflows/jekyll.yml?ref=$BRANCH" | jq -r '.sha')

echo "SHA: $SHA"

# Update file
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Content-Type: application/json" \
  -d @- \
  "https://api.github.com/repos/$REPO/contents/.github/workflows/jekyll.yml" << EOF
{
  "message": "fix: Update workflow with ubuntu-latest, cache v4, checkout v4, workflow_dispatch",
  "content": "$CONTENT",
  "sha": "$SHA",
  "branch": "$BRANCH"
}
EOF
