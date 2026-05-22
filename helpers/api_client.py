"""
- Sets Authorization header on every request
- Provides one method per endpoint
- Logs every request and response
- Used in API tests AND as setup/teardown for UI tests
"""

import logging

import allure
from playwright.sync_api import APIRequestContext, Playwright

from config.settings import settings

logger = logging.getLogger(__name__)


class ApiClient:
  def __init__(self, playwright: Playwright) -> None:
    self._context: APIRequestContext = playwright.request.new_context(
      base_url=settings.api_base_url,
      extra_http_headers={
        "Authorization": f"Basic {settings.auth_token}",
        "Content-Type": "application/json",
      },
    )

  def dispose(self) -> None:
    """Clears the request context, called in fixture teardown to avoid resource leaks."""
    self._context.dispose()

  @allure.step("API POST /api/Employees")
  def create_employee(self, payload: dict):
    logger.info("POST /api/Employees | payload: %s", payload)
    response = self._context.post(
      f"{settings.api_base_url}/api/Employees", data=payload
    )
    body_text = response.text()
    logger.debug("Response | status: %s | body: %s", response.status, body_text[:500])
    return response

  @allure.step("API GET /api/Employees")
  def get_all_employees(self):
    logger.info("GET /api/Employees")
    response = self._context.get(
      f"{settings.api_base_url}/api/Employees"
    )
    body_text = response.text()
    logger.debug("Response | status: %s | body: %s", response.status, body_text[:500])
    return response

  @allure.step("API GET /api/Employees/{employee_id}")
  def get_employee(self, employee_id: str):
    logger.info("GET /api/Employees/%s", employee_id)
    response = self._context.get(
      f"{settings.api_base_url}/api/Employees/{employee_id}"
    )
    body_text = response.text()
    logger.debug("Response | status: %s | body: %s", response.status, body_text[:500])
    return response

  @allure.step("API PUT /api/Employees")
  def update_employee(self, payload: dict):
    logger.info("PUT /api/Employees | payload: %s", payload)
    response = self._context.put(
      f"{settings.api_base_url}/api/Employees", data=payload
    )
    body_text = response.text()
    logger.debug("Response | status: %s | body: %s", response.status, body_text[:500])
    return response

  @allure.step("API DELETE /api/Employees/{employee_id}")
  def delete_employee(self, employee_id: str):
    logger.info("DELETE /api/Employees/%s", employee_id)
    response = self._context.delete(
      f"{settings.api_base_url}/api/Employees/{employee_id}"
    )
    body_text = response.text()
    logger.debug("Response | status: %s | body: %s", response.status, body_text[:500])
    return response

  @allure.step("API GET /api/Employees — no auth header")
  def get_all_employees_no_auth(self):
    logger.info("GET /api/Employees (no auth)")
    response = self._context.get(
      f"{settings.api_base_url}/api/Employees",
      headers={
        "Authorization": "",
        "Content-Type": "application/json",
      },
    )
    body_text = response.text()
    logger.debug("Response | status: %s | body: %s", response.status, body_text[:500])
    return response

  @allure.step("API GET /api/Employees — invalid auth token")
  def get_all_employees_bad_auth(self):
    logger.info("GET /api/Employees (bad auth)")
    response = self._context.get(
      f"{settings.api_base_url}/api/Employees",
      headers={
        "Authorization": "Basic invalidtoken==",
        "Content-Type": "application/json",
      },
    )
    body_text = response.text()
    logger.debug("Response | status: %s | body: %s", response.status, body_text[:500])
    return response

  def create_employee_and_get_id(self, payload: dict) -> str:
    """
    Create an employee and return the ID.
    Raises AssertionError if creation fails.
    """
    response = self.create_employee(payload)
    assert response.status == 200, (
      f"Setup failed: could not create test employee\n"
      f"Status: {response.status}"
    )
    data = response.json()
    employee_id = data.get("id")
    assert employee_id, f"Response did not include id field: {data}"
    logger.info("Created employee with id: %s", employee_id)
    return employee_id

  def cleanup_employee(self, employee_id: str) -> None:
    """Delete an employee silently for teardown. Does not raise on 404."""
    response = self.delete_employee(employee_id)
    if response.status not in (200, 404):
      logger.warning(
        "Unexpected status %s when cleaning up employee %s", response.status, employee_id,
      )
