"""
Root-level pytest fixtures shared across all tests

Fixture scope guide:
  session: created once for the entire run
  function: created and destroyed for every test
"""

import logging
from collections.abc import Generator

import pytest
from playwright.sync_api import Playwright

from config.settings import settings
from helpers.api_client import ApiClient
from helpers.data_factory import EmployeeFactory

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
  """Override Playwright default launch args. Reads HEADLESS from .env."""
  return {**browser_type_launch_args, "headless": settings.headless}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
  """Configure each browser context with a fixed viewport size."""
  return {
    **browser_context_args,
    "viewport": {"width": 1280, "height": 720},
  }


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> Generator:
  """Store the test result on the node so fixtures can check it."""
  outcome = yield
  rep = outcome.get_result()
  setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(scope="session")
def api(playwright: Playwright) -> Generator[ApiClient, None, None]:
  """Session-scoped API client. One instance shared across all tests."""
  client = ApiClient(playwright)
  yield client
  client.dispose()


@pytest.fixture(scope="session", autouse=True)
def cleanup_all_employees(api: ApiClient) -> Generator[None, None, None]:
  """
  Session teardown: delete every employee from the test account after every run.
  Prevents ghost records from accumulating across runs.
  Note: BUG-API-008 means DELETE may not actually remove records server-side,
  but we attempt cleanup regardless so the intent is clear in the logs.
  """
  yield
  response = api.get_all_employees()
  if response.status != 200:
    logger.warning(
      "Session cleanup: could not fetch employee list (status %s) — skipping",
      response.status,
    )
    return
  employees = response.json()
  for employee in employees:
    api.cleanup_employee(employee.get("id"))
  logger.info("Session cleanup: attempted deletion of %d employees", len(employees))


@pytest.fixture
def created_employee(api: ApiClient) -> Generator[dict, None, None]:
  """
  Creates a valid employee via API before a test and deletes it after,
  regardless of test outcome. Yields the full response body dict.

  Usage:
    def test_edit(page, created_employee):
      employee_id = created_employee["id"]
  """
  payload = EmployeeFactory.valid(dependants=0)
  response = api.create_employee(payload)
  assert response.status == 200, (
    f"Setup failed: could not create test employee.\n"
    f"Status: {response.status}"
  )
  employee_data = response.json()
  logger.info("Fixture created employee: %s", employee_data.get("id"))

  yield employee_data

  api.cleanup_employee(employee_data["id"])
  logger.info("Fixture cleaned up employee: %s", employee_data.get("id"))
