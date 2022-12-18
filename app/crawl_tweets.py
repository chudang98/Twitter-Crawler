from utilities.selenium_driver import TwitterSeleniumDriver
import utilities.env_managment as global_env
import logging
import argparse
import gspread
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
import pytz
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + '/../')

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description="Parameters for crawl tweet of channel."
  )
  parser.add_argument("--project", help="Name of project")
  args = parser.parse_args()

  project = (
    args.project
  )
  # project = 'SuiGlobal'
  tz = pytz.timezone('Asia/Ho_Chi_Minh')

  with TwitterSeleniumDriver() as driver:
    logging.warning("Inited driver !")
    # TODO : Login TWITTER
    driver.login_twitter()

    # TODO : Read config of project
    gc = gspread.service_account(filename=global_env.KEY_PATH)
    checkpoint_sheet = gc.open_by_url(global_env.SHEET_DATA).worksheet(global_env.CHECKPOINT_SHEET)
    list_of_dicts = checkpoint_sheet.get_all_records()
    config_project = next((x for x in list_of_dicts if x.get('Project Name') == project), None)

    time_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    latest_time = None
    upper_limit_time = None
    index_sheet = 1
    page_url = None
    new_checkpoint = None
    try:
      page_url = config_project.get("Twitter Page")
      latest_time = datetime.strptime(config_project.get("Latest tweet'time"), '%Y-%m-%dT%H:%M:%S.%fZ')
      upper_limit_time = datetime.strptime(config_project.get("Tweet's upper limit time"), '%Y-%m-%dT%H:%M:%S.%fZ')
      index_sheet = int(config_project.get("Index sheet", "1"))
    except Exception as e:
      logging.warning("Have error when parsing time config. Set as None")
      logging.warning(e)
      latest_time = datetime.strptime('2020-10-09T09:03:06.676583Z', '%Y-%m-%dT%H:%M:%S.%fZ')
      upper_limit_time = datetime.strptime('2020-10-09T09:03:06.676583Z', '%Y-%m-%dT%H:%M:%S.%fZ')
    new_checkpoint = latest_time

    sheet_data = gc.open_by_url(global_env.SHEET_DATA).worksheet(project)
    is_pass_checkpoint = False

    stop_condition = False
    result_tmp = []
    limit_result = 10
    cache_url = []
    driver.get(page_url)
    driver.wait_loading()

    while not stop_condition:
      logging.warning(len(result_tmp))
      if len(result_tmp) > limit_result:
        logging.warning("Clear cache...")
        index_sheet += 1
        try:
          sheet_data.update(f'A{index_sheet}:I', result_tmp)
        except Exception as e:
          logging.warning("Error !")
        index_sheet += len(result_tmp)
        result_tmp = []

      list_tweet = []
      while len(list_tweet) <= 0:
        list_tweet = driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")

      try:
        for tweet in list_tweet:
          is_pined_tweet = False
          is_retweet = False
          chanel_retweet_name = ''
          try:
            pined_tweet_text = tweet.find_element(By.XPATH, ".//span[contains(text(), 'Pinned Tweet')]")
            is_pined_tweet = True
            logging.warning("Pinned tweet")
          except Exception as e:
            is_pined_tweet = False

          try:
            retweet_text = tweet.find_element(By.XPATH, ".//span[text()[contains(., 'Retweeted')]]")
            is_retweet = True
            chanel_retweet_name = tweet.find_element(By.XPATH, './/div[@data-testid="User-Names"]/div').text
          except Exception as e:
            is_retweet = False

          try:
            tweet_time_utc = tweet.find_element(By.XPATH, ".//time").get_attribute('datetime')
            link_tweet = tweet.find_element(By.XPATH, ".//time//..").get_attribute('href')
            print(link_tweet)
            if link_tweet == 'https://twitter.com/MojitoMarkets/status/1590305805123080192':
              pass
            medias = tweet.find_elements(By.XPATH,
                                         './/div[@data-testid="tweetText"]/../../div[@aria-labelledby]//img[@alt="Image"]')
            link_media = []
            for media in medias:
              link_media.append(media.get_attribute('src'))
            try:
              reply = tweet.find_element(By.XPATH,
                                         ".//div[@data-testid='reply']//span[@data-testid='app-text-transition-container']/span/span").text
            except Exception as e:
              reply = '0'
            try:
              like = tweet.find_element(By.XPATH,
                                        ".//div[@data-testid='like']//span[@data-testid='app-text-transition-container']/span/span").text
            except Exception as e:
              like = '0'
            try:
              retweet = tweet.find_element(By.XPATH,
                                           ".//div[@data-testid='retweet']//span[@data-testid='app-text-transition-container']/span/span").text
            except Exception as e:
              retweet = '0'
            # content_tweet = tweet.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
            content_elements = (
              tweet.find_element(By.XPATH,
                                 './/div[@data-testid="tweetText"]')
              .find_elements(By.XPATH,
                             './/*[self::span[not(@class="r-18u37iz") and not(@aria-hidden="true")] or self::a or self::img[@alt and contains(@src, "/emoji/")]]')
            )
            contents = []
            for ele in content_elements:
              if ele.tag_name == 'img':
                contents.append(ele.get_attribute("alt"))
              elif ele.tag_name == 'a':
                link_href = ele.get_attribute("href")
                text_link = ele.text
                if ('/hashtag/' in link_href) or text_link.startswith('@') or text_link.startswith("$"):
                  contents.append(text_link)
                else:
                  contents.append(link_href)
              else:
                contents.append(ele.get_attribute('innerHTML').replace('&amp', '&'))
            content_tweet = "".join(contents)
            height_tweet = tweet.size.get('height')
            post_time = datetime.strptime(tweet_time_utc, time_format)
            if ((post_time < latest_time and not is_pined_tweet)
                    or (post_time < upper_limit_time)):
              stop_condition = True
              break
            elif post_time > new_checkpoint:
              new_checkpoint = post_time
              index_sheet += 1
            attachment_eles = []
            username_texts = []

            try:
              attached_content = tweet.find_element(By.XPATH,
                                                    ".//div[@aria-labelledby]")
              content_attached_contents = attached_content.find_elements(By.XPATH,
                                                                         './/div[@data-testid="tweetText"]//*[self::span[not(@class="r-18u37iz") and not(@aria-hidden="true")] or self::a or self::img[@alt and contains(@src, "/emoji/")]]')
              username_eles = (
                attached_content.find_elements(By.XPATH,
                                               './/div[@data-testid="UserAvatar-Container-unknown"]/../div[2]//*[self::span[not(@class="r-18u37iz") and not(@aria-hidden="true") and not(ancestor::*)] or self::a or self::img[@alt and contains(@src, "/emoji/")]]')
              )
              for ele in username_eles:
                if ele.tag_name == 'img':
                  username_texts.append(ele.get_attribute("alt"))
                elif ele.tag_name == 'a':
                  link_href = ele.get_attribute("href")
                  text_link = ele.text
                  if ('/hashtag/' in link_href) or text_link.startswith('@') or text_link.startswith("$"):
                    username_texts.append(text_link)
                  else:
                    username_texts.append(link_href)
                else:
                  # username_texts.append(ele.get_attribute('innerHTML').replace('&amp', '&'))
                  username_texts.append(ele.text)
              for ele in content_attached_contents:
                if ele.tag_name == 'img':
                  attachment_eles.append(ele.get_attribute("alt"))
                elif ele.tag_name == 'a':
                  link_href = ele.get_attribute("href")
                  text_link = ele.text
                  if ('/hashtag/' in link_href) or text_link.startswith('@') or text_link.startswith("$"):
                    attachment_eles.append(text_link)
                  else:
                    attachment_eles.append(link_href)
                else:
                  # attachment_eles.append(ele.get_attribute('innerHTML').replace('&amp', '&'))
                  attachment_eles.append(ele.text.replace('&amp', '&'))
            except Exception as e:
              logging.warning("Don't have attached content !!!!")

            if link_tweet not in cache_url:
              result_tmp.append([
                                  link_tweet,
                                  retweet,
                                  like,
                                  reply,
                                  content_tweet if not is_retweet else '',
                                  (post_time + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
                                  '\n'.join(link_media),
                                  ''.join(attachment_eles) if not is_retweet else content_tweet,
                                  ''.join(username_texts) if not is_retweet else chanel_retweet_name])
              cache_url.append(link_tweet)
          except Exception as e:
            logging.warning("Detect info of tweet error !!!!")
            logging.warning(e)

          last_tweet = tweet
        driver.execute_script("arguments[0].scrollIntoView(true);", last_tweet)
      except Exception as e:
        print("Have exception !!!!")
        print(e)
      driver.execute_script(f"window.scrollBy(0, {10})")
    sheet_data.update(f'A{index_sheet}:I', result_tmp)

    pass
