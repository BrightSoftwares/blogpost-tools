# Pemavor.com Autocomplete Trends
# Author: Stefan Neefischer (stefan.neefischer@gmail.com)
import concurrent.futures
from datetime import date
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
import itertools
import requests
import string
import json
import time
import os
import fnmatch

charList = " " + string.ascii_lowercase + string.digits
keyword_suggestions_generation_folder = os.getenv(
    'INPUT_KEYWORD_SUGGESTIONS_GENERATION_FOLDER')
keyword_suggestions_generation_file = keyword_suggestions_generation_folder + \
    "/" + "keyword_suggestions.csv"
keyword_min_volume_eligible = int(os.getenv('INPUT_KEYWORD_MIN_VOLUME_ELIGIBLE', '0'))
keyword_max_volume_eligible = int(os.getenv('INPUT_KEYWORD_MAX_VOLUME_ELIGIBLE', '5000000'))
keyword_suggestions_blogpost_file = keyword_suggestions_generation_folder + "/" + os.getenv('INPUT_KEYWORD_SUGGESTIONS_BLOGPOST_FILE')


def makeGoogleRequest(query):
    # If you make requests too quickly, you may be blocked by google
    time.sleep(WAIT_TIME)
    URL = "http://suggestqueries.google.com/complete/search"
    PARAMS = {"client": "opera",
              "hl": LANGUAGE,
              "q": query,
              "gl": COUNTRY}
    response = requests.get(URL, params=PARAMS)
    if response.status_code == 200:
        try:
            suggestedSearches = json.loads(response.content.decode('utf-8'))[1]
        except:
            suggestedSearches = json.loads(
                response.content.decode('latin-1'))[1]
        return suggestedSearches
    else:
        return "ERR"


def getGoogleSuggests(keyword):
    # err_count1 = 0
    queryList = [keyword + " " + char for char in charList]
    suggestions = []
    for query in queryList:
        suggestion = makeGoogleRequest(query)
        if suggestion != 'ERR':
            suggestions.append(suggestion)

    # Remove empty suggestions
    suggestions = set(itertools.chain(*suggestions))
    if "" in suggestions:
        suggestions.remove("")

    return suggestions


def is_valid_suggestion(suggestion):
    # A suggestion must not contain any of these characters : \!@%,*{}<>;
    invalid_chars = r"\!@%,*{}<>;"
    is_char_safe = not any(elem in suggestion for elem in invalid_chars)
    is_length_safe = len(suggestion.split(" ")) < 10
    is_max_80_chars = len(suggestion) < 80
    #print("Suggestion {} is charsafe? {} and length safe? {}".format(suggestion, is_char_safe, is_length_safe))
    return is_char_safe and is_length_safe and is_max_80_chars
    
                     


def autocomplete(csv_fileName):
    dateTimeObj = datetime.now().date()
    # read your csv file that contain keywords that you want to send to google autocomplete
    df = pd.read_csv(csv_fileName)
    keywords = df.iloc[:, 0].tolist()
    resultList = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futuresGoogle = {executor.submit(
            getGoogleSuggests, keyword): keyword for keyword in keywords}

        for future in concurrent.futures.as_completed(futuresGoogle):
            key = futuresGoogle[future]
            for suggestion in future.result():
                if is_valid_suggestion(suggestion):
                    resultList.append([key, suggestion])

    # Convert the results to a dataframe
    suggestion_new = pd.DataFrame(
        resultList, columns=['Keyword', 'Suggestion'])
    del resultList

    # if we have old results read them
    try:
        suggestion_df = pd.read_csv(keyword_suggestions_generation_file)

    except:
        suggestion_df = pd.DataFrame(
            columns=['first_seen', 'last_seen', 'Keyword', 'Suggestion', 'category', 'blogpost_title', 'silot_terms', 'cornerstone', 'semantic_cluster'])

    suggestionCommon_list = []
    suggestionNew_list = []
    for keyword in suggestion_new["Keyword"].unique():
        new_df = suggestion_new[suggestion_new["Keyword"] == keyword]
        old_df = suggestion_df[suggestion_df["Keyword"] == keyword]
        newSuggestion = set(new_df["Suggestion"].to_list())
        oldSuggestion = set(old_df["Suggestion"].to_list())
        commonSuggestion = list(newSuggestion & oldSuggestion)
        new_Suggestion = list(newSuggestion - oldSuggestion)

        for suggest in commonSuggestion:
            suggestionCommon_list.append([dateTimeObj, keyword, suggest])
        for suggest in new_Suggestion:
            suggestionNew_list.append(
                [dateTimeObj, dateTimeObj, keyword, suggest])

    # new keywords
    newSuggestion_df = pd.DataFrame(suggestionNew_list, columns=[
                                    'first_seen', 'last_seen', 'Keyword', 'Suggestion'])
    # shared keywords with date update
    commonSuggestion_df = pd.DataFrame(suggestionCommon_list, columns=[
                                       'last_seen', 'Keyword', 'Suggestion'])
    merge = pd.merge(suggestion_df, commonSuggestion_df, left_on=[
                     "Suggestion"], right_on=["Suggestion"], how='left')
    merge = merge.rename(
        columns={'last_seen_y': 'last_seen', "Keyword_x": "Keyword"})
    merge["last_seen"].fillna(merge["last_seen_x"], inplace=True)
    del merge["last_seen_x"]
    del merge["Keyword_y"]

    # merge old results with new results
    frames = [merge, newSuggestion_df]
    keywords_df = pd.concat(frames, ignore_index=True, sort=False)
    # Save dataframe as a CSV file
    keywords_df['first_seen'] = pd.to_datetime(keywords_df['first_seen'])
    keywords_df = keywords_df.sort_values(
        by=['first_seen', 'Keyword'], ascending=[False, False])
    keywords_df['first_seen'] = pd.to_datetime(keywords_df['first_seen'])
    keywords_df['last_seen'] = pd.to_datetime(keywords_df['last_seen'])
    keywords_df['is_new'] = (keywords_df['first_seen']
                             == keywords_df['last_seen'])
    
    # Add required columns if not exist
    keywords_df['blogpost_created'] = keywords_df['blogpost_created'] if 'blogpost_created' in keywords_df.columns else False
    keywords_df['category'] = keywords_df['category'] if 'category' in keywords_df.columns else np.nan
    keywords_df['blogpost_title'] = keywords_df['blogpost_title'] if 'blogpost_title' in keywords_df.columns else np.nan
    keywords_df['silot_terms'] = keywords_df['silot_terms'] if 'silot_terms' in keywords_df.columns else np.nan
    keywords_df['cornerstone'] = keywords_df['cornerstone'] if 'cornerstone' in keywords_df.columns else np.nan
    keywords_df['semantic_cluster'] = keywords_df['semantic_cluster'] if 'semantic_cluster' in keywords_df.columns else np.nan
    
    # Keep the interesting columns
    keywords_df = keywords_df[['first_seen', 'last_seen',
                               'Keyword', 'Suggestion', 'is_new', 'blogpost_created', 'category', 'blogpost_title', 'silot_terms', 'cornerstone', 'semantic_cluster']]
    
    # Remove invalid suggestions
    keywords_df = keywords_df[ keywords_df["Suggestion"].apply(lambda x: len(x.split(" ")) <= 10) | keywords_df["Suggestion"].apply(lambda x: not any(elem in x for elem in r"\!@%,*{}<>;")) ]
    
    # Remove duplicates
    keywords_df.drop_duplicates(inplace=True)
    
    # Saving the whole result into a csv file
    print("autocomplete > keywords_df size before saving to csv =", keywords_df.shape)
    keywords_df.to_csv(keyword_suggestions_generation_file, index=False)

    
def compute_clusters():
    
  df = pd.read_csv(keyword_suggestions_generation_file)

  documents = df['Suggestion'].values.astype("U")

  stp_wrd = 'french' if LANGUAGE == 'fr' else 'english'
  vectorizer = TfidfVectorizer(stop_words=stp_wrd)
  features = vectorizer.fit_transform(documents)

  arbitrary_quotient = 0.0321
  nbrows = features.shape[0]
  k = int(nbrows * arbitrary_quotient)
  nb_max_iterations=300
  print("features df size =", features.shape)
  print("Clustering {} rows into {} clusters in {} iterations".format(nbrows, k, nb_max_iterations))


  model = KMeans(n_clusters=k, init='k-means++', max_iter=nb_max_iterations, n_init=1)
  model.fit(features)

  print("Cluster labels shape =", model.labels_.shape)

  df['cluster'] = model.labels_

  #df.head()
  print("compute_clusters > features df size before saving to csv =", features.shape)
  df.to_csv(keyword_suggestions_generation_file, index=False)

def add_volumes_data(folder):
    print("Pandas version:", pd.__version__)
    # Load the volume data from local csv
    entries = os.listdir(folder)
    final_keywords_df = None
    for entry in entries:
        if fnmatch.fnmatch(entry, 'Keyword Stats *.csv'):
            print(entry)
            # print(entry)
            try:
                tmp_final_keywords_df = pd.read_csv(
                    keyword_suggestions_generation_folder + "/" + entry, delimiter='\t', encoding="ISO-8859-1")
                final_keywords_df = tmp_final_keywords_df if final_keywords_df is None else pd.concat((final_keywords_df,
                                                                                                      tmp_final_keywords_df))

            except Exception as e:
                print("An error occured. Error = ", str(e))
        else:
            print("The file does not match the keyword planner pattern", entry)

    # Add the volumes data
    suggested_kw_df = pd.read_csv(keyword_suggestions_generation_file)
    merged_df = suggested_kw_df.merge(
        final_keywords_df, how='left', left_on='Suggestion', right_on='Keyword')
    
    merged_df = merged_df.sort_values(by=['Competition', 'Avg. monthly searches', 'Competition (indexed value)'], ascending=[True, False, True])
    
    # Replace the N/As in blogpost_created column with False
    merged_df['blogpost_created'].fillna(value={'blogpost_created':False})
    
    merged_df.to_csv(keyword_suggestions_generation_folder + "/keyword_suggestions_merged.csv", index=False)
    
    merged_df_perbidcost = merged_df.sort_values(by=['Competition', 'Avg. monthly searches', 'Top of page bid (low range)'], ascending=[True, False, False])
    merged_df_perbidcost.to_csv(keyword_suggestions_generation_folder + "/keyword_suggestions_merged_per_bid_cost_low.csv", index=False)
    
    # Generate a file with keywords that meet the requirements for a blogpost    
    print("Keeping only the keywords with volume above {} and below {}".format(keyword_min_volume_eligible, keyword_max_volume_eligible))
    blogpost_candidates_df = merged_df[ merged_df['Avg. monthly searches'] >= keyword_min_volume_eligible ]
    print("0. blogpost_candidates_df size: ", blogpost_candidates_df.shape)

    blogpost_candidates_df = merged_df[ merged_df['Avg. monthly searches'] <= keyword_max_volume_eligible ]
    print("1. blogpost_candidates_df size: ", blogpost_candidates_df.shape)
    
    blogpost_candidates_df = blogpost_candidates_df[ blogpost_candidates_df.Competition == 'Faible' | blogpost_candidates_df.Competition == 'Low' ]
    print("2. blogpost_candidates_df size: ", blogpost_candidates_df.shape)
    
    blogpost_candidates_df = blogpost_candidates_df[ blogpost_candidates_df.Competition.notnull() ]
    print("3. blogpost_candidates_df size: ", blogpost_candidates_df.shape)
    
    print("Load previously processed blogpost created data")
    print(" 1. Merge data from csv with this one")
    print(" Checking if file {} exists".format(keyword_suggestions_blogpost_file))
    if os.path.exists(keyword_suggestions_blogpost_file):
        print("File exists:", keyword_suggestions_blogpost_file)
        exiting_blogpost_candidates_df = pd.read_csv(keyword_suggestions_blogpost_file)
        print("exiting_blogpost_candidates_df Size =", exiting_blogpost_candidates_df.shape)
        
        blogpost_candidates_df = pd.concat([blogpost_candidates_df, exiting_blogpost_candidates_df], ignore_index=True, sort=False)
        print("blogpost_candidates_df Size =", blogpost_candidates_df.shape)
        
        print("Sort by blogpost created to be able to remove duplicates")
        blogpost_candidates_df = blogpost_candidates_df.sort_values(by=['blogpost_created'], ascending=[True])
        print("blogpost_candidates_df Size =", blogpost_candidates_df.shape)
        
        print(" 2. Remove duplicates")
        blogpost_candidates_df = blogpost_candidates_df.drop_duplicates(subset=['Keyword_x', 'Suggestion', 'Keyword_y'], keep='last')
        print("blogpost_candidates_df Size =", blogpost_candidates_df.shape)
        
        print(" 3. Sort the dataframe back to it's original sorting before saving")
        blogpost_candidates_df = blogpost_candidates_df.sort_values(by=['Competition', 'Avg. monthly searches', 'Competition (indexed value)'], ascending=[True, False, True])
        print("blogpost_candidates_df Size =", blogpost_candidates_df.shape)
    
    print("Saving the blogpost_candidates_df to disk")
    blogpost_candidates_df['blogpost_created'].fillna(value={'blogpost_created':False})
    blogpost_candidates_df.to_csv(keyword_suggestions_blogpost_file, index=False)

    # Generate a file containing the keyword with no volume data
    cond = merged_df['Suggestion'].isin(final_keywords_df['Keyword'])
    missing_volume_kw_df = merged_df.drop(merged_df[cond].index, inplace=False)

    print("Size merged_df =", merged_df.shape)
    
    #missing_volume_kw_df = merged_df[ merged_df.Competition.isnull()]
    print("Size missing_volume_kw_df =", missing_volume_kw_df.shape)

    missing_volume_kw_df = missing_volume_kw_df[ merged_df["Avg. monthly searches"].isnull()]
    print("Size missing_volume_kw_df =", missing_volume_kw_df.shape)

    missing_volume_kw_df.to_csv(keyword_suggestions_generation_folder + "/keyword_suggestions_missing.csv", index=False)
    
    missing_volume_kw_1col_df = missing_volume_kw_df.iloc[:, 3]
    print("Size missing_volume_kw_1col_df =", missing_volume_kw_1col_df.shape)

    missing_volume_kw_1col_df.to_csv(keyword_suggestions_generation_folder +
                                     "/keyword_suggestions_missing_1col.csv", index=False)
    print("Size missing_volume_kw_1col_df =", missing_volume_kw_1col_df.shape)
    
    

# If you use more than 50 seed keywords you should slow down your requests - otherwise google is blocking the script
# If you have thousands of seed keywords use e.g. WAIT_TIME = 1 and MAX_WORKERS = 5
WAIT_TIME = 0.2
MAX_WORKERS = 20
# set the autocomplete language
LANGUAGE = "en"
# set the autocomplete country code - DE, US, TR, GR, etc..
COUNTRY = "US"
# Keyword_seed csv file name. One column csv file.
# csv_fileName="keyword_seeds.csv"

CSV_FILE_NAME = os.getenv('INPUT_KEYWORD_SEED')
autocomplete(CSV_FILE_NAME)

# Compute the clusters
compute_clusters()

# Merge data
keywordplanner_folder = folder = os.getenv('INPUT_DRAFTS_PATH')
#add_volumes_data(keywordplanner_folder)

# Output the generated file
print(keyword_suggestions_generation_file)
