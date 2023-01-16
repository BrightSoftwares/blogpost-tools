import concurrent.futures
from datetime import date
from datetime import datetime, timedelta
from slugify import slugify
from io import BytesIO
import pandas as pd
import frontmatter
import feedparser
import itertools
import requests
import string
import json
import time
import os

charList = " " + string.ascii_lowercase + string.digits

keyword_suggestion = os.getenv('INPUT_KEYWORD_SUGGESTION_FILE')
feeds_file=os.getenv('INPUT_FEEDS_FILE')
feed_blogpost_url_used=os.getenv('INPUT_FEED_BLOGPOST_URL_USED')
keyword_suggestions_generation_folder = os.getenv('INPUT_KEYWORD_SUGGESTIONS_GENERATION_FOLDER')
CSV_FILE_NAME = os.getenv('INPUT_KEYWORD_SEED')
destination_folder = os.getenv('INPUT_DRAFTS_PATH')
batch_size = int(os.getenv('INPUT_BATCH_SIZE'))
language = os.getenv('INPUT_LANGUAGE')
keyword_min_volume_eligible = int(os.getenv('INPUT_KEYWORD_MIN_VOLUME_ELIGIBLE', '0'))
keyword_max_volume_eligible = int(os.getenv('INPUT_KEYWORD_MAX_VOLUME_ELIGIBLE', '5000000'))


# Try to load the used urls. If not found, create an empty one
def get_feedblogposturlused_df(file_url):
  try:
    return pd.read_csv(file_url)
  except:
    return pd.DataFrame(columns=['Suggestion', 'silot_terms', 'blogpost_title', 'blogpost_link', 'category'])


def extract_blogposts(feed_url, keywords, silot_terms, category, since, feed_blogpost_url_used_df):
  # Load the rss feed and get posts that has the  keywords
  try:
    print("extract_blogposts > url = {}, silot_terms = {}, keywords = {}, since = {}".format(feed_url, silot_terms, keywords, since))
    
    # Do request using requests library and timeout
    try:
        resp = requests.get(feed_url, timeout=20.0)
    except requests.ReadTimeout:
        logger.warn("Timeout when reading RSS %s", feed_url)
        return feed_blogpost_url_used_df

    # Put it to memory stream object universal feedparser
    content = BytesIO(resp.content)

    # Parse content
    #feed = feedparser.parse(feed_url) # Old implementation, is subject to connection hang
    feed = feedparser.parse(content)

    #blogposts = []
    for entry in feed.entries:
      blogpost_title = entry['title']
      blogpost_summary = entry['summary']
      blogpost_link = entry['link']
      blogpost_new_title = ""

      print("Looking for keywords {} in title {} and summary".format(silot_terms, blogpost_title))

      keyword_array = silot_terms.split(" ")
      all_keywords_found = True

      for keyword_item in keyword_array:
        all_keywords_found = (keyword_item in blogpost_title) or (keyword_item in blogpost_summary)
        if not all_keywords_found:
          print("keyword '{}' not found neither in title of summary. breaking from loop".format(keyword_item))
          break

      if all_keywords_found:
        if blogpost_link in feed_blogpost_url_used_df['blogpost_link'].values:
          print("Link {} is already in the dataframe. Skipping...".format(blogpost_link))
        else:
          print("New blogpost inspiration found. Adding ...")
          feed_blogpost_url_used_df.loc[len(feed_blogpost_url_used_df)] = [keywords, silot_terms, blogpost_title, blogpost_link, category]
      else:
        print("Some keywords were not found. Skipping ...")
          
  except Exception as e:
      print("extract_blogposts > An error occured. ", str(e))
      #return False

  print(feed_blogpost_url_used_df)
  return feed_blogpost_url_used_df


def process_rss_feeds(feeds_csv, suggestions_file, feedblogposturlused_df):
  print("Loading the feeds from csv file")
  rss_feed_df = pd.read_csv(feeds_csv)
  suggestions_file_df = pd.read_csv(suggestions_file)
  suggestions_file_df.drop_duplicates(subset=['silot_terms'], inplace=True)
  suggestions_file_df.dropna(subset=['silot_terms'], inplace=True)

  today = date.today()
  since = today - timedelta(days=7)

  for index, feed_url in rss_feed_df.iterrows():
    print("Processing feed {}".format(feed_url))
    for index_keyword, keywords in suggestions_file_df.iterrows():
      # Extract blog posts
      feedblogposturlused_df = extract_blogposts(feed_url['feed_url'], keywords['Suggestion'], keywords['silot_terms'], keywords['category'], since, feedblogposturlused_df)
      

  print("Generate the blog posts")
  for index_post,row_bpost in feedblogposturlused_df.iterrows():
    generate_blog_post(destination_folder, row_bpost)


def generate_blog_post(destination_folder, data):

    # keywords, blogpost_title, blogpost_link, category
    keywords = data['Suggestion']
    silot_terms = data['silot_terms']
    link = data['blogpost_link']
    title = data['blogpost_title']
    category = data['category']

    print("Generate blog post", title)
    try:
        post = frontmatter.loads("---\n---\n")
        post_date = datetime.now()
        post_date_str = post_date.strftime("%Y-%m-%d")

        print("Updating frontmatter")
        if not pd.isna(data['blogpost_title']) and data['blogpost_title'] != '':
          post['title'] = data['blogpost_title']
        else:
          post['title'] = title

        post['date'] = date.today()
        post['keyword_suggestion'] = keywords
        post['silot_terms'] = silot_terms
        post['post_inspiration'] = link

        # If we have the category, we add it to the blogpost
        #if not pd.isna(data['category']) and data['category'] != '':
        post['category'] = [ category ]

        # If we have the silot_terms is provided, we fill it in the blogpost
        if not pd.isna(data['silot_terms']) and data['silot_terms'] != '':
          post['silot_terms'] = data['silot_terms']

        newfilename = "{}/{}-{}.md".format(destination_folder, post_date_str,
                                           slugify(title.lower()))

        print("Saving the content of the file")
        filecontent = frontmatter.dumps(post)
        with open(newfilename, 'w') as f:
            f.write(filecontent)

        return True
    except Exception as e:
        print("An error occured. ", str(e))
        return False


feedblogposturlused_df = get_feedblogposturlused_df(feed_blogpost_url_used)

process_rss_feeds(feeds_file, keyword_suggestion, feedblogposturlused_df)
feedblogposturlused_df.to_csv(feed_blogpost_url_used, index=False)
