# importing the module
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from pytube import YouTube
import frontmatter
import os
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs


def is_manually_generated(transcript):
  # throw error if it is the case.
  if not transcript.is_generated:
    raise Exception("We don't want manually generated transcriptions")


def get_best_transcript(transcript_list, language, ignore_manually_generated=True):

  final_transcript = None

  # Try to get directly the language
  for transcript in transcript_list:
    print("Looking for language {} against transcription {} ({})".format(language, transcript.language, transcript.language_code))

    if language == transcript.language_code:

      if ignore_manually_generated and not transcript.is_generated:
        print("This transcript is manually generated. Escaping")
        continue
      else:
        final_transcript = transcript
        break

  if final_transcript is None:
    # Not found, check if I can translate an existing one
    for transcript in transcript_list:
      print("Checking whetehr the translation {} ({}) is translatable to {}".format(transcript.language, transcript.language_code, language))

      if transcript.is_translatable:
        print("Translating transcript to language {}".format(language))

        final_transcript = transcript.translate(language)
        break
  

  return final_transcript
  

def get_video_description(video_id):
  video_url = "https://www.youtube.com/watch?v={}".format(video_id)
  print("Getting description for video url {}".format(video_url))
  video = YouTube(video_url)
  description = video.description
  print(video.description)
  return description


def parse_video_descrption(description):
  print("Parsing video description", description[:50])
  pattern = re.compile(r"(\(?[0-9:]{3,8}\)?) [-\s]?(.*)$", re.MULTILINE)
  matches = pattern.findall(description)
  print(matches)

  if len(matches) > 0:
    return matches
  else:
    # If there is no chapters found in the description, return something to genetate all the text at once
    return [('00:00:00', '')]

def parse_time_duration(time_duration):

  if len(time_duration) < 8:
    # The duration format is probably 00:00. Let's make it 00:00:00
    time_duration = "00:{}".format(time_duration)

  #print("Parsing time duration", time_duration)
  #print("Parsing line time_duration: {}, duration: {}".format(time_duration, duration))

  parsed_time = datetime.strptime(time_duration,"%H:%M:%S")
  #delta = timedelta(hours=parsed_time.hour, minutes=parsed_time.minute, seconds=parsed_time.second)
  ##print("  result:", delta)
  #return delta
  return parsed_time


def parse_line_duration(time_duration, duration):
  #print("Parsing line time_duration: {}, duration: {}".format(time_duration, duration))
  parsed_time = datetime.fromtimestamp(time_duration) #datetime.strptime(time_duration,"%H:%M:%S")
  parsed_time = parsed_time.replace(year=1900)
  #time_and_duration = time_duration + duration
  #delta = timedelta(hours=0, minutes=0, seconds=time_and_duration)
  #print("  result:", delta)
  #return delta
  return parsed_time


def get_yt_video_transcript(video_id, language='en'):
    # retrieve the available transcripts
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    my_transcript = get_best_transcript(transcript_list, language)

    transcript_data = my_transcript.fetch()

    # The idea here is: 
    # 0. We don't want manually created transcripts
    # 1. We look for the language in the default transcription.
    # 2. If not found, we search in the translations
    # 3. Get the description and see if there are chapters inside
    # 4. If yes, extract the chapters and timecodes
    # 5. Extract the text with the chapters if available (empty array if no chapters)


    # Parse the description
    description = get_video_description(video_id)
    parsed_description = parse_video_descrption(description)
    print("Parsed descrption", parsed_description)

    # 1. We loop through the parsed description
    # 2. We loop through the transcript data
    # 2.a. If the timecode of the transcript match the description section => we add the text in that section
    # 2.b. Else we ignore that transcript

    transcript_data_string = ""
    for index, desc in enumerate(parsed_description):

      next_index = index + 1
      next_desc = parsed_description[next_index][0] if next_index < len(parsed_description) else "23:59:59"

      try:
        desc_time = parse_time_duration(desc[0])
        desc_title = desc[1]
        next_desc_time = parse_time_duration(next_desc)
        print("desc {} => {} ({})".format(desc_time, next_desc_time, desc_title))

        transcript_data_string += "\n\n# {}\n\n".format(desc_title)

        debug_str = ""
        for line in transcript_data:
            #print(line['text'])
            
            line_time = parse_line_duration(line['start'], line['duration'])
            #print("{} <= {} and {} < {}".format(desc_time, line_time, line_time, next_desc_time))
            

            if desc_time <= line_time and line_time < next_desc_time:
              debug_str += "{}, ".format(line_time)
              transcript_data_string += "{}\n".format(line['text'])

        print(debug_str)
        transcript_data_string += "\n"
      except Exception as e:
        print(str(e))

    return transcript_data_string


def get_yt_video_id(url):
    """Returns Video_ID extracting from the given url of Youtube

    Examples of URLs:
      Valid:
        'http://youtu.be/_lOT2p_FCvA',
        'www.youtube.com/watch?v=_lOT2p_FCvA&feature=feedu',
        'http://www.youtube.com/embed/_lOT2p_FCvA',
        'http://www.youtube.com/v/_lOT2p_FCvA?version=3&amp;hl=en_US',
        'https://www.youtube.com/watch?v=rTHlyTphWP0&index=6&list=PLjeDyYvG6-40qawYNR4juzvSOg-ezZ2a6',
        'youtube.com/watch?v=_lOT2p_FCvA',

      Invalid:
        'youtu.be/watch?v=_lOT2p_FCvA',
    """

    if url.startswith(('youtu', 'www')):
        url = 'http://' + url

    query = urlparse(url)

    if 'youtube' in query.hostname:
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        elif query.path.startswith(('/embed/', '/v/')):
            return query.path.split('/')[2]
    elif 'youtu.be' in query.hostname:
        return query.path[1:]
    else:
        raise ValueError


#folder = '../../en/_drafts/'
folder = os.getenv('INPUT_DRAFTS_PATH')
entries = os.listdir(folder)
for entry in entries:
    # print(entry)
    try:
        post = frontmatter.load(folder + "/" + entry)
        title = post['title'] if 'title' in post else None
        ytvideo_url = post['youtube_video'] if 'youtube_video' in post else None
        transcribed = post['transcribed'] if 'transcribed' in post else None
        lang = post['lang'] if 'lang' in post else 'en'
        # nb_words = len(post.content.split())
        # contains_readmore = 1 if "Read more" in post.content else 0
        # title_spanish = 1 if "como" in entry else 0
        # # print("Processing post with title {}. Nb words: {}. Contains readmore {}. Title is spanish: {}".format(title, nb_words, contains_readmore, title_spanish))
        # android_authority = 1 if "androidauthority" in post['post_inspiration'] else 0
        # e27co = 1 if "e27.co" in post['post_inspiration'] else 0
        # macrumors = 1 if "macrumors" in post['post_inspiration'] else 0
        # podgalleryorg = 1 if "podgallery.org" in post['post_inspiration'] else 0
        # bgrcom = 1 if "bgr.com" in post['post_inspiration'] else 0
        # lifehacker = 1 if "lifehacker" in post['post_inspiration'] else 0
        # kinjadeals = 1 if "kinjadeals" in post['post_inspiration'] else 0

        # if kinjadeals == 1 and nb_words < 1000:
        #     print(entry)
        #     os.remove(folder + "/" + entry)

        # print(post.metadata)
        # print("YT video: {}, title: {}".format(ytvideo, title))

        if ytvideo_url is not None and ytvideo_url != '' and transcribed is not True:
        
            transcription = ""
            try:
                print("Getting video ID from url ", ytvideo_url)
                ytvideo = get_yt_video_id(ytvideo_url)

                print("Found a post {} with a youtube video to transcribe. Video id = {}".format(
                    title, ytvideo))
                # print("Content is =", post.content.strip())
                transcription = get_yt_video_transcript(ytvideo, lang)
                #post['transcribed'] = True
                transcribed = True
                post['youtube_video_id'] = ytvideo
                post.content = transcription

                # print(filecontent)
                
            except TranscriptsDisabled as e2:
                transcription = "An error occured while trying to get transcript TranscriptsDisabled. Error: {}".format(str(e2))
                transcribed = False
                post["youtube_video"] = None
                post["youtube_video_id"] = None
                post["youtube_video_title"] = None
                post["youtube_video_description"] = None
                post.content = transcription
                print(transcription)

            except Exception as e1:
                transcription = "An error occured while trying to get transcript. Error: {}".format(str(e1))
                transcribed = False
                post.content = transcription
                print(transcription)
            finally:
                print("Adding the transcribed and lang tags")
                post['transcribed'] = transcribed
                post['lang'] = lang
                print("Final transcription:", transcription)
                print("transcribed? = ", transcribed)
                print("Saving the content of the file")
                filecontent = frontmatter.dumps(post)
                with open(folder + "/" + entry, 'w') as f:
                    f.write(filecontent)

    except Exception as e:
        print("Error. = ", str(e))
