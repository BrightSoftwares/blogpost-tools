import os
import json
import frontmatter
import pandas as pd

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from pyunsplash import PyUnsplash
import cloudinary
import cloudinary.uploader
import cloudinary.api
import requests



def get_unsplash_results_dataframe(obj_array):
  return pd.DataFrame(obj_array, columns=['query', 'photo_id', 'photo_link'])

def search_unsplash_image(query, api_access_key, results_file, max_results):

    # Load the results youtube videos
    print("Results file to load", results_file)
    results_df = pd.read_csv(results_file)

    # Attempt to find existing results
    existing_result_df = results_df[ results_df['query'] == query ]
    print(existing_result_df)

    if existing_result_df.empty:
      print("No existing result found for this query. Asking unsplash ...")

      pu = PyUnsplash(api_key=api_access_key)

      # Append the new data to it
      theresults = []

      #photos = pu.photos(type_='random', count=max_results, query=query, orientation='landscape')
      #photos = pu.search(type_='photos', per_page=max_results, query=query)
      url = "https://api.unsplash.com/search/photos?page=1&query={}&client_id={}&orientation=landscape&per_page={}".format(query, api_access_key, max_results)

      params = dict()

      resp = requests.get(url=url, params=params)
      data = resp.json() # Check the JSON Response Content documentation below
      print(data)

      for photo in data['results']:
        print(photo)
        print(photo['id'], photo['links']['download'])
        theresults.append([query, photo['id'], photo['links']['download']])
        #theresults = pd.concat([theresults, [query, photo['id'], photo['links']['download']]])

      print("At the end of the processing we transform it into a dataframe")
      existing_result_df = get_unsplash_results_dataframe(theresults)
      
      # Save the results got from youtube
      save_unsplash_search(query, existing_result_df, results_file)


    else:
      print("Existing results found. returning it")

    print("The results:", existing_result_df)
    return existing_result_df


def find_best_item(results_df, used_vids_df):

    print("Remove the used videos from the results")
    print("results_df size", results_df.shape)
    print("used_vids_df size", used_vids_df.shape)

    values_list = used_vids_df['item_id']
    #print("Values list", values_list)

    boolean_series = ~results_df.photo_id.isin(values_list)
    #print("boolean_series", boolean_series)

    results_notused_df = results_df[boolean_series]
    #print("results_notused_df size", results_notused_df.shape)

    best_item_id = results_notused_df.head(1) if len(results_notused_df) > 0 else None

    print("Best video id: ", best_item_id)
    return best_item_id

def save_unsplash_search(query, results_df, dest_file):

  print("Saving unsplash search results to ", dest_file)
  unsplash_results_df = pd.read_csv(dest_file)

  #print("results_df = ", results_df)

  # Concat the dataframe
  unsplash_results_df = unsplash_results_df.append(results_df)
  #unsplash_results_df = pd.concat([unsplash_results_df, results_df])
  unsplash_results_df.drop_duplicates(inplace=True)
  
  # Save the final data
  print("unsplash_results_df = ", unsplash_results_df)
  unsplash_results_df.to_csv(dest_file, index=False)


def upload_image_to_cloudinary(photo_id, photo_link, cloudinary_dest_folder, cloudinary_transformation):
  config = cloudinary.config(secure=True)
  #print("****1. Set up and configure the SDK:****\nCredentials: ", config.cloud_name, config.api_key, "\n")

  # Upload the image.
  # Set the asset's public ID and allow overwriting the asset with new versions
  upload_response = cloudinary.uploader.upload(photo_link, folder = cloudinary_dest_folder, public_id = photo_id, unique_filename = False, overwrite=True)
  print("upload_response = ", upload_response)
  print("upload_response public id = ", upload_response['public_id'])

  # Build the URL for the image and save it in the variable 'srcURL'
  srcURL = cloudinary.CloudinaryImage(upload_response['public_id']).build_url(transformation=[cloudinary_transformation])

  # Log the image URL to the console. 
  # Copy this URL in a browser tab to generate the image on the fly.
  print("****2. Upload an image****\nDelivery URL: ", srcURL, "\n")

  return srcURL


def unsplash_to_cloudinary(folder, api_access_key, results_file, already_used_csv, cloudinary_dest_folder, cloudinary_transformation, max_results=10):
    
    # Loading already used videos
    try:
        used_vids_df = pd.read_csv(already_used_csv)
    except:
        used_vids_df = pd.DataFrame(columns=['item_id'])

    
    # Load the destination file if exists
    results_df = None
    try:
      print("Loading file {}.".format(results_file))
      results_df = pd.read_csv(results_file)
      print("File {} loaded.".format(results_file))
    except FileNotFoundError:
      print("File {} not found. Creating an empty dataframe".format(results_file))
      results_df = get_unsplash_results_dataframe([])
      print("results_df = ", results_df)
      results_df.to_csv(results_file, index=False)


    entries = os.listdir(folder)
    for entry in entries:
        print("Processing entry {} and folder {}".format(entry, folder))
        try:
            post = frontmatter.load(folder + "/" + entry)
            title = post['title'] if 'title' in post else None
            image_search_query = post['image_search_query'] if 'image_search_query' in post else None
            silot_terms = post['silot_terms'] if 'silot_terms' in post else None
            image_search_query = silot_terms if image_search_query is None else image_search_query
            image = post['image'] if 'image' in post else None
            #image = None
            #ytvideo_url = post['youtube_video'] if 'youtube_video' in post else None

            if (image is None or image == "null") and image_search_query is not None:

                # Get the best video for this query
                search_results = search_unsplash_image(image_search_query, api_access_key, results_file, max_results)
                print("search_results = ", search_results)
                
                # Save the results got from youtube
                #save_youtube_search(title, search_results, yt_results_file)
                
                # Check that the video is suitable for use
                cloudinary_image_url = None
                video_found_df = find_best_item(search_results, used_vids_df)

                if video_found_df is not None:
                  photo_id = video_found_df.iloc[0]['photo_id']
                  photo_link = video_found_df.iloc[0]['photo_link']
                  #video_found_description = video_found_df.iloc[0]['video_description']
  
                  print(">>>>> photo_id = ", photo_id)
  
                  print("Saving unsplash photos url as image url")
  
                  print("Upload photo link to cloudinary", photo_link)
                  cloudinary_image_url = upload_image_to_cloudinary(photo_id, photo_link, cloudinary_dest_folder, cloudinary_transformation)
                else:
                  print("find_best_item = None :(. No image found. Try to add a 'image_search_query' in the frontmatter to search for another image.")

                # Saving the image
                post['image'] = cloudinary_image_url

                print("Saving the content of the file")
                filecontent = frontmatter.dumps(post)
                with open(folder + "/" + entry, 'w') as f:
                    f.write(filecontent)

                new_items_df = pd.DataFrame(
                    [photo_id], columns=['item_id'])

                # Add the video to the used videos file
                used_vids_df = pd.concat(
                    [used_vids_df, new_items_df], sort=False)
            else:
                print("Did not process this file because image is NOT None ({}) or silot_terms is None ({})".format(
                    image, silot_terms))

        except Exception as e:
            print("Error. = ", str(e))

    # Export the result to csv
    used_vids_df.drop_duplicates(inplace=True)
    used_vids_df.to_csv(already_used_csv, index=False)



# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
folder = os.getenv('INPUT_SRC_FOLDER')
DEVELOPER_KEY = os.getenv('INPUT_UNSPLASH_ACCESS_KEY')
already_used_items = os.getenv('INPUT_ALREADY_USED_ITEMS')
results_file = os.getenv('INPUT_SEARCH_RESULTS_FILE')
max_results = os.getenv('INPUT_MAX_RESULTS', 30)
cloudinary_dest_folder = os.getenv('INPUT_CLOUDINARY_DESTFOLDER', 'blog')
cloudinary_transformation = os.getenv('INPUT_CLOUDINARY_TRANSFORMATION', 'BlogImage')
#YOUTUBE_VIDEO_DURATION = os.getenv('INPUT_YOUTUBE_VIDEO_DURATION', 'any')
#YOUTUBE_API_SERVICE_NAME = 'youtube'
#YOUTUBE_API_VERSION = 'v3'


unsplash_to_cloudinary(folder, DEVELOPER_KEY, results_file, already_used_items, cloudinary_dest_folder, cloudinary_transformation, max_results)
