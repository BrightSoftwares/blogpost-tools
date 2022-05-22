# Pemavor.com Autocomplete Trends
# Author: Stefan Neefischer (stefan.neefischer@gmail.com)
import concurrent.futures
from datetime import date
from datetime import datetime
from slugify import slugify
import pandas as pd
import frontmatter
import itertools
import requests
import string
import json
import time
import os

charList = " " + string.ascii_lowercase + string.digits

keyword_suggestion = os.getenv('INPUT_KEYWORD_SUGGESTION')
keyword_suggestions_generation_folder = os.getenv(
    'INPUT_KEYWORD_SUGGESTIONS_GENERATION_FOLDER')
keyword_suggestions_generation_file = keyword_suggestions_generation_folder + \
    "/" + keyword_suggestion


def suggestion_to_blogpost():
    destination_folder = os.getenv('INPUT_DRAFTS_PATH')

    # Loop through the keyword suggestions and process the ones with the blogpost_created = false
    try:
        suggestion_df = pd.read_csv(keyword_suggestions_generation_file)

        if 'blogpost_created' in suggestion_df.columns and 'Suggestion' in suggestion_df.columns:

            # Create the blogpost in the suggested folder
            for index, row in suggestion_df.iterrows():
                # print(row)
                if not row['blogpost_created']:
                    success = generate_blog_post(destination_folder,
                                                 row['Suggestion'].capitalize())

                    # Set the keyword suggestion blogpost_created to true
                    suggestion_df['blogpost_created'] = success
                else:
                    print("This suggestion have been already generated: {}".format(
                        row['Suggestion']))
            # Save the csv file
            suggestion_df.to_csv(
                keyword_suggestions_generation_file, index=False)
        else:
            print(
                "Could not find the column blogpost_created or Suggestion in the csv file")
    except:
        print("Cannot read the keyword suggestion file ",
              keyword_suggestions_generation_file)


def generate_blog_post(destination_folder, title):

    print("Generate blog post", title)
    try:
        post = frontmatter.loads("---\n---\n")
        post_date = datetime.now()
        post_date_str = post_date.strftime("%Y-%m-%d")

        print("Updating frontmatter")
        post['title'] = title
        post['date'] = date.today()

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


# If you use more than 50 seed keywords you should slow down your requests - otherwise google is blocking the script
# If you have thousands of seed keywords use e.g. WAIT_TIME = 1 and MAX_WORKERS = 5
# WAIT_TIME = 0.2
# MAX_WORKERS = 20
# set the autocomplete language
# LANGUAGE = "en"
# set the autocomplete country code - DE, US, TR, GR, etc..
# COUNTRY = "US"
# Keyword_seed csv file name. One column csv file.
# csv_fileName="keyword_seeds.csv"

CSV_FILE_NAME = os.getenv('INPUT_KEYWORD_SEED')
suggestion_to_blogpost()
# The result will save in keyword_suggestions.csv csv file

# Output the generated file
print(keyword_suggestions_generation_file)