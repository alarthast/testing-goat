from django.conf import settings
from django.contrib.auth import get_user_model
from selenium.webdriver.common.by import By

from .base import FunctionalTest
from .container_commands import create_session_on_server
from .management.commands.create_session import create_pre_authenticated_session


User = get_user_model()


class MyListsTest(FunctionalTest):
    def create_pre_authenticated_session(self, email):
        if self.test_server:
            session_key = create_session_on_server(self.test_server, email)
        else:
            session_key = create_pre_authenticated_session(email)
        ## to set a cookie we need to first visit the domain.
        ## 404 pages load the quickest!
        self.browser.get(self.live_server_url + "/404_no_such_url/")
        self.browser.add_cookie(
            dict(
                name=settings.SESSION_COOKIE_NAME,
                value=session_key,
                path="/",
            )
        )

    def test_logged_in_users_lists_are_saved_as_my_lists(self):
        email = "edith@example.com"
        self.browser.get(self.live_server_url)
        self.wait_to_be_logged_out(email)

        # Edith is a logged-in user
        self.create_pre_authenticated_session(email)

        # She goes to the home page and starts a list
        self.browser.get(self.live_server_url)
        self.add_list_item("Reticulate splines")
        self.add_list_item("Immanentize eschaton")
        first_list_url = self.browser.current_url

        # She notices a "My lists" link, for the first time.
        self.browser.find_element(By.LINK_TEXT, "My lists").click()
        # She sees her email is there in the page heading
        h1_text = self.wait_for_element(By.CSS_SELECTOR, "h1").text
        self.assertIn("edith@example.com", h1_text)

        # And she sees that her list is in there,
        # named according to its first list item
        first_item = self.wait_for_element(By.LINK_TEXT, "Reticulate splines")
        first_item.click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, first_list_url)
        )
