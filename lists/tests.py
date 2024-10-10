from django.test import TestCase


class HomePageTest(TestCase):
    def test_uses_home_template(self):
        # get() simulates a user's browser requesting a page.
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")
