import pandas as pd
import spacy
import os
from pathlib import Path
import re

def generate_alias_file(aliases_file, aliases_new_file, internal_linking_root_folder, lang):
    print("Create language folder if not present")

    # aliases_file = os.path.join(internal_linking_root_folder, lang, aliases_file_name)
    # # aliases_new_file = os.path.join(internal_linking_root_folder, lang, "aliases_new.csv")
    # aliases_new_file = os.path.join(internal_linking_root_folder, lang, aliases_new_file_name)

    print(aliases_file)
    print(aliases_new_file)

    seo_lang_path = os.path.join(internal_linking_root_folder, lang)
    if not os.path.exists(seo_lang_path):
        print("Path {} does not exist, creating ...".format(seo_lang_path))
        os.makedirs(seo_lang_path)

        print("Generate the .gitkeep file")
        gitkeepfile = os.path.join(seo_lang_path, ".gitkeep")
        print(gitkeepfile)
        Path(gitkeepfile).touch()
    else:
        print("Path {} exists, skipping ...".format(seo_lang_path))

    if not os.path.exists(aliases_file):
        print("Generate the aliases file")
        with open(aliases_file, 'w') as f:
            f.write("dst_file,link_text\n")
    else:
        print("Path {} exists, skipping ...".format(aliases_file))

    if not os.path.exists(aliases_new_file):
        print("Generate the aliases new file")
        with open(aliases_new_file, 'w') as f:
            f.write("dst_file,link_text\n")
    else:
        print("Path {} exists, skipping ...".format(aliases_new_file))
        
def generate_silot_terms_file(silot_terms_file):
    print("Create silot_terms file if not present")

    print(silot_terms_file)

    if not os.path.exists(silot_terms_file):
        print("Generate the silot_terms_file file")
        with open(silot_terms_file, 'w') as f:
            f.write("silot_terms,title,path,cornerstone,categories\n")
    else:
        print("Path {} exists, skipping ...".format(silot_terms_file))
        
def generate_internallinking_per_silot_terms_file(internallinking_per_silot_terms_file):
    print("Create internallinking_per_silot_terms file if not present")

    print(internallinking_per_silot_terms_file)

    if not os.path.exists(internallinking_per_silot_terms_file):
        print("Generate the internallinking_per_silot_terms_file file")
        with open(internallinking_per_silot_terms_file, 'w') as f:
            f.write("silot_terms,src_file,dst_file,src_is_cornerstone,link_exist,link_text,full_link,full_link_and_text\n")
    else:
        print("Path {} exists, skipping ...".format(internallinking_per_silot_terms_file))

        
def generate_anchor_text_to_post_file(anchor_text_to_post_file):
    print("Create anchor_text_to_post_file file if not present")

    print(anchor_text_to_post_file)

    if not os.path.exists(anchor_text_to_post_file):
        print("Generate the anchor_text_to_post_file file")
        with open(anchor_text_to_post_file, 'w') as f:
            f.write("link_text,path,lang\n")
    else:
        print("Path {} exists, skipping ...".format(anchor_text_to_post_file))


def configure_nlp(lang):
    # nlp = spacy.load(lang, parser=False, entity=False)  
    # nlp = spacy.load(lang)
    if lang == "en":
        model_name = "en_core_web_sm"
    elif lang == "fr":
        model_name = "fr_core_news_sm"
    elif lang == "de":
        model_name = "de_core_news_sm"
    elif lang == "es":
        model_name = "es_core_news_sm"
    elif lang == "it":
        model_name = "it_core_news_sm"
    elif lang == "pt":
        model_name = "pt_core_news_sm"
    else:
        model_name = "en_core_web_sm"
        
    nlp = spacy.load(model_name)
    # nlp = spacy.load("fr_core_news_sm")

    customize_stop_words = [
    '1604', "2004", "create", "install", "sur", "par", "ses", "set", "100000", "des", "les", "stay", "like"
    ]

    # Mark them as stop words
    for w in customize_stop_words:
        nlp.vocab[w].is_stop = True

    return nlp

def generate_ngrams(s, n):
    # Convert to lowercases
    s = s.lower()
    
    # Replace all non-alphanumeric characters with spaces
    s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)
    
    # Break sentence in the token, remove empty tokens
    tokens = [token for token in s.split(" ") if token != ""]
    
    # Use the zip function to help us generate n-grams
    # Concatentate the tokens into ngrams and return
    ngrams = zip(*[tokens[i:] for i in range(n)])
    return [" ".join(ngram) for ngram in ngrams]

def generate_and_append_ngrams(dstfile, dstfile_nodate_ngrams, df, ngram_length, nlp):
    for kw in generate_ngrams(dstfile_nodate_ngrams, ngram_length):
        if len(kw) > 2 and not is_stopword(kw, nlp): #kw not in kw_to_ignore:
            # print(kw)
            df.loc[len(df)] = [dstfile, kw]

def is_stopword(text, nlp):
    print("{} is stop word?".format(text))
    for token in nlp(text):
        if token.is_stop:
            return True
    return False

def generate_short_keywords(aliases_file_name, aliases_new_file_name, folder_to_scan, lang):

    internal_linking_root_folder = "_seo/internal-linking"

    kw_to_ignore = ["how", "to", "set", "up", "on", "with", "1604", "create", "a", "new", "for", "8", "manage", "in", "i", "the", "2004", "from", "not", "can", "but", "abb", "2023"]

    aliases_file = os.path.join(internal_linking_root_folder, lang, aliases_file_name)
    aliases_new_file = os.path.join(internal_linking_root_folder, lang, aliases_new_file_name)

    generate_alias_file(aliases_file, aliases_new_file, internal_linking_root_folder, lang)

    nlp = configure_nlp(lang)

    df = pd.read_csv(aliases_file)

    df = df.sort_values(by=['dst_file'])

    # dstfile_uniq = df['dst_file'].unique()
    entries = [f for f in os.listdir(folder_to_scan) if os.path.isfile(os.path.join(folder_to_scan, f)) and os.path.join(folder_to_scan, f).endswith(".md") ] # os.listdir(folder_to_scan)


    print("Generate the keywords from the file name")
    for dstfile in entries: # dstfile_uniq:
        dstfile_nodate = dstfile[11:-3] # Remove the date and the first - and the .md at the end
        print(dstfile_nodate)

        print("Generate the n-grams")
        dstfile_nodate_ngrams = dstfile_nodate.replace("-", " ")
        # the_3grams = generate_ngrams(dstfile_nodate_ngrams, 3) # nltk.bigrams(dstfile_nodate_ngrams)
        # print(the_ngrams)

        # for kw in generate_ngrams(dstfile_nodate_ngrams, 5):
        #     if len(kw) > 2 and not is_stopword(kw): #kw not in kw_to_ignore:
        #         print(kw)
        #         df.loc[len(df)] = [dstfile, kw]

        generate_and_append_ngrams(dstfile, dstfile_nodate_ngrams, df, 5, nlp)
        generate_and_append_ngrams(dstfile, dstfile_nodate_ngrams, df, 4, nlp)
        generate_and_append_ngrams(dstfile, dstfile_nodate_ngrams, df, 3, nlp)
        generate_and_append_ngrams(dstfile, dstfile_nodate_ngrams, df, 2, nlp)

        kw_array = dstfile_nodate.split("-")
        for kw in kw_array:
            if len(kw) > 2 and not is_stopword(kw, nlp): #kw not in kw_to_ignore:
                # print(kw)
                df.loc[len(df)] = [dstfile, kw]

    print("Dropping duplicates")
    df = df.drop_duplicates()

    if df.size > 0:
        print("Creating a new table with the nb of words in the link text")
        df['nbwords'] = df.apply(lambda row: len(row.link_text.split(" ")), axis=1)
        
        print(df)
    
        print("Sort by length of link_text")
        df.sort_values("nbwords", ascending=False, inplace=True)
    
        print("Delete the nbwords column after the sorting")
        df.drop(columns=["nbwords"], inplace=True)
    else:
        print("The size of the df <= 0. Not sorting...")
        
    print("df = ", df)

    # Convert each row into spacy document and return the lemma of the tokens in 
    # the document if it is not a sotp word. Finally join the lemmas into as a string
    # df['link_text_lema'] = df.link_text.apply(lambda text: " ".join(token.lemma_ for token in nlp(text) if not token.is_stop))
    # df['link_text_lema'] = df.link_text.apply(is_stopword)


    print("Saving the result")
    df.to_csv(aliases_new_file, index=False)

if __name__ == "__main__":

    aliases_file_name = "aliases.csv"
    aliases_new_file_name = "aliases_new.csv"
    lang = "fr"
    folder_to_scan = "_posts/" + lang + "/"

    generate_short_keywords(aliases_file_name, aliases_new_file_name, folder_to_scan, lang)
