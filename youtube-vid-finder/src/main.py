import os
import frontmatter
import pandas as pd

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_yt_results_dataframe(obj_array):
  return pd.DataFrame(obj_array, columns=['query', 'video_kind', 'video_title', 'video_id', 'video_description'])

def youtube_search(query, yt_service_name, yt_api_version, yt_api_key, yt_results_file, max_results=25):

    # Load the results youtube videos
    print("Results file to load", yt_results_file)
    yt_results_df = pd.read_csv(yt_results_file)

    youtube = build(yt_service_name, yt_api_version, developerKey=yt_api_key)

    # Attempt to find existing results
    existing_result_df = yt_results_df[ yt_results_df['query'] == query ]
    print(existing_result_df)

    if existing_result_df.empty:
      print("No existing result found for this query. Asking youtube")
      # Call the search.list method to retrieve results matching the specified
      # query term.
      search_response = youtube.search().list(
          q=query,
          part='id,snippet',
          maxResults=max_results,
          order='relevance',
          type='video',
          # videoDuration='medium',
          # videoLicense='creativeCommon'
      ).execute()

      # Append the new data to it
      theresults = []
      for search_result in search_response.get('items', []):
        print(search_result)
        video_kind = search_result['id']['kind']

        if video_kind == "youtube#video":
          video_title = search_result['snippet']['title']
          video_id = search_result['id']['videoId']
          video_description = search_result['snippet']['description']

          theresults.append([query, video_kind, video_title, video_id, video_description])

      print("At the end of the processing we transform it into a dataframe")
      existing_result_df = get_yt_results_dataframe(theresults)


    else:
      print("Existing results found. returning it")

    print("The results:", existing_result_df)
    return existing_result_df


def find_youtube_video(results_df, used_vids_df):

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    best_video_id = None

    for index, search_result in results_df.iterrows():
        video_kind = search_result['video_kind']
        video_title = search_result['video_title']
        video_id = search_result['video_id']
        video_description = search_result['video_description']
        video_used = video_id in used_vids_df['yt_video_id'].unique()

        print("Video with id {} already used? {}".format(video_id, video_used))

        if not video_used:
            best_video_id = [video_title, video_id, video_description]
            break
        else:
            print("YT video is either not kind video = ({}) or is already used = ({})".format(
                video_kind, video_used))

    print("Best video id: ", best_video_id)
    return best_video_id

def save_youtube_search(query, results_df, dest_file):

  print("Saving youtube search results to ", dest_file)
  yt_results_df = pd.read_csv(dest_file)

  #print("results_df = ", results_df)

  # Concat the dataframe
  yt_results_df = yt_results_df.append(results_df)
  
  # Save the final data
  print("yt_results_df = ", yt_results_df)
  yt_results_df.to_csv(dest_file, index=False)


def blogpost_to_ytvideo(folder, yt_service_name, yt_api_version, yt_api_key, yt_results_file, yt_already_used, max_results=25):
    
    # Loading already used videos
    try:
        used_vids_df = pd.read_csv(yt_already_used)
    except:
        used_vids_df = pd.DataFrame(columns=['yt_video_id'])

    
    # Load the destination file if exists
    yt_results_df = None
    try:
      print("Loading file {}.".format(yt_results_file))
      yt_results_df = pd.read_csv(yt_results_file)
      print("File {} loaded.".format(yt_results_file))
    except FileNotFoundError:
      print("File {} not found. Creating an empty dataframe".format(yt_results_file))
      yt_results_df = get_yt_results_dataframe([]) #pd.DataFrame([], columns=['query', 'video_kind', 'video_title', 'video_id', 'video_description'])
      print("yt_results_df = ", yt_results_df)
      yt_results_df.to_csv(yt_results_file, index=False)


    entries = os.listdir(folder)
    for entry in entries:
        # print(entry)
        try:
            post = frontmatter.load(folder + "/" + entry)
            title = post['title'] if 'title' in post else None
            ytvideo_url = post['youtube_video'] if 'youtube_video' in post else None

            if ytvideo_url is None and title is not None:

                # Get the best video for this query
                search_results = youtube_search(title, yt_service_name, yt_api_version, yt_api_key, yt_results_file, max_results)
                print("search_results = ", search_results)
                
                # Save the results got from youtube
                save_youtube_search(title, search_results, yt_results_file)
                
                # Check that the video is suitable for use
                video_found = find_youtube_video(search_results, used_vids_df)
                video_found_title = video_found[0]
                video_found_id = video_found[1]
                video_found_description = video_found[2]

                print("Saving youtube_video and youtube_video_id tags")
                post['youtube_video'] = "http://www.youtube.com/watch?v={}".format(
                    video_found_id)
                post['youtube_video_id'] = video_found_id
                post['youtube_video_title'] = video_found_title
                post['youtube_video_description'] = video_found_description

                print("Saving the content of the file")
                filecontent = frontmatter.dumps(post)
                with open(folder + "/" + entry, 'w') as f:
                    f.write(filecontent)

                new_yt_video_df = pd.DataFrame(
                    [video_found_id], columns=['yt_video_id'])

                # Add the video to the used videos file
                used_vids_df = pd.concat(
                    [used_vids_df, new_yt_video_df], sort=False)
            else:
                print("Did not process this file because ytvideo_url = url ({}) or title was None ({})".format(
                    ytvideo_url, title))

        except Exception as e:
            print("Error. = ", str(e))

    # Export the result to csv
    used_vids_df.to_csv(yt_already_used, index=False)



# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
folder = os.getenv('INPUT_SRC_FOLDER')
DEVELOPER_KEY = os.getenv('INPUT_YOUTUBE_API_KEY')
yt_already_used = os.getenv('INPUT_YT_ALREADY_USED_VIDS')
yt_results_file = os.getenv('INPUT_YT_SEARCH_RESULTS_FILE')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


#blogpost_to_ytvideo(folder, yt_already_used)
blogpost_to_ytvideo(folder, YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, DEVELOPER_KEY, yt_results_file, yt_already_used)
