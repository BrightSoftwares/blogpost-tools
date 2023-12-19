#!/bin/bash

echo "Linting folder $INPUT_FOLDER_TO_LINT"

# markdownlint en/_posts/*.md -c .markdownlint.jsonc -r no_rendered_comments.js -r markdownlint-rule-search-replace
markdownlint $INPUT_FOLDER_TO_LINT -c /app/.markdownlint.jsonc -r /app/no_rendered_comments.js -r /app/markdownlint-rule-search-replace
# markdownlint $INPUT_FOLDER_TO_LINT
