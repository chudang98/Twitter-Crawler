import argparse
import time

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
  print("Parameter :")
  print(project_url)
  print(table_id)
  print("Start sleep 10 seconds...")
  time.sleep(10)
  print("Done !")