import pytz
import os
import sys
import logging
import re

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + '/../')
import utilities.twitter_api as twitter_api
tz = pytz.timezone('Asia/Ho_Chi_Minh')

def get_timeline_user_toBQ(project_url):
  logging.warning(f"Start get timeline of project url {project_url}")
  username = re.search('(?<=\/\/twitter.com\/)([a-zA-Z0-9]*)', project_url).group()
  profile_response = twitter_api.get_profile_twitter(username)
  # This is project id
  user_id = str(profile_response.json()['data']['id'])
  logging.warning(f"User id is {user_id}")
  logging.warning("Creating client BigQuery...")

  # TODO: Get timeline of user
  response_timeline = twitter_api.get_timeline(user_id)
  pass_checkpoint = False
  static = {}
  while True:
    data = response_timeline.json()['data']
    for tweet in data:
      try:
        refer_tweets = tweet['referenced_tweets']
        if len(refer_tweets) > 0:
          type_tweet = tweet['referenced_tweets'][0]['type']
          if type_tweet in static:
            static[type_tweet] += 1
          else:
            static[type_tweet] = 1
      except Exception as e:
        pass
    logging.warning("Start create dataframe from pandas...")

    next_token = response_timeline.json().get('meta', {}).get('next_token', None)
    if next_token and not pass_checkpoint:
      logging.warning("Have next token, continue call API...")
      try:
        response_timeline = twitter_api.get_timeline(user_id, next_token)
      except Exception as e:
        logging.error("Have error when call request timeline !!!!")
        logging.error(e)
    else:
      logging.warning("Done get timeline !")
      return


if __name__ == '__main__':
  project_url = "https://twitter.com/playBushi"
  try:
    get_timeline_user_toBQ(project_url)
  except Exception as e:
    logging.error("Have error !!!!")
    logging.error(e)
