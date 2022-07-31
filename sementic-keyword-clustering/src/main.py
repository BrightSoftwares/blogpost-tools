import os
import sys
import time
import sys
import pandas as pd
import chardet
import codecs
from detect_delimiter import detect

#from google.colab import files
from sentence_transformers import SentenceTransformer, util


def detect_encoding(input_file, acceptable_confidence):

  with open(input_file) as f:
    contents = f.read()

    codec_enc_mapping = {
        codecs.BOM_UTF8: 'utf-8-sig',
        codecs.BOM_UTF16: 'utf-16',
        codecs.BOM_UTF16_BE: 'utf-16-be',
        codecs.BOM_UTF16_LE: 'utf-16-le',
        codecs.BOM_UTF32: 'utf-32',
        codecs.BOM_UTF32_BE: 'utf-32-be',
        codecs.BOM_UTF32_LE: 'utf-32-le',
    }

    encoding_type = 'utf-8'  # Default assumption
    is_unicode = False

    for bom, enc in codec_enc_mapping.items():
        if contents.startswith(bom):
            encoding_type = enc
            is_unicode = True
            break

    if not is_unicode:
        # Didn't find BOM, so let's try to detect the encoding
        guess = chardet.detect(contents)
        if guess['confidence'] >= acceptable_confidence:
            encoding_type = guess['encoding']

    print("Character Encoding Type Detected", encoding_type)

    return encoding_type

def detect_delimiter(input_file, encoding_type):
  # automatically detect the delimiter
  with open(input_file,encoding=encoding_type) as myfile:
      firstline = myfile.readline()
  myfile.close()
  delimiter_type = detect(firstline)

  print("Delimiter type =", delimiter_type)

  return delimiter_type

  
def cluster_keywords(keyword_suggestions_generation_file, clustered_kw_file, acceptable_confidence, cluster_accuracy, min_cluster_size, transformer):
  
  print("Clustering keywords. Src file {}, dest file {}, acceptable confidence = {}, cluster accuracy = {}, min cluster size = {}".format(keyword_suggestions_generation_file, clustered_kw_file, acceptable_confidence, cluster_accuracy, min_cluster_size))
  print("Transformer =", transformer)

  # detecting the encoding of the file
  encoding_type = "UTF-8" # detect_encoding(keyword_suggestions_generation_file, acceptable_confidence)

  # detect the delimiter
  delimiter_type = detect_delimiter(keyword_suggestions_generation_file, encoding_type)

  # create a dataframe using the detected delimiter and encoding type
  df = pd.read_csv((keyword_suggestions_generation_file), on_bad_lines='skip', encoding=encoding_type, delimiter=delimiter_type)
  count_rows = len(df)
  if count_rows > 50_000:
    print("WARNING: You May Experience Crashes When Processing Over 50,000 Keywords at Once. Please consider smaller batches!")
  print("Uploaded Keyword CSV File Successfully!")
  print("Loaded csv df size = ", df.shape)
  
  # create the silot_terms column if not exists
  if "silot_terms" not in df.columns:
    df["silot_terms"] = ""

  # standardise the keyword columns
  #df.rename(columns={"Search term": "Keyword", "keyword": "Keyword", "query": "Keyword", "query": "Keyword", "Top queries": "Keyword", "queries": "Keyword", "Keywords": "Keyword","keywords": "Keyword", "Search terms report": "Keyword"}, inplace=True)

  if "Suggestion" not in df.columns:
    print("Error! Please make sure your csv file contains a column named 'Suggestion!")

  # store the data
  cluster_name_list = []
  corpus_sentences_list = []
  df_all = []

  corpus_set = set(df['Suggestion'])
  corpus_set_all = corpus_set
  cluster = True

  # keep looping through until no more clusters are created

  cluster_accuracy = cluster_accuracy / 100
  model = SentenceTransformer(transformer)

  print("corpus_set = ", corpus_set)

  while cluster:

      corpus_sentences = list(corpus_set)
      check_len = len(corpus_sentences)

      corpus_embeddings = model.encode(corpus_sentences, batch_size=256, show_progress_bar=True, convert_to_tensor=True)
      clusters = util.community_detection(corpus_embeddings, min_community_size=min_cluster_size, threshold=cluster_accuracy, init_max_size=len(corpus_embeddings))

      for keyword, cluster in enumerate(clusters):
          print("\nCluster {}, #{} Elements ".format(keyword + 1, len(cluster)))

          for sentence_id in cluster[0:]:
              print("\t", corpus_sentences[sentence_id])
              corpus_sentences_list.append(corpus_sentences[sentence_id])
              cluster_name_list.append("Cluster {}, #{} Elements ".format(keyword + 1, len(cluster)))

      df_new = pd.DataFrame(None)
      df_new['silot_terms'] = cluster_name_list
      df_new["Suggestion"] = corpus_sentences_list

      df_all.append(df_new)
      have = set(df_new["Suggestion"])

      corpus_set = corpus_set_all - have
      remaining = len(corpus_set)
      print("Total Unclustered Keywords: ", remaining)
      if check_len == remaining:
          break


  # make a new dataframe from the list of dataframe and merge back into the orginal df
  df_new = pd.concat(df_all)
  df = df.merge(df_new.drop_duplicates('Suggestion'), how='left', on="Suggestion")

  # rename the clusters to the shortest keyword in the cluster
  df['Length'] = df['Suggestion'].astype(str).map(len)
  df = df.sort_values(by="Length", ascending=True)

  df['silot_terms'] = df.groupby('silot_terms')['Suggestion'].transform('first')
  df.sort_values(['silot_terms', "Suggestion"], ascending=[True, True], inplace=True)

  df['silot_terms'] = df['silot_terms'].fillna("zzz_no_cluster")

  del df['Length']

  # move the cluster and keyword columns to the front
  col = df.pop("Suggestion")
  df.insert(0, col.name, col)

  col = df.pop('silot_terms')
  df.insert(0, col.name, col)

  df.sort_values(["silot_terms", "Suggestion"], ascending=[True, True], inplace=True)

  uncluster_percent = (remaining / count_rows) * 100
  clustered_percent = 100 - uncluster_percent
  print(clustered_percent,"% of rows clustered successfully!")

  df.to_csv(clustered_kw_file, index=False)
  #files.download("Your Keywords Clustered.csv")


keyword_suggestions_generation_file = os.getenv("INPUT_KEYWORD_SUGGESTIONS_FILE")
clustered_kw_file = os.getenv("INPUT_CLUSTERED_KW_FILE")
acceptable_confidence = float(os.getenv("INPUT_ACCEPTABLE_CONFIDENCE"))
transformer = os.getenv("INPUT_TRANSFORMER")


cluster_accuracy = int(os.getenv("INPUT_CLUSTER_ACCURACY"))  # 0-100 (100 = very tight clusters, but higher percentage of no_cluster groups)
min_cluster_size = int(os.getenv("INPUT_MIN_CLUSTER_SIZE"))  # set the minimum size of cluster groups. (Lower number = tighter groups)

cluster_keywords(keyword_suggestions_generation_file, clustered_kw_file, acceptable_confidence, cluster_accuracy, min_cluster_size, transformer)
