import requests
import logging
import time

def call_api_twitter(url, req_headers, req_params):
  try:
    response = requests.get(
      url,
      headers=req_headers,
      params=req_params
    )
    res_json = response.json()
    data_request = res_json['data']
  except Exception as e:
    logging.warning("Have error when call Twitter API...")
    if res_json.get('status', 0) == 429:
      logging.warning("Limit quota, sleep 15 minutes...")
      time.sleep(900)
      response = requests.get(
        url,
        headers=req_headers,
        params=req_params
      )
    else:
      logging.warning(e)

  return res_json