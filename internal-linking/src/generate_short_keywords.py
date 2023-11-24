import pandas as pd
import spacy
import os
from pathlib import Path

lang = "es"
folder_to_scan = "_posts/" + lang + "/"
internal_linking_root_folder = "_seo/internal-linking"
kw_to_ignore = ["how", "to", "set", "up", "on", "with", "1604", "create", "a", "new", "for", "8", "manage", "in", "i", "the", "2004", "from", "not", "can", "but", "abb", "2023"]
# lang = "en"



print("Create language folder if not present")

aliases_file = os.path.join(internal_linking_root_folder, lang, "aliases.csv")
aliases_new_file = os.path.join(internal_linking_root_folder, lang, "aliases_new.csv")

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

    print("Generate the aliases file")
    with open(aliases_file, 'w') as f:
        f.write("dst_file,link_text\n")
else:
    print("Path {} exists, skipping ...".format(seo_lang_path))


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

def is_stopword(text):
    print("{} is stop word?".format(text))
    for token in nlp(text):
        if token.is_stop:
            return True
    return False

def generate_short_keywords():
    df = pd.read_csv(aliases_file)

    df = df.sort_values(by=['dst_file'])

    # dstfile_uniq = df['dst_file'].unique()
    entries = [f for f in os.listdir(folder_to_scan) if os.path.isfile(os.path.join(folder_to_scan, f)) and os.path.join(folder_to_scan, f).endswith(".md") ] # os.listdir(folder_to_scan)


    print("Generate the keywords from the file name")
    for dstfile in entries: # dstfile_uniq:
        dstfile_nodate = dstfile[11:-3] # Remove the date and the first - and the .md at the end
        print(dstfile_nodate)
        kw_array = dstfile_nodate.split("-")

        for kw in kw_array:
            if len(kw) > 2 and not is_stopword(kw): #kw not in kw_to_ignore:
                print(kw)
                df.loc[len(df)] = [dstfile, kw]

    print("Dropping duplicates")
    df = df.drop_duplicates()

    #print("Remove stop words")


    # Convert each row into spacy document and return the lemma of the tokens in 
    # the document if it is not a sotp word. Finally join the lemmas into as a string
    # df['link_text_lema'] = df.link_text.apply(lambda text: " ".join(token.lemma_ for token in nlp(text) if not token.is_stop))
    # df['link_text_lema'] = df.link_text.apply(is_stopword)


    print("Saving the result")
    df.to_csv(aliases_new_file, index=False)

if __name__ == "__main__":
    generate_short_keywords()
