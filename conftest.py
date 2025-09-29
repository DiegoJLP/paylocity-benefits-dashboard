import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


CHROME_DRIVER = ChromeService(ChromeDriverManager().install())
@pytest.fixture
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=CHROME_DRIVER, options=chrome_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()
