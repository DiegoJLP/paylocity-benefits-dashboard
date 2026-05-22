"""
Root-level pytest fixtures shared across all tests

Fixture scope guide:
  session: created once for the entire run
  function: created and destroyed for every test

Autouse fixtures run automatically for every test
without the test explicitly requesting them.
"""

import logging
import os
from collections.abc import Generator

import allure
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright

from config.settings import settings
from helpers.api_client import ApiClient
from helpers.data_factory import EmployeeFactory

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
  """
  Override Playwright default launch args
  Reads HEADLESS from settings loaded from .env.
  """
  return {**browser_type_launch_args, "headless": settings.headless}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
  """
  Configure each browser context.
  Sets viewport size.
  """
  os.makedirs("reports/traces", exist_ok=True)

  return {
    **browser_context_args,
    "viewport": {"width": 1280, "height": 720},
  }


@pytest.fixture(autouse=True)
def configure_timeouts(page: Page) -> None:
  """Apply timeout settings from .env to every page."""
  page.set_default_timeout(settings.default_timeout)
  page.set_default_navigation_timeout(settings.navigation_timeout)


@pytest.fixture(autouse=True)
def capture_console_errors(page: Page,request: pytest.FixtureRequest) -> Generator:
  """
  Collect all browser console errors during a test.
  Attaches them to the Allure report after the test.
  Tests can also access errors via the console_errors fixture.
  """
  errors: list[str] = []

  def on_console(msg) -> None:
    if msg.type == "error":
      text = f"[ERROR] {msg.text}"
      errors.append(text)
      logger.warning(
        "Console error in %s: %s", request.node.name, text
      )

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
def screenshot_on_failure(page: Page,request: pytest.FixtureRequest) -> Generator:
  """
  Capture and attach a screenshot to Allure when a test fails.
  Runs automatically for every test.
  """
  yield
  if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
    screenshot = page.screenshot(full_page=True)
    allure.attach(
      screenshot,
      name=f"Failure — {request.node.name}",
      attachment_type=allure.attachment_type.PNG,
    )
    logger.error(
      "Test FAILED: %s — screenshot attached", request.node.name
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> Generator:
  """Store the test result on the node so fixtures can check it."""
  outcome = yield
  rep = outcome.get_result()
  setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(autouse=True)
def capture_trace(context: BrowserContext, request: pytest.FixtureRequest) -> Generator:
  """
  Record a Playwright trace for every test.
  Saves and attaches to Allure only on failure.
  Discards the trace on pass to save disk space.
  """
  context.tracing.start(
    screenshots=True,
    snapshots=True,
    sources=True,
  )
  yield

  test_name = request.node.name.replace("/", "_").replace(" ", "_")
  trace_path = f"reports/traces/{test_name}.zip"

  failed = getattr(request.node, "rep_call", None)
  if failed and failed.failed:
    context.tracing.stop(path=trace_path)
    allure.attach.file(
      trace_path,
      name="Playwright Trace",
      attachment_type=allure.attachment_type.ZIP,
    )
    logger.info("Trace saved: %s", trace_path)
  else:
    context.tracing.stop()


@pytest.fixture(scope="session")
def api(playwright: Playwright) -> Generator[ApiClient, None, None]:
  """
  Session-scoped API client.
  One instance shared across all tests in the run.
  """
  client = ApiClient(playwright)
  yield client
  client.dispose()

@pytest.fixture
def created_employee(api: ApiClient) -> Generator[dict, None, None]:
  """
  Creates a valid employee via API before a test
  and deletes it after regardless of test outcome

  Yields the full response body dict including the assigned id.

  Usage:
    def test_edit(page, created_employee):
      employee_id = created_employee["id"]
      first_name = created_employee["firstName"]
  """
  payload = EmployeeFactory.valid(dependants=0)
  response = api.create_employee(payload)
  assert response.status == 200, (
    f"Setup failed: could not create test employee.\n"
    f"Status: {response.status}\n"
    f"Body: {response.text()}"
  )
  employee_data = response.json()
  logger.info(
    "Fixture created employee: %s", employee_data.get("id")
  )

  yield employee_data

  # Teardown —> always runs even if the test failed
  api.cleanup_employee(employee_data["id"])
  logger.info(
    "Fixture cleaned up employee: %s", employee_data.get("id")
  )