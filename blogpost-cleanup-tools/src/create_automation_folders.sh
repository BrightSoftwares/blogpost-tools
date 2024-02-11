#!/bin/bash

create_single_folder(){
    BASE_FOLDER=$1
    FOLDER_NAME=$2
    FULL_PATH=$BASE_FOLDER/$FOLDER_NAME
    GITKEEP=$FULL_PATH/.gitkeep

    echo "Create a folder in base $BASE_FOLDER with folder name $FOLDER_NAME"
    echo "Full path = $FULL_PATH"
    echo ""Gitkeep = $GITKEEP
    echo "mkdir -p $FULL_PATH"
    echo "gitkeep = $GITKEEP"

    mkdir -p $FULL_PATH
    touch $GITKEEP
}

create_automation_folders() {
    BASE_FOLDER=$1
    echo "Make sure that the base folder exists"
    echo "mkdir -p $BASE_FOLDER"

    echo "create automation folder with base $BASE_FOLDER"

    # create_single_folder $BASE_FOLDER 

    create_single_folder $BASE_FOLDER 200_youtube_download_transcript
    echo ""
    create_single_folder $BASE_FOLDER 300_generated_raw_content
    echo ""
    create_single_folder $BASE_FOLDER 200_rss_inspired_posts
    echo ""
    create_single_folder $BASE_FOLDER 400_refined_content
    echo ""
    create_single_folder $BASE_FOLDER 500_featured_image_generated
    echo ""
    create_single_folder $BASE_FOLDER 501_beautified_content
    echo ""
    create_single_folder $BASE_FOLDER 600_auto_scheduled
    echo ""
}

create_language_automation_folders(){
    THELANGUAGE=$1
    echo "Creating all the folders for $THELANGUAGE language"
    DRAFT_EN_FOLDERS=_drafts/$THELANGUAGE
    create_automation_folders $DRAFT_EN_FOLDERS
}

create_seo_folders(){
    echo "Creating the _seo folders"
    mkdir -p _seo/keyword-generation
    touch _seo/keyword-generation/.gitkeep

    mkdir -p _seo/markdown-linting
    touch _seo/markdown-linting/.gitkeep

    mkdir -p _seo/jekyll-filename-pretifier
    touch _seo/jekyll-filename-pretifier/.gitkeep

    mkdir -p _seo/internal-linking
    touch _seo/internal-linking/.gitkeep
}

# create_language_automation_folders en
# create_language_automation_folders fr
create_seo_folders
