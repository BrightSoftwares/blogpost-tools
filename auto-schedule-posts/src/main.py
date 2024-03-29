import pandas as pd
import os
import frontmatter
import datetime
import glob
from datetime import timedelta

def reschedule_files(posts_df, src_folder_path, dest_folder_path, dry_run):

  #src_folder_path = src_folder_path[-1] if src_folder_path.endswith("/") else src_folder_path
  #dest_folder_path = dest_folder_path[-1] if dest_folder_path.endswith("/") else dest_folder_path

  # Rename the files date based on the order in the dataframe
  if dry_run == "false":
    for index, post_df in posts_df.iterrows():
      print("Saving the content of the file", post_df['filename'])
      post = frontmatter.load(src_folder_path + "/" + post_df['filename'])

      post['post_date'] = post_df['new_date'].date()
      post['date'] = post_df['new_date'].date()
      post['pretified'] = False

      filecontent = frontmatter.dumps(post)

      with open(dest_folder_path + "/" + os.path.basename(post_df['filename']), 'w') as f:
        f.write(filecontent)
  else:
    print("In dry run mode, skipping file write ...")


def get_startdate(extract_most_recent_date_from, nb_days_ahead=0):
  """
  Get the most recent date from the folder containing the post if provided.
  Else it computes the most recent date from the nb of days ahead provided
  """
  start_date = datetime.date.today() # datetime.datetime.now()
  
  # If the user provided a folder to get the max date, use it.
  if extract_most_recent_date_from is not None:
    posts_dates = [datetime.date.today()] # [datetime.datetime.now()] # Add now initially so that at lease we get the current date a most recent
    entries = glob.glob(extract_most_recent_date_from + "/**/*.md", recursive=True)
    for entry in entries:
        try:
          entry = os.path.basename(entry)
          print("Collecting date for the entry {}".format(entry))
          post = frontmatter.load(extract_most_recent_date_from + "/" + entry)
          if 'date' in post:
            post_date = post['date']
            posts_dates.append(post_date)
        except Exception as e:
          print("Error while collecting the date for the post ", entry)
    
    print("Dates collected: ", posts_dates)
    start_date = max(posts_dates)
    print("Most recent date = ", start_date)
    return start_date
  else:
    # Else compute with the days ahead
    # Generate the date range and associate them with the previous dataframe
    print("Generating the new dates with {} days ahead".format(nb_days_ahead))
    start_date = datetime.date.today() + datetime.timedelta(days=nb_days_ahead)
  
  start_date_str = start_date.strftime("%m/%d/%Y")
  return start_date_str

def auto_schedule_posts(src_folder_path, dest_folder_path, days_mask, start_date, dry_run):

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
  

  # # Generate the date range and associate them with the previous dataframe
  # print("Generating the new dates wit {} days ahead".format(nb_days_ahead))
  # tomorrow = datetime.date.today() + datetime.timedelta(days=nb_days_ahead)
  # start_date = tomorrow.strftime("%m/%d/%Y")
  print("Start date: ", start_date)
  dates_df = pd.bdate_range(start=start_date, periods=posts_df.shape[0], freq='C', weekmask=days_mask)
  assigned_posts_df = posts_df.assign(new_date=dates_df)
  print(assigned_posts_df)
  #print(posts_df)

  # Save new date in posts
  reschedule_files(assigned_posts_df, src_folder_path, dest_folder_path, dry_run)

  # End


src_folder_path = os.getenv('INPUT_SRC_FOLDER')
src_folder_path = src_folder_path[:-1] if src_folder_path.endswith("/") else src_folder_path
print("Source folder = ", src_folder_path)

dest_folder_path = os.getenv('INPUT_DEST_FOLDER')
dest_folder_path = dest_folder_path[:-1] if dest_folder_path.endswith("/") else dest_folder_path
print("Destination folder = ", dest_folder_path)

days_mask = os.getenv('INPUT_DAYS_MASK')
dry_run = os.getenv('INPUT_DRY_RUN')
nb_days_ahead = int(os.getenv('INPUT_NB_DAYS_AHEAD', 1))

#use this folder to extract the most recent date so I can build on top of it
extract_most_recent_date_from = os.getenv('INPUT_MOST_RECENT_DATE_FOLDER', None)
if extract_most_recent_date_from is not None:
  if extract_most_recent_date_from.endswith("/"):
    extract_most_recent_date_from = extract_most_recent_date_from[:-1]
print("Folder to extract the most recent date from: ", extract_most_recent_date_from)


start_date = get_startdate(extract_most_recent_date_from, nb_days_ahead)

auto_schedule_posts(src_folder_path, dest_folder_path, days_mask, start_date, dry_run)
