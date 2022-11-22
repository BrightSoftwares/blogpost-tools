from googletrans import Translator
import frontmatter
import os
import re
import glob
from slugify import slugify

translator = Translator()

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
  #tokens_array = []
  # Find the code blocks
  #pattern = re.compile(r"```.*?```", re.MULTILINE)
  #matches = pattern.findall(content)
  #print(matches)

  # Replace code blocks with tokens
  #replacement_counter = 10000
  for token in tokens:
    #codeblock_text = match
    #replacement_token = "##@@{}@@##".format(replacement_counter)
    content = content.replace(token[1], token[0])
    #tokens_array.append([codeblock_text, replacement_token])
    #replacement_counter = replacement_counter + 1

  # return the array where we have the tokens and the content
  return content

# process the markdown files one by one
def process_source_markdown(src_folder_path, scan_folder_path, dest_folder_path, dest_lang, dry_run=False):
  
  print("Processing post folder", src_folder_path)
  src_entries = glob.glob(src_folder_path + "/**/*.md", recursive=True) #[f for f in os.listdir(src_folder_path) if f.endswith('.md')]
  scanned_entries = glob.glob(scan_folder_path + "/**/*.md", recursive=True) #[f for f in os.listdir(dest_folder_path) if f.endswith('.md')]

  for entry in src_entries:
      # print(entry)
      try:
          src_post_filepath = entry #src_folder_path + "/" + entry
          print("Loading src file", src_post_filepath)
          post = frontmatter.load(src_post_filepath)
          title = post['title'] if 'title' in post else None
          ref = post['ref'] if 'ref' in post else None
          lang = post['lang'] if 'lang' in post else None
          post_date = post['date'] if 'date' in post else None


          if lang is not None and ref is not None:

            already_translated = False

            for scanned_entry in scanned_entries:
              dest_post_filepath = scanned_entry #dest_folder_path + "/" + dest_entry
              print("   Loading dest file", dest_post_filepath)
              dest_post = frontmatter.load(dest_post_filepath)
              dest_ref = dest_post['ref'] if 'ref' in dest_post else None
          
              if dest_ref is not None and dest_ref == ref:
                print("   Found another post in the destination with the same ref = {}. Skipping ...".format(ref))
                already_translated = True
                break

            # Process to the translation if there is no translation found
            if not already_translated:
              print("Post ref {} not translated. Translating ...".format(ref))

              transcription = ""
              try:
                  print("Replace code block with tokens for post title = ", title)
                  tokens, new_content = replace_codeblock_with_tokens(post.content)
                  print("Remplacement tokens", tokens)
                  #print("New content: ", new_content)

                  print("Split the nex content into chunks of 10K each")
                  n = 10000 # chunk length
                  new_content_chunks = [new_content[i:i+n] for i in range(0, len(new_content), n)]
                  print("Nb chunsk generated", len(new_content_chunks))

                  print("Translate the chunks")
                  new_translated_content = translate_text(new_content_chunks, lang, dest_lang)

                  print("Replace the tokens back")

                  print("  Add few custom replacements first")
                  tokens.append(["{% include", "{% incluent"])
                  tokens.append(["{% endraw %}", "{% dessiner %}"])
                  tokens.append(["{% raw %}", "{% cru %}"])
                  
                  replaced_content_chunks = replace_tokens_with_codeblocks(new_translated_content, tokens)

                  post.content = replaced_content_chunks

                  #ytvideo = get_yt_video_id(ytvideo_url)

                  #print("Found a post {} with a youtube video to transcribe. Video id = {}".format(
                  #    title, ytvideo))
                  ## print("Content is =", post.content.strip())
                  #transcription = get_yt_video_transcript(ytvideo, lang)
                  ##post['transcribed'] = True
                  #transcribed = True
                  #post['youtube_video_id'] = ytvideo

                  # print(filecontent)

              except Exception as e1:
                  transcription = "An error occured while trying to get translation. Error: {}".format(str(e1))
                  post.content = transcription
                  print(transcription)
              finally:
                  print("Change the language tag")
                  translated_title = translate_posttitle(post['title'], post['lang'], dest_lang)
                  post['title'] = translated_title
                  post['lang'] = dest_lang
                  post['pretified'] = False # So that the file name gets generated again
                  print("Saving the content of the file")
                  filecontent = frontmatter.dumps(post)
                  
                  # Make sure we have a post date
                  if post_date is None:
                    post_date = date.today()
                    post['date'] = post_date
                  
                  # Generate a translated file name
                  newfilename = "{}/{}-{}.md".format(dest_folder_path, post_date.strftime("%Y-%m-%d"), slugify(translated_title.lower()))
                  
                  if not dry_run:
                    with open(newfilename, 'w') as f:
                        f.write(filecontent)
                  else:
                    print("In dry run mode, skipping file write ...")
            else:
              print("Post with ref {} is already translated".format(ref))
          else:
            print("There was no ref ({}) or lang ({}) for this post title = {}".format(ref, lang, title))

      except Exception as e:
          print("Error. = ", str(e))



def process_markdown_file():
  pass

def translate_posttitle(title, src_lang, dest_lang):
  translation = translator.translate(title, dest=dest_lang)
  return translation.text

def translate_text(post_sections, src_lang, dest_lang):
  #translator = Translator()
  # bulk translate the sections of the post
  #post_sections = ['The quick brown fox', 'jumps over', 'the lazy dog']
  translations = translator.translate(post_sections, dest=dest_lang)
  #translator.translate('Il fait beau')

  translated_text = ""
  for translation in translations:
    #print(translation.origin, ' -> ', translation.text)
    translated_text += translation.text

  return translated_text

#translate_text([markdown_str], 'en', 'fr')

#
# Main
#
src_folder_path = os.getenv('INPUT_SRC_FOLDER')
dest_folder_path = os.getenv('INPUT_DEST_FOLDER')
scan_folder_path = os.getenv('INPUT_SCAN_FOLDER')
dest_lang = os.getenv('INPUT_DEST_LANG')
dry_run = os.getenv('INPUT_DRY_RUN')

process_source_markdown(src_folder_path, scan_folder_path, dest_folder_path, dest_lang, dry_run)
