mkdir -p _drafts/200_youtube_download_transcript/
mkdir -p _drafts/300_generated_raw_content/
mkdir -p _drafts/200_rss_inspired_posts/
mkdir -p _drafts/400_refined_content/
mkdir -p _drafts/500_featured_image_generated/
mkdir -p _drafts/501_beautified_content/
mkdir -p _drafts/600_auto_scheduled/

echo "Create the .gitkeep file inside the folders"
touch _drafts/200_youtube_download_transcript/.gitkeep
touch _drafts/300_generated_raw_content/.gitkeep
touch _drafts/200_rss_inspired_posts/.gitkeep
touch _drafts/400_refined_content/.gitkeep
touch _drafts/500_featured_image_generated/.gitkeep
touch _drafts/501_beautified_content/.gitkeep
touch _drafts/600_auto_scheduled/.gitkeep



mkdir -p _drafts/300_generated_raw_content/900_posts_1/
mkdir -p _drafts/300_generated_raw_content/900_posts_2/
mkdir -p _drafts/300_generated_raw_content/900_posts_3/
mkdir -p _drafts/300_generated_raw_content/900_posts_4/
mkdir -p _drafts/300_generated_raw_content/900_posts_5/
mkdir -p _drafts/300_generated_raw_content/900_posts_6/
mkdir -p _drafts/300_generated_raw_content/900_posts_7/
mkdir -p _drafts/300_generated_raw_content/900_posts_8/
mkdir -p _drafts/300_generated_raw_content/900_posts_9/
mkdir -p _drafts/300_generated_raw_content/900_posts_10/
mkdir -p _drafts/300_generated_raw_content/900_posts_11/
mkdir -p _drafts/300_generated_raw_content/900_posts_12/
mkdir -p _drafts/300_generated_raw_content/900_posts_13/
mkdir -p _drafts/300_generated_raw_content/900_posts_14/
mkdir -p _drafts/300_generated_raw_content/900_posts_15/
mkdir -p _drafts/300_generated_raw_content/900_posts_16/
mkdir -p _drafts/300_generated_raw_content/900_posts_17/

mkdir -p _drafts/300_generated_raw_content/900_posts_$count/;count=$count+1;find _drafts/ -name '*.md' | head -n 900 | xargs -d $'\n' mv -t _drafts/300_generated_raw_content/900_posts_$count/



mv `ls *.md | head -900` ./_drafts/300_generated_raw_content/900_posts_1/

find _drafts/ -name '*.md' | head -n 900 | xargs -d $'\n' mv -t _drafts/300_generated_raw_content/900_posts_1/

mkdir -p _drafts/300_generated_raw_content/900_posts_$count/ && find _drafts/ -maxdepth 1 -name '*.md' | head -n 900 | xargs -d $'\n' mv -t _drafts/300_generated_raw_content/900_posts_$count/ && echo $((count++))

