MDLINT_TEST_FILE=../test_md_files/corporate-website-master/blog/laravel.md

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

echo ">>> Detecting placeholders in the md file"
markdownlint --fix -c .mdlint_continue_replacement.jsonc -r markdownlint-rule-search-replace $MDLINT_TEST_FILE
if [ $? -eq 0 ]; then echo ">>> No placeholders tokens found. We can continue"; else echo ">>> There are still placeholders. Exiting"; exit 1; fi

echo ">>> Regular markdown rules. Nothing custom here. Fix it automatically"
markdownlint -c .markdownlint.original.jsonc -r markdownlint-rule-search-replace $MDLINT_TEST_FILE

#git checkout $MDLINT_TEST_FILE
