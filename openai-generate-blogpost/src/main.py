import os
import openai
from datetime import datetime
import random
import time
import requests
import json

posts_channel = os.getenv('INPUT_CHANNEL') # "keyword_suggestions_merged.csv"
posts_requests_base_url = os.getenv('INPUT_POSTS_REQUESTS_BASE_URL')
dst_generated_posts = os.getenv('INPUT_DST_GENERATED_POSTS') # "internallinking_per_silot_terms.csv"
MAX_RETRIES = int(os.getenv('INPUT_MAX_RETRIES'))
max_tokens = int(os.getenv('INPUT_MAX_TOKENS'))
temperature = int(os.getenv('INPUT_TEMPERATURE'))

openai.api_key = os.getenv('INPUT_OPENAI_API_KEY') # "aliases.csv"

RETRIABLE_EXCEPTIONS = (openai.error.RateLimitError, openai.error.APIConnectionError, openai.error.APIError)

def generate_post(post_subject, brands, internal_links, references, keywords):
    response = None
    nb_reties = 0
    continuation_attemps = 0
    max_continuation_requests = 5
    final_content = ""
    error = None
    history = ""

    prompt = generate_post_prompt(post_subject, brands, internal_links, references, keywords)

    while True:
      continuation_attemps += 1
      history += prompt

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


def save_post(title, content, dst_folder):
    frontmatter = """
    ---
    title: {}
    date: {}
    ---
    """.format(title, datetime.today().strftime('%Y-%m-%d'))

    final_content = """
    {}

    {}
    """.format(frontmatter, content)

    filename = "{} - {}".format(datetime.today().strftime('%Y-%m-%d-%h-%M-%s'), title)

    with open(dst_folder + "/" + filename + ".md", 'w') as f:
      f.write(final_content)


def generate_post_prompt(post_subject, brands, internal_links, references, keywords):
    brands_prompt = """
    Include some of these brands: 
    {}
    """.format(brands) if brands is not None else ""

    internal_linking_prompt = """
    and these links for external SEO: 
    {}
    """.format(internal_links) if internal_links is not None else ""

    references_prompts = """
      Include references like: {}.
    """.format(references) if references is not None else ""
    
    keywords_prompts = """
      Also include these keywords: {}.
    """.format(keywords) if keywords is not None else ""

    return """I Want You To Act As A Content Writer Very Proficient SEO Writer Writes Fluently English. 
      First Create Two Tables. First Table Should be the Outline of the Article and the Second Should be the Article. 
      Bold the Heading of the Second Table using Markdown language. 
      Write an outline of the article separately before writing it, at least 15 headings and subheadings (including H1, H2, H3, and H4 headings). 
      Then, start writing based on that outline step by step. Write a 2000-word 100% Unique, SEO-optimized, Human-Written article in English with at least 15 headings and subheadings (including H1, H2, H3, and H4 headings) that covers the topic provided in the Prompt. 
      Write The article In Your Own Words Rather Than Copying And Pasting From Other Sources. 
      Consider perplexity and burstiness when creating content, ensuring high levels of both without losing specificity or context. 
      Use fully detailed paragraphs that engage the reader. 
      Write In A Conversational Style As Written By A Human (Use An Informal Tone, Utilize Personal Pronouns, Keep It Simple, Engage The Reader, Use The Active Voice, Keep It Brief, Use Rhetorical Questions, and Incorporate Analogies And Metaphors).  
      End with a conclusion paragraph and 5 unique FAQs After The Conclusion. 
      this is important to Bold the Title and all headings of the article, and use appropriate headings for H tags.

      Now Write An Article On This Topic: "{}". 
      
      {}

      {}

      {}      
      """.format(post_subject, brands_prompt, internal_linking_prompt, references_prompts, keywords_prompts)

def mark_post_as_completed(channel, post_id):
  json_api_url = posts_requests_base_url + "?channel=" + channel + "&row=" + str(post_id)
  r = requests.post(json_api_url)
  print("exec result =" + r.text)
  # r_json = json.loads(r.text)

  # print(r_json)
  # json_results = r_json['results']

def collect_posts_to_generate(channel):
  json_api_url = posts_requests_base_url + "?channel=" + channel
  r = requests.get(json_api_url)
  print("collect_posts_to_generate > API call, response text = " + r.text)
  r_json = json.loads(r.text)

  print(r_json)
  json_results = r_json['results']

  print("Got the json url")
  if json_results:
    for post in json_results:
      # [
      # 1,
      # "drone pilot license",
      # "\n\nDJI, \nAlta, \nParrot, \nYuneec, \nBrink, \nDedrone, \ndrone sense, \nairobotics, \naerovironment, \nair hogs, \nfreefly, \nsensefly, \nuvifly, \nhubsan, \naerialtronics, \nehang, \ndelair, \ninsitu, \nskydio, \nautel robotics, \nkespry\n\n",
      # "\n\nhttps://www.dji.com/fr\nhttps://www.parrot.com/fr\nhttps://freeflysystems.com/alta-x\nhttps://us.yuneec.com/",
      # "\n\nhttps://eagles-techs.com/why-pix4d-react-is-the-best-and-most-affordable-drone-mapping-software-for-public-safety-operations/\nhttps://eagles-techs.com/best-drone-app-and-website-for-checking-wind-speed-and-direction/\nhttps://eagles-techs.com/little-known-facts-about-drone-insurance-that-you-may-not-be-aware-of/\nhttps://eagles-techs.com/how-can-i-view-pix4d-maps-in-vr/\n\n",
      # "",
      # "\"drone pilot, drone pilot speed, drone pilot license, drone range, affordable drone, safety\"\n\n",
      # "todo"
      # ]
      post_id = post[0]
      post_title = post[1]
      post_brands = post[2]
      post_external_urls = post[3]
      post_internal_urls = post[4]
      post_silot_terms = post[5]
      post_keywords = post[6]
      post_references = None

      # post_subject, brands, internal_links, references, keywords
      post_content = generate_post(post_title, post_brands, post_internal_urls, post_references, post_keywords)
      save_post(post_title, post_content, dst_generated_posts)
      mark_post_as_completed(channel, post_id)

# post_title = "Run docker on homelab"
# post_content = generate_post(post_title, "Home Assistant, Google Home", None, None, "docker, homelab, do it yourself")
# save_post(post_title, post_content, dst_generated_posts)

collect_posts_to_generate(posts_channel)
# mark_post_as_completed(posts_channel, 3)
