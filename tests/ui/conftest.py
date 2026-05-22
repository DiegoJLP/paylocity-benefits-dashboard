"""
UI-specific fixtures.

Only UI tests load these —> API tests never need a browser session.
Keeping these separate from the root conftest avoids loading
browser fixtures for API-only test runs.
"""

import logging

import pytest
from playwright.sync_api import Page

from config.settings import settings
from tests.ui.pages.login_page import LoginPage

logger = logging.getLogger(__name__)


@pytest.fixture
def authenticated_page(page: Page) -> Page:
  """
  Returns a Page that is already logged into the Benefits Dashboard.

  Use this for UI tests that do not test login itself.
  Avoids repeating the login flow in every test.

  Usage:
    def test_add_employee(authenticated_page):
      dashboard = DashboardPage(authenticated_page)
      dashboard.navigate()
      dashboard.add_employee("John", "Doe")
  """
  login = LoginPage(page)
  login.navigate()
  login.login(settings.ui_username, settings.ui_password)
  logger.info("authenticated_page fixture: logged in as %s", settings.ui_username)
  return page