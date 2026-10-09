#!/bin/bash

set -e

# Run install command
if [[ -n "${INSTALL_COMMAND}" ]]
then
  ${INSTALL_COMMAND}
elif [[ -f yarn.lock ]]
then
  yarn
else
  npm i
fi

# Run build command
if [[ -n "${BUILD_COMMAND}" ]]
then
  ${BUILD_COMMAND}
else
  npm run build
fi

if [[ -n "${INPUT_BUILD_DIRECTORY}" ]]
then
  BUILD_DIRECTORY=$INPUT_BUILD_DIRECTORY
else
  BUILD_DIRECTORY="build"
fi

if [[ -n "${INPUT_FUNCTIONS_DIRECTORY}" ]]
then
  FUNCTIONS_DIRECTORY=$INPUT_FUNCTIONS_DIRECTORY
else
  FUNCTIONS_DIRECTORY=""
fi

# Deploy to Netlify
export NETLIFY_SITE_ID="${NETLIFY_SITE_ID}"
export NETLIFY_AUTH_TOKEN="${NETLIFY_AUTH_TOKEN}"

# --no-build: the site is already built (BUILD_COMMAND above / the Jekyll action).
# Recent netlify-cli (27.11.0 confirmed) otherwise runs a framework build inside `netlify deploy`, which for
# Jekyll repos means `bundle exec jekyll build` in an image without Ruby (2026-10-08 incident).
COMMAND="netlify deploy --no-build --dir=${BUILD_DIRECTORY} --functions=${FUNCTIONS_DIRECTORY} --message=\"${NETLIFY_DEPLOY_MESSAGE}\""

if [[ "${NETLIFY_DEPLOY_TO_PROD}" == "true" ]]
then
  COMMAND+=" --prod"
elif [[ -n "${DEPLOY_ALIAS}" ]]
then
  COMMAND+=" --alias ${DEPLOY_ALIAS}"
fi

if [[ -n "${MONOREPO_PACKAGE}" ]]
then
  COMMAND+=" --filter ${MONOREPO_PACKAGE}"
fi

echo "Running command: $COMMAND"
OUTPUT=$(sh -c "$COMMAND")
echo "Command execution output: $OUTPUT"

# Set outputs
NETLIFY_OUTPUT=$(echo "$OUTPUT")
NETLIFY_PREVIEW_URL=$(echo "$OUTPUT" | grep -Eo '(http|https)://[a-zA-Z0-9./?=_-]*(--)[a-zA-Z0-9./?=_-]*') #Unique key: --
NETLIFY_LOGS_URL=$(echo "$OUTPUT" | grep -Eo '(http|https)://app.netlify.com/[a-zA-Z0-9./?=_-]*') #Unique key: app.netlify.com
NETLIFY_LIVE_URL=$(echo "$OUTPUT" | grep -Eo '(http|https)://[a-zA-Z0-9./?=_-]*' | grep -Eov "netlify.com") #Unique key: don't containr -- and app.netlify.com

echo "NETLIFY_OUTPUT<<EOF" >> $GITHUB_ENV
echo "$NETLIFY_OUTPUT" >> $GITHUB_ENV
echo "EOF" >> $GITHUB_ENV

echo "NETLIFY_PREVIEW_URL<<EOF" >> $GITHUB_ENV
echo "$NETLIFY_PREVIEW_URL" >> $GITHUB_ENV
echo "EOF" >> $GITHUB_ENV

echo "NETLIFY_LOGS_URL<<EOF" >> $GITHUB_ENV
echo "$NETLIFY_LOGS_URL" >> $GITHUB_ENV
echo "EOF" >> $GITHUB_ENV

echo "NETLIFY_LIVE_URL<<EOF" >> $GITHUB_ENV
echo "$NETLIFY_LIVE_URL" >> $GITHUB_ENV
echo "EOF" >> $GITHUB_ENV
