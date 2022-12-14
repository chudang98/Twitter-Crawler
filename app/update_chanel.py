from utilities.selenium_driver import TwitterSeleniumDriver
import utilities.env_managment as global_env
import logging
import argparse
import gspread
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
import pytz

if __name__ == '__main__':
  project = 'SuiPad'
  tz = pytz.timezone('Asia/Ho_Chi_Minh')
  sheet_project = 'Thông tin dự án'

  with TwitterSeleniumDriver() as driver:
    logging.warning("Inited driver !")
    # TODO : Login TWITTER
    driver.login_twitter()

    gc = gspread.service_account(filename=global_env.KEY_PATH)
    checkpoint_sheet = gc.open_by_url(global_env.SHEET_DATA).worksheet(global_env.CHECKPOINT_SHEET)
    list_of_dicts = checkpoint_sheet.get_all_records()
    config_project = next((x for x in list_of_dicts if x.get('Project Name') == project), None)
    page_url = config_project.get("Twitter Page")
    sheet_data = gc.open_by_url(global_env.SHEET_DATA).worksheet(sheet_project)
    driver.get(page_url)
    driver.wait_loading()
    project_data = []
    for page in list_of_dicts:
      page_url = page.get("Twitter Page")
      driver.get(page_url)
      driver.wait_loading()
      project_name = driver.find_element(By.XPATH, '//div[@data-testid="UserName"]//div[@dir="ltr"]').text
      joined_date = driver.find_element(By.XPATH, '//span[@data-testid="UserJoinDate"]').text.replace('Joined ', '')
      following = driver.find_element(By.XPATH, '//div[@data-testid="UserName"]/..//a[contains(@href, "/following")]').text.replace(' Following', '')
      follower = driver.find_element(By.XPATH, '//div[@data-testid="UserName"]/..//a[contains(@href, "/followers")]').text.replace(' Followers', '')
      total_tweet = driver.find_element(By.XPATH, '//div[@aria-label="Home timeline"]/div[1]//h2[@role="heading"]//..//div[@dir="ltr"]').text.replace(' Tweets', '')
      project_data.append([project_name, joined_date, following, follower, total_tweet])
    sheet_data.update(f'A2:E', project_data)
    pass
