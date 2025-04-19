# Pemavor.com Autocomplete Trends
# Author: Stefan Neefischer (stefan.neefischer@gmail.com)
import concurrent.futures
from datetime import date
from datetime import datetime
# from slugify import slugify
import pandas as pd
import frontmatter
import itertools
import requests
import string
import json
import time
import os
import re

charList = " " + string.ascii_lowercase + string.digits

def slugify(text):
    # text = unidecode.unidecode(text).lower()
    # return re.sub(r'[\W_]+', '-', text)
    return re.sub(r'\W+', '-', text).strip('-').lower()

def get_yt_video_id_from_url(url):
    """Returns Video_ID extracting from the given url of Youtube

    Examples of URLs:
      Valid:
        'http://youtu.be/_lOT2p_FCvA',
        'www.youtube.com/watch?v=_lOT2p_FCvA&feature=feedu',
        'http://www.youtube.com/embed/_lOT2p_FCvA',
        'http://www.youtube.com/v/_lOT2p_FCvA?version=3&amp;hl=en_US',
        'https://www.youtube.com/watch?v=rTHlyTphWP0&index=6&list=PLjeDyYvG6-40qawYNR4juzvSOg-ezZ2a6',
        'youtube.com/watch?v=_lOT2p_FCvA',

      Invalid:
        'youtu.be/watch?v=_lOT2p_FCvA',
    """

    if url.startswith(('youtu', 'www')):
        url = 'http://' + url

    query = urlparse(url)

    if 'youtube' in query.hostname:
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        elif query.path.startswith(('/embed/', '/v/')):
            return query.path.split('/')[2]
    elif 'youtu.be' in query.hostname:
        return query.path[1:]
    else:
        raise ValueError


def generate_blog_post(destination_folder, data, language):

    if data['title'] == "":
        title = slugify(data['url'])
    else:
        title = data['title']

    print("Generate blog post", title)
    try:
        post = frontmatter.loads("---\n---\n")
        post_date = datetime.now()
        post_date_str = post_date.strftime("%Y-%m-%d")

        print("Updating frontmatter")
        # TODO - Check whether this blogpost_title is mandatory in the downstream processes - will subsequent run fail if it is not there?
        # if not pd.isna(data['blogpost_title']) and data['blogpost_title'] != '':
        #   post['title'] = data['blogpost_title']
        # else:
        #   post['title'] = title
        post['title'] = title

        post['date'] = date.today()
        post['lang'] = language
        post['keyword_suggestion'] = title.lower()

        # # If we have the category, we add it to the blogpost
        # if not pd.isna(data['category']) and data['category'] != '':
        #   post['category'] = [ data['category'] ]

        # # If we have the cornerstone is provided, we fill it in the blogpost
        # if not pd.isna(data['cornerstone']) and data['cornerstone'] != '':
        #   post['cornerstone'] = data['cornerstone']

        # # If we have the silot_terms is provided, we fill it in the blogpost
        # if not pd.isna(data['silot_terms']) and data['silot_terms'] != '':
        #   post['silot_terms'] = data['silot_terms']

        print("Saving youtube_video and youtube_video_id tags")
        post['youtube_video'] = data['url']
        video_found_id = get_yt_video_id_from_url(data['url'])
        post['youtube_video_id'] = video_found_id

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



def expand_yturls_to_blogpost():

    # CSV_FILE_NAME = os.getenv('INPUT_URLS_FILE')

    urls_file = os.getenv('INPUT_URLS_FILE')
    # expanded_blogposts_generation_folder = os.getenv(
    #     'INPUT_EXPANDED_BLOGPOSTS_GENERATION_FOLDER')
    # keyword_suggestions_generation_file = expanded_blogposts_generation_folder + \
    #     "/" + urls_file

    # Output the generated file
    # print(keyword_suggestions_generation_file)

    destination_folder = os.getenv('INPUT_EXPANDED_BLOGPOSTS_GENERATION_FOLDER')
    batch_size = int(os.getenv('INPUT_BATCH_SIZE', '10'))
    language = os.getenv('INPUT_LANGUAGE', 'en')
    dry_run = os.getenv("INPUT_DRY_RUN", 'true')
    # keyword_min_volume_eligible = int(os.getenv('INPUT_KEYWORD_MIN_VOLUME_ELIGIBLE', '0'))
    # keyword_max_volume_eligible = int(os.getenv('INPUT_KEYWORD_MAX_VOLUME_ELIGIBLE', '5000000'))

    # Loop through the keyword suggestions and process the ones with the blogpost_created = false
    try:
        print("0. Loading csv file", urls_file)
        urlsfile_df_orig = pd.read_csv(urls_file)
        print("1. urlsfile_df_orig", urlsfile_df_orig)

        #print("df dtypes", urlsfile_df_orig.dtypes)
        #urlsfile_df_orig['Avg. monthly searches'].astype(int)
        #urlsfile_df_orig['blogpost_created'].astype(bool)
        #print("df dtypes (after explicit type conversion)", urlsfile_df_orig.dtypes)
        #suggestion_df = urlsfile_df_orig.loc[urlsfile_df_orig['Avg. monthly searches'] > 0]

        # Sort by silot_terms > blogpost_title > Suggestion
        urlsfile_df_orig.sort_values(by=['status', 'language', 'url'], ascending=[False, False, False], inplace=True)
        print("2. urlsfile_df_orig after sort", urlsfile_df_orig)

        # Add new variables: min month searches and max monthly searches
        # Keep only the items between min, max avg monthly searches and first batch_size
        blogpost_candidates_df = urlsfile_df_orig[ urlsfile_df_orig['url'].notnull() & (urlsfile_df_orig['status'].isnull()) ]
        print("3. blogpost_candidates_df size: ", blogpost_candidates_df.shape)

        # Keep first batch size
        blogpost_candidates_batchsized_df = blogpost_candidates_df.head(batch_size)
        print("4. blogpost_candidates_batchsized_df size: ", blogpost_candidates_batchsized_df.shape)
        print(blogpost_candidates_batchsized_df)

        # We make sure that there are url and language coulmns in this df
        if 'url' in blogpost_candidates_batchsized_df.columns and 'language' in blogpost_candidates_batchsized_df.columns:
            
            # Create the blogpost in the suggested folder
            nb_rows_processed = 0
            for index, row in blogpost_candidates_batchsized_df.iterrows():
                print("5. Processing row {} with language = {}".format(row['url'], row['language']))
                
                if row['status'] == 'done':
                    print("6. This expansion have been already generated: {}".format(row['url']))

                else:
                    #if not pd.isna(row['blogpost_created']) and row['blogpost_created'] is not True:
                    success = generate_blog_post(destination_folder, row, language)
                    print("7. Result of blogpost generation: ", success)

                    # Set the keyword suggestion blogpost_created to true
                    #suggestion_df.at[index,'blogpost_created'] = success #row['blogpost_created'] = success
                    mask = (urlsfile_df_orig['url'] == row['url'])
                    #print("Mask result ", mask)
                    urlsfile_df_orig.loc[ mask, 'status'] = success
                    
                    # Increment the nb processed items if the blog post has been created successfully
                    if success:
                        nb_rows_processed = nb_rows_processed + 1
                        print("8. Processed {} items.".format(nb_rows_processed))
                #else:
                    
                    
                if nb_rows_processed >= batch_size:
                    break
                    
                  
            # Save the csv file
            if dry_run == 'true':
                print("In dry run mode, not scraping!")
            else:
                print('No dry run. updaing urls file')
                urlsfile_df_orig.to_csv(urls_file, index=False)
            
        else:
            print(
                "Could not find the column url or language in the csv file")
            
        print("9. urlsfile_df_orig after processing", urlsfile_df_orig)
    except Exception as e:
        #print("Cannot read the keyword suggestion file ", keyword_suggestions_generation_file)
        print("An error occured. ", str(e))


# Running the main function
expand_yturls_to_blogpost()


