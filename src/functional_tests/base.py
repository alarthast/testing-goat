import os
import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .container_commands import reset_database


MAX_WAIT = 10


def start_browser():
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
        self.test_server = os.environ.get("TEST_SERVER")
        if self.test_server:
            self.live_server_url = "http://" + self.test_server
            reset_database(self.test_server)

    def tearDown(self):
        self.browser.quit()

    @wait
    def wait_for(self, fn):
        return fn()

    @wait
    def wait_for_element(self, by, value):
        return self.browser.find_element(by, value)

    @wait
    def wait_for_row_in_list_table(self, row_text):
        table = self.browser.find_element(By.ID, "id_list_table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertIn(row_text, [row.text for row in rows])

    def wait_to_be_logged_in(self, email):
        self.wait_for_element(By.CSS_SELECTOR, "#id_logout")
        navbar = self.browser.find_element(By.CSS_SELECTOR, ".navbar")
        self.assertIn(email, navbar.text)

    def wait_to_be_logged_out(self, email):
        self.wait_for_element(By.CSS_SELECTOR, "input[name=email]")
        navbar = self.browser.find_element(By.CSS_SELECTOR, ".navbar")
        self.assertNotIn(email, navbar.text)

    def get_item_input_box(self):
        return self.browser.find_element(By.ID, "id_text")

    def add_list_item(self, item_text):
        num_rows = len(self.browser.find_elements(By.CSS_SELECTOR, "#id_list_table tr"))
        self.get_item_input_box().send_keys(item_text)
        self.get_item_input_box().send_keys(Keys.ENTER)
        item_number = num_rows + 1
        self.wait_for_row_in_list_table(f"{item_number}: {item_text}")
