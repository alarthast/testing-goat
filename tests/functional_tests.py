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


browser = start_browser()
browser.get("http://localhost:8000")

assert "Congratulations!" in browser.title
print("OK")
