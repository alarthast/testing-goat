from django.test import TestCase


class HomePageTest(TestCase):
    def test_home_page_returns_correct_html(self):
        # get() simulates a user's browser requesting a page.
        response = self.client.get("/")
        self.assertContains(response, "<title>To-Do lists</title>")
        self.assertContains(response, "<html>")
        self.assertContains(response, "</html>")
