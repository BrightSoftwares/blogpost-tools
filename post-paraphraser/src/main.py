from newspaper import Article, fulltext, Config
from markdownify import markdownify as md
from rpunct import RestorePuncts
#from spacy_langdetect import LanguageDetector
#from spacy.language import Language
#from googletrans import Translator
from summarizer import Summarizer
import traceback
import spacy
import nltk
import newspaper
import os
import frontmatter
import tomd
import re
from parrot import Parrot
import torch
import warnings


warnings.filterwarnings("ignore")
os.environ['TRANSFORMERS_CACHE'] = '/root/.cache/huggingface/transformers/'

nltk.download('punkt')
#translator = Translator()
#model = Summarizer()
#Init models (make sure you init ONLY once if you integrate this to your code)
parrot = Parrot(model_tag="prithivida/parrot_paraphraser_on_T5", use_gpu=False)
rpunct = RestorePuncts()


def replace_codeblock_with_tokens_template(content, tokens_array, regex, replacement_counter):
  # Find the code blocks
  pattern = re.compile(regex, re.DOTALL)
  matches = pattern.findall(content)
  print(matches)

  # Replace code blocks with tokens
  for match in matches:
    codeblock_text = match
    replacement_token = "##@@{}@@##".format(replacement_counter)
    content = content.replace(codeblock_text, replacement_token)
    tokens_array.append([codeblock_text, replacement_token])
    replacement_counter = replacement_counter + 1

  # return the array where we have the tokens and the content
  return tokens_array, content, replacement_counter

def replace_codeblock_with_tokens(content):
  replacement_counter = 10000
  tokens_array = []

  # Replace the code blocks
  regex = r"```.*?```"
  tokens_array, content, replacement_counter = replace_codeblock_with_tokens_template(content, tokens_array, regex, replacement_counter)

  # Replace the links
  regex = r"(\[.*\]\(.*\))"
  tokens_array, content, replacement_counter = replace_codeblock_with_tokens_template(content, tokens_array, regex, replacement_counter)

  # Replace the images
  regex = r"(\!\[.*\]\(.*\))"
  tokens_array, content, replacement_counter = replace_codeblock_with_tokens_template(content, tokens_array, regex, replacement_counter)

  return tokens_array, content

def replace_tokens_with_codeblocks(content, tokens):
  for token in tokens:
    content = content.replace(token[1], token[0])
  # return the array where we have the tokens and the content
  return content

def get_automatic_minsentencelength(text):
  return 60

def get_automatic_nbsentences(text):
  return 25

def paraphrase_text(text):
  
  prefix = ""
  para_phrases = None
  elected_text = ""
  rest_of_title = ""

  if text.strip() == "":
    return ""
  elif text.startswith("!["):
    # we could attempt to paraphrase the alt text also
    return text
  else:

    if text.startswith("#"): # detect a heading
      prefix = text.split(" ")[0]
      rest_of_title = text[len(prefix):] # we remove the ### from the begining of the title

    else:
      rest_of_title = text

    #para_phrases = parrot.augment(input_phrase=rest_of_title, do_diverse = True)
    para_phrases = parrot.rephrase(input_phrase=rest_of_title, do_diverse = False, adequacy_threshold = 0.79,
                               fluency_threshold = 0.70, use_gpu=True)
    print("para_phrases = ", para_phrases)

    if para_phrases == None:
      elected_text = text
    elif len(para_phrases) > 0:

      # Sometimes the result is not a list (does not contain the similarity score)
      if isinstance(para_phrases, list):
        elected_text = "{} {}".format(prefix, para_phrases[0][0])
      else:
        elected_text = "{} {}".format(prefix, para_phrases[0])

    else:
      elected_text = text

    try:
      # Apply punctuation restauration to the paraphrased text
      elected_text_punctuate = rpunct.punctuate(elected_text, lang='en')
      elected_text = elected_text_punctuate
    except Exception as e2:
      print("Error while trying to puntuate. ", str(e2))


    return elected_text

def paraphrase_markdown_text(md_text):
    print("Markdown version", md_text[:200])

    paraphrased_md_text = []

    for line in md_text.splitlines():
      print(line)

      # Split sentences in the line


      paraphrases_line = paraphrase_text(line)
      print("==> ", paraphrases_line)
      paraphrased_md_text.append(paraphrases_line)


    return ' \n'.join(paraphrased_md_text)

def paraphrase_markdown_text_with_nltk(md_text):
    print("**** nltk Markdown  version", md_text[:200])
    print("  ** Length before paraphrase : ", len(md_text))

    paraphrased_md_text = []

    for line in md_text.splitlines():
      print("Splitted line = ", line)

      # Split sentences in the line
      sent_text = nltk.sent_tokenize(line) # this gives us a list of sentences
      
      # now loop over each sentence and tokenize it separately
      nltk_final_paraphrased = []
      for sentence in sent_text:
          #tokenized_text = nltk.word_tokenize(sentence)
          #tagged = nltk.pos_tag(tokenized_text)
          #print(tagged)

          paraphrased = paraphrase_text(sentence)
          nltk_final_paraphrased.append(paraphrased.strip())
      

      paraphrases_line = ' '.join(nltk_final_paraphrased)
      print("==> ", paraphrases_line)
      paraphrased_md_text.append(paraphrases_line)


    ready_paraphrase = '\n'.join(paraphrased_md_text)
    print("  ** Length after : ", len(ready_paraphrase))
    return ready_paraphrase

def process_post_inspiration(post_inspiration_url):
  user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
  config = Config()
  config.browser_user_agent = user_agent

  # Let newspaper get the sumarry and keywords
  article = Article(post_inspiration_url, keep_article_html=True, config=config)
  article.download()
  article.parse()
  article.nlp()

  article_text = fulltext(article.html)
  article_text = article_text.replace('\ufeff', '')
  #print("Article text = ", article_text)

  #article_bert_summarry = model(article_text, num_sentences=nb_sentences, min_length=min_length)
  #print("Bert summarry = ", article_bert_summarry)

  print("Authors: ", article.authors)
  print("Publish date: ", article.publish_date)
  print("Top image: ", article.top_image)
  print("Keywords: ", article.keywords)
  print("Summary: ", article.summary)

  print("Language: ", article.meta_lang)

  # Transform the content into markdown
  thebody = article.article_html
  thebody_md = md(thebody, strip=['a'], heading_style="ATX", strong_em_symbol="*", code_language="```") # tomd.Tomd(thebody).markdown[:200]
  
  ## Replace items with tokens
  #tokens_array, thebody_md_replaced = replace_codeblock_with_tokens(thebody_md)

  ## Paraphrase the text
  #thebody_md_paraphrased = paraphrase_markdown_text_with_nltk(thebody_md_replaced)

  ## Replace back tokens with items
  #final_post_content = replace_tokens_with_codeblocks(thebody_md_paraphrased, tokens_array)

  # Paraphrase the text
  final_post_content = paraphrase_markdown_text_with_nltk(thebody_md)

  # Print the final result
  print("="*100)
  print("Final md file")
  print("="*100)
  print(final_post_content)

  # Translate the text before saving
  #translated_text = translate_large_text2(thebody_md, dest_lang)
  #print("Translated text = ", translated_text[:100])
  #post.content = article.summary

  return final_post_content, article


def post_summarizer(folder, dest_folder_path, dest_lang, nb_sentences, min_length, dry_run=False):
  print("post summarizer > nb sentences = {}, min_length = {}".format(nb_sentences, min_length))
  entries = os.listdir(folder)
  for entry in entries:

      try:
        print("Processing entry {}, dry run {} ({})".format(entry, dry_run, type(dry_run)))
        post = frontmatter.load(folder + "/" + entry)
        post_inspiration = post['post_inspiration'] if 'post_inspiration' in post else None
        #post_length = len(post.content)
        
        #post_inspiration = "https://en.as.com/olympic_games/2024-olympic-games-in-paris-mascot-what-is-a-phryge-and-how-is-it-pronounced-n/"
        #post_inspiration = "https://www.euronews.com/culture/2022/11/16/liberte-egalite-clitoris-we-need-to-talk-about-the-controversial-french-olympic-mascot"
        #post_inspiration = "https://www.pymnts.com/healthcare/2022/digital-platforms-seen-as-potential-cure-for-healthcare-access-challenges"
        #post_inspiration = "http://linuxize.com/post/docker-run-command/"
        #post_inspiration = "https://fintech.global/2022/12/05/nationwide-smart365-partner-to-boost-automation-in-mortgage-processes/"
        #post_inspiration = "https://www.everydayhealth.com/migraine/guide/treatment/nerve-stimulation-devices/"
        #post_inspiration = "https://www.thedroneu.com/adu-01074-dji-phantom-4-pro-v2/"
        #post_inspiration = "https://diydrones.com/profiles/blogs/revolutionizing-the-oil-and-gas-industry-using-nested-drone-syste"
        post_length = 0
        
        

        if post_inspiration is not None and post_length < 200:
          print("Processing post inspiration url", post_inspiration)

          try:
            final_post_content, article = process_post_inspiration(post_inspiration)
            post.content = final_post_content
            post.title = paraphrase_markdown_text_with_nltk(article.title)

            post["orig_post_authors"] = article.authors
            post["orig_post_publish_date"] = article.publish_date
            post["orig_post_top_image"] = article.top_image
            post["orig_post_keywords"] = article.keywords
            post["orig_post_title"] = article.title
            #post["orig_post_summary"] = article.summary
          except Exception as e1:
            error_str = "An error occured: {}".format(str(e1))
            print(error_str)
            post.content = error_str

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
