import os

PATH_DRIVER = os.getenv('PATH_DRIVER', '/Users/dangchu/Documents/driver/chromedriver_107')
KEY_PATH = os.getenv('KEY_PATH', '/Users/dangchu/Documents/cert/ggsheet_personal.json')
LINK_SHEET_PARSER = os.getenv('LINK_SHEET_PARSER', 'https://docs.google.com/spreadsheets/d/1UKtxXz9e8dJftp-dWi62vNN0vAfoQOCg0zP1TbP4TgA')
CACHE_DRIVER_LOCATION = os.getenv('CACHE_LOCATION', '/Users/dangchu/Documents/cache')
USER_TWITTER = os.getenv('USER_TWITTER', 'Test95311417')
PWD_TWITTER = os.getenv('PWD_TWITTER', 'randompass1234')
CHECKPOINT_SHEET = os.getenv('CHECKPOINT_SHEET', 'Checkpoint Crawler')
SHEET_DATA = os.getenv('SHEET_DATA', 'https://docs.google.com/spreadsheets/d/1vrDqX94v0NL-rviyKjAeA1hJUlxhGmD28VuJkwNZT5Y/')