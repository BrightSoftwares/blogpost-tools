import os
import frontmatter
import pandas as pd

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = os.getenv('INPUT_YOUTUBE_API_KEY')
yt_already_used = os.getenv('INPUT_YT_ALREADY_USED_VIDS')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def youtube_search(query, max_results=25):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    # Load the already used youtube videos
    used_vids_df = pd.read_csv(yt_already_used)

    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        maxResults=max_results,
        order='viewCount',
        # videoDuration='medium',
        # videoLicense='creativeCommon'
    ).execute()

    # videos = []
    # channels = []
    # playlists = []

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    best_video_id = None

    for search_result in search_response.get('items', []):
        video_kind = search_result['id']['kind']
        video_title = search_result['snippet']['title']
        video_id = search_result['id']['videoId']
        video_used = video_id in used_vids_df['yt_video_id'].unique()

        print("Video with id {} already used? {}".format(video_id, video_used))

        if video_kind == 'youtube#video' and not video_used:
            # videos.append('%s (%s)' % (search_result['snippet']['title'],
            #                            search_result['id']['videoId']))
            best_video_id = [video_title, video_id]

            # We return the one that suits our needs
            break
        # elif search_result['id']['kind'] == 'youtube#channel':
        #     channels.append('%s (%s)' % (search_result['snippet']['title'],
        #                                  search_result['id']['channelId']))
        # elif search_result['id']['kind'] == 'youtube#playlist':
        #     playlists.append('%s (%s)' % (search_result['snippet']['title'],
        #                                   search_result['id']['playlistId']))
        else:
            print("YT video is either not kind video = ({}) or is already used = ({})".format(
                video_kind, video_used))

    # print('Videos:\n', '\n'.join(videos), '\n')
    # print('Channels:\n', '\n'.join(channels), '\n')
    # print('Playlists:\n', '\n'.join(playlists), '\n')
    print("Best video id: ", best_video_id)
    return best_video_id


def blogpost_to_ytvideo():
    folder = os.getenv('INPUT_DRAFTS_PATH')

    try:
        used_vids_df = pd.read_csv(yt_already_used)
    except:
        used_vids_df = pd.DataFrame(columns=['yt_video_id'])

    entries = os.listdir(folder)
    for entry in entries:
        # print(entry)
        try:
            post = frontmatter.load(folder + "/" + entry)
            title = post['title'] if 'title' in post else None
            ytvideo_url = post['youtube_video'] if 'youtube_video' in post else None

            if ytvideo_url is None and title is not None:

                # Get the best video for this query
                video_found = youtube_search(title)
                video_found_id = video_found[1]

                print("Saving youtube_video and youtube_video_id tags")
                post['youtube_video'] = "http://www.youtube.com/watch?v={}".format(
                    video_found_id)
                post['youtube_video_id'] = video_found_id

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


# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--q', help='Search term', default='Google')
#     parser.add_argument('--max-results', help='Max results', default=25)
#     args = parser.parse_args()

#     try:
#         youtube_search(args)
#     except HttpError as e:
#         print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))

blogpost_to_ytvideo()
