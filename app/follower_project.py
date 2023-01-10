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
from utilities.request_twitter import call_api_twitter

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

  bearer_token = 'AAAAAAAAAAAAAAAAAAAAAD%2BUkgEAAAAAxuCobQH%2FAcqOzlk6MitTc3vy9no%3DjtTDVRwOEtPhdJEVP1NVIgCtrTIJGAFVDkv7z3UnfV6mvKOlUG'
  header = {"Authorization": f"Bearer {bearer_token}"}

  gc = gspread.service_account(filename=global_env.KEY_PATH)
  checkpoint_sheet = gc.open_by_url(global_env.SHEET_DATA).worksheet(global_env.CHECKPOINT_SHEET)

  list_of_dicts = checkpoint_sheet.get_all_records()
  for project in list_of_dicts:
    page_url = project.get("Twitter Page")
    name_project = page_url.split("https://twitter.com/")[1]

    #TODO: Init BigQuery client :

    path_auth = global_env.SA_AUTH
    credentials = service_account.Credentials.from_service_account_file(
      path_auth, scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    table_id = 'smiling-mark-368816.twitter_crawler.followers'


    #TODO:  Get id of project

    user_api = f'https://api.twitter.com/2/users/by/username/{name_project}'
    user_api_response = requests.get(user_api, headers=header)
    user_id = user_api_response.json()['data']['id']

    #TODO: Get all tweet of project
    api_followers = f'https://api.twitter.com/2/users/{user_id}/followers'
    query_params = {
      "max_results": 100,
      "user.fields": "created_at"
    }
    response = requests.get(
      api_followers,
      headers=header,
      params=query_params
    )
    while True:
      response = call_api_twitter(api_followers, header, query_params)
      data = response['data']
      data_process = [
        {
          "follower_id": user['id'],
          "username": user['username'],
          "name": user['name'],
          "created_date": datetime.strptime(user['created_at'], time_format) + timedelta(hours=7),
          "project_follow": project,
          "project_id": user_id
        } for user in data
      ]
      # TODO: Save data here
      df = pandas.DataFrame(data_process)
      client.load_table_from_dataframe(
        df,
        table_id
      )

      # TODO: Check DONE condition
      meta_token = response.json().get('meta', None)
      print(meta_token['next_token'])
      if meta_token.get('next_token', None) is None:
        print('Done !!!')
        break
      response = requests.get(
        api_followers,
        headers=header,
        params={
          **query_params,
          "pagination_token": meta_token['next_token']
        }
      )



