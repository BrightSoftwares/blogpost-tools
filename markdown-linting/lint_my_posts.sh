#!/bin/bash

echo "Linting folder $INPUT_FOLDER_TO_LINT"
markdownlint $INPUT_FOLDER_TO_LINT
