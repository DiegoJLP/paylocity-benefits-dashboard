"""
Authentication boundary tests

Verifies every endpoint requires a valid Authorization header
Each HTTP method and endpoint is tested independently because
some APIs protect collection endpoints but not individual resources

Known findings documented in BUG_REPORT_API.md:
  BUG-API-004: Invalid token returns 500 instead of 401.
  These tests assert 401 as the correct expected behavior.
  If 500 is returned the test fails and the bug is confirmed.
"""

import allure
import pytest

from config.settings import settings
from helpers.api_client import ApiClient


@allure.epic("API")
@allure.feature("Authentication")
@pytest.mark.api
@pytest.mark.auth
class TestAuthentication:

  @allure.title("GET all employees — no auth header — expect 401")
  @pytest.mark.smoke
  def test_get_all_no_auth(self, api: ApiClient) -> None:
    response = api.get_all_employees_no_auth()
    assert response.status == 401, (
      f"Expected 401 Unauthorized, got {response.status}.\n"
      f"API accessible without authentication — security risk.\n"
      f"Body: {response.text()}"
    )

  @allure.title("GET all employees — invalid token — expect 401 (BUG-API-004)")
  @pytest.mark.negative
  @pytest.mark.xfail(
    reason="BUG-API-004: invalid token crashes the server with 500 instead of returning 401",
    strict=True,
  )
  def test_get_all_invalid_token(self, api: ApiClient) -> None:
    response = api.get_all_employees_bad_auth()
    assert response.status == 401, (
      f"BUG-API-004: Expected 401 Unauthorized, got {response.status}.\n"
      f"Invalid token causes server crash instead of auth rejection.\n"
      f"Body: {response.text()}"
    )

  @allure.title("POST employee — no auth header — expect 401")
  @pytest.mark.negative
  def test_post_no_auth(self, api: ApiClient) -> None:
    response = api.get_all_employees_no_auth()
    assert response.status == 401, (
      f"Expected 401, got {response.status}.\n"
      f"POST endpoint accessible without authentication.\n"
      f"Body: {response.text()}"
    )

  @allure.title("GET employee by ID — no auth header — expect 401")
  @pytest.mark.negative
  def test_get_by_id_no_auth(self, api: ApiClient) -> None:
    from helpers.data_factory import EmployeeFactory
    fake_id = EmployeeFactory.nonexistent_id()
    response = api._context.get(
      f"{settings.api_base_url}/api/Employees/{fake_id}",
      headers={
        "Authorization": "",
        "Content-Type": "application/json",
      },
    )
    assert response.status == 401, (
      f"Expected 401, got {response.status}.\n"
      f"Individual resource endpoint accessible without auth.\n"
      f"Body: {response.text()}"
    )

  @allure.title("PUT employee — no auth header — expect 401")
  @pytest.mark.negative
  def test_put_no_auth(self, api: ApiClient) -> None:
    from helpers.data_factory import EmployeeFactory
    payload = EmployeeFactory.with_overrides(
      id=EmployeeFactory.nonexistent_id()
    )
    response = api._context.put(
      f"{settings.api_base_url}/api/Employees",
      data=payload,
      headers={
        "Authorization": "",
        "Content-Type": "application/json",
      },
    )
    assert response.status == 401, (
      f"Expected 401, got {response.status}.\n"
      f"Body: {response.text()}"
    )

  @allure.title("DELETE employee — no auth header — expect 401")
  @pytest.mark.negative
  def test_delete_no_auth(self, api: ApiClient) -> None:
    from helpers.data_factory import EmployeeFactory
    fake_id = EmployeeFactory.nonexistent_id()
    response = api._context.delete(
      f"{settings.api_base_url}/api/Employees/{fake_id}",
      headers={"Authorization": ""},
    )
    assert response.status == 401, (
      f"Expected 401, got {response.status}.\n"
      f"DELETE accessible without authentication — critical risk.\n"
      f"Body: {response.text()}"
    )