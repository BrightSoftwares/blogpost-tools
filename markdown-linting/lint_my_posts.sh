#!/bin/bash

DST_FOLDER=/github/workspace/_seo/markdown-linting/
OUTPUT_FILE=$DST_FOLDER/linting_results.txt

echo "Create destimation folder $DST_FOLDER if not exist"

echo "Linting folder $INPUT_FOLDER_TO_LINT"
echo "Output file for the linting results $OUTPUT_FILE"

# markdownlint en/_posts/*.md -c .markdownlint.jsonc -r no_rendered_comments.js -r markdownlint-rule-search-replace
markdownlint $INPUT_FOLDER_TO_LINT -c /app/.markdownlint.jsonc -r /app/no_rendered_comments.js -o $OUTPUT_FILE
# markdownlint $INPUT_FOLDER_TO_LINT
