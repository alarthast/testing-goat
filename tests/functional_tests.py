import unittest

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


def start_browser():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    geckodriver_path = "/snap/bin/geckodriver"
    driver_service = Service(executable_path=geckodriver_path)

    browser = webdriver.Firefox(options=options, service=driver_service)
    return browser


class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = start_browser()

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_todo_list(self):
        # Edith has heard about a cool new online to-do app.
        # She goes to check out its homepage
        self.browser.get("http://localhost:8000")

        # She notices the page title and header mention to-do lists
        self.assertIn("To-Do", self.browser.title)

        # She is invited to enter a to-do item straight away
        self.fail("Finish the test!")

        [...]

        # Satisfied, she goes back to sleep


if __name__ == "__main__":
    unittest.main()
