#!/bin/bash

echo "Linting folder $INPUT_FOLDER_TO_LINT"

# markdownlint en/_posts/*.md -c .markdownlint.jsonc -r no_rendered_comments.js -r markdownlint-rule-search-replace
markdownlint $INPUT_FOLDER_TO_LINT -c .markdownlint.jsonc -r no_rendered_comments.js -r markdownlint-rule-search-replace
# markdownlint $INPUT_FOLDER_TO_LINT
