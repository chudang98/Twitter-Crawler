from google.cloud import bigquery
from google.oauth2 import service_account
import pandas
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + '/../')
import utilities.env_managment as global_env

def create_client():
  path_auth = global_env.SA_AUTH
  credentials = service_account.Credentials.from_service_account_file(
    path_auth, scopes=["https://www.googleapis.com/auth/cloud-platform"],
  )
  client = bigquery.Client(credentials=credentials, project=credentials.project_id)
  return client

def write_data(table_id, client, data):
  df = pandas.DataFrame(data)
  client.load_table_from_dataframe(
    df,
    table_id
  )
