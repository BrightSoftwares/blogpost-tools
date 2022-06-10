# Pemavor.com Autocomplete Trends
# Author: Stefan Neefischer (stefan.neefischer@gmail.com)
import concurrent.futures
from datetime import date
from datetime import datetime
import pandas as pd
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
keyword_min_volume_eligible = int(os.getenv(INPUT_KEYWORD_MIN_VOLUME_ELIGIBLE))


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
            columns=['first_seen', 'last_seen', 'Keyword', 'Suggestion'])

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
    keywords_df['blogpost_created'] = keywords_df['blogpost_created'] if 'blogpost_created' in keywords_df.columns else False
    keywords_df = keywords_df[['first_seen', 'last_seen',
                               'Keyword', 'Suggestion', 'is_new', 'blogpost_created']]
    
    # Remove duplicates
    keywords_df.drop_duplicates(inplace=True)
    keywords_df.to_csv(keyword_suggestions_generation_file, index=False)


def add_volumes_data(folder):
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
    merged_df.to_csv(keyword_suggestions_generation_folder + "/keyword_suggestions_merged.csv", index=False)
    
    merged_df_perbidcost = merged_df.sort_values(by=['Competition', 'Avg. monthly searches', 'Top of page bid (low range)'], ascending=[True, False, False])
    merged_df_perbidcost.to_csv(keyword_suggestions_generation_folder + "/keyword_suggestions_merged_per_bid_cost_low.csv", index=False)
    
    # Generate a file with keywords that meet the requirements for a blogpost
    blogpost_candidates_df = merged_df[ merged_df['Avg. monthly searches'] >= keyword_min_volume_eligible ]
    blogpost_candidates_df = blogpost_candidates_df[ blogpost_candidates_df.Competition == 'Faible' ]
    blogpost_candidates_df = blogpost_candidates_df[ blogpost_candidates_df.Competition.notnull() ]
    blogpost_candidates_df.to_csv(keyword_suggestions_generation_folder + "/keyword_suggestions_merged_blogpost_candidates.csv", index=False)

    # Generate a file containing the keyword with no volume data
    cond = merged_df['Suggestion'].isin(final_keywords_df['Keyword'])
    #missing_volume_kw_df = merged_df.drop(merged_df[cond].index, inplace=False)
    missing_volume_kw_df = merged_df[ merged_df.Competition.isnull()]
    missing_volume_kw_df = missing_volume_kw_df[ merged_df["Avg. monthly searches"].isnull()]
    missing_volume_kw_df.to_csv(keyword_suggestions_generation_folder + "/keyword_suggestions_missing.csv", index=False)
    missing_volume_kw_1col_df = missing_volume_kw_df.iloc[:, 3]
    missing_volume_kw_1col_df.to_csv(keyword_suggestions_generation_folder +
                                     "/keyword_suggestions_missing_1col.csv", index=False)


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

# Merge data
keywordplanner_folder = folder = os.getenv('INPUT_DRAFTS_PATH')
add_volumes_data(keywordplanner_folder)

# Output the generated file
print(keyword_suggestions_generation_file)
