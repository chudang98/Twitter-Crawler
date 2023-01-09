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
  project = 'Nexon Finance'
  tz = pytz.timezone('Asia/Ho_Chi_Minh')

  bearer_token = 'AAAAAAAAAAAAAAAAAAAAAD%2BUkgEAAAAAxuCobQH%2FAcqOzlk6MitTc3vy9no%3DjtTDVRwOEtPhdJEVP1NVIgCtrTIJGAFVDkv7z3UnfV6mvKOlUG'
  header = {"Authorization": f"Bearer {bearer_token}"}

  gc = gspread.service_account(filename=global_env.KEY_PATH)
  checkpoint_sheet = gc.open_by_url(global_env.SHEET_DATA).worksheet(global_env.CHECKPOINT_SHEET)
  # sheet_data = gc.open_by_url(global_env.SHEET_DATA).worksheet(project)

  list_of_dicts = checkpoint_sheet.get_all_records()
  config_project = next((x for x in list_of_dicts if x.get('Project Name') == project), None)
  # page_url = config_project.get("Twitter Page")
  # name_project = page_url.split("https://twitter.com/")[1]

  #TODO: Init BigQuery client :
  path_auth = global_env.SA_AUTH
  credentials = service_account.Credentials.from_service_account_file(
    path_auth, scopes=["https://www.googleapis.com/auth/cloud-platform"],
  )
  client = bigquery.Client(credentials=credentials, project=credentials.project_id)
  table_id = 'smiling-mark-368816.twitter_crawler.twitter_posts'
  time_update = datetime.utcnow() + timedelta(hours=7)

  for project in list_of_dicts:
    page_url = project.get("Twitter Page")
    name_project = page_url.split("https://twitter.com/")[1]
    project_name = project.get("Project Name")
    #TODO:  Get id of project
    user_api = f'https://api.twitter.com/2/users/by/username/{name_project}'
    user_api_response = requests.get(user_api, headers=header)
    user_id = user_api_response.json()['data']['id']

    #TODO: Get all tweet of project
    api_timeline = f'https://api.twitter.com/2/users/{user_id}/tweets'
    query_params = {
      "max_results": 50,
      # "max_results": 100,
      "expansions": "attachments.media_keys",
      # "expansions": "attachments.media_keys,author_id,referenced_tweets.id,referenced_tweets.id.author_id",
      # "tweet.fields": "attachments,author_id,created_at,edit_history_tweet_ids,id,public_metrics,text,in_reply_to_user_id",
      "tweet.fields": "attachments,author_id,created_at,entities,id,in_reply_to_user_id,lang,public_metrics,referenced_tweets,text",
      "media.fields": "media_key,preview_image_url,url",
      # "poll.fields": "duration_minutes,end_datetime,id,options,voting_status",
      "user.fields": "id,name,username,url"
    }
    try:
      response_timeline = requests.get(
        api_timeline,
        headers=header,
        params=query_params
      )
      data = response_timeline.json()['data']
    except Exception as e:
      print('Have error !!!!')
      print(e)
      if response_timeline.json().get('status', 0) == 429:
        print('Sleep 15 minutes....')
        time.sleep(900)
        response_timeline = requests.get(
          api_timeline,
          headers=header,
          params=query_params
        )
        data = response_timeline.json()['data']
    medias = response_timeline.json().get('includes', {}).get('media', [])
    meta_token = response_timeline.json().get('meta', None)
    index_sheet = 2
    # result_tmp = [[f"{page_url}/status/{i['id']}", (datetime.strptime(i['created_at'], time_format) + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S"), i['text']] for i in data]
    # sheet_data.update(f'A{index_sheet}:I', result_tmp)
    # index_sheet += len(data)
    while True:
      # time.sleep(30)
      append_data = []
      for tweet in data:
        # TODO: Get detail retweet :
        refers_info = tweet.get('referenced_tweets', [])
        if refers_info:
          is_saved = False
          for refer_tweet in refers_info:
            if refer_tweet.get('type', None) == 'retweeted':
              retweet_id = refer_tweet['id']
              tweet_info_api = f"https://api.twitter.com/2/tweets/{retweet_id}"
              param = {
                "tweet.fields": "attachments,in_reply_to_user_id,created_at,author_id,text",
                "expansions": "referenced_tweets.id,referenced_tweets.id.author_id",
                "media.fields": "alt_text,media_key,url,type"
              }
              try:
                retweet = requests.get(tweet_info_api, headers=header, params=param)
                response_data = retweet.json()
                data = response_data['data']
              except Exception as e:
                print('Have error !!!!')
                print(e)
                if response_data.get('status', 0) == 429:
                  print('Sleep 15 minutes....')
                  time.sleep(900)
                  retweet = requests.get(tweet_info_api, headers=header, params=param)
                  response_data = retweet.json()
              # append_data.append([
              #   f"{page_url}/status/{tweet['id']}",
              #   (datetime.strptime(tweet['created_at'], time_format) + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
              #   'Retweet',
              #   response_data['data']['text'],
              #   '',
              #   response_data['includes']['users'][0]['name'],
              #   response_data['includes']['users'][0]['username']
              # ])
              append_data.append({
                "link_tweet": f"{page_url}/status/{tweet['id']}",
                "post_date": datetime.strptime(tweet['created_at'], time_format) + timedelta(hours=7),
                "type": 'Retweet',
                "content": response_data['data']['text'],
                "content_refer": '',
                "user_refer": response_data['includes']['users'][0]['username'],
                "project": project_name,
                "like": tweet['public_metrics']['like_count'],
                "reply": tweet['public_metrics']['reply_count'],
                "retweet": tweet['public_metrics']['retweet_count'],
                "attachments": [media.get('url', media.get('preview_image_url')) for media in medias if
                                media['media_key'] in tweet.get('attachments', {}).get('media_keys', [])],
                "update_time": time_update,
                "project_id": tweet['author_id']
              })
              is_saved = True
            elif refer_tweet.get('type', None) == 'quoted':
              quoted_tweet_id = refer_tweet['id']
              tweet_info_api = f"https://api.twitter.com/2/tweets/{quoted_tweet_id}"
              param = {
                "tweet.fields": "attachments,in_reply_to_user_id,created_at,author_id,text",
                "expansions": "referenced_tweets.id,referenced_tweets.id.author_id",
                "media.fields": "alt_text,media_key,url,type"
              }
              try:
                quoted_tweet = requests.get(tweet_info_api, headers=header, params=param)
                response_data = quoted_tweet.json()
                data_json = response_data['data']
              except Exception as e:
                print('Have error !!!!')
                print(e)
                if response_data.get('status', 0) == 429:
                  print('Sleep 15 minutes....')
                  time.sleep(900)
                  quoted_tweet = requests.get(tweet_info_api, headers=header, params=param)
                  response_data = quoted_tweet.json()
              # append_data.append([
              #   f"{page_url}/status/{tweet['id']}",
              #   (datetime.strptime(tweet['created_at'], time_format) + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
              #   'Quote',
              #   tweet['text'],
              #   response_data['data']['text'],
              #   response_data['includes']['users'][0]['name'],
              #   response_data['includes']['users'][0]['username']
              # ])
              append_data.append({
                "link_tweet": f"{page_url}/status/{tweet['id']}",
                "post_date": datetime.strptime(tweet['created_at'], time_format) + timedelta(hours=7),
                "type": 'Quote',
                "content": tweet['text'],
                "content_refer": response_data['data']['text'],
                "user_refer": response_data['includes']['users'][0]['username'],
                "project": project_name,
                "like": tweet['public_metrics']['like_count'],
                "reply": tweet['public_metrics']['reply_count'],
                "retweet": tweet['public_metrics']['retweet_count'],
                "attachments": [media.get('url', media.get('preview_image_url')) for media in medias if
                                media['media_key'] in tweet.get('attachments', {}).get('media_keys', [])],
                "project_id": tweet['author_id'],
                "update_time": time_update
              })
              is_saved = True
            elif refer_tweet.get('type', None) == 'replied_to':
              break
              reply_tweet_id = refer_tweet['id']
              tweet_info_api = f"https://api.twitter.com/2/tweets/{reply_tweet_id}"
              param = {
                "tweet.fields": "attachments,in_reply_to_user_id,created_at,author_id,text",
                "expansions": "referenced_tweets.id,referenced_tweets.id.author_id",
                "media.fields": "alt_text,media_key,url,type"
              }
              quoted_tweet = requests.get(tweet_info_api, headers=header, params=param)
              response_data = quoted_tweet.json()
              if not response_data.get('data', None):
                reply_tweet_id = tweet['conversation_id']
                tweet_info_api = f"https://api.twitter.com/2/tweets/{reply_tweet_id}"
                param = {
                  "tweet.fields": "attachments,in_reply_to_user_id,created_at,author_id,text",
                  "expansions": "referenced_tweets.id,referenced_tweets.id.author_id",
                  "media.fields": "alt_text,media_key,url,type"
                }
                quoted_tweet = requests.get(tweet_info_api, headers=header, params=param)
                response_data = quoted_tweet.json()
              append_data.append([
                f"{page_url}/status/{tweet['id']}",
                (datetime.strptime(tweet['created_at'], time_format) + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
                'Reply',
                tweet['text'],
                response_data['data']['text'],
                response_data['includes']['users'][0]['name'],
                response_data['includes']['users'][0]['username']
              ])
              is_saved = True
          if not is_saved:
            append_data.append({
              "link_tweet": f"{page_url}/status/{tweet['id']}",
              "post_date": datetime.strptime(tweet['created_at'], time_format) + timedelta(hours=7),
              "type": 'Tweet',
              "content": tweet['text'],
              "content_refer": '',
              "user_refer": '',
              "project": project_name,
              "like": tweet['public_metrics']['like_count'],
              "reply": tweet['public_metrics']['reply_count'],
              "retweet": tweet['public_metrics']['retweet_count'],
              "attachments": [media.get('url', media.get('preview_image_url')) for media in medias if
                              media['media_key'] in tweet.get('attachments', {}).get('media_keys', [])],
              "project_id": tweet['author_id'],
              "update_time": time_update
            })
        else:
          # append_data.append([
          #   f"{page_url}/status/{tweet['id']}",
          #   (datetime.strptime(tweet['created_at'], time_format) + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
          #   'Tweet',
          #   tweet['text'],
          #   '',
          #   '',
          #   ''
          # ])
          append_data.append({
            "link_tweet": f"{page_url}/status/{tweet['id']}",
            "post_date": datetime.strptime(tweet['created_at'], time_format) + timedelta(hours=7),
            "type": 'Tweet',
            "content": tweet['text'],
            "content_refer": '',
            "user_refer": '',
            "project": project_name,
            "like": tweet['public_metrics']['like_count'],
            "reply": tweet['public_metrics']['reply_count'],
            "retweet": tweet['public_metrics']['retweet_count'],
            "attachments": [media.get('url', media.get('preview_image_url')) for media in medias if media['media_key'] in tweet.get('attachments', {}).get('media_keys', [])],
            "project_id": tweet['author_id'],
            "update_time": time_update
          })
      df = pandas.DataFrame(append_data)
      client.load_table_from_dataframe(
        df,
        table_id
      )
      # sheet_data.update(f'A{index_sheet}:I', append_data)
      index_sheet += len(append_data)

      # result_tmp = [[f"{page_url}/status/{i['id']}", (datetime.strptime(i['created_at'], time_format) + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S"), i['text']] for i in data]
      # sheet_data.update(f'A{index_sheet}:I', result_tmp)
      # total += len(result_tmp)
      # index_sheet += len(result_tmp)
      print(index_sheet)
      if meta_token.get('next_token', None) is None:
        print('Done !!!')
        break
      next_page_response_timeline = requests.get(
        api_timeline,
        headers=header,
        params={**query_params,
                "pagination_token": meta_token['next_token']
                }
                # } if meta_token.get('next_token', None) is not None else query_params
      )
      try:
        data = next_page_response_timeline.json()['data']
        medias = next_page_response_timeline.json().get('includes', {}).get('media', [])
        meta_token = next_page_response_timeline.json().get('meta', None)
      except Exception as e:
        print('Have error !!!!')
        print(e)
        if response_timeline.json().get('status', 0) == 429:
          print('Sleep 15 minutes....')
          time.sleep(900)
          next_page_response_timeline = requests.get(
            api_timeline,
            headers=header,
            params={**query_params,
                    "pagination_token": meta_token['next_token']
                    }
            # } if meta_token.get('next_token', None) is not None else query_params
          )
          data = next_page_response_timeline.json()['data']
          medias = next_page_response_timeline.json().get('includes', {}).get('media', [])
          meta_token = next_page_response_timeline.json().get('meta', None)

  client.close()