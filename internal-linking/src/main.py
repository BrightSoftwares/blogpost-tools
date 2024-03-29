import pandas as pd
import numpy as np
import os, re, sys
import frontmatter
import yaml
import datetime
from generate_short_keywords import generate_short_keywords, generate_anchor_text_to_post_file, generate_internallinking_per_silot_terms_file, generate_silot_terms_file

# charList = " " + string.ascii_lowercase + string.digits

src_folder_toscan = os.getenv('INPUT_SRC_FOLDER_TOSCAN')
dst_folder_tosaveresults = os.getenv('INPUT_DST_FOLDER_TOSAVERESULTS')
internal_link_text_file = os.getenv('INPUT_INTERNAL_LINK_TEXT_FILE')
anchor_text_to_post = os.getenv('INPUT_ANCHOR_TEXT_TO_POST')
aliases_yml = os.getenv('INPUT_ALIASES_YML_FILE')
aliases_csv_file = os.getenv('INPUT_ALIASES_CSV_FILE')
lang = os.getenv('INPUT_LANG')
aliases_new_csv_file = os.getenv('INPUT_ALIASES_NEW_CSV_FILE')
aliases_yml_filtered = os.getenv('INPUT_ALIASESFILTERED_YML_FILE')
dry_run = os.getenv('INPUT_DRY_RUN', False)

page_titles = []
page_aliases = {}
generated_aliases = {}
obsidian_home = src_folder_toscan
wikipedia_mode = True
paragraph_mode = False
yaml_mode = True
regenerate_aliases = False
clear_links = False

print("Processing markdown files")


# # Try to load the used urls. If not found, create an empty one
# def get_feedblogposturlused_df(file_url):
#   try:
#     return pd.read_csv(file_url)
#   except:
#     return pd.DataFrame(columns=['Suggestion', 'silot_terms', 'blogpost_title', 'blogpost_link', 'category'])

def replace_with_tokens(content, pattern, replacement_counter):
  tokens_array = []
  # Find the code blocks
  # pattern = re.compile(r"```.*?```", re.DOTALL)
  matches = pattern.findall(content)
  # print(matches)

  # Replace code blocks with tokens
  # replacement_counter = 10000
  for amatch in matches:
    try:
      # print("Processing match =", amatch)
      codeblock_text = amatch
      replacement_token = "##@@{}@@##".format(replacement_counter)
      content = content.replace(codeblock_text, replacement_token)
      tokens_array.append([codeblock_text, replacement_token])
      replacement_counter = replacement_counter + 1
    except Exception as e:
      print("replace_with_tokens > Error: ", str(e))

  # return the array where we have the tokens and the content
  return tokens_array, content


def extract_headers(data_str):
  print("Extract headers")
  return extract_data_with_regex(data_str, "^#+\s(.*)$")

def extract_codeblocks(data_str):
  print("Extract code blocks")
  return extract_data_with_regex(data_str, "`{3}([\w]*)\n([\S\s]+?)\n`{3}")

def extract_inline_codeblocks(data_str):
  print("Extract inline code blocks")
  return extract_data_with_regex(data_str, "`{3}([\w]*)\n([\S\s]+?)\n`{3}")

def extract_wikilinks(data_str):
  print("Extract wikilinks")
  #return extract_data_with_regex(data_str, "\[\[(.+?)(\|.+)?\]\]")
  return extract_data_with_regex(data_str, "\[\[(.*?)(\|(.*?))?\]\]")

def replace_codeblock_with_tokens(content):
  print(">>> Replacing codeblocks")
  replacement_counter = 10000
  pattern = re.compile(r"```.*?```", re.DOTALL)

  return replace_with_tokens(content, pattern, replacement_counter)

def replace_title_with_tokens(content):
  print(">>> Replacing titles")
  replacement_counter = 30000
  pattern = re.compile(r"^#+\s.*$", re.MULTILINE)

  return replace_with_tokens(content, pattern, replacement_counter)

def replace_link_with_tokens(content):
  print(">>> Replacing links")
  replacement_counter = 40000
  # pattern = re.compile(r"\[([^\[]+)\](\(.*\))", re.DOTALL)
  pattern = re.compile(r"\[[^\[]+\]\(.*\)", re.MULTILINE)

  return replace_with_tokens(content, pattern, replacement_counter)

def replace_image_with_tokens(content):
  print(">>> Replacing images")
  replacement_counter = 50000
  # pattern = re.compile(r'!\[[^\]]*\]\((.*?)\s*("(?:.*[^"])")?\s*\)', re.MULTILINE)
  # pattern = re.compile(r'!\[[^\]]*\]\(.*?\s*("(?:.*[^"])")?\s*\)', re.MULTILINE)
  pattern = re.compile(r'!\[.*?\]\(.*?\)', re.MULTILINE)

  return replace_with_tokens(content, pattern, replacement_counter)

def replace_tokens_with_codeblocks(content, tokens):
  print(">>> Replacing back")
  for token in tokens:
    try:
      # print("Replacing back token {} with token {}".format(token[1], token[0]))
      content = content.replace(token[1], token[0])
    except Exception as e:
      print("replace_tokens_with_codeblocks > Error while replacing back token. = ", str(e))

  # return the array where we have the tokens and the content
  return content

def replace_all_with_tokens(initial_content):
  # Replace text with tokens
  tokens_array_codeblocks, content_codeblock = replace_codeblock_with_tokens(initial_content)
  tokens_array_titles, content_titles = replace_title_with_tokens(content_codeblock)
  tokens_array_images, content_images = replace_image_with_tokens(content_titles)
  tokens_array_links, content_links = replace_link_with_tokens(content_images)

  return tokens_array_codeblocks, tokens_array_titles, tokens_array_images, tokens_array_links, content_links # Return the final content


def replace_back_all(new_content, tokens_array_codeblocks, tokens_array_images, tokens_array_links, tokens_array_titles):
  content_codeblocks_replaced = replace_tokens_with_codeblocks(new_content, tokens_array_codeblocks)
  content_titles_replaced = replace_tokens_with_codeblocks(content_codeblocks_replaced, tokens_array_titles)
  content_images_replaced = replace_tokens_with_codeblocks(content_titles_replaced, tokens_array_images)
  content_links_replaced = replace_tokens_with_codeblocks(content_images_replaced, tokens_array_links)

  return content_links_replaced


def generate_aliases_ymls(df, aliases_yml, aliases_yml_filtered):
  data = {}

  # Transform the df into an array of path and link text
  for current_post_index, current_post in df.iterrows():
    header_key = "[[{}]]".format(current_post.dst_file)

    # If there is data already for this key, we append
    # Else we create a new one
    print("generate_aliases_ymls > processing path = {} and link text = {}".format(header_key, current_post.link_text))

    # Not adding empty link texts
    if current_post.link_text == "":
      continue

    if header_key not in data.keys():
      data[header_key] = [current_post.link_text]
    else:
      # We append only if the item is not in the list already
      data[header_key].append(current_post.link_text) if current_post.link_text not in data[header_key] else data[header_key]


  # Writing a new yaml file with the modifications
  yaml.default_flow_style=False
  yaml.default_style=False

  with open(aliases_yml, "w") as new_file:
    yaml.dump(data, new_file, default_style=False, default_flow_style=False)

  # THIS IS A KIND OF HACK - PyYAML generates a quote arround [[]]
  # Replace the '[[ with [[
  # Replace the ]]' with ]]
  # Read in the file
  with open(aliases_yml, 'r') as file :
    filedata = file.read()

  # Replace the target string
  filedata = filedata.replace('\'[[', '[[')
  filedata = filedata.replace(']]\'', ']]')

  # Write the file out again
  with open(aliases_yml, 'w') as file:
    file.write(filedata)

def extract_data_with_regex(data_str, regex):
  
  results = {}
  matches = re.finditer(regex, data_str, re.MULTILINE)

  for matchNum, match in enumerate(matches, start=1):
      
      # print("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
      
      for groupNum in range(0, len(match.groups())):
          groupNum = groupNum + 1
          
          # print("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))
          
          current_key = "{}_{}".format(matchNum, groupNum)
          current_value = match.group(groupNum)
          results.update({current_key: current_value})
  return results


def md2df_by_silotterms(folder_to_scan, dst_folder_tosaveresults):
  silot_terms_df = pd.DataFrame(columns=['silot_terms', 'title', 'path', 'cornerstone', 'categories'])
  entries = [f for f in os.listdir(folder_to_scan) if os.path.isfile(os.path.join(folder_to_scan, f))] # os.listdir(folder_to_scan)

  for entry in entries:
    try:
      print("Processing entry", entry)
      post = frontmatter.load(folder_to_scan + "/" + entry)
      silot_terms = post['silot_terms'] if 'silot_terms' in post else "unknown"
      cornerstone = post['cornerstone'] if 'cornerstone' in post else "no"
      title = post['title'] if 'title' in post else None
      categories = post['categories'] if 'categories' in post else ''
      silot_terms_df.loc[len(silot_terms_df)] = [silot_terms, title, entry, cornerstone, categories]
    except Exception as e:
      print("Error, something unexpected occured", str(e))

  print("Save the result into a csv file")
  silot_terms_df.to_csv("{}/silot_terms.csv".format(dst_folder_tosaveresults), index=False)

  # pvtable = pd.pivot_table(silot_terms_df, values='title', index=['silot_terms'], columns=['cornerstone'], aggfunc=np.count_nonzero)
  # print("Save the pivot table in a csv format")
  # pvtable.to_csv("{}/silot_terms_by_cornerstone.csv".format(dst_folder_tosaveresults), index=False)
  # return pvtable

  return silot_terms_df


def generate_full_link_and_text(post_title, post_link, anchor_df, link_text_df):
  # Get a random text from the link text dataframe
  sample_text = link_text_df.sample().head()
  #print("generate_full_link_and_text > sample =", sample_text)
  full_link_and_text = sample_text['internal_link_text'].iloc[0]
  # print("generate_full_link_and_text > full_link_and_text =", full_link_and_text)

  # Get the corresponding anchor text
  # If none if found, use the post title
  regex = ".*{}.*".format(post_link[11:-3])
  # regex = ".*solutions.*"
  #print("Filtering anchor with the regex", regex)
  eligible_anchors = anchor_df[anchor_df.path.str.match(regex, na=False)]
  #print("Eligible anchors =", eligible_anchors)
  if eligible_anchors.empty:
    anchor_text = post_title
  else:
    anchor_text = eligible_anchors.sample().head()['link_text'].iloc[0]

  # Replace the tokens
  full_link_and_text = full_link_and_text.replace("[topic]", post_title.lower()).replace("[[link to blog post]]", "[[{}|{}]]".format(post_link, anchor_text))
  # print("full link and text for post '{}' with full link '{}' is '{}'".format(post_title, post_link, full_link_and_text))
  return anchor_text, post_link, full_link_and_text


def generate_internal_linking_requirements(silot_terms_df, folder_to_scan, dst_folder_tosaveresults, anchor_df, link_text_df):
  il_requirements = pd.DataFrame(columns=['silot_terms', 'src_file', 'dst_file', 'src_is_cornerstone', 'link_exist', 'link_text', 'full_link', 'full_link_and_text'])

  print("Ignoring unknown posts with unknown silot_terms")
  st_df = silot_terms_df[silot_terms_df.silot_terms != "unknown"]

  for term in st_df.silot_terms.unique():
    print("Generate requirements for term '{}'".format(term))
    try:
      related_posts_df = st_df[st_df.silot_terms == term]
      print("Related destination files ", related_posts_df["path"].to_string())
  
      print("Checking the linking for term '{}' with df '{}'".format(term, related_posts_df))
      for current_post_index, current_post in related_posts_df.iterrows():
        print("  Load the post {} ({}) and check if there is a link to the others".format(current_post.title, current_post.path))

        try:
          post = frontmatter.load(folder_to_scan + "/" + current_post.path)
          silot_terms = post['silot_terms'] if 'silot_terms' in post else "unknown"
          cornerstone = post['cornerstone'] if 'cornerstone' in post else "no"
    
          print("  Extract the wikilinks in this post")
          post_wklinks = extract_wikilinks(post.content)
          print("  Found links: ", post_wklinks)
    
          # If the post is cornerstone, we only need to check that 
          # there is 1 link to the rest of the post in the same silot term
          # Else, we need to check that every post has a link to the others
          # in the same silot term
          # TODO - Compute the number of links from cornerstone links to the other posts
          # to make sure that the cornerstone post has only one link
    
          print("  Checking whether this post has link to all the other posts")
          # Now we check if the current value matches the path of other posts in the same silot term
          for other_post_index, other_post in related_posts_df.iterrows():

            try:
    
              # We avoid comparing the src post with itself
              if current_post.path == other_post.path:
                print("Not comparing a post with itself = {} <--> {}".format(current_post.path, other_post.path))
              else:
                has_link_to_dst_post = False
                link_text = ""
                full_link_and_text = ""
                full_link = "[[{}|{}]]".format(other_post.path, other_post.title)
      
                # print("    Check if the src post {} has links to {} in the wikilink list {}".format(current_post.path, other_post.path, post_wklinks))
                for post_wklinks_key in post_wklinks.keys():
                  post_wklinks_value = post_wklinks[post_wklinks_key]
      
                  current_other_post_path = other_post.path[:-3] if other_post.path.endswith(".md") else other_post.path
      
                  print("Is this post {} already linked to {} in this wikilink {} ? Test = {} in {} ?".format(current_post.path, other_post.path, post_wklinks_value, current_other_post_path, post_wklinks_value))
      
                  if current_other_post_path in post_wklinks_value:
                    print("     We found a link from {} to {}. Post key = {} and value is {}".format(current_post.path, other_post.path, post_wklinks_key, post_wklinks_value))
                    has_link_to_dst_post = True
                    link_text = post_wklinks["{}_2".format(post_wklinks_key.split("_")[0])] # 1_2
                    link_text = link_text[1:] if link_text.startswith('|') else link_text
                    # full_link = "[[{}|{}]]".format(post_wklinks_value ,link_text)
                  else:
                    print("     No correspondance found in the link.")
                    
                print("Checking if we need to generate another full link and text")
                
                # il_requirements = internal linking requirements : used to gather the links that are missing and must be created.
                # current_il_requirements = the links from the src file to the dest file in the silot term
                # Used to check if previously we have detected that there must be a link between the src and dest file.
                
                current_il_requirements = il_requirements.loc[(il_requirements['src_file'] == current_post.path) & (il_requirements['dst_file'] == other_post.path) & (il_requirements['silot_terms'] == silot_terms)]
                print("Current internal linking requirements for dst_file (did we detected previously that a link must be created?) ", current_il_requirements)
                
                # If there is no existing link between src file and dest file AND we did not record that we need to create a link between these two.
                # The current_il_requirements.empty makes sure that we don't create this requirements twice.
                if not has_link_to_dst_post and current_il_requirements.empty:
                  print("       No link between the two files and no previously detected that we need to create one")
                  _, post_link, full_link_and_text = generate_full_link_and_text(other_post.title, other_post.path, anchor_df, link_text_df)
                else:
                  print("       Either a link has been found ({}) or we already planed to create it ({})".format(has_link_to_dst_post, not current_il_requirements.empty))
      
                il_requirements.loc[len(il_requirements)] = [silot_terms, current_post.path, other_post.path, cornerstone, has_link_to_dst_post, link_text, full_link, full_link_and_text]
            except ValueError as e3:
              print("An error 3 occured for this other post", other_post.path)
              print("Error 3 = ", e3)
        except ValueError as e2:
          print("An error occured while processing the file", current_post.path)
          print("Error 2 = ", e2)
          
    except ValueError as e1:
      print("Error while processing the term ", term)
      print("Error = ", e1)
    
  # print("Sort the df before saving it")
  # il_requirements = il_requirements.sort_values(['silot_terms', 'link_exist'], ascending = [False, True])
  # print("Saving the analysis result")
  # il_requirements.to_csv("{}/internallinking_per_silot_terms.csv".format(dst_folder_tosaveresults), index=False)

  # Save also a aliases.yml file for automatic internal linking
  # generate_aliases_ymls(il_requirements, aliases_yml, aliases_yml_filtered)

  return il_requirements



def link_title(title, txt):
    updated_txt = txt
    # find instances of the title where it's not surrounded by [], | or other letters
    matches = re.finditer('(?<!([\[\w\|]))' + re.escape(title.lower()) + '(?!([\|\]\w]))', txt.lower())
    offset = 0 # track the offset of our matches (start index) due to document modifications
    
    for m in matches:
        # get the original text to link
        txt_to_link = updated_txt[m.start() + offset:m.end() + offset]
        
        # where is the next ]]?
        next_closing_index = updated_txt.find("]]", m.end() + offset)
        # where is the next [[?
        next_opening_index = updated_txt.find("[[", m.end() + offset)   
        
        # only proceed to link if our text is not already enclosed in a link
        # don't link if there's a ]] ahead, but no [[ (can happen with first few links)
        if not (next_opening_index == -1 and next_closing_index > -1):
            # proceed to link if no [[ or ]] ahead (first link) or [[ appears before ]]
            if (next_opening_index == -1 and next_closing_index == -1) or (next_opening_index < next_closing_index):
                updated_title = title
                # handle aliases
                if title in page_aliases: updated_title = page_aliases[title]
                # handle the display text if it doesn't match the page title
                if txt_to_link != updated_title: updated_title += '|' + txt_to_link
                # create the link and update our text
                updated_txt = updated_txt[:m.start() + offset] + '[[' + updated_title + ']]' + updated_txt[m.end() + offset:]
                # change our offset due to modifications to the document
                offset = offset + (len(updated_title) + 4 - len(txt_to_link))  # pairs of double brackets adds 4 chars
                # if wikipedia mode is on, return after first link is created
                if wikipedia_mode: return updated_txt
            
    return updated_txt


def link_title2(title, txt, page_aliases):
    # title = the link_text we will use as text anchor
    # txt = the full body of the post, where we will look for the anchor text
    # page_aliases = a dict of link_text and dst_file
    updated_txt = txt
    # find instances of the title where it's not surrounded by [], | or other letters
    matches = re.finditer('(?<!([\[\w\|]))' + re.escape(title.lower()) + '(?!([\|\]\w]))', txt.lower())
    offset = 0 # track the offset of our matches (start index) due to document modifications
    
    for m in matches:
        # get the original text to link
        txt_to_link = updated_txt[m.start() + offset:m.end() + offset]
        
        # where is the next ]]?
        next_closing_index = updated_txt.find("]]", m.end() + offset)
        # where is the next [[?
        next_opening_index = updated_txt.find("[[", m.end() + offset)   
        
        # only proceed to link if our text is not already enclosed in a link
        # don't link if there's a ]] ahead, but no [[ (can happen with first few links)
        if not (next_opening_index == -1 and next_closing_index > -1):
            # proceed to link if no [[ or ]] ahead (first link) or [[ appears before ]]
            if (next_opening_index == -1 and next_closing_index == -1) or (next_opening_index < next_closing_index):
                updated_title = title
                # handle aliases
                if title in page_aliases: updated_title = page_aliases[title]
                # handle the display text if it doesn't match the page title
                if txt_to_link != updated_title: updated_title += '|' + txt_to_link
                # create the link and update our text
                updated_txt = updated_txt[:m.start() + offset] + '[[' + updated_title + ']]' + updated_txt[m.end() + offset:]
                # change our offset due to modifications to the document
                offset = offset + (len(updated_title) + 4 - len(txt_to_link))  # pairs of double brackets adds 4 chars
                # if wikipedia mode is on, return after first link is created
                if wikipedia_mode: return updated_txt
            
    return updated_txt
  
  
def link_title3(link_text, content, dst_file):
    # title = the link_text we will use as text anchor
    # txt = the full body of the post, where we will look for the anchor text
    # page_aliases = a dict of link_text and dst_file

    # Replace text with tokens
    tokens_array_codeblocks, content_codeblock = replace_codeblock_with_tokens(content)
    tokens_array_titles, content_titles = replace_title_with_tokens(content_codeblock)
    tokens_array_images, content_images = replace_image_with_tokens(content_titles)
    tokens_array_links, content_links = replace_link_with_tokens(content_images)

    updated_txt = content_links
    # find instances of the title where it's not surrounded by [], | or other letters
    matches = re.finditer('(?<!([\[\w\|]))' + re.escape(link_text.lower()) + '(?!([\|\]\w]))', content_links.lower())
    offset = 0 # track the offset of our matches (start index) due to document modifications
    
    for m in matches:
        # get the original text to link
        txt_to_link = updated_txt[m.start() + offset:m.end() + offset]
        
        # where is the next ]]?
        next_closing_index = updated_txt.find("]]", m.end() + offset)
        # where is the next [[?
        next_opening_index = updated_txt.find("[[", m.end() + offset)   
        
        # only proceed to link if our text is not already enclosed in a link
        # don't link if there's a ]] ahead, but no [[ (can happen with first few links)
        if not (next_opening_index == -1 and next_closing_index > -1):
            # proceed to link if no [[ or ]] ahead (first link) or [[ appears before ]]
            if (next_opening_index == -1 and next_closing_index == -1) or (next_opening_index < next_closing_index):
                updated_title = link_text
                # handle aliases
                updated_title = dst_file
                # handle the display text if it doesn't match the page title
                if txt_to_link != updated_title: updated_title += '|' + txt_to_link
                # create the link and update our text
                updated_txt = updated_txt[:m.start() + offset] + '[[' + updated_title + ']]' + updated_txt[m.end() + offset:]
                # change our offset due to modifications to the document
                offset = offset + (len(updated_title) + 4 - len(txt_to_link))  # pairs of double brackets adds 4 chars
                # if wikipedia mode is on, return after first link is created
                if wikipedia_mode: return updated_txt
            

    # Replace tokens with text
    content_codeblocks_replaced = replace_tokens_with_codeblocks(updated_txt, tokens_array_codeblocks)
    content_images_replaced = replace_tokens_with_codeblocks(content_codeblocks_replaced, tokens_array_images)
    content_links_replaced = replace_tokens_with_codeblocks(content_images_replaced, tokens_array_links)
    content_titles_replaced = replace_tokens_with_codeblocks(content_links_replaced, tokens_array_titles)

    return content_titles_replaced
  
  
def link_title4(link_regex, content, dst_file):

    updated_txt = content
    anchor_text = "unknown"
    link_found = False
    
    # Remove the .md from the dst_file if there is one
    if dst_file.endswith(".md"):
      dst_file = dst_file[:-3]
      print("dst_file without .md extension = ", dst_file)
      
    # find instances of the title where it's not surrounded by [], | or other letters
    matches = re.finditer(link_regex, content.lower())
    offset = 0 # track the offset of our matches (start index) due to document modifications
    
    for m in matches:
      try:
        # get the original text to link
        txt_to_link = updated_txt[m.start() + offset:m.end() + offset]
        
        # where is the next ]]?
        next_closing_index = updated_txt.find("]]", m.end() + offset)
        # where is the next [[?
        next_opening_index = updated_txt.find("[[", m.end() + offset)   
        
        # only proceed to link if our text is not already enclosed in a link
        # don't link if there's a ]] ahead, but no [[ (can happen with first few links)
        if not (next_opening_index == -1 and next_closing_index > -1):
            # proceed to link if no [[ or ]] ahead (first link) or [[ appears before ]]
            if (next_opening_index == -1 and next_closing_index == -1) or (next_opening_index < next_closing_index):
                print(">>> link_title4 > We found a match = {} in file {}".format(txt_to_link, dst_file))
                # updated_title = txt_to_link
                # handle aliases
                updated_title = dst_file

                # handle the display text if it doesn't match the page title
                if txt_to_link != updated_title: updated_title += '|' + txt_to_link

                # create the link and update our text
                updated_txt = updated_txt[:m.start() + offset] + '[[' + updated_title + ']]' + updated_txt[m.end() + offset:]

                # change our offset due to modifications to the document
                offset = offset + (len(updated_title) + 4 - len(txt_to_link))  # pairs of double brackets adds 4 chars

                # # if wikipedia mode is on, return after first link is created
                # if wikipedia_mode: return updated_txt
                # print("5")

                # Mark this match as good and return the data
                anchor_text = txt_to_link
                link_found = True

                break
      except Exception as e:
        print("link_title4 > Error : ", str(e))

    return updated_txt, anchor_text, link_found


def link_content(content):
    # make a copy of our content and lowercase it for search purposes
    content_low = content.lower()

    # iterate through our page titles
    for page_title in page_titles:
        # if we have a case-insenitive title match...
        if page_title.lower() in content_low:        
            updated_txt = link_title(page_title, content)            
            # we can tell whether we've matched the term if
            # the linking process changed the updated text length
            if len(updated_txt) != len(content):
                content = updated_txt
                print("linked %s" % page_title)

            # lowercase our updated text for the next round of search
            content_low = content.lower()        
    
    return content


def link_content2(content, page_titles, page_aliases):
    # make a copy of our content and lowercase it for search purposes
    generated_links = False
    content_low = content.lower()

    # iterate through our page titles
    for page_title in page_titles:
        # if we have a case-insenitive title match...
        if page_title.lower() in content_low:        
            updated_txt = link_title2(page_title, content, page_aliases)            
            # we can tell whether we've matched the term if
            # the linking process changed the updated text length
            if len(updated_txt) != len(content):
                content = updated_txt
                generated_links = True
                print("linked = %s" % (page_title))
                # print("Linked text =", updated_txt)

            # lowercase our updated text for the next round of search
            content_low = content.lower() 
        
        # We stop linking when 1 link is found
        if generated_links:
          break
    
    return generated_links, page_title, content
  

def link_content3(folder_to_scan, src_file, dst_file, aliases_df):
    updated_txt = ""
    anchor_text = ""
    link_found = False
    # Get all the aliases that corresponds to the destination file
    dst_aliases_df = aliases_df.loc[aliases_df['dst_file'] == dst_file]
    dst_aliases_df = dst_aliases_df.drop_duplicates() # Removing duplicates
    # Shuffle the data to inject randomness
    dst_aliases_df = dst_aliases_df.sample(frac = 1)

    
    ## -- Initial solution --
    # # iterate through our page titles
    # for current_item_index, current_item in dst_aliases_df.iterrows():
    #   # Attempt to link the src content to the destination using one of the aliases
    #   #print("Processing src = {} and dst = {}".format(src_file, dst_file))
    #   post = frontmatter.load(folder_to_scan + "/" + src_file)
    #   updated_txt = link_title3(current_item.link_text, post.content, dst_file)
      
    #   # If we find a match we stop looking for other links, for this dst file
    #   if len(updated_txt) != len(post.content):
    #     print("linked = %s" % (current_item.link_text))
    #     anchor_text = current_item.link_text
    #     link_found = True
    #     break
    ## -- End of initial solution --
    
    ## -- Alternate solution to improve performances --
    # Turn the aliases into a regex
    aliases_list = dst_aliases_df["link_text"].values.tolist()
    print(aliases_list)
    if len(aliases_list) > 0: # No need to prepare the regex if there is nothing to search for
      aliases_list = ["\\b{}\\b".format(i) for i in aliases_list]
      aliases_regex_str = "({})".format("|".join(aliases_list))
      print("link_content3 > Regex str from aliases = ", aliases_regex_str)

      # Find the matches for the aliases_regex_str in the content
      post = frontmatter.load(folder_to_scan + "/" + src_file)

      # protect data by replacing them with tokens
      tokens_array_codeblocks, content_codeblock = replace_codeblock_with_tokens(post.content)
      tokens_array_titles, content_titles = replace_title_with_tokens(content_codeblock)
      tokens_array_images, content_images = replace_image_with_tokens(content_titles)
      tokens_array_links, content_links = replace_link_with_tokens(content_images)

      # search and generate the internal link
      print("link_content3 > Searching the aliases in title")
      updated_txt, anchor_text, link_found = link_title4(aliases_regex_str, content_links, dst_file)
      print(" link_content3 > Done. Link found ? =", link_found)

      if len(updated_txt) != len(post.content):
        link_found = True

      # restore data by replacing back the tokens
      content_codeblocks_replaced = replace_tokens_with_codeblocks(updated_txt, tokens_array_codeblocks)
      content_images_replaced = replace_tokens_with_codeblocks(content_codeblocks_replaced, tokens_array_images)
      content_links_replaced = replace_tokens_with_codeblocks(content_images_replaced, tokens_array_links)
      content_titles_replaced = replace_tokens_with_codeblocks(content_links_replaced, tokens_array_titles)
      

    else:
      print("link_content3 > Nothing to link for this dst_file")
    
    #print("Nothing found in src file {}. Returning False and None, None".format(src_file))
    return link_found, anchor_text, updated_txt

def link_content4(folder_to_scan, src_content_replaced_with_tokens, dst_file, aliases_df):
    updated_txt = ""
    anchor_text = ""
    link_found = False
    # Get all the aliases that corresponds to the destination file
    dst_aliases_df = aliases_df.loc[aliases_df['dst_file'] == dst_file]
    dst_aliases_df = dst_aliases_df.drop_duplicates() # Removing duplicates
    # Shuffle the data to inject randomness
    dst_aliases_df = dst_aliases_df.sample(frac = 1)
    
    ## -- Alternate solution to improve performances --
    # Turn the aliases into a regex
    aliases_list = dst_aliases_df["link_text"].values.tolist()
    # print(aliases_list)
    if len(aliases_list) > 0: # No need to prepare the regex if there is nothing to search for
      aliases_list = ["\\b{}\\b".format(i) for i in aliases_list]
      aliases_regex_str = "({})".format("|".join(aliases_list))
      print("link_content4 > Regex str from aliases = ", aliases_regex_str)

      # # Find the matches for the aliases_regex_str in the content
      # post = frontmatter.load(folder_to_scan + "/" + src_file)

      # # protect data by replacing them with tokens
      # tokens_array_codeblocks, content_codeblock = replace_codeblock_with_tokens(post.content)
      # tokens_array_images, content_images = replace_image_with_tokens(content_codeblock)
      # tokens_array_links, content_links = replace_link_with_tokens(content_images)
      # tokens_array_titles, content_titles = replace_title_with_tokens(content_links)

      # search and generate the internal link
      updated_txt, anchor_text, link_found = link_title4(aliases_regex_str, src_content_replaced_with_tokens, dst_file)

      # if len(updated_txt) != len(src_content_replaced_with_tokens):
      #   link_found = True

      # # restore data by replacing back the tokens
      # content_codeblocks_replaced = replace_tokens_with_codeblocks(updated_txt, tokens_array_codeblocks)
      # content_images_replaced = replace_tokens_with_codeblocks(content_codeblocks_replaced, tokens_array_images)
      # content_links_replaced = replace_tokens_with_codeblocks(content_images_replaced, tokens_array_links)
      # content_titles_replaced = replace_tokens_with_codeblocks(content_links_replaced, tokens_array_titles)
      

    else:
      print("link_content4 > Nothing to link for this dst_file")
    
    #print("Nothing found in src file {}. Returning False and None, None".format(src_file))
    return link_found, anchor_text, updated_txt


def unlink_text(txt):
    # keep track of the location in our text as we process it
    index = 0

    while True:
        # where is the next [[?
        next_opening_index = txt.find("[[", index)
        # where is the next ]]?
        next_closing_index = txt.find("]]", index)
        
        # if we don't find matching brackets, break
        match_exists = (next_opening_index > -1) and (next_closing_index > -1)
        if not match_exists: break
        
        # if there is a match, but there is an exclamation point 
        # (embed syntax) in front, move our index ahead and continue
        if (next_opening_index > 0 and txt[next_opening_index - 1] == '!'):
            index = next_closing_index + 2
            continue
        
        # grab the text between the square brackets
        txt_between = txt[next_opening_index + 2:next_closing_index]
        index = next_closing_index - 2 # move index to end of matched brackets
        
        # handle links with different display text
        if ('|' in txt_between):
            txt_remaining = txt_between[txt_between.find("|") + 1:] 
            # adjust our index to handle the text being removed
            index = index - (len(txt_between) - len(txt_remaining))
            txt_between = txt_remaining
        
        # update our text
        txt = txt[0:next_opening_index] + txt_between + txt[next_closing_index + 2:]
    
    return txt


def run_obs_linkr():
  # main entry point
  # validate obsidian vault location
  # if len(sys.argv) > 1:
  #     obsidian_home = sys.argv[1]
  #     if not os.path.isdir(obsidian_home):
  #         print('folder specified is not valid')
  #         exit()
      
  #     # check for additional flags
  #     if len(sys.argv) > 2:
  #         for arg_index in range(2, len(sys.argv)):
  #             flag = sys.argv[arg_index]

  #             if flag == "-w":
  #                 wikipedia_mode = True
  #             elif flag == "-p":
  #                 wikipedia_mode = True
  #                 paragraph_mode = True
  #             elif flag == "-r":
  #                 regenerate_aliases = True
  #             elif flag == "-y":
  #                 yaml_mode = True
  #             elif flag == "-u":
  #                 clear_links = True

  # else:
  #     print("usage - python obs-link.py <path to obsidian vault> [-r] [-y] [-w / -p]")
  #     print("-r = regenerate the aliases.md file using yaml frontmatter inside vault markdown files")
  #     print("-y = use aliases.yml as aliases file instead of aliases.md")
  #     print("-w = only the first occurrence of a page title (or alias) in the content will be linked ('wikipedia mode')")
  #     print("-p = only the first occurrence of a page title (or alias) in each paragraph will be linked ('paragraph mode')")
  #     print("-u = remove existing links in clipboard text before performing linking")
  #     exit()

  # aliases_file = obsidian_home + "/aliases" + (".yml" if yaml_mode else ".md")
  aliases_file = aliases_csv_file

  # get a directory listing of obsidian *.md files
  # use it to build our list of titles and aliases
  for root, dirs, files in os.walk(obsidian_home):
      for file in files:
          # ignore any 'dot' folders (.trash, .obsidian, etc.)
          if file.endswith('.md') and '\\.' not in root and '/.' not in root:
              page_title = re.sub(r'\.md$', '', file)
              #print(page_title)
              page_titles.append(page_title)
              
              # load yaml frontmatter and parse aliases
              if regenerate_aliases:
                  try:
                      with open(root + "/" + file, encoding="utf-8") as f:
                          #print(file)
                          fm = frontmatter.load(f)
                          
                          if fm and 'aliases' in fm:
                              #print(fm['aliases'])
                              generated_aliases[page_title] = fm['aliases']
                  except yaml.YAMLError as exc:
                      print("Error processing aliases in file: " + file)
                      exit()

  # if -r passed on command line, regenerate aliases.yml
  # this is only necessary if new aliases are present
  if regenerate_aliases:
      with open(aliases_file, "w", encoding="utf-8") as af:
          for title in generated_aliases:
              af.write(title + ":\n" if yaml_mode else "[[" + title + "]]:\n")
              #print(title)
              for alias in generated_aliases[title]:
                  af.write("- " + alias + "\n")
                  #print(alias)
              af.write("\n")
          if not yaml_mode: af.write("aliases:\n- ")

  # load the aliases file
  # we pivot (invert) the dict for lookup purposes
  if os.path.isfile(aliases_file):
      with open(aliases_file, 'r') as stream:
          try:
              # this line injects quotes around wikilinks so that yaml parsing won't fail
              # we remove them later, so they are only a temporary measure
              aliases_txt = stream.read().replace("[[", "\"[[").replace("]]", "]]\"")
              aliases = yaml.full_load(aliases_txt)
              
              if aliases:
                  for title in aliases:         
                      if aliases[title]:                  
                          for alias in aliases[title]:
                              # strip out wikilinks and quotes from title if present
                              sanitized_title = title.replace("[[", "").replace("]]", "").replace("\"", "")
                              if alias:
                                  page_aliases[alias] = sanitized_title
                              else:
                                  # empty entry will signal to ignore page title in matching
                                  print("Empty alias (will be ignored): " + sanitized_title)
                                  if sanitized_title in page_titles:
                                      page_titles.remove(sanitized_title)
                      #print(page_aliases)
          except yaml.YAMLError as exc:
              print(exc)
              exit()

  # append our aliases to the list of titles
  for alias in page_aliases:
      page_titles.append(alias)

  # sort from longest to shortest page titles so that we don't
  # identify scenarios where a page title is a subset of another
  page_titles = sorted(page_titles, key=lambda x: len(x), reverse=True)

  # get text from clipboard
  # clip_txt = pyperclip.paste()
  #print('--- clipboard text ---')
  #print(clip_txt)
  print('----------------------')

  # unlink text prior to processing if enabled
  if (clear_links):
      clip_txt = unlink_text(clip_txt)
      #print('--- text after scrubbing links ---')
      #print(clip_txt)
      #print('----------------------')

  # prepare our linked text output
  linked_txt = ""

  if paragraph_mode:
      for paragraph in clip_txt.split("\n"):
          linked_txt += link_content(paragraph) + "\n"
      linked_txt = linked_txt[:-1] # scrub the last newline
  else:
      linked_txt = link_content(clip_txt)

  # send the linked text to the clipboard
  # pyperclip.copy(linked_txt)
  #print(clip_txt)
  print('----------------------')
  print('linked text copied to clipboard')


def autolink(folder_to_scan, audited_df, aliases_df):
  list_page_titles = []
  list_page_aliases = {}

  # list_page_titles = audited_df['dst_file'].values
  for current_item_index, current_item in audited_df.iterrows():
    list_page_titles.append(current_item.dst_file)

  # Transform the pandas df into a dict
  for current_item_index, current_item in aliases_df.iterrows():
    if current_item.link_text != "" and current_item.link_text not in list_page_aliases.keys():
      list_page_aliases[current_item.link_text] = current_item.dst_file
    

  # for current_post_index, current_post in audited_df.iterrows():
  #   if current_post.link_text != "" and current_post.link_text not in list_page_aliases[current_post.link_text]:
  #     list_page_aliases[current_post.link_text] = current_post.dst_file

  # Add all aliases to page titles
  # We don't add a page title if it has no aliases
  for page_alias in list_page_aliases:
    list_page_titles.append(page_alias)

  # # Filter here the aliases that where already used
  # # TODO - Rewrite using pandas => faster
  # used_aliases = audited_df.loc[audited_df['link_text'] != ""].values
  # for alias in used_aliases:
  #   print("<<<< removing used alias {}".format(alias))
  #   list_page_titles.remove(alias)

  # Linking the content
  print("Start linking content ...")
  #print("Page titles = ", list_page_titles)
  #print("Page aliases = ", list_page_aliases)
  
  # Process only the src -> dst that are not linked yet
  # print("Here is the list of audited links")
  #print(audited_df)
  #print(audited_df.to_string())
  # audited_df.to_csv("audited_df_{}.csv".format(lang), index=False)
  audited_notlinked_df = audited_df.loc[ audited_df['link_exist'] == False ]

  # print("Here is the dataframe with the not linked pages in the same silot term")
  #audited_notlinked_df.set_option('display.max_colwidth', None)
  #print(audited_notlinked_df)
  #print(audited_notlinked_df.to_string())
  # audited_notlinked_df.to_csv("audited_notlinked_df_{}.csv".format(lang), index=False)

  for current_item_index, current_item in audited_notlinked_df.iterrows():
  # for current_item_index, current_item in audited_notlinked_df.head(2).iterrows():
    has_linked = False
    # Load the post using the frontmatter
    try:
      
      print("Linking content from {} to {}".format(current_item.src_file, current_item.dst_file))
      # has_linked, text_linked, new_content = link_content3(folder_to_scan, current_item.src_file, current_item.dst_file, aliases_df)

      # Load the file to process it's content
      post = frontmatter.load(folder_to_scan + "/" + current_item.src_file)
      dest_post = frontmatter.load(folder_to_scan + "/" + current_item.dst_file)

      # Check that the dest_post has a date that is anterior to day's date
      dest_post_date = dest_post['date'] if 'date' in dest_post else datetime.datetime.strptime("1980-01-01", '%Y-%m-%d')
      # Shortening the date if it contains the time also
      # dest_post_date_str = dest_post_date_str[:10]
      # dest_post_date = datetime.datetime.strptime(dest_post_date_str, '%Y-%m-%d')
      print("Dest post date = {}  ".format(dest_post_date))
      today = datetime.datetime.today().date()
      yesterday = today + datetime.timedelta(days=-1)

      if dest_post_date <= yesterday:
        print("Dest date is earlier than yesterday. Linking ...")

        tokens_array_codeblocks, content_codeblock = replace_codeblock_with_tokens(post.content)
        tokens_array_titles, content_titles = replace_title_with_tokens(content_codeblock)
        tokens_array_images, content_images = replace_image_with_tokens(content_titles)
        tokens_array_links, content_links = replace_link_with_tokens(content_images)

        has_linked, text_linked, new_content = link_content4(folder_to_scan, content_links, current_item.dst_file, aliases_df)

        content_codeblocks_replaced = replace_tokens_with_codeblocks(new_content, tokens_array_codeblocks)
        content_images_replaced = replace_tokens_with_codeblocks(content_codeblocks_replaced, tokens_array_images)
        content_links_replaced = replace_tokens_with_codeblocks(content_images_replaced, tokens_array_links)
        content_titles_replaced = replace_tokens_with_codeblocks(content_links_replaced, tokens_array_titles)

        final_content = content_titles_replaced
        
        print("***** Found Link = ", has_linked)

        # Save new content in the file
        if has_linked:
          # Mark the link_text as used
          if text_linked:
            audited_df.loc[(audited_df['link_text'] == text_linked) & (audited_df['dst_file'] == current_item.dst_file), 'link_exist'] = True
          # Save the content
          if dry_run == "true":
                print("---> In dry run mode. Not saving files")
          else:
            print("Saving auto linked post")
            post = frontmatter.load(folder_to_scan + "/" + current_item.src_file)
            post.content = final_content
            filecontent = frontmatter.dumps(post)
            
            with open(folder_to_scan + "/" + current_item.src_file, 'w') as f:
              f.write(filecontent)
      else:
        print("Destination post date {} is newer than yesterday {}. Not linking the file".format(dest_post_date, yesterday))        

    except Exception as e:
      print("bad error for file {}".format(current_item.dst_file), str(e))

  return audited_df

def perform_internal_linking():

  # codeblocks_results = extract_codeblocks(md_content)
  # print(codeblocks_results)

  # headers_results = extract_headers(md_content)
  # print(headers_results)

  # wikilinks_results = extract_wikilinks(md_content)
  # print(wikilinks_results)

  st_df = md2df_by_silotterms(src_folder_toscan, dst_folder_tosaveresults)

  anchor_df = pd.read_csv(anchor_text_to_post)
  link_text_df = pd.read_csv(internal_link_text_file)
  aliases_df = pd.read_csv(aliases_csv_file)

  # Step 1: AUDIT - Parse the files and list src, dst, is linked, anchor text
  # Step 1.1: GENERATE MANUAL LINK - For src, dst files that are not linked, generate a linked text to ease manual linking
  audited_df = generate_internal_linking_requirements(st_df, src_folder_toscan, dst_folder_tosaveresults, anchor_df, link_text_df)

  # Step 2: AUTOLINK - Load the aliases files (contains dst, link_text) inputed by human to try to autolink.
  autolinked_df = autolink(src_folder_toscan, audited_df, aliases_df)

  # Save the results of the audit
  print("Sort the df before saving it")
  autolinked_df = autolinked_df.sort_values(['silot_terms', 'link_exist'], ascending = [False, True])
  print("Saving the analysis result")
  autolinked_df.to_csv("{}/internallinking_per_silot_terms.csv".format(dst_folder_tosaveresults), index=False)



# # Testing only the markdown example above
# tokens_array_codeblocks, content_codeblock = replace_codeblock_with_tokens(md_content)
# tokens_array_titles, content_titles = replace_title_with_tokens(content_codeblock)
# tokens_array_images, content_images = replace_image_with_tokens(content_titles)
# tokens_array_links, content_links = replace_link_with_tokens(content_images)
# link_title4("(kubernetes|start)", content_links, "mydstfile")

generate_short_keywords("aliases.csv", "aliases.csv", src_folder_toscan, lang)
# generate_silot_terms_file(silot_terms_file)
generate_internallinking_per_silot_terms_file(internal_link_text_file)
generate_anchor_text_to_post_file(anchor_text_to_post)

perform_internal_linking()
