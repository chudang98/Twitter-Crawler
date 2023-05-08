import logging

import pytz
import os
import sys
import time
import requests
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + '/../')
import utilities.env_managment as global_env
tz = pytz.timezone('Asia/Ho_Chi_Minh')
time_format = '%Y-%m-%dT%H:%M:%S.%fZ'
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAD%2BUkgEAAAAAxuCobQH%2FAcqOzlk6MitTc3vy9no%3DjtTDVRwOEtPhdJEVP1NVIgCtrTIJGAFVDkv7z3UnfV6mvKOlUG'
header_token = {"Authorization": f"Bearer {bearer_token}"}

def __call_api(api_url, req_params):
  for _ in range(5):
    try:
      response_api = requests.get(
        api_url,
        headers=header_token,
        params=req_params
      )
      if response_api.json().get('status', 0) == 429:
        logging.ERROR("Error limit request Twitter API !!!")
        raise Exception("Limit request Twitter API !!!!!")
    except Exception as e:
      logging.error(f'Error when call API !!!!')
      if response_api.json().get('status', 0) == 429:
        logging.warning('Sleeping 5 minutes...')
        time.sleep(300)
        continue
      else:
        logging.error("Error Tweeter API cannot handle !")
        logging.error(e)
        break
    else:
      logging.warning('Call request success.')
      return response_api

def get_timeline(user_id, next_token=None):
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
  if next_token:
    query_params['pagination_token'] = next_token
  response_api = __call_api(api_timeline, query_params)
  return response_api
  pass

def get_detail_tweet(tweet_id):
  tweet_info_api = f"https://api.twitter.com/2/tweets/{tweet_id}"
  query_param = {
    "tweet.fields": "attachments,in_reply_to_user_id,created_at,author_id,text",
    "expansions": "referenced_tweets.id,referenced_tweets.id.author_id",
    "media.fields": "alt_text,media_key,url,type"
  }
  response_api = __call_api(tweet_info_api, query_param)
  return response_api

def get_profile_twitter(username):
  api_url = f'https://api.twitter.com/2/users/by/username/{username}'
  query_param = {
    "user.fields": "created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld"
  }
  response_api = __call_api(api_url, query_param)
  return response_api

def schema_tweet(page_url, tweet, project_name, medias_ref):
  refer_info = tweet.get('referenced_tweets', [])
  if refer_info:
    refer_tweet = refer_info[0]
    if (refer_tweet.get('type', None) == 'retweeted' or
        refer_tweet.get('type', None) == 'quoted' or
        refer_tweet.get('type', None) == 'replied_to'):
      tweet_id = refer_tweet['id']
      response_reftweet = get_detail_tweet(tweet_id)
      ref_tweet_data = response_reftweet.json()
      if refer_tweet.get('type', None) == 'retweeted':
        tweet_type = 'Retweet'
      elif refer_tweet.get('type', None) == 'quoted':
        tweet_type = 'Quote'
      else:
        tweet_type = "Reply"
      return {
        "link_tweet": f"{page_url}/status/{tweet['id']}",
        "post_date": datetime.strptime(tweet['created_at'], time_format) + timedelta(hours=7),
        "type": tweet_type,
        "content": ref_tweet_data['data']['text'] if refer_tweet.get('type', None) == 'retweeted' else tweet['text'],
        "content_refer": '' if refer_tweet.get('type', None) == 'retweeted' else ref_tweet_data['data']['text'],
        "user_refer": ref_tweet_data['includes']['users'][0]['username'],
        "project": project_name,
        "like": tweet['public_metrics']['like_count'],
        "reply": tweet['public_metrics']['reply_count'],
        "retweet": tweet['public_metrics']['retweet_count'],
        "attachments": [media.get('url', media.get('preview_image_url')) for media in medias_ref if
                        media['media_key'] in tweet.get('attachments', {}).get('media_keys', [])],
        "project_id": tweet['author_id'],
        "update_time": datetime.utcnow() + timedelta(hours=7)
      }
    else:
      logging.warning("Cannot detect this tweet !")
      logging.warning(refer_info)
  else:
    return {
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
      "attachments": [media.get('url', media.get('preview_image_url')) for media in medias_ref if
                      media['media_key'] in tweet.get('attachments', {}).get('media_keys', [])],
      "project_id": tweet['author_id'],
      "update_time": datetime.utcnow() + timedelta(hours=7)
    }

def get_followers(user_id):
  api_timeline = f'https://api.twitter.com/2/users/{user_id}/followers'
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
  pass