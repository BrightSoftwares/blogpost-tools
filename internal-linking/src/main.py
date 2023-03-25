import pandas as pd
import numpy as np
import os, re
import frontmatter

# charList = " " + string.ascii_lowercase + string.digits

src_folder_toscan = os.getenv('INPUT_SRC_FOLDER_TOSCAN')
dst_folder_tosaveresults = os.getenv('INPUT_DST_FOLDER_TOSAVERESULTS')
internal_link_text_file = os.getenv('INPUT_INTERNAL_LINK_TEXT_FILE')
anchor_text_to_post = os.getenv('INPUT_ANCHOR_TEXT_TO_POST')
# keyword_suggestion = os.getenv('INPUT_KEYWORD_SUGGESTION_FILE')
# feeds_file=os.getenv('INPUT_FEEDS_FILE')
# feed_blogpost_url_used=os.getenv('INPUT_FEED_BLOGPOST_URL_USED')
# keyword_suggestions_generation_folder = os.getenv('INPUT_KEYWORD_SUGGESTIONS_GENERATION_FOLDER')
# CSV_FILE_NAME = os.getenv('INPUT_KEYWORD_SEED')
# destination_folder = os.getenv('INPUT_DRAFTS_PATH')
# batch_size = int(os.getenv('INPUT_BATCH_SIZE'))
# language = os.getenv('INPUT_LANGUAGE')
# keyword_min_volume_eligible = int(os.getenv('INPUT_KEYWORD_MIN_VOLUME_ELIGIBLE', '0'))
# keyword_max_volume_eligible = int(os.getenv('INPUT_KEYWORD_MAX_VOLUME_ELIGIBLE', '5000000'))

print("Processing markdown files")


# # Try to load the used urls. If not found, create an empty one
# def get_feedblogposturlused_df(file_url):
#   try:
#     return pd.read_csv(file_url)
#   except:
#     return pd.DataFrame(columns=['Suggestion', 'silot_terms', 'blogpost_title', 'blogpost_link', 'category'])


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

def extract_headers(data_str):
  print("Extract headers")
  return extract_data_with_regex(data_str, "^#+\s(.*)$")

def extract_codeblocks(data_str):
  print("Extract code blocks")
  return extract_data_with_regex(data_str, "`{3}([\w]*)\n([\S\s]+?)\n`{3}")

def extract_inline_codeblocks(data_str):
  print("Extract code blocks")
  return extract_data_with_regex(data_str, "`{3}([\w]*)\n([\S\s]+?)\n`{3}")

def extract_wikilinks(data_str):
  print("Extract wikilinks")
  return extract_data_with_regex(data_str, "\[\[(.+?)(\|.+)?\]\]")

def md2df_by_silotterms(folder_to_scan, dst_folder_tosaveresults):
  silot_terms_df = pd.DataFrame(columns=['silot_terms', 'title', 'path', 'cornerstone', 'categories'])
  entries = [f for f in os.listdir(folder_to_scan) if os.path.isfile(os.path.join(folder_to_scan, f))] # os.listdir(folder_to_scan)

  for entry in entries:

    post = frontmatter.load(folder_to_scan + "/" + entry)
    silot_terms = post['silot_terms'] if 'silot_terms' in post else "unknown"
    cornerstone = post['cornerstone'] if 'cornerstone' in post else "no"
    title = post['title'] if 'title' in post else None
    categories = post['categories'] if 'categories' in post else ''
    # pretified = post['pretified'] if 'pretified' in post else None
    # post_date = post['date'] if 'date' in post else None
    # fileref = post['ref'] if 'ref' in post else None
    # post_category = post['category'] if 'category' in post else []
    # post_description = post['description'] if 'description' in post else None
    # post_image = post['image'] if 'image' in post else None
    # post_author = post['post_author'] if 'post_author' in post else post_author_env
    # post_tags = post['tags'] if 'tags' in post else []
    silot_terms_df.loc[len(silot_terms_df)] = [silot_terms, title, entry, cornerstone, categories]

  print("Save the result into a csv file")
  silot_terms_df.to_csv("{}/silot_terms.csv".format(dst_folder_tosaveresults), index=False)

  # pvtable = pd.pivot_table(silot_terms_df, values='title', index=['silot_terms'], columns=['cornerstone'], aggfunc=np.count_nonzero)
  # print("Save the pivot table in a csv format")
  # pvtable.to_csv("{}/silot_terms_by_cornerstone.csv".format(dst_folder_tosaveresults), index=False)
  # return pvtable

  return silot_terms_df

# def add_linksFromSheet():
#     var sheet = SpreadsheetApp.openById(YOUR_GOOGLE_SHEET_ID).getSheets()[0];
#     var data = sheet.getDataRange().getValues();

#     var googleDocument = DocumentApp.getActiveDocument();
#     var body = googleDocument.getBody();

#     var keywords = []
#     for (var i = 0; i < data.length; i++) {
#         var searchPhrase = data[i][0];
#         var hyperlink = data[i][1];
#         keywords.push([searchPhrase, hyperlink]);
#     }
#     keywords.sort(() => Math.random() - 0.5);
#     var paragraphs = body.getParagraphs();
#     paragraphs.sort(() => Math.random() - 0.5);

#     var linksUsed = []
#     for (i = 0; i < keywords.length; i += 1) {
#         if (linksUsed.length >= MAX_INTERNAL_LINKS) {
#             console.log(`I've added ${linksUsed.length} links, I'm now stopping`)
#             break;
#         }
#         var keyword = keywords[i];
#         if (!keyword[0] || !keyword[1]) {
#             continue;
#         }
#         if (linksUsed.indexOf(keyword[1]) !== -1) {
#             console.log(`Already added a link for ${keyword[1]}, skipping keyword ${keyword[0]}`)
#             continue;
#         }
#         console.log(`Looking for keyword ${keyword[0]}`);
#         var textToFind = "(?i)(^| )" + keyword[0] + "[!?., :;]";

#         for (var j = 0; j < paragraphs.length; j += 1) {
#             var paragraph = paragraphs[j];
#             if (paragraph.getHeading() == DocumentApp.ParagraphHeading.NORMAL) {
#                 var text = paragraph.getText();
#                 if (!text.trim().length) {
#                     continue;
#                 }
#                 // var search = paragraph.findText(keyword[0]);
#                 var search = paragraph.findText(textToFind);
#                 if (search) {
#                     var searchElement = search.getElement();
#                     var startIndex = search.getStartOffset();
#                     var endIndex = search.getEndOffsetInclusive();
#                     if (endIndex > 0) {
#                       console.log(`${startIndex}, ${endIndex}, ${keyword[0].length}`)
#                         if (endIndex - startIndex > keyword[0].length) {
#                           startIndex += 1;
#                         }
#                         console.log(`Found keyword '${keyword[0]}, replacing with link ${keyword[1]}`);
#                         searchElement.asText().setLinkUrl(startIndex, endIndex - 1, keyword[1]);
#                         linksUsed.push(keyword[1].trim())
#                         break;
#                     }
#                 }
#             }
#         }
#     }
#     googleDocument.saveAndClose();
#     console.log("All Done");
# }



def generate_full_link_and_text(post_title, post_link, anchor_df, link_text_df):
  # Get a random text from the link text dataframe
  sample_text = link_text_df.sample().head()
  print("generate_full_link_and_text > sample =", sample_text)
  full_link_and_text = sample_text['internal_link_text'].iloc[0]
  print("generate_full_link_and_text > full_link_and_text =", full_link_and_text)

  # Get the corresponding anchor text
  # If none if found, use the post title
  regex = ".*{}.*".format(post_link[11:-3])
  # regex = ".*solutions.*"
  print("Filtering anchor with the regex", regex)
  eligible_anchors = anchor_df[anchor_df.path.str.match(regex, na=False)]
  print("Eligible anchors =", eligible_anchors)
  if eligible_anchors.empty:
    anchor_text = post_title
  else:
    anchor_text = eligible_anchors.sample().head()['link_text'].iloc[0]

  # Replace the tokens
  full_link_and_text = full_link_and_text.replace("[topic]", post_title).replace("[[link to blog post]]", "[[{}|{}]]".format(post_link, anchor_text))
  print("full link and text for post '{}' with full link '{}' is '{}'".format(post_title, post_link, full_link_and_text))
  return full_link_and_text


def generate_internal_linking_requirements(silot_terms_df, folder_to_scan, dst_folder_tosaveresults, anchor_df, link_text_df):
  il_requirements = pd.DataFrame(columns=['silot_terms', 'src_file', 'dst_file', 'src_is_cornerstone', 'link_exist', 'link_text', 'full_link', 'full_link_and_text'])

  print("Ignoring unknown posts with unknown silot_terms")
  st_df = silot_terms_df[silot_terms_df.silot_terms != "unknown"]

  for term in st_df.silot_terms.unique():
    print("Generate requirements for term '{}'".format(term))
    related_posts_df = st_df[st_df.silot_terms == term]

    print("Checking the linking for term '{}' with df '{}'".format(term, related_posts_df))
    for current_post_index, current_post in related_posts_df.iterrows():
      print("  Load the post {} ({}) and check if there is a link to the others".format(current_post.title, current_post.path))
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

        # We avoid comparing the src post with itself
        if current_post.path == other_post.path:
          pass
        else:
          has_link_to_dst_post = False
          link_text = ""
          full_link_and_text = ""
          full_link = "[[{}|{}]]".format(other_post.path, other_post.title)

          print("    Check if the src post {} has links to {} in the wikilink list {}".format(current_post.path, other_post.path, post_wklinks))
          for post_wklinks_key in post_wklinks.keys():
            post_wklinks_value = post_wklinks[post_wklinks_key]

            if other_post.path in post_wklinks_value:
              print("     We found a link from {} to {}.".format(current_post.path, other_post.path))
              has_link_to_dst_post = True
              # link_text = post_wklinks["{}_2".format(post_wklinks_key.split("_")[0])] # 1_2
              # full_link = "[[{}|{}]]".format(post_wklinks_value ,link_text)
              
          if not has_link_to_dst_post:
            full_link_and_text = generate_full_link_and_text(other_post.title, other_post.path, anchor_df, link_text_df)

          il_requirements.loc[len(il_requirements)] = [silot_terms, current_post.path, other_post.path, cornerstone, has_link_to_dst_post, link_text, full_link, full_link_and_text]

  print("Sort the df before saving it")
  il_requirements = il_requirements.sort_values(['silot_terms', 'link_exist'], ascending = [False, True])
  print("Saving the analysis result")
  il_requirements.to_csv("{}/internallinking_per_silot_terms.csv".format(dst_folder_tosaveresults), index=False)


# codeblocks_results = extract_codeblocks(md_content)
# print(codeblocks_results)

# headers_results = extract_headers(md_content)
# print(headers_results)

# wikilinks_results = extract_wikilinks(md_content)
# print(wikilinks_results)

st_df = md2df_by_silotterms(src_folder_toscan, dst_folder_tosaveresults)

anchor_df = pd.read_csv(anchor_text_to_post)
link_text_df = pd.read_csv(internal_link_text_file)
generate_internal_linking_requirements(st_df, src_folder_toscan, dst_folder_tosaveresults, anchor_df, link_text_df)

