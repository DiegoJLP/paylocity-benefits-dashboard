"""
Page Object for the Login page.

Selector strategy:
  - id attribute for Username and Password — stable, semantic ids confirmed from HTML
  - type+class CSS selector for the submit button — confirmed as button[type=submit].btn-primary
  - CSS class for error message — only option available on this page

Selectors confirmed from manual inspection:
  Username: <input class="form-control" id="Username" name="Username" type="text">
  Password: <input class="form-control" id="Password" name="Password" type="password">
  Submit:   <button type="submit" class="btn btn-primary">Log In</button>
  Error:    <div class="error-code">HTTP ERROR 405</div>
"""

import logging
import re

import allure
from playwright.sync_api import Page, expect

from config.settings import settings
from tests.ui.pages.base_page import BasePage

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
  """Encapsulates all interactions on the /Account/Login page."""

  # Path relative to BASE_URL
  PATH = "Account/Login"

  def __init__(self, page: Page) -> None:
    super().__init__(page)

    # ––– SELECTORS –––
    # Priority: stable id > type+class CSS > label > CSS
    # Confirmed from DevTools inspection during manual execution

    # id="Username" — stable
    self.username_input = page.locator("#Username")

    # id="Password" — stable
    self.password_input = page.locator("#Password")

    # <button type="submit" class="btn btn-primary">Log In</button>
    self.submit_button = page.locator("button[type='submit'].btn-primary")

    # <div class="error-code">HTTP ERROR 405</div> — confirmed from failed login
    self.error_message = page.locator("div.error-code")

  
  def navigate(self) -> None:
    """Go to the login page and wait for it to be ready."""
    super().navigate(self.PATH)
    self.wait_for_visible(self.submit_button, "Submit button")

  @allure.step("Log in with username='{username}'")
  def login(self, username: str, password: str) -> None:
    """
    Fill credentials and submit the login form.
    Waits for navigation to Benefits Dashboard after submit.
    Args:
      username: Login username.
      password: Login password.
    """
    self.fill(self.username_input, username, "Username field")
    self.fill(self.password_input, password, "Password field")
    with self.wait_for_api_response("Account/Login"):
      self.click(self.submit_button, "Submit button")
    self.wait_for_url("**/Benefits")

  @allure.step("Attempt login with empty credentials")
  def login_empty(self) -> None:
    """Submit the login form without filling any fields."""
    self.click(self.submit_button, "Submit button (empty form)")

  def get_error_message(self) -> str:
    """
    Return the visible error message text after a failed login.

    Returns:
      Error message text as a string.
    """
    self.wait_for_visible(self.error_message, "Error message")
    return self.get_text(self.error_message)

  def assert_error_visible(self) -> None:
    """Assert that a login error message is displayed on the page."""
    self.assert_visible(self.error_message, "Login error message")

  def assert_on_login_page(self) -> None:
    """Assert we are still on the login page after a failed attempt."""
    expect(self.page).to_have_url(re.compile(re.escape(self.PATH)))