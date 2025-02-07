import os
import platform
import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


MAX_WAIT = 10


def start_browser():
    if platform.system() == "Linux":
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        geckodriver_path = "/snap/bin/geckodriver"
        driver_service = Service(executable_path=geckodriver_path)

        browser = webdriver.Firefox(options=options, service=driver_service)
        return browser
    return webdriver.Firefox()


class FunctionalTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = start_browser()
        test_server = os.environ.get("TEST_SERVER")
        if test_server:
            self.live_server_url = "http://" + test_server

    def tearDown(self):
        self.browser.quit()

    def wait_for(self, fn):
        start_time = time.time()
        while True:
            try:
                return fn()
            except (AssertionError, WebDriverException):
                if time.time() - start_time > MAX_WAIT:
                    raise
                time.sleep(0.5)

    def wait_for_element(self, by, value):
        return self.wait_for(lambda: self.browser.find_element(by, value))

    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element(By.ID, "id_list_table")
                rows = table.find_elements(By.TAG_NAME, "tr")
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException):
                if time.time() - start_time > MAX_WAIT:
                    raise
                time.sleep(0.5)

    def get_item_input_box(self):
        return self.browser.find_element(By.ID, "id_text")
