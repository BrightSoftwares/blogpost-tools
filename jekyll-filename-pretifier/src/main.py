# importing the module
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
import frontmatter
import os
from urllib.parse import urlparse, parse_qs
from slugify import slugify

#folder = '../../en/_drafts/'
folder = os.getenv('INPUT_DRAFTS_PATH')
wordpress_frontmatter = os.getenv('INPUT_WORDPRESS_FRONTMATTER', default=False)
entries = os.listdir(folder)
for entry in entries:
    print(entry)
    try:
        post = frontmatter.load(folder + "/" + entry)
        title = post['title'] if 'title' in post else None
        # ytvideo_url = post['youtube_video'] if 'youtube_video' in post else None
        pretified = post['pretified'] if 'pretified' in post else None
        post_date = post['date'] if 'date' in post else None
        fileref = post['ref'] if 'ref' in post else None

        if pretified is not True and title is not None:

            if post_date is None:
                post_date = datetime.now()
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
            
            print("Wordpress frontmatter variable = {} of type {}".format(wordpress_frontmatter, type(wordpress_frontmatter)))
            if wordpress_frontmatter == "true":
                print("Adding additional variables to frontmatter to support wordpress")
                post['featured_image'] = post['image']  if 'image' in post else None
                post['wp_url'] = "{}.md".format(slugify(title.lower()))
                post['menu_order'] = 0
                post['post_date'] = "{} 10:29:02".format(post['date'])  if 'date' in post else None
                post['post_excerpt'] = post['description']  if 'description' in post else None
                post['post_status'] = "future"
                post['taxonomy'] = { 'category': ['drones'], 'post_tag': ['diy', 'productivity'] }

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
