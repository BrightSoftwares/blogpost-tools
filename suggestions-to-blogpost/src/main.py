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
    batch_size = int(os.getenv('INPUT_BATCH_SIZE'))
    language = os.getenv('INPUT_LANGUAGE')

    # Loop through the keyword suggestions and process the ones with the blogpost_created = false
    try:
        print("Loading csv file", keyword_suggestions_generation_file)
        suggestion_df_orig = pd.read_csv(keyword_suggestions_generation_file)
        #suggestion_df = suggestion_df_orig.loc[suggestion_df_orig['Avg. monthly searches'] > 0]
        
        # We make sure that there are blogpost_created and Suggestion coulmns in this df
        if 'blogpost_created' in suggestion_df_orig.columns and 'Suggestion' in suggestion_df_orig.columns:
            
            # We process only the entries with silot_terms column filled in
            suggestion_df = suggestion_df_orig[ (pd.notnull(suggestion_df_orig['silot_terms'])) &  (suggestion_df_orig['silot_terms'] != "") ]
            print("Shape suggestion_df_orig", suggestion_df_orig.shape)
            print("Shape suggestion_df", suggestion_df.shape)
            #suggestion_df = suggestion_df.head(batch_size) # Process only the first item of the batch_size amount of blog posts

            # Create the blogpost in the suggested folder
            nb_rows_processed = 0
            for index, row in suggestion_df.iterrows():
                #print("Processing row:", row)
                print("Processing row {} with silot_terms = {}".format(row['Suggestion'], row['silot_terms']))
                #print("blogpost_created is NA:", pd.isna(row['blogpost_created']))
                #print("blogpost_created is False/True?:", not row['blogpost_created'])
                
                if not pd.isna(row['blogpost_created']) and row['blogpost_created'] is not True:
                    success = generate_blog_post(destination_folder, row, language)
                    print("Result of blogpost generation: ", success)

                    # Set the keyword suggestion blogpost_created to true
                    suggestion_df.at[index,'blogpost_created'] = success #row['blogpost_created'] = success
                    
                    # Increment the nb processed items if the blog post has been created successfully
                    if success:
                        nb_rows_processed = nb_rows_processed + 1
                        print("Processed {} items.".format(nb_rows_processed))
                else:
                    print("This suggestion have been already generated: {}".format(
                        row['Suggestion']))
                    
                if nb_rows_processed >= batch_size:
                    break
                    
            # Save the csv file
            suggestion_df.to_csv(
                keyword_suggestions_generation_file, index=False)
        else:
            print(
                "Could not find the column blogpost_created or Suggestion in the csv file")
    except Exception as e:
        #print("Cannot read the keyword suggestion file ", keyword_suggestions_generation_file)
        print("An error occured. ", str(e))


def generate_blog_post(destination_folder, data, language):

    title = data['Suggestion']
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
        post['lang'] = language
        post['keyword_suggestion'] = title.lower()

        # If we have the category, we add it to the blogpost
        if not pd.isna(data['category']) and data['category'] != '':
          post['category'] = [ data['category'] ]

        # If we have the blogpost_title is provided, we fill it in the blogpost
        #if data['blogpost_title'] is not None and data['blogpost_title'] != '':
        #  post['blogpost_title'] = title if pd.isna(data['blogpost_title']) else data['blogpost_title']

        # If we have the cornerstone is provided, we fill it in the blogpost
        if not pd.isna(data['cornerstone']) and data['cornerstone'] != '':
          post['cornerstone'] = data['cornerstone']

        # If we have the silot_terms is provided, we fill it in the blogpost
        if not pd.isna(data['silot_terms']) and data['silot_terms'] != '':
          post['silot_terms'] = data['silot_terms']

        # If we have the  is provided, we fill it in the blogpost
        #if data['']:
        #  post[''] = data['']

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
