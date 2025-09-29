import pytest
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#Page objects
from page_objects.LogIn import LogIn
from page_objects.BenefitsDashboard import BenefitsDashboard

#Utils
from utils.decorators import capture_screenshot
from utils.environment import environment

#Test data
test_data = {
    "first_name": "Post",
    "last_name": "Malone",
    "dependents": "2"
}

invalid_test_data = {
    "first_name": "",
    "last_name": "123",
    "dependents": "0"
}

url = f'{environment["prod"]["base_url"]}/Account/Login'

def test_ui_bugs(driver):
    login_page = LogIn(driver)
    benefits_dashboard = BenefitsDashboard(driver)

    #Decided to structure the test this way to capture all assertion errors and report them at once, and avoid opening the browser several times
    errors = []
    try:
        driver.get(url)
        time.sleep(2)
        # Log in
        login_page.login(environment["prod"]["username"], environment["prod"]["password"])
        login_page.wait_until_url_contains("Benefits")
        try:
            assert "Benefits" in driver.title, "Login failed or Benefits page not loaded"
        except AssertionError as e:
            screenshot_path = capture_screenshot(driver, "login_error")
            errors.append(str(e))

        # Add new valid employee
        benefits_dashboard.add_employee(test_data["first_name"], test_data["last_name"], test_data["dependents"])
        row = driver.find_element(By.XPATH, "//table//tr[td[contains(text(), 'Malone')]]")
        benefits_dashboard.scroll_to(f"//table//tr[td[contains(text(), '{test_data['last_name']}')]]")
        tds = row.find_elements(By.TAG_NAME, "td")
        time.sleep(2)  # Wait for UI to load table
        try:
            assert tds[1].text == "Malone", f"Expected last name in 2nd column, but got '{tds[1].text}'"
        except AssertionError as e:
            screenshot_path = capture_screenshot(driver, "last_name_error")
            errors.append(str(e))
        try:
            assert tds[2].text == "Post", f"Expected first name in 3rd column, but got '{tds[2].text}'"
        except AssertionError as e:
            screenshot_path = capture_screenshot(driver, "first_name_error")
            errors.append(str(e))
        
        # Add invalid employee
        benefits_dashboard.scroll_to(benefits_dashboard.add_employee_button_xpath)
        benefits_dashboard.click_element(benefits_dashboard.add_employee_button_xpath)
        benefits_dashboard.type(benefits_dashboard.first_name_xpath, invalid_test_data["first_name"])
        benefits_dashboard.type(benefits_dashboard.last_name_xpath, invalid_test_data["last_name"])
        benefits_dashboard.type(benefits_dashboard.dependents_xpath, invalid_test_data["dependents"])

        # Assert that the add button is not clickable (disabled)
        add_button = driver.find_element(By.XPATH, benefits_dashboard.add_employee_button_xpath)
        try:
            assert not add_button.is_enabled(), "Add Employee button should be disabled for invalid data, but it is enabled."
        except AssertionError as e:
            errors.append(str(e))

    except Exception as e:
        screenshot_path = capture_screenshot(driver, "test_add_employee")
        pytest.fail(f"Test failed: {e}. Screenshot saved at {screenshot_path}")

    if errors:
        pytest.fail("Assertions failed:\n" + "\n".join(errors))