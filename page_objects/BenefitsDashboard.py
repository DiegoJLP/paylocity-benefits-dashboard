from page_objects.BasePage import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class BenefitsDashboard(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.add_employee_button_xpath = '(//*[@id="add"])'
        self.first_name_xpath = '(//*[@id="firstName"])'
        self.last_name_xpath = '(//*[@id="lastName"])'
        self.dependents_xpath = '(//*[@id="dependants"])'
        self.submit_button_xpath = '(//*[@id="addEmployee"])'

    def add_employee(self, first_name, last_name, dependents):
        self.scroll_to(self.add_employee_button_xpath)
        self.click_element(self.add_employee_button_xpath)
        self.type(self.first_name_xpath, first_name)
        self.type(self.last_name_xpath, last_name)
        self.type(self.dependents_xpath, dependents)
        self.click_element(self.submit_button_xpath)