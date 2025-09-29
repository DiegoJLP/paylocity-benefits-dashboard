from page_objects.BasePage import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class LogIn(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.username_xpath = '(//*[@id="Username"])'
        self.password_xpath = '(//*[@id="Password"])'
        self.login_button_xpath = '(/html/body/div/main/div/div/form/button)'

    def login(self, username, password):
        self.type(self.username_xpath, username)
        self.type(self.password_xpath, password)
        self.click_element(self.login_button_xpath)