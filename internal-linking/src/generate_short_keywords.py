import pandas as pd
import spacy

kw_to_ignore = ["how", "to", "set", "up", "on", "with", "1604", "create", "a", "new", "for", "8", "manage", "in", "i", "the", "2004", "from", "not", "can", "but", "abb", "2023"]
lang = "en"

# nlp = spacy.load(lang, parser=False, entity=False)  
# nlp = spacy.load(lang)  
nlp = spacy.load("en_core_web_sm")
# nlp = spacy.load("fr_core_news_sm")

customize_stop_words = [
'1604', "2004", "create", "install"
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
    df = pd.read_csv("./aliases.csv")

    df = df.sort_values(by=['dst_file'])

    dstfile_uniq = df['dst_file'].unique()

    print("Generate the keywords from the file name")
    for dstfile in dstfile_uniq:
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
    df.to_csv("./aliases_new.csv", index=False)

if __name__ == "__main__":
    generate_short_keywords()