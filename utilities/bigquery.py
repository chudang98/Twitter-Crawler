from google.cloud import bigquery
from google.oauth2 import service_account
import pandas
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + '/../')
import utilities.env_managment as global_env
import logging

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

def add_read_project_id_permission(list_prj_ids, email, table='canvas-figure-378911.twitter_crawl.permission'):
  bq_client = create_client()
  condition_qr = ','.join([f"'{prj_id}'" for prj_id in list_prj_ids])
  # TODO: Check have permission for project_id by 2 step : Query by project_id and check email.
  check_permission_qr = f"""
    SELECT project_id, email
    FROM `{table}`
    WHERE project_id in ({condition_qr})
  """
  logging.warning(f"Query get all project_id permission : {check_permission_qr}")
  existed_permission = bq_client.query(check_permission_qr)
  for project_permission in existed_permission:
    # TODO: Check email has permisstion for this project_id
    list_emails = project_permission[1]
    if email not in list_emails:
      query_update = f"""
        UPDATE `{table}`
        SET email = ARRAY_CONCAT(email, ['{email}'])
        WHERE project_id = '{project_permission[0]}'
      """
      logging.warning(f"Query add email {email} to project_id {project_permission[0]} : {query_update}...")
      query_job = bq_client.query(query_update)
      query_job.result()

# TODO: Add project_id permision for first time save or had been deleted.
  prj_existed = [proj[0] for proj in existed_permission]
  for prj_id in list_prj_ids:
    if prj_id not in prj_existed:
      query = f"""
        INSERT INTO `{table}`(project_id, email)
        VALUES('{prj_id}', ['{email}'])  
      """
      logging.warning(f"""
          Project id {prj_id} is new.
          Query add new project id {prj_id} for email {email}
      """)
      bq_client.query(query)
  bq_client.close()