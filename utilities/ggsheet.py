import gspread
import os
import sys
import pytz
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + '/../')
import utilities.env_managment as global_env
tz = pytz.timezone('Asia/Ho_Chi_Minh')
import time

def write_sheet(sheet_name, list_frequency_array_data, start_col, end_col,
                start_row=2,
                sheet_link=global_env.SHEET_DATA,
                sa_credential_path=global_env.KEY_PATH
                ):
  for _ in range(5):
    try:
      gc = gspread.service_account(filename=sa_credential_path)
      sheet_data = gc.open_by_url(sheet_link).worksheet(sheet_name)
      sheet_data.update(f'{start_col}{start_row}:{end_col}', list_frequency_array_data)
    except gspread.exceptions.APIError as e:
      print(f'Error when writing to GoogleSheet {sheet_name} : {e}')
      if '\'code\': 429' in str(e):
        print('Sleeping 1 minutes...')
        time.sleep(60)
        continue
      else:
        print('Cannot handle this error !!!!!!!')
        break

    else:
      print('Done write data to GoogleSheet')
      break

def read_sheet(sheet_name,
               sheet_link=global_env.SHEET_DATA,
               sa_credential_path=global_env.KEY_PATH):
  for _ in range(5):
    try:
      gc = gspread.service_account(filename=sa_credential_path)
      sheet_data = gc.open_by_url(sheet_link).worksheet(sheet_name)
      list_of_dicts = sheet_data.get_all_records()
      sheet_data.session.close()
    except gspread.exceptions.APIError as e:
      print(f'Error when writing to GoogleSheet {sheet_name} : {e}')
      if '\'code\': 429' in str(e):
        print('Sleeping 1 minutes...')
        time.sleep(60)
        continue
      else:
        print('Cannot handle this error !!!!!!!')
        break
    else:
      print('Done read data to GoogleSheet')
      return list_of_dicts