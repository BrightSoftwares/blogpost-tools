import pandas as pd
import frontmatter
import os

folder_to_scan = "_drafts"
result_file_path = "drafts_analysis_result.csv"

# An empty dataframe
df = pd.DataFrame(columns=['image', 'author', 'content', 'category', 'date', 'description', 'layout', 'pretified', 'ref', 'tags', 'title', 'silot_terms', 'keyword_suggestion', 'post_inspiration', 'transcribed', 'youtube_video', 'youtube_video_id', 'filename'])
# Load the files in the path
print("Loading files ...")
entries = [f for f in os.listdir(folder_to_scan) if os.path.isfile(os.path.join(folder_to_scan, f)) and f.endswith(".md")]
print("Done")

total_nb_items = len(entries)
# Fill in the dataframe
for index, entry in enumerate(entries):
    try:
        print("{} / {}".format(index, total_nb_items))
        post = frontmatter.load(os.path.join(folder_to_scan, entry))
        

        image = post['image']  if 'image' in post else None
        author = post['author']  if 'author' in post else None
        content = post['content']  if 'content' in post else None
        category = post['category']  if 'category' in post else None
        date = post['date']  if 'date' in post else None
        description = post['description']  if 'description' in post else None
        layout = post['layout']  if 'layout' in post else None
        pretified = post['pretified']  if 'pretified' in post else None
        ref = post['ref']  if 'ref' in post else None
        tags = post['tags']  if 'tags' in post else None
        title = post['title']  if 'title' in post else None
        silot_terms = post['silot_terms']  if 'silot_terms' in post else None
        keyword_suggestion = post['keyword_suggestion']  if 'keyword_suggestion' in post else None
        post_inspiration = post['post_inspiration']  if 'post_inspiration' in post else None
        transcribed = post['transcribed']  if 'transcribed' in post else None
        youtube_video = post['youtube_video']  if 'youtube_video' in post else None
        youtube_video_id = post['youtube_video_id']  if 'youtube_video_id' in post else None

        #print("Cleaning")
        tags_str = "" if tags is None else ",".join(tags)
        image = image[:20] if image is not None else None
        content = content[:200] if content is not None else None
        description = description[:50] if description is not None else None
        ref = ref[:20] if ref is not None else None
        
        #print("Adding")
        df.loc[len(df)] = [image, author, content, category, date, description, layout, pretified, ref, tags_str, title, silot_terms, keyword_suggestion, post_inspiration, transcribed, youtube_video, youtube_video_id, entry]
    except Exception as e:
        print("Error happened for ({}). Error = ".format(entry), str(e))

# Save the result to csv
df.to_csv(result_file_path, index=None)
