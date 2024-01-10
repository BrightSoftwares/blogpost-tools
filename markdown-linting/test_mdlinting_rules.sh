lint_andmove_markdownfile(){

    MDLINT_TEST_FILE=$1
    NEXT_FOLDER_PATH=$2

    echo ">>> Detect only the ##@@1234@@##, there is no fix for this one. We fix it manually"
    markdownlint -c .markdownlint.replacementtokens.jsonc -r markdownlint-rule-search-replace $MDLINT_TEST_FILE
    if [ $? -eq 0 ]; then 
        echo ">>> No replacement tokens found. We can continue"; 
        echo ">>> Detecting continue writing commands in the md file"
        markdownlint $MDLINT_TEST_FILE -c .mdlint_continue_replacement.jsonc -r markdownlint-rule-search-replace --fix
        if [ $? -eq 0 ]; then 
            echo ">>> No continue writing commands tokens found. We can continue"; 

            echo ">>> Detecting placeholders in the md file"
            markdownlint $MDLINT_TEST_FILE -c .mdlint.placeholders.jsonc -r markdownlint-rule-search-replace --fix
            if [ $? -eq 0 ]; then 
                echo ">>> No placeholders tokens found. We can continue"; 

                echo ">>> Regular markdown rules. Nothing custom here. Fix it automatically"
                markdownlint -c .markdownlint.original.jsonc -r markdownlint-rule-search-replace $MDLINT_TEST_FILE

                echo "All linting tests passed, moving the file to the next folder"
                if test -d $NEXT_FOLDER_PATH; then
                    echo "Destination Directory $NEXT_FOLDER_PATH exists."
                    echo "Moving file $MDLINT_TEST_FILE to $NEXT_FOLDER_PATH"
                    mv $MDLINT_TEST_FILE $NEXT_FOLDER_PATH
                else
                    echo "The folder $NEXT_FOLDER_PATH does not exist. Not moving..."
                    # exit 1
                fi
            else 
                echo ">>> There are still placeholders. Exiting"; 
                # exit 1; 
            fi
        else 
            echo ">>> There are still continue writing. Exiting"; 
            # exit 1; 
        fi
    else 
        echo ">>> There are still replacement tokens. Exiting"; 
        # exit 1; 
    fi

}

lint_files_infolder(){
    FOLDER_TO_PROCESS=$1
    DEST_FOLDER=$2

    echo "Linting markdown files in folder $FOLDER_TO_PROCESS. If correct move them to folder $DEST_FOLDER"

    FILES="$FOLDER_TO_PROCESS/*.md"
    for f in $FILES
    do
        echo "Processing $f file..."
        # take action on each file. $f store current file name
        #cat "$f"
        lint_andmove_markdownfile $f 
    done

}

git_restore_files(){
    FOLDER_TO_PROCESS=$1
    echo "Restoring files in folder $FOLDER_TO_PROCESS"

    FILES="$FOLDER_TO_PROCESS/*.md"
    for f in $FILES
    do
        echo ">>> Restore the markdown file $f to it's original state before testing"
        git checkout $f
        if [ $? -eq 0 ]; then echo ">>> $f Restored successfully"; else echo ">>> Error while restoring file $f"; fi
    done
}

MDLINT_SRC_FOLDER=$1
MDLINT_DST_FOLDER=$2

echo "Run the linting process over the $MDLINT_SRC_FOLDER and move result to $MDLINT_DST_FOLDER"
git_restore_files $MDLINT_SRC_FOLDER
lint_files_infolder $MDLINT_SRC_FOLDER $MDLINT_DST_FOLDER
lint_andmove_markdownfile $MDLINT_SRC_FOLDER $MDLINT_DST_FOLDER
