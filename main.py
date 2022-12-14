from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
from selenium.webdriver.common.by import By
import csv
import gspread
from datetime import datetime, timedelta

PATH_DRIVER = os.getenv('PATH_DRIVER', '/Users/dangchu/Documents/driver/chromedriver_107')
KEY_PATH = os.getenv('KEY_PATH', '/Users/dangchu/Documents/cert/ggsheet_personal.json')
LINK_SHEET_PARSER = os.getenv('LINK_SHEET_PARSER', 'https://docs.google.com/spreadsheets/d/1UKtxXz9e8dJftp-dWi62vNN0vAfoQOCg0zP1TbP4TgA')

def get_element(driver, type, path, await_loading=True):
    loop_check = True
    element = None
    while loop_check:
        try:
            element = driver.find_element(by=type, value=path)
            loop_check = False
        except Exception as e:
            print("Have error !")
            print(e)
            print("Sleep 5 seconds !")
            time.sleep(5)
            if not await_loading:
                loop_check = False
    return element

def wait_loading(driver, timeout=100):
    is_loading = True
    while is_loading:
        try:
            driver.find_element(by=By.XPATH, value="//div[@data-testid='UserName']")
            is_loading = False
        except:
            print("Sleep 2 second waiting loading...")
            time.sleep(2)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # TODO: Open ggsheet
    gc = gspread.service_account(filename=KEY_PATH)
    checkpoint_sheet = gc.open_by_url(LINK_SHEET_PARSER).worksheet('checkpoint')
    latest = checkpoint_sheet.acell('A1').value or None
    latest_index = checkpoint_sheet.acell('B1').value or '1'
    start_idx_sheet = int(latest_index)
    checkpoint_time = datetime.now() - timedelta(days=100)
    if latest is not None:
        checkpoint_time = datetime.strptime(latest, '%Y-%m-%dT%H:%M:%S.%fZ')
    working_sheet = gc.open_by_url(LINK_SHEET_PARSER).worksheet('@Test2')

    user = 'Test95311417'
    pwd = 'randompass1234'
    url = 'https://twitter.com/?lang=en'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--user-agent=%s' % user_agent)
    chrome_options.add_argument(f"user-data-dir=/Users/dangchu/Documents/cache")
    driver = webdriver.Chrome(
        PATH_DRIVER,
        options=chrome_options)

    driver.get(url)
    # TODO: Check loading
    loading = True
    while loading:
        try:
            profile_or_login_btn = driver.find_element(By.XPATH, "//a[@aria-label='Profile'] | //div[@role='button']//span[contains(text(), 'Log in')]")
            loading = False
        except Exception as e:
            print("Still loading...")
            print("Sleep 2 seconds...")
            time.sleep(2)

    # TODO: Check driver loading
    current_url = driver.current_url

    if not current_url.startswith('https://twitter.com/home'):
        print("Login to Twitter...")
        # TODO: LOGIN
        sign_in_btn = get_element(driver, By.XPATH, "//a[@href='/login']")
        sign_in_btn.click()
        username_input = get_element(driver, By.XPATH, "//input[@autocomplete='username']")
        username_input.clear()
        username_input.send_keys(user)
        next_btn = get_element(driver, By.XPATH, "//div[@role='button']//span[contains(text(), 'Next')]")
        next_btn.click()
        pwd_input = get_element(driver, By.XPATH, "//input[@autocomplete='current-password']")
        pwd_input.clear()
        pwd_input.send_keys(pwd)
        login_btn = get_element(driver, By.XPATH, "//div[@role='button']//span[contains(text(), 'Log in')]")
        login_btn.click()

    driver.execute_script("window.scrollBy(0, 250)")
    # TODO: Go to page. HAVE BUG HERE
    page = 'https://twitter.com/LunarCrush'
    driver.get(page)
    wait_loading(driver)

    number_post = 50
    cache_url = []
    result = []
    previous_post = ''
    height_tweet = 10
    is_pass_checkpoint = False
    new_checkpoint = checkpoint_time
    while number_post > 0 and not is_pass_checkpoint:
        try:
            if len(result) >= number_post:
                print("Clear cache...")
                start_idx_sheet += 1
                working_sheet.update(f'A{start_idx_sheet}:F', result)
                start_idx_sheet += len(result)
                cache_url = []
                result = []
            last_tweet = None
            tweets = []
            while len(tweets) <= 0:
                tweets = driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")
            for tweet in tweets:
                pinned_tweet = False
                tweet_time_utc = tweet.find_element(By.XPATH, ".//time").get_attribute('datetime')
                link_tweet = tweet.find_element(By.XPATH, ".//time//..").get_attribute('href')
                reply = tweet.find_element(By.XPATH, ".//div[@data-testid='reply']//span[@data-testid='app-text-transition-container']/span/span").text
                try:
                    tweet.find_element(By.XPATH, ".//span[contains(text(), 'Pinned Tweet')]")
                    pinned_tweet = True
                except Exception as e:
                    pinned_tweet = False
                like = tweet.find_element(By.XPATH, ".//div[@data-testid='like']//span[@data-testid='app-text-transition-container']/span/span").text
                retweet = tweet.find_element(By.XPATH, ".//div[@data-testid='retweet']//span[@data-testid='app-text-transition-container']/span/span").text
                content_tweet = tweet.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
                height_tweet = tweet.size.get('height')
                previous_post = link_tweet
                post_time = datetime.strptime(tweet_time_utc, '%Y-%m-%dT%H:%M:%S.%fZ')
                if post_time <= checkpoint_time:
                    if not pinned_tweet:
                        is_pass_checkpoint = True
                        break
                elif post_time > new_checkpoint:
                    start_idx_sheet += 1
                    new_checkpoint = post_time
                if link_tweet not in cache_url:
                    result.append([link_tweet, retweet, like, reply, content_tweet, tweet_time_utc])
                    cache_url.append(link_tweet)
                last_tweet = tweet
                # number_post -= 1
            driver.execute_script("arguments[0].scrollIntoView(true);", last_tweet)
        except Exception as e:
            height_tweet = 10
            print('Have error !')
            print(len(result))
            print(number_post)
            print(e)
        driver.execute_script(f"window.scrollBy(0, {height_tweet})")
    working_sheet.update(f'A{start_idx_sheet}:F', result)
    checkpoint_sheet.update('A1', new_checkpoint.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
    checkpoint_sheet.update('B1', str(start_idx_sheet))
    print(1)
    driver.close()
