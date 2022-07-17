import os
import fnmatch
import pandas as pd


def add_volumes_data(folder, keyword_suggestions_generation_folder, keyword_suggestions_generation_file, keyword_suggestions_blogpost_file, keyword_min_volume_eligible, keyword_max_volume_eligible):
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
    

    allowed_values = ['Faible', 'Low']
    blogpost_candidates_df = blogpost_candidates_df[ blogpost_candidates_df.Competition.isin(allowed_values) ]
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
        blogpost_candidates_df = blogpost_candidates_df.fillna(value={'blogpost_created':False, 'category':""})
        print("blogpost_candidates_df Size =", blogpost_candidates_df.shape)
        
        print("Sort by blogpost created to be able to remove duplicates")
        if 'category' in blogpost_candidates_df.columns:
            print("Include category in the sorting")
            blogpost_candidates_df = blogpost_candidates_df.sort_values(by=['blogpost_created', 'category'], ascending=[True, True])
            blogpost_candidates_df.to_csv(keyword_suggestions_generation_folder + "/keyword_blogpost_candidates_df_sorted.csv", index=False)
        else:
            print("Category not found. Sorting blogpost created only")
            blogpost_candidates_df = blogpost_candidates_df.sort_values(by=['blogpost_created'], ascending=[True])
        print("blogpost_candidates_df Size =", blogpost_candidates_df.shape)
        
        print(" 2. Remove duplicates")
        blogpost_candidates_df = blogpost_candidates_df.drop_duplicates(subset=['Keyword_x', 'Suggestion', 'Keyword_y'], keep='last')
        print("blogpost_candidates_df Size =", blogpost_candidates_df.shape)
        
        print(" 3. Sort the dataframe back to it's original sorting before saving")
        blogpost_candidates_df = blogpost_candidates_df.sort_values(by=['Suggestion', 'Avg. monthly searches', 'Competition (indexed value)'], ascending=[True, False, True])
        print("blogpost_candidates_df Size =", blogpost_candidates_df.shape)
    
    print("Saving the blogpost_candidates_df to disk  on {}".format(keyword_suggestions_blogpost_file))
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
    
    
src_folder = os.getenv("INPUT_SRC_FOLDER")
keyword_suggestions_generation_folder = os.getenv("INPUT_KEYWORD_SUGGESTION_GENERATION_FOLDER")
keyword_suggestions_generation_file = os.getenv("INPUT_KEYWORD_SUGGESTION_GENERATION_FILE")
keyword_suggestions_blogpost_file = os.getenv("INPUT_KEYWORD_SUGGESTIONS_BLOGPOST_FILE")
keyword_min_volume_eligible = int(os.getenv("INPUT_KEYWORD_MIN_VOLUME_ELIGIBLE", 10))
keyword_max_volume_eligible = int(os.getenv("INPUT_KEYWORD_MAX_VOLUME_ELIGIBLE", 100))
add_volumes_data(src_folder, keyword_suggestions_generation_folder, keyword_suggestions_generation_file, keyword_suggestions_blogpost_file, keyword_min_volume_eligible, keyword_max_volume_eligible)
