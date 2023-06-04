import pandas
import pytz
import os
import sys
import logging
import argparse
import re
import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + '/../')
from utilities.env_managment import PROJECT_STATUS
import utilities.bigquery as bq_utils
import utilities.twitter_api as twitter_api
import utilities.mongodb_utils as mongo_utils
tz = pytz.timezone('Asia/Ho_Chi_Minh')

# Range timeline update - DAY unit
RANGE_UPDATE_TIMELINE = 0
mode_run = "run"

def get_timeline_user_toBQ(project_url, table_id, email):
  logging.warning(f"Start get timeline of project url {project_url}")
  username = re.search('(?<=\/\/twitter.com\/)([a-zA-Z0-9]*)', project_url).group()
  profile_response = twitter_api.get_profile_twitter(username)
  # This is project id
  user_id = str(profile_response.json()['data']['id'])
  logging.warning(f"User id is {user_id}")
  logging.warning("Creating client BigQuery...")
  client_BQ = bq_utils.create_client()

  checkpoint = None
  lower_bound_time = None
  new_checkpoint = None
  # TODO: Get checkpoint of project
  if mode_run != "debug":
    if email != 'None':
      bq_utils.add_read_project_id_permission([user_id], email)
    checkpoint = mongo_utils.get_checkpoint_project(user_id)
    if checkpoint:
      logging.warning("Have checkpoint !")
      logging.warning(checkpoint)
      lower_bound_time = checkpoint - datetime.timedelta(days=RANGE_UPDATE_TIMELINE)
      new_checkpoint = lower_bound_time

  # TODO: Get timeline of user
  response_timeline = twitter_api.get_timeline(user_id)
  pass_checkpoint = False
  while True and not pass_checkpoint:
    data = response_timeline.json()['data']
    medias_ref = response_timeline.json().get('includes', {}).get('media', [])
    append_data = []
    for tweet in data:
      try:
        new_data = twitter_api.schema_tweet(f'https://twitter.com/{username}', tweet, username, medias_ref)
        append_data.append(new_data)

        # TODO : Check checkpoint
        if lower_bound_time and new_data['post_date'] < lower_bound_time:
          pass_checkpoint = True
        if new_checkpoint and new_checkpoint < new_data['post_date']:
          new_checkpoint = new_data['post_date']
        else:
          new_checkpoint = new_data['post_date']

      except Exception as e:
        logging.warning(f"Have error when convert schema data for tweet id {tweet['id']}!")
        logging.warning(e)
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
    if next_token and not pass_checkpoint:
      logging.warning("Have next token, continue call API...")
      try:
        response_timeline = twitter_api.get_timeline(user_id, next_token)
      except Exception as e:
        logging.error("Have error when call request timeline !!!!")
        logging.error(e)
    else:
      logging.warning(f"Update new checkpoint for project {user_id}...")
      mongo_utils.update_checkpoint_project(user_id, new_checkpoint)
      logging.warning("Done get timeline !")
      client_BQ.close()
      return

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description="Parameters for crawl tweet of channel."
  )
  parser.add_argument("--project_url", help="Url of project", default="https://twitter.com/CamelotDEX")
  parser.add_argument("--table_id", help="BigQuery table id", default="canvas-figure-378911.twitter_crawl.tweet")
  parser.add_argument("--project_id", help="Project id", default=None)
  parser.add_argument("--email", help="Email user", default=None)
  args = parser.parse_args()

  # ! Turn off debug mode
  # project_url = "https://twitter.com/playBushi"
  # table_id = "canvas-figure-378911.twitter_crawl.tweet"
  # project_id = "646a46fe3fe233708a2f2df9"
  # email = "admin@wispswap.io"

  project_url, table_id, project_id, email = (
    args.project_url,
    args.table_id,
    args.project_id,
    args.email
  )
  logging.warning("All parameter:")
  logging.warning(args)

  try:
    if project_id and mode_run != "debug":
      mongo_utils.update_status(project_id, PROJECT_STATUS['running'])
    get_timeline_user_toBQ(project_url, table_id, email)
  except Exception as e:
    logging.error("Have error !!!!")
    logging.error(e)
  if project_id and mode_run != "debug":
    logging.warning(f"Update status DONE for project id {project_id}")
    mongo_utils.update_status(project_id, PROJECT_STATUS['done'])
