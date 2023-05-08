import os

PATH_DRIVER = os.getenv('PATH_DRIVER', '/Users/dangchu/Documents/driver/chromedriver_109')

# KEY_PATH = os.getenv('KEY_PATH', '/app/cert/ggsheet_personal.json')
KEY_PATH = os.getenv('KEY_PATH', '/Users/dangchu/Documents/cert/ggsheet_personal.json')

LINK_SHEET_PARSER = os.getenv('LINK_SHEET_PARSER', 'https://docs.google.com/spreadsheets/d/1UKtxXz9e8dJftp-dWi62vNN0vAfoQOCg0zP1TbP4TgA')
CACHE_DRIVER_LOCATION = os.getenv('CACHE_LOCATION', '/Users/dangchu/Documents/cache')
USER_TWITTER = os.getenv('USER_TWITTER', 'Test95311417')
PWD_TWITTER = os.getenv('PWD_TWITTER', 'randompass1234')
CHECKPOINT_SHEET = os.getenv('CHECKPOINT_SHEET', 'Checkpoint Crawler')
SHEET_DATA = os.getenv('SHEET_DATA', 'https://docs.google.com/spreadsheets/d/1vrDqX94v0NL-rviyKjAeA1hJUlxhGmD28VuJkwNZT5Y/')

SA_AUTH = os.getenv('SA_AUTH', '/Users/dangchu/Documents/GitRepo/secret/cert/canvas-figure-bq.json')
# SA_AUTH = os.getenv('SA_AUTH', '/app/cert/canvas-figure-bq.json')

API_TOKEN = os.getenv('API_TOKEN', 'AAAAAAAAAAAAAAAAAAAAAD%2BUkgEAAAAAxuCobQH%2FAcqOzlk6MitTc3vy9no%3DjtTDVRwOEtPhdJEVP1NVIgCtrTIJGAFVDkv7z3UnfV6mvKOlUG')

MONGO_HOST = os.getenv('MONGO_HOST', 'mongodb://admin:password@mongodb:27017/twitter_crawler?authSource=admin&retryWrites=true&w=majority')
MONGO_DB = os.getenv('MONGO_DB', 'twitter_crawler')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION', 'project')
CHECKPOINT_COLLECTION = os.getenv('CHECKPOINT_COLLECTION', 'checkpoint_project')

PROJECT_STATUS = {
  'running': 'RUNNING',
  'done': 'UPDATED',
  'not_process': 'NOT PROCESS',
  'error': 'ERROR'
}