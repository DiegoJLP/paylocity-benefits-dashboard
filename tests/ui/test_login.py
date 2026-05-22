"""
UI Login tests.

Selector note:
  error_message selector may need adjusting after first run.
  BUG-UI-009: wrong username returns 405 — marked xfail.
"""

import allure
import pytest

from config.settings import settings
from tests.ui.pages.login_page import LoginPage


@allure.epic("UI")
@allure.feature("Login")
@pytest.mark.ui
class TestLogin:

  @allure.title("Valid credentials — redirect to dashboard")
  @pytest.mark.smoke
  def test_valid_login(self, page) -> None:
    login = LoginPage(page)
    login.navigate()
    login.login(settings.ui_username, settings.ui_password)
    login.assert_url_contains("Benefits")

  @allure.title("Wrong password — stays on login")
  @pytest.mark.negative
  @pytest.mark.xfail(reason="BUG-UI-009: wrong credentials may return 405", strict=False)
  def test_wrong_password(self, page) -> None:
    login = LoginPage(page)
    login.navigate()
    login.fill(login.username_input, settings.ui_username, "Username")
    login.fill(login.password_input, "wrongpassword123", "Password")
    login.click(login.submit_button, "Submit")
    login.assert_on_login_page()

  @allure.title("Empty credentials — stays on login")
  @pytest.mark.negative
  def test_empty_credentials(self, page) -> None:
    login = LoginPage(page)
    login.navigate()
    login.login_empty()
    login.assert_on_login_page()

  @allure.title("Wrong username — returns 405 (BUG-UI-009)")
  @pytest.mark.negative
  @pytest.mark.xfail(reason="BUG-UI-009: wrong username returns 405 browser error page", strict=True,
  )
  def test_wrong_username_returns_graceful_error(self, page) -> None:
    login = LoginPage(page)
    login.navigate()
    login.fill(login.username_input, "wronguser", "Username")
    login.fill(login.password_input, settings.ui_password, "Password")
    login.click(login.submit_button, "Submit")
    login.assert_on_login_page()
    login.assert_error_visible()

  @allure.title("No console errors on login page load")
  @pytest.mark.regression
  def test_no_console_errors_on_load(self, page, console_errors) -> None:
    login = LoginPage(page)
    login.navigate()
    assert console_errors == [], (f"Console errors on login page load: {console_errors}")

  @allure.title("Favicon loads without 403 on login page (BUG-UI-010)")
  @pytest.mark.regression
  @pytest.mark.xfail(reason="BUG-UI-010: favicon.ico not deployed, always returns 403", strict=False)
  def test_favicon_no_error(self, page) -> None:
    favicon_errors = []
    page.on("response", lambda r: favicon_errors.append(r.url) if "favicon" in r.url.lower() and r.status == 403 else None)
    login = LoginPage(page)
    login.navigate()
    assert not favicon_errors, f"Favicon returned 403: {favicon_errors}"

  @allure.title("Password field is masked")
  @pytest.mark.regression
  def test_password_field_masked(self, page) -> None:
    login = LoginPage(page)
    login.navigate()
    field_type = login.password_input.get_attribute("type")
    assert field_type == "password", (f"Password field type should be 'password', got '{field_type}'")