"""
UI-specific fixtures — browser, screenshots, traces, console errors.

Only UI tests load these. API and unit tests never trigger a browser.
"""

import logging
import os
from collections.abc import Generator

import allure
import pytest
from playwright.sync_api import BrowserContext, Page

from config.settings import settings
from tests.ui.pages.login_page import LoginPage

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def configure_timeouts(page: Page) -> None:
  """Apply timeout settings from .env to every page."""
  page.set_default_timeout(settings.default_timeout)
  page.set_default_navigation_timeout(settings.navigation_timeout)


@pytest.fixture(autouse=True)
def capture_console_errors(page: Page, request: pytest.FixtureRequest) -> Generator:
  """
  Collect browser console errors during a test and attach to Allure on failure.
  Favicon 403 errors are filtered out — they are a known missing asset
  documented separately in the favicon xfail tests.
  Tests can also access errors directly via the console_errors fixture.
  """
  errors: list[str] = []

  def on_console(msg) -> None:
    if msg.type == "error":
      # "403 ()" with empty parens = browser asset/resource load failure with no
      # response body (static assets, favicon). Known infrastructure issue,
      # tested separately. Real API 403s carry a body and produce a different format.
      # "401 ()" is intentionally NOT filtered — it documents BUG-UI-008
      # (session expiry) and should surface in tests.
      if "403 ()" in msg.text:
        return
      text = f"[ERROR] {msg.text}"
      errors.append(text)
      logger.warning("Console error in %s: %s", request.node.name, text)

  page.on("console", on_console)
  yield errors

  if errors:
    allure.attach(
      "\n".join(errors),
      name="Console Errors",
      attachment_type=allure.attachment_type.TEXT,
    )


@pytest.fixture
def console_errors(capture_console_errors: list) -> list[str]:
  """
  Exposes collected console errors for tests that assert on them.

  Usage:
    def test_no_errors(page, console_errors):
      page.goto("/some-page")
      assert console_errors == []
  """
  return capture_console_errors


@pytest.fixture(autouse=True)
def screenshot_on_failure(page: Page, request: pytest.FixtureRequest) -> Generator:
  """Capture and attach a full-page screenshot to Allure when a test fails."""
  yield
  if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
    screenshot = page.screenshot(full_page=True)
    allure.attach(
      screenshot,
      name=f"Failure — {request.node.name}",
      attachment_type=allure.attachment_type.PNG,
    )
    logger.error("Test FAILED: %s — screenshot attached", request.node.name)


@pytest.fixture(autouse=True)
def capture_trace(context: BrowserContext, request: pytest.FixtureRequest) -> Generator:
  """
  Record a Playwright trace for every UI test.
  Saves to disk only on failure — discarded on pass to save disk space.
  Open the .zip at https://trace.playwright.dev to replay the test.
  """
  os.makedirs("reports/traces", exist_ok=True)
  context.tracing.start(screenshots=True, snapshots=True, sources=True)
  yield

  test_name = request.node.name.replace("/", "_").replace(" ", "_")
  trace_path = f"reports/traces/{test_name}.zip"
  failed = getattr(request.node, "rep_call", None)
  if failed and failed.failed:
    context.tracing.stop(path=trace_path)
    # allure-pytest 2.13.5 has no ZIP attachment type — log path instead
    allure.attach(
      f"Trace saved to: {trace_path}\nOpen at: https://trace.playwright.dev",
      name="Playwright Trace Path",
      attachment_type=allure.attachment_type.TEXT,
    )
    logger.info("Trace saved: %s", trace_path)
  else:
    context.tracing.stop()


@pytest.fixture
def authenticated_page(page: Page) -> Page:
  """
  Returns a Page already logged into the Benefits Dashboard.
  Use for UI tests that do not test the login flow itself.

  Usage:
    def test_add_employee(authenticated_page):
      dashboard = DashboardPage(authenticated_page)
  """
  login = LoginPage(page)
  login.navigate()
  login.login(settings.ui_username, settings.ui_password)
  logger.info("authenticated_page fixture: logged in as %s", settings.ui_username)
  return page
