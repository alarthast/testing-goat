import os
import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By


MAX_WAIT = 10


def start_browser():
    if not os.environ.get("GRAPHICAL_FUNCTIONAL_TESTS"):
        options = FirefoxOptions()
        options.add_argument("--headless")
        return webdriver.Firefox(options=options)
    return webdriver.Firefox()


def wait(fn):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except (AssertionError, WebDriverException):
                if time.time() - start_time > MAX_WAIT:
                    raise
                time.sleep(0.5)

    return wrapper


class FunctionalTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = start_browser()
        test_server = os.environ.get("TEST_SERVER")
        if test_server:
            self.live_server_url = "http://" + test_server

    def tearDown(self):
        self.browser.quit()

    @wait
    def wait_for(self, fn):
        return fn()

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

    def wait_to_be_logged_in(self, email):
        self.wait_for(
            lambda: self.browser.find_element(By.CSS_SELECTOR, "#id_logout"),
        )
        navbar = self.browser.find_element(By.CSS_SELECTOR, ".navbar")
        self.assertIn(email, navbar.text)

    def wait_to_be_logged_out(self, email):
        self.wait_for(
            lambda: self.browser.find_element(By.CSS_SELECTOR, "input[name=email]")
        )
        navbar = self.browser.find_element(By.CSS_SELECTOR, ".navbar")
        self.assertNotIn(email, navbar.text)

    def get_item_input_box(self):
        return self.browser.find_element(By.ID, "id_text")
