from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import shutil


class Scraper:
    def __init__(self, headless=False):
        options = webdriver.ChromeOptions()
        prefs = {
            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "download.default_directory":
            r"C:\Users\user\Desktop\Test\\",
            "directory_upgrade": True
        }
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])
        if headless:
            options.add_argument("--headless")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def open_page(self, url):
        self.driver.get(url)
        time.sleep(2)

    def close(self):
        self.driver.quit()


def run_scraper():
    scraper = Scraper()

    scraper.open_page('https://google.com')

    scraper.close()


