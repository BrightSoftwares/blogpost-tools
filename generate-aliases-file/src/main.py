import pandas as pd
import os

src_keyword_suggestion_merged = os.getenv('INPUT_KEYWORD_SUGGESTION_MERGED') # "keyword_suggestions_merged.csv"
src_interlinking_csv = os.getenv('INPUT_SRC_INTERLINKING_CSV') # "internallinking_per_silot_terms.csv"
dst_aliases_file = os.getenv('INPUT_DST_ALIASES_FILE') # "aliases.csv"


def generate_aliases_file(src_keyword_suggestion_merged, src_interlinking_csv, dst_aliases_file):
  kw_df = pd.read_csv(src_keyword_suggestion_merged)
  kwfiltered_df = kw_df.loc[kw_df['silot_terms'] != ""]
  il_df = pd.read_csv(src_interlinking_csv)

  # aliases_df = pd.DataFrame(columns=['dst_file', 'link_text'])

  # for current_item_index, current_item in il_df.iterrows():
  #     print("Processing ", current_item.dst_file)

  #     # Go through the keywords that has the same silot_terms
  #     kw_silotterms_df = kwfiltered_df.loc[kwfiltered_df['silot_terms'] == current_item.silot_terms]
  #     for kw_current_item_index, kw_current_item in kw_silotterms_df.iterrows():
  #         # Generate a line for the post and the keyword

  #         aliases_df.loc[len(aliases_df)] = [current_item.dst_file, kw_current_item.Suggestion]

  print("Converting the two silot_terms columns types to string")
  il_df['silot_terms'] = pd.Series(il_df['silot_terms'], dtype=pd.StringDtype()) # il_df['silot_terms'].astype("string")
  kwfiltered_df['silot_terms'] = pd.Series(kwfiltered_df['silot_terms'], dtype=pd.StringDtype()) # kwfiltered_df['silot_terms'].astype("string")
  
  print(il_df['silot_terms'])
  print(kwfiltered_df['silot_terms'])

  aliases_df = pd.merge(il_df, kwfiltered_df, on="silot_terms")
  aliases_df = aliases_df[['dst_file', 'Suggestion']]
  aliases_df = aliases_df.rename(columns={"Suggestion": "link_text"})
  print(aliases_df.head(100))

  print("Removing duplicates")
  aliases_df.drop_duplicates()

  print("Saving the aliases to", dst_aliases_file)
  aliases_df.to_csv(dst_aliases_file, index=False)


print("Generating aliases file")
generate_aliases_file(src_keyword_suggestion_merged, src_interlinking_csv, dst_aliases_file)
print("Done")
