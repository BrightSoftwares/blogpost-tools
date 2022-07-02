import pandas as pd
import os
import frontmatter
import datetime
import glob
from datetime import timedelta

def reschedule_files(posts_df, src_folder_path, dest_folder_path, dry_run):

  # Rename the files date based on the order in the dataframe
  if dry_run == "false":
    for index, post_df in posts_df.iterrows():
      print("Saving the content of the file", post_df['filename'])
      post = frontmatter.load(src_folder_path + "/" + post_df['filename'])

      post[post_df['date_source']] = post_df['new_date'].date()
      post['pretified'] = False

      filecontent = frontmatter.dumps(post)

      with open(dest_folder_path + "/" + os.path.basename(post_df['filename']), 'w') as f:
        f.write(filecontent)
  else:
    print("In dry run mode, skipping file write ...")

def auto_schedule_posts(src_folder_path, dest_folder_path, days_mask, nb_days_ahead, dry_run):

  print("Auto scheduling posts from src folder ({}), to dest folder ({}) and days mask ({}) and dry run ({})".format(src_folder_path, dest_folder_path, days_mask, dry_run))
  

  # Get all the post from that folder

  posts = []
  entries = glob.glob(src_folder_path + "/**/*.md", recursive=True) #os.listdir(src_folder_path)
  for entry in entries:

      post_score = 0
      try:
        entry = os.path.basename(entry)
        print("Processing entry {}, dry run {} ({})".format(entry, dry_run, type(dry_run)))
        post = frontmatter.load(src_folder_path + "/" + entry)
        post_date = None
        date_source = 'date'
        if 'date' in post:
          post_date = post['date']
          date_source = 'date'
        if 'post_date' in post: # wordpress version
          post_date = post['post_date']
          date_source = 'post_date'
        else:
          post_date = None
          
        post_length = len(post.content)

        # Compute the order of the posts based on the content and frontmatter
        post_score += 40 if post_date is not None else 0
        post_score += 10 if post_length > 500 else 0

        posts.append([entry, post_date, post_length, post_score, date_source])
      
      except Exception as e:
        print("Error. = ", str(e))

  
  # Put the posts into a dataframe
  #posts = ["post1", "post2", "post3", "post4", "post5", "post6", "post7", "post8", "post9", "post10"]
  posts_df = pd.DataFrame(posts, columns=["filename", "current_date", "content_length", "score", "date_source"])

  # Sort the posts by the order computed previously
  posts_df.sort_values(by=['current_date', 'score'], inplace=True)
  

  # Generate the date range and associate them with the previous dataframe
  print("Generating the new dates wit {} days ahead".format(nb_days_ahead))
  tomorrow = datetime.date.today() + datetime.timedelta(days=nb_days_ahead)
  start_date = tomorrow.strftime("%m/%d/%Y")
  print("Start date: ", start_date)
  dates_df = pd.bdate_range(start=start_date, periods=posts_df.shape[0], freq='C', weekmask=days_mask)
  assigned_posts_df = posts_df.assign(new_date=dates_df)
  print(assigned_posts_df)
  #print(posts_df)

  # Save new date in posts
  reschedule_files(assigned_posts_df, src_folder_path, dest_folder_path, dry_run)

  # End


src_folder_path = os.getenv('INPUT_SRC_FOLDER')
dest_folder_path = os.getenv('INPUT_DEST_FOLDER')
days_mask = os.getenv('INPUT_DAYS_MASK')
dry_run = os.getenv('INPUT_DRY_RUN')
nb_days_ahead = int(os.getenv('INPUT_NB_DAYS_AHEAD', 1))

auto_schedule_posts(src_folder_path, dest_folder_path, days_mask, nb_days_ahead, dry_run)
