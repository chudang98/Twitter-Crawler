import pandas
import pytz
import os
import sys
import logging
import argparse
import re

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + '/../')
from utilities.env_managment import PROJECT_STATUS
import utilities.bigquery as bq_utils
import utilities.twitter_api as twitter_api
import utilities.mongodb_utils as mongo_utils
tz = pytz.timezone('Asia/Ho_Chi_Minh')

def get_timeline_user_toBQ(project_url, table_id):
  logging.warning(f"Start get timeline of project url {project_url}")
  username = re.search('(?<=\/\/twitter.com\/)([a-zA-Z0-9]*)', project_url).group()
  profile_response = twitter_api.get_profile_twitter(username)
  user_id = profile_response.json()['data']['id']
  logging.warning(f"User id is {user_id}")
  logging.warning("Creating client BigQuery...")
  client_BQ = bq_utils.create_client()
  # TODO: Get userinfo
  # response_user_info = twitter_api.get_profile_twitter(user_id)
  # user_info = response_user_info.json().get('data')

  # TODO: Get timeline of user
  response_timeline = twitter_api.get_timeline(user_id)
  while True:
    data = response_timeline.json()['data']
    medias_ref = response_timeline.json().get('includes', {}).get('media', [])
    append_data = []
    for tweet in data:
      append_data.append(
        twitter_api.schema_tweet(f'https://twitter.com/{username}', tweet, username, medias_ref)
      )
    logging.warning("Start create dataframe from pandas...")
    #TODO: Get timeline return None object
    tweet_data = [x for x in append_data if x is not None]
    df = pandas.DataFrame(tweet_data)
    client_BQ.load_table_from_dataframe(
        df,
        table_id
    )
    logging.warning(f"Saved {len(append_data)} record.")
    next_token = response_timeline.json().get('meta', {}).get('next_token', None)
    if next_token:
      logging.warning("Have next token, continue call API...")
      response_timeline = twitter_api.get_timeline(user_id, next_token)
    else:
      logging.warning("Done get timeline !")
      return


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description="Parameters for crawl tweet of channel."
  )
  parser.add_argument("--project_url", help="Url of project")
  parser.add_argument("--table_id", help="BigQuery table id")
  parser.add_argument("--project_id", help="BigQuery table id")
  args = parser.parse_args()
  project_url, table_id, project_id = (
    args.project_url,
    args.table_id,
    args.project_id
  )
  if project_id:
    mongo_utils.update_status(project_id, PROJECT_STATUS['running'])
  get_timeline_user_toBQ(project_url, table_id)
  if project_id:
    mongo_utils.update_status(project_id, PROJECT_STATUS['done'])
