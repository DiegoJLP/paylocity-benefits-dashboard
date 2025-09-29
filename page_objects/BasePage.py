from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

from conftest import driver

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def click_element(self, xpath):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
    
    def scroll_to(self, xpath):
        element = self.driver.find_element(By.XPATH, xpath)
        self.driver.execute_script("arguments[0].scrollIntoView();", element)

    def type(self, xpath, text, key = None):
        field = self.driver.find_element(By.XPATH, xpath)
        field.clear()
        field.send_keys(text)
        if key:
            key = key.upper()
            match key:
                case "TAB":
                    time.sleep(1)
                    field.send_keys(Keys.TAB)
                case "ENTER":
                    time.sleep(1)
                    field.send_keys(Keys.ENTER)
                case _:
                    pass
    
    def wait_until_url_contains(self, text):
        return self.wait.until(EC.url_contains(text))
