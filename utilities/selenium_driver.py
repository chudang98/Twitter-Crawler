from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import utilities.env_managment as global_env
import time
import logging

class TwitterSeleniumDriver(WebDriver):
  # This class extend from Selenium.WebDriver for flexible using
  def __init__(self, chrome_options=None):
    if chrome_options is None:
      logging.warning("Chrome option is None, init option...")
      chrome_options = Options()
      user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
      # chrome_options.add_argument('--headless')
      chrome_options.add_argument('--user-agent=%s' % user_agent)
      chrome_options.add_argument(f"user-data-dir={global_env.CACHE_DRIVER_LOCATION}")
    # driver = webdriver.Chrome(
    #   ENV.PATH_DRIVER,
    #   options=chrome_options)
    super().__init__(executable_path=global_env.PATH_DRIVER,
                     options=chrome_options)
    # self.driver = driver

  def get_element_and_await(self, path, type_selector=By.XPATH, await_loading=True):
    loop_check = True
    element = None
    while loop_check:
      try:
        element = self.find_element(by=type_selector, value=path)
        loop_check = False
      except Exception as e:
        logging.warning("Have error !")
        logging.warning(e)
        logging.warning("Sleep 3 seconds !")
        time.sleep(3)
        if not await_loading:
          loop_check = False
    return element

  def wait_loading(self, type_selector_await=By.XPATH, path_selector_await="//div[@data-testid='UserName']", timeout=100):
      is_loading = True
      while is_loading:
        try:
          self.find_element(by=type_selector_await, value=path_selector_await)
          is_loading = False
        except Exception as e:
          logging.warning("Sleep 2 second waiting loading...")
          time.sleep(2)

  def login_twitter(self, timeout=100):
    url_login = 'https://twitter.com/?lang=en'
    self.get(url_login)
    loading = True
    while loading:
      try:
        # Find button Login or Profile
        self.find_element(By.XPATH, "//a[@aria-label='Profile'] | //div[@role='button']//span[contains(text(), 'Log in')]")
        loading = False
      except Exception as e:
        print("Still loading...")
        print("Sleep 2 seconds...")
        time.sleep(2)

    current_url = self.current_url
    # If last login session is expired, login again
    if not current_url.startswith('https://twitter.com/home'):
        print("Login to Twitter...")
        # TODO: LOGIN
        sign_in_btn = self.get_element_and_await(type_selector=By.XPATH, path="//a[@href='/login']")
        sign_in_btn.click()
        username_input = self.get_element_and_await(type_selector=By.XPATH, path="//input[@autocomplete='username']")
        username_input.clear()
        username_input.send_keys(global_env.USER_TWITTER)
        next_btn = self.get_element_and_await(type_selector=By.XPATH, path="//div[@role='button']//span[contains(text(), 'Next')]")
        next_btn.click()
        pwd_input = self.get_element_and_await(type_selector=By.XPATH, path="//input[@autocomplete='current-password']")
        pwd_input.clear()
        pwd_input.send_keys(global_env.PWD_TWITTER)
        login_btn = self.get_element_and_await(type_selector=By.XPATH, path="//div[@role='button']//span[contains(text(), 'Log in')]")
        login_btn.click()
