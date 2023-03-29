import argparse
import logging
import time
import docker

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description="Parameters for crawl tweet of channel."
  )
  parser.add_argument("--project_url", help="Url of project")
  parser.add_argument("--table_id", help="BigQuery table id")
  args = parser.parse_args()
  project_url, table_id = (
    args.project_url,
    args.table_id
  )
  logging.warning("Parameter :")
  logging.warning(project_url)
  logging.warning(table_id)
  client_docker = docker.from_env()
  client_docker.containers.run(
    'test_app',
    '--project_url test_url --table_id test_table',
    detach=True
  )
  logging.warning("Started container !")
  logging.warning("Start sleep 5 seconds...")
  time.sleep(5)
  # logging.warning("Done !")