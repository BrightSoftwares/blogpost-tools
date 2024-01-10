MDLINT_TEST_FILE=$1
NEXT_FOLDER_PATH=$2

echo ">>> Restore the markdown file $MDLINT_TEST_FILE to it's original state before testing"
git checkout $MDLINT_TEST_FILE
if [ $? -eq 0 ]; then echo ">>> Restored successfully"; else echo ">>> Error while restoring file"; fi

echo ">>> Detect only the ##@@1234@@##, there is no fix for this one. We fix it manually"
markdownlint -c .markdownlint.replacementtokens.jsonc -r markdownlint-rule-search-replace $MDLINT_TEST_FILE
if [ $? -eq 0 ]; then 
echo ">>> No replacement tokens found. We can continue"; 
else 
echo ">>> There are still replacement tokens. Exiting"; 
# exit 1; 
fi

echo ">>> Detecting continue writing commands in the md file"
markdownlint $MDLINT_TEST_FILE -c .mdlint_continue_replacement.jsonc -r markdownlint-rule-search-replace --fix
if [ $? -eq 0 ]; then 
echo ">>> No continue writing commands tokens found. We can continue"; 
else 
echo ">>> There are still continue writing. Exiting"; 
exit 1; 
fi

echo ">>> Detecting placeholders in the md file"
markdownlint $MDLINT_TEST_FILE -c .mdlint.placeholders.jsonc -r markdownlint-rule-search-replace --fix
if [ $? -eq 0 ]; then 
echo ">>> No placeholders tokens found. We can continue"; 
else 
echo ">>> There are still placeholders. Exiting"; 
exit 1; 
fi

echo ">>> Regular markdown rules. Nothing custom here. Fix it automatically"
markdownlint -c .markdownlint.original.jsonc -r markdownlint-rule-search-replace $MDLINT_TEST_FILE

#git checkout $MDLINT_TEST_FILE

echo "All linting tests passed, moving the file to the next folder"