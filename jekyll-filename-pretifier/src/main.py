from datetime import datetime, date
from youtube_transcript_api import YouTubeTranscriptApi
import frontmatter
import os
import re
from urllib.parse import urlparse, parse_qs
from slugify import slugify

#folder = '../../en/_drafts/'
folder = os.getenv('INPUT_DRAFTS_PATH')
wordpress_frontmatter = os.getenv('INPUT_WORDPRESS_FRONTMATTER', default=False)
post_author_env = os.getenv('INPUT_POST_AUTHOR', 1)
dry_run = os.getenv('INPUT_DRY_RUN', False)
entries = os.listdir(folder)

def get_clean_description(content):

  #print("get_clean_description > content =", content)
  # Process line by line and 
  #   ignore the lines that begin with #
  #   ignore the lines that begin with ![
  final_text = ""
  for line in content.split("\n"):
    # Remove tabs and line returns and white spaces
    line_striped = line.strip(' \t\n\r') #re.sub('[\s+]', ' ', line)
    #print("line_striped =", line_striped)

    if not line_striped.startswith("#") and not line_striped.startswith("!["):
      final_text = final_text + " " + line_striped
      #final_text += " "

  # Get 160 words instead of 160 characters.
  
  clean_description = " ".join(final_text.split(" ")[:160]).strip() # final_text[:160]
  print("clean_description = ", clean_description)
  return clean_description


for entry in entries:
    print(entry)
    try:
        post = frontmatter.load(folder + "/" + entry)
        title = post['title'] if 'title' in post else None
        # ytvideo_url = post['youtube_video'] if 'youtube_video' in post else None
        pretified = post['pretified'] if 'pretified' in post else None
        post_date = post['date'] if 'date' in post else None
        fileref = post['ref'] if 'ref' in post else None
        post_category = post['category'] if 'category' in post else []
        post_description = post['description'] if 'description' in post else None
        post_image = post['image'] if 'image' in post else None
        post_author = post['post_author'] if 'post_author' in post else post_author_env
        post_tags = post['tags'] if 'tags' in post else []

        print("post category: {} of type {}".format(post_category, type(post_category)))
        print("post tags: {} of type {}".format(post_tags, type(post_tags)))

        if pretified is not True and title is not None:

            if post_date is None:
                post_date = date.today() # datetime.now()
                post['date'] = post_date

            if fileref is None:
                fileref = slugify(title.lower())

            oldfilename = "{}/{}".format(folder, entry)
            
            #if wordpress_frontmatter == "true":
            #    # we don't add the date in the post filename
            #    newfilename = "{}/{}.md".format(folder, slugify(title.lower()))
            #else:
            #    newfilename = "{}/{}-{}.md".format(folder, post_date.strftime("%Y-%m-%d"),
            #                                       slugify(title.lower()))
                
            newfilename = "{}/{}-{}.md".format(folder, post_date.strftime("%Y-%m-%d"), slugify(title.lower()))
            newfilename_nodate = "{}/{}.md".format(folder, slugify(title.lower()))

            print("Saving pretified and ref tags")
            post['pretified'] = True
            post['ref'] = fileref
            
            # Make the image item appear in the frontmatter if there was no image supplied
            if 'image' not in post:
                post['image'] = None
                
            # Make the tags item appear in the frontmatter if there was no tags supplied
            if 'tags' not in post:
                # We use the keyword_suggestion if there is any
                if 'keyword_suggestion' in post:
                    post['tags'] = post['keyword_suggestion'].split(' ')
                else:
                    post['tags'] = []
                # Finally assign the tags
                post_tags = post['tags']
                
            # If there was no description provided, we take the first 160 characters of the content
            if 'description' not in post or post['description'] == '':
                post['description'] = get_clean_description(post.content)
            
            print("Wordpress frontmatter variable = {} of type {}".format(wordpress_frontmatter, type(wordpress_frontmatter)))
            if wordpress_frontmatter == "true":
                print("Adding additional variables to frontmatter to support wordpress")
                post['featured_image'] = post['image']  if 'image' in post else None
                post['wp_url'] = "{}".format(slugify(title.lower()))
                post['menu_order'] = 0
                post['post_date'] = "{} 03:29:02".format(post['date'])  if 'date' in post else None
                post['post_excerpt'] = post['description']  if 'description' in post else None
                post['post_author'] = post_author
                post['post_status'] = "future"

                wp_post_category = [ cat for cat in post_category ]
                wp_post_tags = [ tg for tg in post_tags ]
                post['taxonomy'] = { 'category': wp_post_category, 'post_tag': wp_post_tags }

            if dry_run == "true":
              print("---> In dry run mode. Not saving files")
            else:
              print("Saving the content of the file")
              filecontent = frontmatter.dumps(post)
              with open(oldfilename, 'w') as f:
                  f.write(filecontent)

              print("Renaming the file to the correct file name")
              os.rename(oldfilename, newfilename)

        else:
            print("Did not process this file because Pretified = True ({}) or title was None ()".format(
                pretified, title))

    except Exception as e:
        print("Error. = ", str(e))
