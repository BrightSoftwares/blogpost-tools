from datetime import datetime, date
from youtube_transcript_api import YouTubeTranscriptApi
import frontmatter
import pandas as pd
import os
import re
from urllib.parse import urlparse, parse_qs
from slugify import slugify

#folder = '../../en/_drafts/'
folder = os.getenv('INPUT_DRAFTS_PATH')
force_pretify = os.getenv('INPUT_FORCE_PRETIFY', False)
wordpress_frontmatter = os.getenv('INPUT_WORDPRESS_FRONTMATTER', default=False)
post_author_env = os.getenv('INPUT_POST_AUTHOR', 1)
dry_run = os.getenv('INPUT_DRY_RUN', False)
silot_term_to_links = os.getenv('INPUT_SILOTERM_TO_LINKS_FILE', None)
silot_term_to_categories = os.getenv('INPUT_SILOTERM_TO_CATEGORIES_FILE', None)
default_author = os.getenv('INPUT_DEFAULT_AUTHOR', None)
default_layout = os.getenv('INPUT_DEFAULT_LAYOUT', None)
category_type = os.getenv('INPUT_CATEGORY_TYPE', "categories")
generate_silottermtolinks_file_if_missing = os.getenv('INPUT_GENERATE_SILOTERMTOLINKSFILE_IF_MISSING', False)
generate_silottermtocategories_file_if_missing = os.getenv('INPUT_GENERATE_SILOTERMTOCATEGORIESFILE_IF_MISSING', False)
file_generation_src_path = os.getenv('INPUT_FILE_GENERATION_SRC_PATH')
entries = os.listdir(folder)


def generate_silottermtocategories_file(file_path, folder_to_scan):
  print("Generating silot term to categories file from {} to {}".format(folder_to_scan, file_path))
  # An empty dataframe
  df = pd.DataFrame(columns=['silot_terms', 'category'])
  # Load the files in the path
  entries = [f for f in os.listdir(folder_to_scan) if os.path.isfile(os.path.join(folder_to_scan, f))]

  # Fill in the dataframe
  for entry in entries:
    try:
      post = frontmatter.load(os.path.join(folder_to_scan, entry))
      current_silotterm = post['silot_terms']  if 'silot_terms' in post else None
      current_categories = post[category_type]  if category_type in post else []

      if current_silotterm != "" and current_silotterm is not None and current_categories is not None and len(current_categories) > 0:
        for category in current_categories:
          df.loc[len(df)] = [current_silotterm, category]
      else:
        print("Cannot process this silot term ({}) for categories ({}) because they are empty or None".format(current_silotterm, current_categories))
    except Exception as e:
      print("Error occured during analysis of the file {}. ".format(entry), str(e))

  # Remove the duplicates
  df = df.drop_duplicates()

  # Save the result to csv
  df.to_csv(file_path, index=None)

  # Return the dataframe
  return df


def generate_silottermtolinks_file(file_path, folder_to_scan):
  print("Generating silot term to links file from {} to {}".format(folder_to_scan, file_path))
  # An empty dataframe
  df = pd.DataFrame(columns=['silot_terms', 'link'])
  # Load the files in the path
  entries = [f for f in os.listdir(folder_to_scan) if os.path.isfile(os.path.join(folder_to_scan, f))]

  # Fill in the dataframe
  for entry in entries:
    try:
      post = frontmatter.load(os.path.join(folder_to_scan, entry))
      current_silotterm = post['silot_terms']  if 'silot_terms' in post else None
      current_links = post['seo']['links']  if 'seo' in post else []

      if current_silotterm != "" and current_silotterm is not None and current_links is not None and len(current_links) > 0:
        for link in current_links:
          df.loc[len(df)] = [current_silotterm, link]
      else:
        print("Cannot process this silot term ({}) for link ({}) because they are empty or None".format(current_silotterm, current_links))
    except Exception as e:
      print("Error occured during analysis of the file {}. ".format(entry), str(e))
  
  # Remove the duplicates
  df = df.drop_duplicates()
  
  # Save the result to csv
  df.to_csv(file_path, index=None)

  # Return the dataframe
  return df

def silotterm_to_categories(silot_term, categories_df):
  # Filter the silot term and get the categories
  df = categories_df.loc[categories_df['silot_terms'] == silot_term]
  print(df)
  # Return an array with the categories
  if df.empty:
    return None
  else:
    unique_values = list(dict.fromkeys(df["category"].values))
    return unique_values

def silotterm_to_links(silot_term, links_df):
  # Filter the silot term and get the categories
  df = links_df.loc[links_df['silot_terms'] == silot_term]
  # Return an array with the links
  print(df)
  if df.empty:
    return None
  else:
    unique_values = list( dict.fromkeys(df["link"].values) )
    return unique_values



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


def process_blogpost(post, folder, entry, categories_df, links_df):
  title = post['title'] if 'title' in post else None
  # ytvideo_url = post['youtube_video'] if 'youtube_video' in post else None
  pretified = post['pretified'] if 'pretified' in post else None
  post_date = post['date'] if 'date' in post else None
  fileref = post['ref'] if 'ref' in post else None
  silot_terms = post['silot_terms'] if 'silot_terms' in post else None
  post_category = post[category_type] if category_type in post else []
  post_description = post['description'] if 'description' in post else None
  post_image = post['image'] if 'image' in post else None
  post_author = post['post_author'] if 'post_author' in post else post_author_env
  post_tags = post['tags'] if 'tags' in post else []

  print("post category: {} of type {}".format(post_category, type(post_category)))
  print("post tags: {} of type {}".format(post_tags, type(post_tags)))

  if (pretified is not True and title is not None) or force_pretify:

      if post_date is None:
          post_date = date.today() # datetime.now()
          post['date'] = post_date

      if fileref is None:
          fileref = slugify(title.lower())

      
      oldfilename = "{}/{}".format(folder, entry)
          
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
      if 'layout' not in post or post['layout'] == '':
        if default_layout is not None:
          post['layout'] = default_layout
        else:
          print("No default layout in the settings. Not setting one for this post")
      
          
      # If there was no description provided, we take the first 160 characters of the content
      if 'author' not in post or post['author'] == '':
        if default_author is not None:
          post['author'] = default_author
        else:
          print("No default author in the settings. Not setting one for this post")
      
          
      # Deduce the links
      if 'links' not in post or post['links'] == '':
        # We attempt to deduce the links of there is a silot term
        if silot_terms is not None:
          links = silotterm_to_links(silot_terms, links_df)

          if links is not None:
            post['links'] =  [ lk for lk in links ]
          else:
            print("No links ({}) found for this silot term ({})".format(links, silot_terms))
        else:
          print("The silot terms is not defined ({}). Not trying to deduce the links".format(silot_terms))
      
      # Deduce the categories
      if category_type not in post or post[category_type] == '' or post[category_type] == []:
        # We attempt to deduce the category of there is a silot term
        if silot_terms is not None:
          categories = silotterm_to_categories(silot_terms, categories_df)

          if categories is not None:
            post[category_type] = [ cat for cat in categories ]
          else:
            print("No categories ({}) found for this silot term ({})".format(categories, silot_terms))
        else:
          print("The silot terms is not defined ({}). Not trying to deduce the categories".format(silot_terms))
      
          
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

        print(filecontent)

        with open(oldfilename, 'w') as f:
            f.write(filecontent)

        print("Renaming the file to the correct file name")
        os.rename(oldfilename, newfilename)

  else:
      print("Did not process this file because Pretified = True ({}) or title was None () or force_pretify was ({})".format(
          pretified, title, force_pretify))

def pretify_files(links_df, categories_df):

  for entry in entries:
      print(entry)
      try:
          post = frontmatter.load(folder + "/" + entry)

          oldfilename = "{}/{}".format(folder, entry)
          
          process_blogpost(post, folder, entry, silot_term_to_categories_df, silot_term_to_links_df)
      except Exception as e:
          print("Error. = ", str(e))

# Generate the categories mapping file
if os.path.exists(silot_term_to_categories):
  silot_term_to_categories_df = pd.read_csv(silot_term_to_categories)
elif generate_silottermtolinks_file_if_missing == 'true':
  silot_term_to_categories_df = generate_silottermtocategories_file(silot_term_to_categories, file_generation_src_path)
else:
  print("I am not authorized to generate the file ({}) and File does not exists ({}) ".format(generate_silottermtolinks_file_if_missing, silot_term_to_categories))

# Generate the links mapping file
if os.path.exists(silot_term_to_links):
  silot_term_to_links_df = pd.read_csv(silot_term_to_links)
elif generate_silottermtocategories_file_if_missing == 'true':
  silot_term_to_links_df = generate_silottermtolinks_file(silot_term_to_links, file_generation_src_path)
else:
  print("I am not authorized to generate the file ({}) and File does not exists ({}) ".format(generate_silottermtocategories_file_if_missing, silot_term_to_links))

pretify_files(silot_term_to_links_df, silot_term_to_categories_df)
# process_blogpost(frontmatter.loads("---\ntitle: The idle post\nsilot_terms: docker compose\n---\n\n Here is the content"), folder, "an idle post", silot_term_to_categories_df, silot_term_to_links_df)
