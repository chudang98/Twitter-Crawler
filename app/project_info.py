import argparse
import requests
import logging
import argparse
import gspread
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
import pytz
import os
import sys
import time
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + '/../')
import utilities.env_managment as global_env

tz = pytz.timezone('Asia/Ho_Chi_Minh')

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description="Parameters for crawl tweet of channel."
  )
  parser.add_argument("--project", help="Name of project")
  args = parser.parse_args()
  time_format = '%Y-%m-%dT%H:%M:%S.%fZ'
  # project = (
  #   args.project
  # )
  tz = pytz.timezone('Asia/Ho_Chi_Minh')

  bearer_token = global_env.API_TOKEN
  header = {"Authorization": f"Bearer {bearer_token}"}

  gc = gspread.service_account(filename=global_env.KEY_PATH)
  sheet_data = gc.open_by_url(global_env.SHEET_DATA).worksheet('Thông tin dự án')
  checkpoint_sheet = gc.open_by_url(global_env.SHEET_DATA).worksheet(global_env.CHECKPOINT_SHEET)

  list_of_dicts = checkpoint_sheet.get_all_records()

  #TODO: Init BigQuery client :

  # path_auth = global_env.SA_AUTH
  # credentials = service_account.Credentials.from_service_account_file(
  #   path_auth, scopes=["https://www.googleapis.com/auth/cloud-platform"],
  # )
  # client = bigquery.Client(credentials=credentials, project=credentials.project_id)
  # table_id = 'smiling-mark-368816.twitter_crawler.projects'

  time_update = datetime.utcnow() + timedelta(hours=7)
  query_param = {
    "user.fields": "created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld"
  }
  data_insert = []
  for project in list_of_dicts:
    page_url = project.get("Twitter Page")
    name_project = page_url.split("https://twitter.com/")[1]
    project_name = project.get("Project Name")
    api = f'https://api.twitter.com/2/users/by/username/{name_project}'
    res = requests.get(
      api,
      headers=header,
      params=query_param
    )
    data = res.json()
    try:
      project_info = data.get('data')
    except Exception as e:
      print("Have error !!!!!!!")
      print(e)
      if data.get('status', 0) == 429:
        print("Sleeping 15 minutes...")
        time.sleep(900)
        res = requests.get(
          api,
          headers=header,
          params=query_param
        )
        data = res.json()
        project_info = data.get('data')
    data_insert.append({
      'id': project_info['id'],
      'name': project_info['name'],
      'url': page_url,
      'username': project_info['username'],
      'follower': project_info['public_metrics']['followers_count'],
      'following': project_info['public_metrics']['following_count'],
      'tweet': project_info['public_metrics']['tweet_count'],
      'join_date': datetime.strptime(project_info['created_at'], time_format) + timedelta(hours=7),
      'verified': project_info['verified']
    })
  sheet_data.update(f'A2:E',
                    [[
                      project['name'],
                      (project['join_date']).strftime("%Y-%m-%d %H:%M:%S"),
                      project['following'],
                      project['follower'],
                      project['tweet']
                    ] for project in data_insert])
  # df = pandas.DataFrame(data_insert)
  # client.load_table_from_dataframe(
  #   df,
  #   table_id
  # )
  # client.close()


