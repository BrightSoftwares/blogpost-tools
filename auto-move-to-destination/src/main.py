import frontmatter
import os
import importlib

dry_run = os.getenv('INPUT_DRY_RUN')
min_content_nb_characters = int(os.getenv('INPUT_MIN_CONTENT_NB_CHARACTERS', 1000))

# Opt-in only (default OFF): when unset/false, is_ready_for_publication()
# behaves exactly as it did before the 2026-09-10 is_approved() gate was
# added -- no publish_status check at all. This keeps the 4 other production
# callers of this shared action (ieatmyhealth.com, keke.li,
# olympics-paris2024.com, foolywise.com) completely unaffected, since none
# of them ever set publish_status in their pipelines. Only a caller that
# explicitly passes `require_approval: true` (corporate-website) gets the
# gate. See is_ready_for_publication() below.
require_approval = os.getenv('INPUT_REQUIRE_APPROVAL', 'false').strip().lower() == 'true'

def is_content_enough(post):
  nb_characters = len(post.content)
  print("is_content_enough >>> nb characters = ", nb_characters)
  return nb_characters > min_content_nb_characters

def is_auto_scheduled(post):
  date = post['date'] if 'date' in post else None
  print("is_auto_scheduled >>> date = ", date)
  return date is not None


def is_bloginspritation_converter(post):
  post_inspiration = post['post_inspiration']  if 'post_inspiration' in post else None
  nb_characters = len(post.content)
  print("is_bloginspritation_converter >>> post inspiration = {}, nb_characters = {}".format(post_inspiration, nb_characters))
  return post_inspiration is not None and nb_characters > min_content_nb_characters


def is_jekyll_filename_pretified(post):
  pretified = post['pretified']  if 'pretified' in post else None
  print("is_jekyll_filename_pretified >>> pretified = {}".format(pretified))
  return pretified is not None and pretified == True

def is_refined_content(post):
  refined = post['refined_content']  if 'refined_content' in post else None
  print("is_refined_content >>> refined = {}".format(refined))
  return refined is not None and refined == True

def is_suggestions_to_blogposted(post):
  nb_characters = len(post.content)
  print("is_suggestions_to_blogposted >>> nb_characters = {}".format(nb_characters))  
  return nb_characters > min_content_nb_characters


def is_transcript_downloaded(post):
  transcribed = post['transcribed']  if 'transcribed' in post else None
  nb_characters = len(post.content)
  print("is_transcript_downloaded >>> transcribed = {}, nb_characters = {}".format(transcribed, nb_characters))
  return transcribed is not None and nb_characters > min_content_nb_characters


def is_unsplash_to_cloudinary(post):
  image = post['image']  if 'image' in post else None
  print("is_unsplash_to_cloudinary >>> image = {}".format(image))

  return image is not None and image != "null"


def is_youtube_vid_finder(post):
  youtube_video_id = post['youtube_video_id']  if 'youtube_video_id' in post else None
  print("is_youtube_vid_finder >>> youtube_video_id = {}".format(youtube_video_id))
  return youtube_video_id is not None


def is_approved(post):
  # Gate for the 600_auto_scheduled -> _posts move: only a human-approved
  # post may go live. Missing entirely (2026-09-06 incident: 25/59 posts
  # with publish_status in {draft, review, changes_requested, superseded}
  # were force-published because this check did not exist) so this must
  # fail closed (default False) rather than treat "field absent" as okay.
  publish_status = post['publish_status'] if 'publish_status' in post else None
  print("is_approved >>> publish_status = {}".format(publish_status))
  return publish_status == "approved"

def move_to_destination(folder_to_scan, destination, condition_func):
  if destination is None:
    print("Destination is not set. Exiting")
    return
  elif condition_func is None:
    print("Condition fonction is not set. Exiting")
    return
  else:
    print("Destination is set. We can process the moves")
    entries = [f for f in os.listdir(folder_to_scan) if os.path.isfile(os.path.join(folder_to_scan, f))] # os.listdir(folder_to_scan)

    for entry in entries:
      try:
        print("Processing entry", entry)
        src_entry = os.path.join(folder_to_scan, entry)
        dst_entry = os.path.join(destination, entry)
        post = frontmatter.load(src_entry)

        test_result = condition_func(post)

        if test_result:
          if dry_run == "true":
            print("Dry run mode. Not moving ...")
          else:
            print("The condition {} is okay ({}). Moving ...".format(condition_func, test_result))
            os.rename(src_entry, dst_entry)

        else:
          print("The condition {} is NOT okay ({}). Pass this entry".format(condition_func, test_result))
        
        # cornerstone = post['cornerstone'] if 'cornerstone' in post else "no"
        # title = post['title'] if 'title' in post else None
        # categories = post['categories'] if 'categories' in post else ''
        # silot_terms_df.loc[len(silot_terms_df)] = [silot_terms, title, entry, cornerstone, categories]
      except Exception as e:
        print("Error, something unexpected occured", str(e))

def is_ready_for_publication(post):
  # NOTE (2026-09-10): added an opt-in is_approved() gate -- this check
  # previously only verified content length / pretified / "has an image
  # field", none of which reflect human review. A post with plausible-
  # looking frontmatter (true of every AI-authored draft) passed all three
  # regardless of publish_status, so 25 of 59 non-approved posts were
  # force-published to _posts/ by run 34062358994 on 2026-09-06. See
  # BrightSoftwares/corporate-website incident writeup
  # (Daily_notes/2026-09-05.md, task 🆔 revert-autopublish-1).
  #
  # The is_approved() check is gated behind require_approval (opt-in,
  # default False) rather than being unconditional: this action is shared
  # by 4 other production sites (ieatmyhealth.com, keke.li,
  # olympics-paris2024.com, foolywise.com) whose fully-auto-scheduled
  # pipelines never set publish_status. Making the gate unconditional would
  # have silently and permanently halted publishing on all four with no
  # error. Only callers that explicitly pass `require_approval: true`
  # (corporate-website) get the new check; every other caller's behavior
  # is byte-for-byte identical to before this fix.
  base_ready = (
    is_content_enough(post)
    and is_jekyll_filename_pretified(post)
    and is_unsplash_to_cloudinary(post)
  )
  if not require_approval:
    return base_ready
  return base_ready and is_approved(post)


src_folder = os.getenv('INPUT_SRC_PATH')
dst_folder = os.getenv('INPUT_DST_PATH')

def move_autoscheduled_to_destination():
  move_to_destination(src_folder, dst_folder, is_auto_scheduled)


def move_autoscheduleposts_to_destination():
  move_to_destination(src_folder, dst_folder, is_auto_scheduled)


def move_bloginspritationconverter_to_destination():
  move_to_destination(src_folder, dst_folder, is_bloginspritation_converter)


def move_jekyllfilenamepretifier_to_destination():
  move_to_destination(src_folder, dst_folder, is_jekyll_filename_pretified)

def move_refinedcontent_to_destination():
  move_to_destination(src_folder, dst_folder, is_refined_content)

def move_suggestionstoblogpost_to_destination():
  move_to_destination(src_folder, dst_folder, is_suggestions_to_blogposted)


def move_transcriptdownloader_to_destination():
  move_to_destination(src_folder, dst_folder, is_transcript_downloaded)


def move_unsplashtocloudinary_to_destination():
  move_to_destination(src_folder, dst_folder, is_unsplash_to_cloudinary)


def move_youtubevidfinder_to_destination():
  move_to_destination(src_folder, dst_folder, is_youtube_vid_finder)

def move_iscontentenough_to_destination():
  move_to_destination(src_folder, dst_folder, is_content_enough)

def move_readyforpublication_to_destination():
  move_to_destination(src_folder, dst_folder, is_ready_for_publication)



# Printing debug information
print("The current directory is = ", os.getcwd())
#print("Here is the content of the current directory")
#for subdir, dirs, files in os.walk('./'):
#    for file in files:
#      print(file)
#    for folder in dirs:
#      print(folder)
# move_autoscheduled_to_destination()
# getattr("", 'move_autoscheduled_to_destination')()  # note the extra "()"
function_to_run_str = os.getenv('INPUT_FUNCTION_TO_RUN')
module = importlib.import_module(__name__)
function_to_run = getattr(module, function_to_run_str)
function_to_run()
