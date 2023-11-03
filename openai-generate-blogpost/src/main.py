import os
import openai
from datetime import datetime
import random
import time
import requests
import json
import frontmatter
import base64


posts_channel = os.getenv('INPUT_CHANNEL')
manually_generated_posts_channel = os.getenv('INPUT_MANUALLY_GENERATED_POSTS_CHANNEL')
posts_requests_base_url = os.getenv('INPUT_POSTS_REQUESTS_BASE_URL')
dst_generated_posts = os.getenv('INPUT_DST_GENERATED_POSTS')
src_posts_to_rephrase = os.getenv('INPUT_SRC_POSTS_TO_REPHRASE')
MAX_RETRIES = int(os.getenv('INPUT_MAX_RETRIES', 5))
max_tokens = int(os.getenv('INPUT_MAX_TOKENS'))
temperature = int(os.getenv('INPUT_TEMPERATURE'))
BATCH_SIZE = int(os.getenv('INPUT_BATCH_SIZE', 5))
useexternal_prompt = os.getenv('INPUT_USEEXTERNAL_PROMPT', "false")
spreadsheet_id = os.getenv('INPUT_SPREADSHEET_ID')

openai.api_key = os.getenv('INPUT_OPENAI_API_KEY') # "aliases.csv"

RETRIABLE_EXCEPTIONS = (openai.error.RateLimitError, openai.error.APIConnectionError, openai.error.APIError)

def generate_post(post_subject, brands, internal_links, references, keywords, prompt):
    response = None
    nb_reties = 0
    continuation_attemps = 0
    max_continuation_requests = 5
    final_content = ""
    error = None
    history = ""


    while True:
      continuation_attemps += 1
      history += prompt
      retry = 0

      try:
        print("Generating post for the prompt: ", history)
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=history,
            temperature=temperature,
            max_tokens=max_tokens,
        )
      except RETRIABLE_EXCEPTIONS as e:
        error = "A retriable error occurred: %s" % e
        print(str(e))
      except Exception as e:
        error = "An unexpected error occured. Breaking the loop. Error = : %s" % e
        print(str(e))
        return None

      if error is not None:
        print(error)
        retry += 1
        if retry > MAX_RETRIES:
          exit("No longer attempting to retry.")

        max_sleep = 2 ** retry
        sleep_seconds = random.random() * max_sleep
        print("Sleeping %f seconds and then retrying..." % sleep_seconds)
        time.sleep(sleep_seconds)

      else:
        first_choice = response.choices[0]
        print("There is no error, we continue. Response =", response)
        final_content += "{}\n\n".format(first_choice.text)
        history += "{}\n".format(first_choice.text)

        if first_choice.finish_reason == "stop":
          # print("We have a stop '{}' or we reached the continuation attempts '{}'".format(first_choice.finish_reason, continuation_attemps))
          print("We have a stop '{}'. Returning the final text".format(first_choice.finish_reason))
          # final_content += "{}\n\n\n".format(first_choice.text)
          return final_content
        else:
          # The response was not complete
          # Check if we can still ask for completion
          if continuation_attemps < max_continuation_requests:
            print("Setting prompt to asking to continue")
            prompt="continue where you stopped"
          else:
            print("Continuation attempts exhausted. Giving up and returning the content we got so far")
            return final_content


def save_post(title, silot_terms, content, dst_folder):
  post = frontmatter.loads("---\n---\n")
  post['title'] = title
  post['date'] = datetime.today().strftime('%Y-%m-%d')
  post['silot_terms'] = silot_terms
  post.content = content

#     frontmatter = """
# ---
# title: {}
# date: {}
# silot_terms: {}
# ---
# """.format(title, , silot_terms)

#     final_content = """
# {}

# {}
# """.format(frontmatter, content)

  final_content = frontmatter.dumps(post)

  filename = "{} - {}".format(datetime.today().strftime('%Y-%m-%d-%h-%M-%s'), title)

  with open(dst_folder + "/" + filename + ".md", 'w') as f:
    f.write(final_content)


def generate_post_prompt(post_subject, brands, internal_links, references, keywords):
    brands_prompt = """
    Include some carefully picked brands from this list:
    {}
    """.format(brands) if brands is not None and brands != "" else ""

    internal_linking_prompt = """
    and some carefully picked links from this list for external SEO:
    {}
    """.format(internal_links) if internal_links is not None and internal_links != "" else ""

    references_prompts = """
      Pick from references from this list and include them into the post: {}.
    """.format(references) if references is not None and references != "" else ""

    keywords_prompts = """
      Also include some carefully picked keywords from this list: {}.
    """.format(keywords) if keywords is not None and keywords != "" else ""

    return """I Want You To Act As A Content Writer Very Proficient SEO Writer Writes Fluently English.
      First Create Two Tables. First Table Should be the Outline of the Article and the Second Should be the Article.
      Bold the Heading of the Second Table using Markdown language.
      Write an outline of the article separately before writing it, at least 15 headings and subheadings (including H1, H2, H3, and H4 headings).
      Then, start writing based on that outline step by step. Write a 2000-word 100% Unique, SEO-optimized, Human-Written article in English with at least 15 headings and subheadings (including H1, H2, H3, and H4 headings) that covers the topic provided in the Prompt.
      Write The article In Your Own Words Rather Than Copying And Pasting From Other Sources.
      Consider perplexity and burstiness when creating content, ensuring high levels of both without losing specificity or context.
      Use fully detailed paragraphs that engage the reader.
      Generate programming code block and command line commands where necessary.
      Write In A Conversational Style As Written By A Human (Use An Informal Tone, Utilize Personal Pronouns, Keep It Simple, Engage The Reader, Use The Active Voice, Keep It Brief, Use Rhetorical Questions, and Incorporate Analogies And Metaphors).
      End with a conclusion paragraph and 5 unique FAQs After The Conclusion.
      this is important to Bold the Title and all headings of the article, and use appropriate headings for H tags.

      Now Write An Article On This Topic: "{}".

      {}

      {}

      {}
      """.format(post_subject, brands_prompt, internal_linking_prompt, references_prompts, keywords_prompts)

def mark_post_as_completed(channel, post_id):
  print("Marking post {} in channel {} as completed".format(post_id, channel))
  json_api_url = posts_requests_base_url + "?channel=" + channel + "&row=" + str(post_id)

  if spreadsheet_id is not None:
     json_api_url +=  "&spreadsheetid=" + spreadsheet_id
  
  r = requests.post(json_api_url)
  print("exec result =" + r.text)
  # r_json = json.loads(r.text)

  # print(r_json)
  # json_results = r_json['results']

def collect_posts_to_generate(channel):
  print("Collecting posts from channel {}, with batch size {} and useexternal_prompt = ({})".format(channel, BATCH_SIZE, useexternal_prompt))
  json_api_url = posts_requests_base_url + "?channel=" + channel
  
  if spreadsheet_id is not None:
     json_api_url +=  "&spreadsheetid=" + spreadsheet_id 

  r = requests.get(json_api_url)
  print("collect_posts_to_generate > API call, response text = " + r.text)
  r_json = json.loads(r.text)

  print(r_json)
  json_results = r_json['results']

  print("Got the json url")
  if json_results:
    for post in json_results[:BATCH_SIZE]:

      post_id = post[0]
      post_title = post[1]
      post_brands = post[2]
      post_external_urls = post[3]
      post_internal_urls = post[4]
      post_silot_terms = post[5]
      post_keywords = post[6]
      remote_prompt = post[8]
      post_references = None

      prompt = remote_prompt if useexternal_prompt == "true" else generate_post_prompt(post_title, post_brands, post_internal_urls, post_references, post_keywords)

      # post_subject, brands, internal_links, references, keywords
      if prompt.strip() != "":
        post_content = generate_post(post_title, post_brands, post_internal_urls, post_references, post_keywords, prompt)

        print("Save the post only if the result os not none")
        if post_content is not None:
          save_post(post_title, post_silot_terms, post_content, dst_generated_posts)
          mark_post_as_completed(channel, post_id)
        else:
          print("The post content is None ({}). Not saving the content of the post. ({})".format(post_content, post_title))

      else:
        print("The prompt is empty ({}). Not requesting openai".format(prompt))

def upload_title_as_postidea(channel):
  print("Uploading title to channel {}, with batch size {}".format(channel, BATCH_SIZE))

  if channel is None:
    print("No channel ({}) specified for the manually generated posts. Skipping".format(channel))
    print("You may want to add the INPUT_MANUALLY_GENERATED_POSTS_CHANNEL parameter to your call.")
  else:
      entries = [f for f in os.listdir(src_posts_to_rephrase) if os.path.isfile(os.path.join(src_posts_to_rephrase, f))]

      processed_count = 0
      for entry in entries:
          try:
              print("Processing entry", entry)
              src_entry = os.path.join(src_posts_to_rephrase, entry)
              
              post = frontmatter.load(src_entry)

              ## Do not process file if it is already uploaded
              uploaded_for_rephrasing = post["uploaded_for_rephrasing"] if "uploaded_for_rephrasing" in post else "no"

              if uploaded_for_rephrasing == "yes":
                  print("File already processed {} for post content is empty {}, skipping ...".format(uploaded_for_rephrasing, post.content[:100]))
              elif post.content == "":
                  ## Upload the post content to the spreadsheet
                  print("Uploading post in channel {} to be rephrased".format(channel))
                  post_title = post["title"] if "title" in post else ""
                  post_ref = post["ref"] if "ref" in post else ""
                  json_api_url = posts_requests_base_url + "?channel=" + channel + "&title=" + post_title + "&post_ref=" + post_ref

                  if spreadsheet_id is not None:
                     json_api_url +=  "&spreadsheetid=" + spreadsheet_id 

                  encoded_post_content = "" # base64.b64encode(bytes(post.content, 'utf-8'))
                  payload = { "text_to_rephrase" : encoded_post_content }
                  r = requests.post(json_api_url, data=payload)
                  print("exec result =" + r.text)
    
                  ## Mark file as upload for rephrasing
                  if "OK" in r.text:
                      print("The upload succeeded. Marking post as uploaded")
                      processed_count = processed_count + 1
                      post['uploaded_for_rephrasing'] = "yes"
                      print("Saving the content of the file")
                      filecontent = frontmatter.dumps(post)
            
                      print(filecontent)
        
                      with open(src_entry, 'w') as f:
                          f.write(filecontent)
                  else:
                      print("Upload failed.")
              else:
                  print("Post content is not empty. Leaving this post for rephrase content...")
          except Exception as e:
              print("Error, something unexpected occured", str(e))
          finally:
              if processed_count > BATCH_SIZE:
                  print("{} reached the Batch size {}. Breaking...".format(processed_count, BATCH_SIZE))
                  break

def upload_text_to_rephrase(channel):
  print("Uploading text to channel {}, with batch size {}".format(channel, BATCH_SIZE))

  if channel is None:
    print("No channel ({}) specified for the manually generated posts. Skipping".format(channel))
    print("You may want to add the INPUT_MANUALLY_GENERATED_POSTS_CHANNEL parameter to your call.")
  else:
      entries = [f for f in os.listdir(src_posts_to_rephrase) if os.path.isfile(os.path.join(src_posts_to_rephrase, f))]

      processed_count = 0
      for entry in entries:
          try:
              print("Processing entry", entry)
              src_entry = os.path.join(src_posts_to_rephrase, entry)
              
              post = frontmatter.load(src_entry)

              ## Do not process file if it is already uploaded
              uploaded_for_rephrasing = post["uploaded_for_rephrasing"] if "uploaded_for_rephrasing" in post else "no"

              if uploaded_for_rephrasing == "yes" or post.content == "":
                  print("File already processed {} for post content is empty {}, skipping ...".format(uploaded_for_rephrasing, post.content[:100]))
              else:
                  ## Upload the post content to the spreadsheet
                  print("Uploading post in channel {} to be rephrased".format(channel))
                  post_title = post["title"] if "title" in post else ""
                  post_ref = post["ref"] if "ref" in post else ""
                  json_api_url = posts_requests_base_url + "?channel=" + channel + "&title=" + post_title + "&post_ref=" + post_ref

                  if spreadsheet_id is not None:
                     json_api_url +=  "&spreadsheetid=" + spreadsheet_id 

                  encoded_post_content = base64.b64encode(bytes(post.content, 'utf-8'))
                  payload = { "text_to_rephrase" : encoded_post_content }
                  r = requests.post(json_api_url, data=payload)
                  print("exec result =" + r.text)
    
                  ## Mark file as upload for rephrasing
                  if "OK" in r.text:
                      print("The upload succeeded. Marking post as uploaded")
                      processed_count = processed_count + 1
                      post['uploaded_for_rephrasing'] = "yes"
                      print("Saving the content of the file")
                      filecontent = frontmatter.dumps(post)
            
                      print(filecontent)
        
                      with open(src_entry, 'w') as f:
                          f.write(filecontent)
                  else:
                      print("Upload failed.")
          except Exception as e:
              print("Error, something unexpected occured", str(e))
          finally:
              if processed_count > BATCH_SIZE:
                  print("{} reached the Batch size {}. Breaking...".format(processed_count, BATCH_SIZE))
                  break

def write_manually_generated_posts(channel):
  print("Collecting posts from channel {}, with batch size {} and useexternal_prompt = ({})".format(channel, BATCH_SIZE, useexternal_prompt))

  if channel is None:
    print("No channel ({}) specified for the manually generated posts. Skipping".format(channel))
    print("You may want to add the INPUT_MANUALLY_GENERATED_POSTS_CHANNEL parameter to your call.")
  else:
    # Collecting the posts to write down
    json_api_url = posts_requests_base_url + "?channel=" + channel + "&savemanuallygenerated=1"

    if spreadsheet_id is not None:
     json_api_url +=  "&spreadsheetid=" + spreadsheet_id 
      
    r = requests.get(json_api_url)
    print("write_manually_generated_posts > API call, response text = " + r.text)
    r_json = json.loads(r.text)

    print(r_json)
    json_results = r_json['results']

    print("Got the json url")
    if json_results:
      for post in json_results[:BATCH_SIZE]:
        post_id = post[0]
        post_title = post[1]
        post_brands = post[2]
        post_external_urls = post[3]
        post_internal_urls = post[4]
        post_silot_terms = post[5]
        post_keywords = post[6]
        remote_prompt = post[8]
        post_content = post[9]
        post_references = None

        prompt = remote_prompt if useexternal_prompt == "true" else generate_post_prompt(post_title, post_brands, post_internal_urls, post_references, post_keywords)

        print("Save the post only if the result os not none")
        if post_content is not None:
          save_post(post_title, post_silot_terms, post_content, dst_generated_posts)
          mark_post_as_completed(channel, post_id)
        else:
          print("The post content is None ({}). Not saving the content of the post. ({})".format(post_content, post_title))


# post_title = "Run docker on homelab"
# post_content = generate_post(post_title, "Home Assistant, Google Home", None, None, "docker, homelab, do it yourself")
# save_post(post_title, "my silot term", "This is a totally fake content", dst_generated_posts)
# save_post(title, silot_terms, content, dst_folder)

function_to_run_str = os.getenv('INPUT_FUNCTION_TO_RUN', 'collect_posts_to_generate')
print("Function to run = ", function_to_run_str)

if function_to_run_str == "write_manually_generated_posts":
    print("Running the write_manually_generated_posts function ")
    write_manually_generated_posts(manually_generated_posts_channel)
elif function_to_run_str == "upload_text_to_rephrase":
    print("Running the function upload_text_to_rephrase")
    upload_text_to_rephrase(manually_generated_posts_channel)
elif function_to_run_str == "upload_title_as_postidea":
    print("Running the function upload_title_as_postidea")
    upload_text_to_rephrase(manually_generated_posts_channel)
elif function_to_run_str == "collect_posts_to_generate":
    print("Running the function collect_posts_to_generate")
    collect_posts_to_generate(posts_channel)
else:
    print("Default case: Running the function collect_posts_to_generate")
    collect_posts_to_generate(posts_channel)


