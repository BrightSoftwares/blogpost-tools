import pandas as pd
import numpy as np
from ecommercetools import seo
import datetime
import os

# Inspiration
# https://practicaldatascience.co.uk/data-science/how-to-identify-seo-keyword-opportunities-with-python

def in_title(row):
    if row['title'] is None:
        return 0
    if str(row['query']) in row['title'].lower():
        return 1
    else:
        return 0

def in_subheading(row, subheading):
    subheading_name = "{}s".format(subheading)
    
    if row[subheading_name] is None:
        return 0
    if str(row['query']) in row[subheading_name].lower():
        return 1
    else:
        return 0
        
def in_h1s(row):
    return in_subheading(row, "h1")
    
def in_h2s(row):
    return in_subheading(row, "h2")
    
def in_h3s(row):
    return in_subheading(row, "h3")
    
def in_h4s(row):
    return in_subheading(row, "h4")
    
def in_h5s(row):
    return in_subheading(row, "h5")
    
def in_h6s(row):
    return in_subheading(row, "h6")

def in_description(row):
    if row['description'] is None:
        return 0

    if str(row['query']) in str(row['description']).lower():
        return 1 
    else:
        return 0

def scrape_website(sitemap_url, dry_run):
  if dry_run == 'true':
    print("In dry run mode, not scraping!")
  else:
    df_sitemap = seo.get_sitemap(sitemap_url)
    #df_sitemap.head()

    df_pages = seo.scrape_site(df_sitemap, 'loc', verbose=False)
    #df_pages.head()

    df_pages.to_csv("scraped_data.csv")

def generate_optimizations(sitemap_url, service_account_json_file_path, site_url, start_date, end_date):

  print("Generating SEO optimizations for {} with json file {} and website {} from {} to {}.".format(sitemap_url, service_account_json_file_path, site_url, start_date, end_date))
  
  # Load the scraped data
  df_pages = pd.read_csv("scraped_data.csv")

  payload = {
      'startDate': start_date, 
      'endDate': end_date,
      'dimensions': ['page', 'query'],  
      'rowLimit': 10000,
      'startRow': 0
  }

  print("Getting the data from google search console")
  sc_df = seo.query_google_search_console(service_account_json_file_path, site_url, payload)


  #sc_df = pd.read_csv(search_console_path)

  print("Data from Google search console", sc_df)

  df = sc_df.sort_values(by=['page', 'impressions'], ascending=False)
  df = df.drop_duplicates(subset='page', keep='first')
  df.sort_values(by='page').head()

  print("Merging scraped data with Google search console one")
  df_all = df_pages.merge(df, how='left', left_on='url', right_on='page')

  print("Generating no traffic data")
  df_no_traffic = df_all[df_all['query'].isnull()].fillna(0)
  df_no_traffic.to_csv('no_traffic.csv', index=False)
  df_no_traffic.head()

  print("Generating traffic data (where query is not null)")
  print(df_all)
  df_traffic = df_all[df_all['query'].notnull()]
  del df_traffic['page']
  df_traffic.sort_values(by='impressions', ascending=False).head()

  in_title_df = df_traffic.apply(in_title, axis=1)
  in_title_df = in_title_df if not in_title_df.empty else []
  print("In title df=", in_title_df)

  in_description_df = df_traffic.apply(in_description, axis=1)
  in_description_df = in_description_df if not in_description_df.empty else []
  print("In description df=", in_description_df)
  
  in_h1s_df = df_traffic.apply(in_h1s, axis=1)
  in_h1s_df = in_h1s_df if not in_h1s_df.empty else []
  print("In h1s df=", in_h1s_df)
  
  in_h2s_df = df_traffic.apply(in_h2s, axis=1)
  in_h2s_df = in_h2s_df if not in_h2s_df.empty else []
  print("In h2s df=", in_h2s_df)
  
  in_h3s_df = df_traffic.apply(in_h3s, axis=1)
  in_h3s_df = in_h3s_df if not in_h3s_df.empty else []
  print("In h3s df=", in_h3s_df)
  
  in_h4s_df = df_traffic.apply(in_h4s, axis=1)
  in_h4s_df = in_h4s_df if not in_h4s_df.empty else []
  print("In h4s df=", in_h4s_df)
  
  in_h5s_df = df_traffic.apply(in_h5s, axis=1)
  in_h5s_df = in_h5s_df if not in_h5s_df.empty else []
  print("In h5s df=", in_h5s_df)
  
  in_h6s_df = df_traffic.apply(in_h6s, axis=1)
  in_h6s_df = in_h6s_df if not in_h6s_df.empty else []
  print("In h6s df=", in_h6s_df)

  df_traffic = df_traffic.assign(in_title=in_title_df)
  df_traffic = df_traffic.assign(in_description=in_description_df)
  df_traffic = df_traffic.assign(in_h1s=in_h1s_df)
  df_traffic = df_traffic.assign(in_h2s=in_h2s_df)
  df_traffic = df_traffic.assign(in_h3s=in_h3s_df)
  df_traffic = df_traffic.assign(in_h4s=in_h4s_df)
  df_traffic = df_traffic.assign(in_h5s=in_h5s_df)
  df_traffic = df_traffic.assign(in_h6s=in_h6s_df)
  df_traffic['in_both'] = np.where(df_traffic['in_title'] + df_traffic['in_description'] == 2, 1, 0)

  df_traffic.to_csv('traffic.csv', index=False)
  df_traffic.head()

  print("Generating the to pages to optimized in priority")
  print("Sorting the data by in both asc")
  df_optimize_priority = df_traffic.sort_values(by='in_both', ascending=True).head(50)
  df_optimize_priority.drop('paragraphs', inplace=True, axis=1)

  print("Reorganizing the columns")
  df_optimize_priority = df_optimize_priority[["url", "query", "clicks", "impressions", "ctr", "position", "in_title", "in_description", "in_h1s", "in_h2s", "in_h3s", "in_h4s", "in_h5s", "in_h6s", "in_both", "hreflang", "generator", "title", "description", "h1s", "h2s", "h3s", "h4s", "h5s", "h6s", "absolute_links", "canonical", "robots"]]
  df_optimize_priority.to_csv("to_optimize_priority.csv")



sitemap_url = os.getenv("INPUT_SITEMAP_URL") #'https://bright-softwares.com/sitemap.xml'
service_account_json_file_path = os.getenv("INPUT_SERVICE_ACCOUNT_JSON_FILE_PATH") # "/content/drive/MyDrive/ColabFiles/search_console/bright-softwares.com/blog-post-and-keywords-da04acec6e8a.secret.json" #"/content/drive/MyDrive/ColabFiles/search_console/bright-softwares.com/blog-post-and-keywords-2d8a34163543.json"
dry_run = os.getenv("INPUT_DRY_RUN", 'true') # 'true'
date_offset = int(os.getenv("INPUT_DATE_OFFSET", "-1")) # -1
date_duration = int(os.getenv("INPUT_DATE_DURATION", "-90")) # -90

site_url = os.getenv("INPUT_SITE_URL") # "sc-domain:bright-softwares.com"

# Convert this input relative dates
#start_date = '2021-01-01'
#end_date = '2022-06-31'
end_date = datetime.date.today() + datetime.timedelta(days=date_offset)
start_date = datetime.date.today() + datetime.timedelta(days=(date_offset + date_duration))
print(start_date)
print(end_date)

scrape_website(sitemap_url, dry_run)

generate_optimizations(sitemap_url, service_account_json_file_path, site_url, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

