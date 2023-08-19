import os
import fnmatch
import pandas as pd


def patch_dataframe_with_customdata(blogpost_candidates_df, keyword_suggestions_blogpost_file):
    print("Load previously processed blogpost created data")
    #print(" 1. Merge data from csv with this one")
    print("1.1 Checking if file {} exists".format(keyword_suggestions_blogpost_file))
    if os.path.exists(keyword_suggestions_blogpost_file):
        print("File exists:", keyword_suggestions_blogpost_file)
        exiting_blogpost_candidates_df = pd.read_csv(keyword_suggestions_blogpost_file)
        print("1.2 exiting_blogpost_candidates_df Size =", exiting_blogpost_candidates_df.shape)
        #print("1.3 exiting_blogpost_candidates_df = ", exiting_blogpost_candidates_df)
        
        #blogpost_candidates_df = pd.concat([blogpost_candidates_df, exiting_blogpost_candidates_df], ignore_index=True, sort=False)
        #blogpost_candidates_df = blogpost_candidates_df.fillna(value={'blogpost_created':False, 'category':""})
        #print("blogpost_candidates_df Size =", blogpost_candidates_df.shape)
        #
        #print("Sort by blogpost created to be able to remove duplicates")
        #if 'category' in blogpost_candidates_df.columns:
        #    print("Include category in the sorting")
        #    blogpost_candidates_df = blogpost_candidates_df.sort_values(by=['blogpost_created', 'category'], ascending=[True, True])
        #    blogpost_candidates_df.to_csv(keyword_suggestions_generation_folder + "/keyword_blogpost_candidates_df_sorted.csv", index=False)
        #else:
        #    print("Category not found. Sorting blogpost created only")
        #    blogpost_candidates_df = blogpost_candidates_df.sort_values(by=['blogpost_created'], ascending=[True])
        #print("blogpost_candidates_df Size =", blogpost_candidates_df.shape)
        #
        #print(" 2. Remove duplicates")
        #blogpost_candidates_df = blogpost_candidates_df.drop_duplicates(subset=['Keyword_x', 'Suggestion', 'Keyword_y'], keep='last')
        #print("blogpost_candidates_df Size =", blogpost_candidates_df.shape)
        
        print("1.4. Sort the dataframe back to it's original sorting before saving")
        blogpost_candidates_df = blogpost_candidates_df.sort_values(by=['Suggestion', 'Avg. monthly searches', 'Competition (indexed value)'], ascending=[True, False, True])
        print("1.5 blogpost_candidates_df Size =", blogpost_candidates_df.shape)
        print("1.5 blogpost_candidates_df columns =", blogpost_candidates_df.columns)
    else:
      print("1.6 File {} not found. Nothing loaded.".format(keyword_suggestions_blogpost_file))
      exiting_blogpost_candidates_df = pd.DataFrame([], columns=['first_seen', 'last_seen', 'Keyword', 'Suggestion', 'is_new', 'blogpost_created', 'category', 'blogpost_title', 'silot_terms', 'cornerstone', 'semantic_cluster'])

    # Patching the data
    print("Merging dataframe blogpost_candidates_df size =", blogpost_candidates_df.shape)
    print("With dataframe exiting_blogpost_candidates_df size =", exiting_blogpost_candidates_df.shape)
    blogpost_candidates_merged_df = blogpost_candidates_df.merge(exiting_blogpost_candidates_df, how='left', left_on='Suggestion', right_on='Suggestion')
    #print("blogpost_candidates_merged_df = ", blogpost_candidates_merged_df)
    print("blogpost_candidates_merged_df right after merge size = ", blogpost_candidates_merged_df.columns)
    print("blogpost_candidates_merged_df columns = ", blogpost_candidates_merged_df.columns)

    # Merge the two columns
    if 'category_x' in blogpost_candidates_merged_df.columns:
        blogpost_candidates_merged_df['category_x'] = blogpost_candidates_merged_df['category_x'] if blogpost_candidates_merged_df['category_y'].isnull else blogpost_candidates_merged_df['category_y']
    
    if 'blogpost_title_x' in blogpost_candidates_merged_df.columns:
        blogpost_candidates_merged_df['blogpost_title_x'] = blogpost_candidates_merged_df['blogpost_title_x'] if blogpost_candidates_merged_df['blogpost_title_y'].isnull else blogpost_candidates_merged_df['blogpost_title_y']
    
    if 'silot_terms_x' in blogpost_candidates_merged_df.columns:
        blogpost_candidates_merged_df['silot_terms_x'] = blogpost_candidates_merged_df['silot_terms_x'] if blogpost_candidates_merged_df['silot_terms_y'].isnull else blogpost_candidates_merged_df['silot_terms_y']
    
    if 'cornerstone_x' in blogpost_candidates_merged_df.columns:
        blogpost_candidates_merged_df['cornerstone_x'] = blogpost_candidates_merged_df['cornerstone_x'] if blogpost_candidates_merged_df['cornerstone_y'].isnull else blogpost_candidates_merged_df['cornerstone_y']
    
    if 'semantic_cluster_x' in blogpost_candidates_merged_df.columns:
        blogpost_candidates_merged_df['semantic_cluster_x'] = blogpost_candidates_merged_df['semantic_cluster_x'] if blogpost_candidates_merged_df['semantic_cluster_y'].isnull else blogpost_candidates_merged_df['semantic_cluster_y']
    
    if 'blogpost_created_x' in blogpost_candidates_merged_df.columns:
        blogpost_candidates_merged_df['blogpost_created_x'] = blogpost_candidates_merged_df['blogpost_created_x'] if blogpost_candidates_merged_df['blogpost_created_y'].isnull else blogpost_candidates_merged_df['blogpost_created_y']
    
    # renaming the columns back
    cols = {}
    for colname in blogpost_candidates_merged_df.columns:
      if colname[-2:] == "_x":
        cols[colname] = colname[:len(colname) - 2]

    print("Rename dict : ", cols)
    blogpost_candidates_merged_df.rename(columns=cols, inplace=True)

    # delete the extra columns
    delcols = []
    for colname in blogpost_candidates_merged_df.columns:
      if colname[-2:] == "_y":
        delcols.append(colname)
    print("Delete array: ", delcols)
    blogpost_candidates_merged_df.drop(columns=delcols, inplace=True)

    print("After cleanup: blogpost_candidates_merged_df columns = ", blogpost_candidates_merged_df.columns)
    
    print(" 2. Remove duplicates")
    blogpost_candidates_merged_df.drop_duplicates(subset=['Suggestion', 'category', 'blogpost_title', 'silot_terms'], keep='last', inplace=False)
    print("blogpost_candidates_merged_df Size =", blogpost_candidates_merged_df.shape)

    blogpost_candidates_merged_df['blogpost_created'].fillna(value={'blogpost_created':False})
    return blogpost_candidates_merged_df


def extract_by_search_volume(merged_df, min_vol, max_vol, keyword_suggestions_blogpost_file):
    # Generate a file with keywords that meet the requirements for a blogpost    
    print("Keeping only the keywords with volume above {} and below {}".format(keyword_min_volume_eligible, keyword_max_volume_eligible))

    allowed_values = ['Faible', 'Low']
    blogpost_candidates_df = merged_df[ (merged_df['Avg. monthly searches'] >= keyword_min_volume_eligible) 
      & (merged_df['Avg. monthly searches'] <= keyword_max_volume_eligible)
      & (merged_df.Competition.isin(allowed_values)) 
      #& (merged_df.Competition.notnull()) 
      ]
    print("0. blogpost_candidates_df size: ", blogpost_candidates_df.shape)

    #blogpost_candidates_df = merged_df[ merged_df['Avg. monthly searches'] <= keyword_max_volume_eligible ]
    #print("1. blogpost_candidates_df size: ", blogpost_candidates_df.shape)
    
    #blogpost_candidates_df = blogpost_candidates_df[ blogpost_candidates_df.Competition.isin(allowed_values) ]
    #print("2. blogpost_candidates_df size: ", blogpost_candidates_df.shape)
    
    #blogpost_candidates_df = blogpost_candidates_df[ blogpost_candidates_df.Competition.notnull() ]
    #print("3. blogpost_candidates_df size: ", blogpost_candidates_df.shape)
    
    blogpost_candidates_df = patch_dataframe_with_customdata(blogpost_candidates_df, keyword_suggestions_blogpost_file)
    return blogpost_candidates_df

def load_keyword_stats(folder):
    entries = os.listdir(folder)
    final_keywords_df = None
    for entry in entries:
        if fnmatch.fnmatch(entry, 'Keyword Stats *.csv'):
            print(entry)
            # print(entry)
            try:
                tmp_final_keywords_df = pd.read_csv(keyword_suggestions_generation_folder + "/" + entry, delimiter='\t', encoding="ISO-8859-1")
                final_keywords_df = tmp_final_keywords_df if final_keywords_df is None else pd.concat((final_keywords_df, tmp_final_keywords_df))
                #print("tmp_final_keywords_df columns = ", tmp_final_keywords_df.columns)
                #print("final_keywords_df = ", final_keywords_df.columns if final_keywords_df is not None else [])

            except Exception as e:
                print("An error occured. Error = ", str(e))
                #pass
        #else:
        #    print("The file does not match the keyword planner pattern", entry)

    # If there is no Keyword stats file to pull data from, create an empty dataframe
    if final_keywords_df is None:
      print("Couldn't load data from stats file. Generating an empty dataframe")
      final_keywords_df = pd.DataFrame([], columns=['Keyword', 'Currency', 'Segmentation', 'Avg. monthly searches', 'Three month change', 'YoY change', 'Competition', 'Competition (indexed value)', 'Top of page bid (low range)', 'Top of page bid (high range)', 'Ad impression share', 'Organic average position', 'Organic impression share', 'In Account'])
    
    print("Size of the stats df", final_keywords_df.shape)
    print("Stats df columns", final_keywords_df.columns)
    #print("final_keywords_df =", final_keywords_df)

    return final_keywords_df


def add_volumes_data(folder, keyword_suggestions_generation_folder, keyword_suggestions_generation_file, keyword_suggestions_blogpost_file, keyword_min_volume_eligible, keyword_max_volume_eligible):
    print("Pandas version:", pd.__version__)
    # Load the volume data from local csv
    final_keywords_df = load_keyword_stats(folder)

    # Add the volumes data
    print("0.0 Loading data from file", keyword_suggestions_generation_file)
    suggested_kw_df = pd.read_csv(keyword_suggestions_generation_file)
    print("0.1 Size of suggested_kw_df", suggested_kw_df.shape)
    print("0.2 Columns of suggested_kw_df", suggested_kw_df.columns)

    # Merging suggested_kw_df with stats df
    merged_df = suggested_kw_df.merge(
        final_keywords_df, how='left', left_on='Suggestion', right_on='Keyword')
    print("Merged dataframe size =", merged_df.shape)
    print("Merged dataframe, Competition column =", merged_df['Competition'])
    
    merged_df = merged_df.sort_values(by=['Competition', 'Avg. monthly searches', 'Competition (indexed value)'], ascending=[True, False, True])
    
    # Replace the N/As in blogpost_created column with False
    merged_df['blogpost_created'].fillna(value={'blogpost_created':False})
    merged_df.to_csv(keyword_suggestions_generation_folder + "/keyword_suggestions_merged.csv", index=False)
    
    merged_df_perbidcost = merged_df.sort_values(by=['Competition', 'Avg. monthly searches', 'Top of page bid (low range)'], ascending=[True, False, False])
    merged_df_perbidcost.to_csv(keyword_suggestions_generation_folder + "/keyword_suggestions_merged_per_bid_cost_low.csv", index=False)
    
    blogpost_candidates_df = extract_by_search_volume(merged_df, keyword_min_volume_eligible, keyword_max_volume_eligible, keyword_suggestions_blogpost_file)
    print("blogpost_candidates_df extracted by search volume size =", blogpost_candidates_df.shape)

    print("0.3 Saving the blogpost_candidates_df to disk  on {}".format(keyword_suggestions_blogpost_file))
    blogpost_candidates_df.to_csv(keyword_suggestions_blogpost_file, index=False)

    # Generate a file containing the keyword with no volume data
    cond = merged_df['Suggestion'].isin(final_keywords_df['Keyword'])
    missing_volume_kw_df = merged_df.drop(merged_df[cond].index, inplace=False)

    print("0.4 Size merged_df =", merged_df.shape)
    
    #missing_volume_kw_df = merged_df[ merged_df.Competition.isnull()]
    print("0.5 Size missing_volume_kw_df =", missing_volume_kw_df.shape)

    missing_volume_kw_df = missing_volume_kw_df[ merged_df["Avg. monthly searches"].isnull()]
    print("0.6 Size missing_volume_kw_df =", missing_volume_kw_df.shape)

    missing_volume_kw_df.to_csv(keyword_suggestions_generation_folder + "/keyword_suggestions_missing.csv", index=False)
    
    missing_volume_kw_1col_df = missing_volume_kw_df.iloc[:, 3]
    print("0.7 Size missing_volume_kw_1col_df =", missing_volume_kw_1col_df.shape)

    missing_volume_kw_1col_df.to_csv(keyword_suggestions_generation_folder +
                                     "/keyword_suggestions_missing_1col.csv", index=False)
    print("0.8 Size missing_volume_kw_1col_df =", missing_volume_kw_1col_df.shape)
    
    
src_folder = os.getenv("INPUT_SRC_FOLDER")
keyword_suggestions_generation_folder = os.getenv("INPUT_KEYWORD_SUGGESTION_GENERATION_FOLDER")
keyword_suggestions_generation_file = os.getenv("INPUT_KEYWORD_SUGGESTION_GENERATION_FILE")
keyword_suggestions_blogpost_file = os.getenv("INPUT_KEYWORD_SUGGESTIONS_BLOGPOST_FILE")
keyword_min_volume_eligible = int(os.getenv("INPUT_KEYWORD_MIN_VOLUME_ELIGIBLE", 10))
keyword_max_volume_eligible = int(os.getenv("INPUT_KEYWORD_MAX_VOLUME_ELIGIBLE", 100))
add_volumes_data(src_folder, keyword_suggestions_generation_folder, keyword_suggestions_generation_file, keyword_suggestions_blogpost_file, keyword_min_volume_eligible, keyword_max_volume_eligible)
