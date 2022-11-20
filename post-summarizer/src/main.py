from newspaper import Article, fulltext
from markdownify import markdownify as md
from spacy_langdetect import LanguageDetector
from spacy.language import Language
from googletrans import Translator
from summarizer import Summarizer
import traceback
import spacy
import nltk
import newspaper
import os
import frontmatter
import tomd
import re

os.environ['TRANSFORMERS_CACHE'] = '/root/.cache/huggingface/transformers/'

nltk.download('punkt')
translator = Translator()
model = Summarizer()


def replace_codeblock_with_tokens(content):
  tokens_array = []
  # Find the code blocks
  pattern = re.compile(r"```.*?```", re.DOTALL)
  matches = pattern.findall(content)
  print(matches)

  # Replace code blocks with tokens
  replacement_counter = 10000
  for match in matches:
    codeblock_text = match
    replacement_token = "##@@{}@@##".format(replacement_counter)
    content = content.replace(codeblock_text, replacement_token)
    tokens_array.append([codeblock_text, replacement_token])
    replacement_counter = replacement_counter + 1

  # return the array where we have the tokens and the content
  return tokens_array, content

def replace_tokens_with_codeblocks(content, tokens):
  for token in tokens:
    content = content.replace(token[1], token[0])
  # return the array where we have the tokens and the content
  return content

def split_into_translatable_chunks(content, n=10000):
  print("Split the nex content into chunks of 10K each")
  n = 10000 # chunk length
  new_content_chunks = [content[i:i+n] for i in range(0, len(content), n)]
  print("Nb chunsk generated", len(new_content_chunks))
  return new_content_chunks

def join_translations_into_largetext(translations):
  translated_text = ""
  for translation in translations:
    print(translation.origin[:100], ' -> ', translation.text[:100])
    translated_text += translation.text
    #print(translated_text[:100])

  return translated_text

def translate_large_text2(large_text, dest_lang):
  print("Translate large text into lang ", dest_lang)
  tokens, new_content = replace_codeblock_with_tokens(large_text)
  print("Remplacement tokens", tokens)
  #print("New content: ", new_content)

  print("Split the nex content into chunks of 10K each")
  new_content_chunks = split_into_translatable_chunks(new_content)
  print("Nb chunsk generated", len(new_content_chunks))

  print("Translate the chunks")
  translations = translator.translate(new_content_chunks, dest=dest_lang) #translate_text(new_content_chunks, lang, dest_lang)

  print("Group the chunks back into a large text")
  new_translated_content = join_translations_into_largetext(translations)
  print("New translated content: ", new_translated_content[:100])

  print("Replace the tokens back")

  print("  Add few custom replacements first")
  tokens.append(["{% include", "{% incluent"])
  tokens.append(["{% endraw %}", "{% dessiner %}"])
  tokens.append(["{% raw %}", "{% cru %}"])
  
  replaced_content_chunks = replace_tokens_with_codeblocks(new_translated_content, tokens)

  return replaced_content_chunks


def post_summarizer(folder, dest_folder_path, dest_lang, nb_sentences, min_length, dry_run=False):
  print("post summarizer > nb sentences = {}, min_length = {}".format(nb_sentences, min_length))
  entries = os.listdir(folder)
  for entry in entries:

      try:
        print("Processing entry {}, dry run {} ({})".format(entry, dry_run, type(dry_run)))
        post = frontmatter.load(folder + "/" + entry)
        post_inspiration = post['post_inspiration'] if 'post_inspiration' in post else None
        #post_inspiration = "https://en.as.com/olympic_games/2024-olympic-games-in-paris-mascot-what-is-a-phryge-and-how-is-it-pronounced-n/"
        #post_inspiration = "https://www.euronews.com/culture/2022/11/16/liberte-egalite-clitoris-we-need-to-talk-about-the-controversial-french-olympic-mascot"
        post_length = len(post.content)

        if post_inspiration is not None and post_length < 200:
          print("Processing post inspiration url", post_inspiration)

          # Let newspaper get the sumarry and keywords
          article = Article(post_inspiration, keep_article_html=True)
          article.download()
          article.parse()
          article.nlp()

          article_text = fulltext(article.html)
          article_text = article_text.replace('\ufeff', '')
          #print("Article text = ", article_text)

          article_bert_summarry = model(article_text, num_sentences=nb_sentences, min_length=min_length)

          print("Bert summarry = ", article_bert_summarry)

          print("Authors: ", article.authors)
          print("Publish date: ", article.publish_date)
          print("Top image: ", article.top_image)
          print("Keywords: ", article.keywords)
          print("Summary: ", article.summary)

          print("Language: ", article.meta_lang)

          # Transform the content into markdown
          thebody = article.article_html
          thebody_md = md(thebody) # tomd.Tomd(thebody).markdown[:200]
          print("Markdown version", thebody_md[:200])

          # Translate the text before saving
          #translated_text = translate_large_text2(thebody_md, dest_lang)
          #print("Translated text = ", translated_text[:100])
          post.content = article.summary

          post["orig_post_authors"] = article.authors
          post["orig_post_publish_date"] = article.publish_date
          post["orig_post_top_image"] = article.top_image
          post["orig_post_keywords"] = article.keywords
          #post["orig_post_summary"] = article.summary

          if dry_run == "false":
            print("Saving the content of the file")
            filecontent = frontmatter.dumps(post)

            with open(dest_folder_path + "/" + os.path.basename(entry), 'w') as f:
              f.write(filecontent)
          else:
            print("In dry run mode, skipping file write ...")
          

        else:
          print("There is no post_inspiration in this entry {} or text is too long already {}.".format(post_inspiration, post_length))

      except Exception as e:
        print("Error for an entry. ", str(e))
        traceback.print_exc()



# Load the files and search for inspiration post
folder = os.getenv('INPUT_SRC_FOLDER')
dest_folder_path = os.getenv('INPUT_DEST_FOLDER')
dry_run = os.getenv('INPUT_DRY_RUN')
dest_lang = os.getenv('INPUT_DEST_LANG')
nb_sentences = int(os.getenv('INPUT_SUMMARIZER_NBSENTENCES', 5))
min_length = int(os.getenv('INPUT_SUMMARIZER_MINLENGTH', 60))
post_summarizer(folder, dest_folder_path, dest_lang, nb_sentences, min_length, dry_run)
