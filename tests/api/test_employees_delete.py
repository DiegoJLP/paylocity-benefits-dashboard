"""
DELETE /api/Employees/{id}

Known bugs:
  BUG-API-010: DELETE already-deleted returns 200 — marked xfail
  BUG-API-006: DELETE non-existent returns 500 — marked xfail
"""

import allure
import pytest

from helpers.api_client import ApiClient
from helpers.data_factory import EmployeeFactory


@allure.epic("API")
@allure.feature("Employees — Delete")
@pytest.mark.api
class TestDeleteEmployee:

  @allure.title("DELETE existing employee — expect 200")
  @pytest.mark.smoke
  def test_delete_existing(self, api: ApiClient) -> None:
    employee_id = api.create_employee_and_get_id(EmployeeFactory.valid())
    response = api.delete_employee(employee_id)
    assert response.status == 200, (f"Expected 200, got {response.status}")

  @allure.title("DELETE then GET — employee is gone")
  @pytest.mark.smoke
  def test_delete_then_get_returns_500(self, api: ApiClient) -> None:
    # BUG-API-008: DELETE succeeds (200) but record is not removed from the data store.
    # A subsequent GET on the same ID still returns 200 with the full employee body.
    # Expected: 404 (not found) or 500. Actual: 200.
    # Failing test left as proof of the bug — do not xfail.
    employee_id = api.create_employee_and_get_id(EmployeeFactory.valid())
    api.delete_employee(employee_id)
    response = api.get_employee(employee_id)
    assert response.status in (404, 500), (f"Expected 404 or 500 after deletion, got {response.status}")

  @allure.title("DELETE non-existent ID — expect 404 (BUG-API-006)")
  @pytest.mark.negative
  @pytest.mark.xfail(reason="BUG-API-006: non-existent ID returns 500 not 404", strict=True,)
  def test_delete_nonexistent(self, api: ApiClient) -> None:
    response = api.delete_employee(EmployeeFactory.nonexistent_id())
    assert response.status == 404, (f"Expected 404, got {response.status}")

  @allure.title("DELETE same employee twice — second expect 404 (BUG-API-010)")
  @pytest.mark.negative
  @pytest.mark.xfail(reason="BUG-API-010: second DELETE returns 200 instead of 404", strict=True)
  def test_delete_twice(self, api: ApiClient) -> None:
    employee_id = api.create_employee_and_get_id(EmployeeFactory.valid())
    api.delete_employee(employee_id)
    response = api.delete_employee(employee_id)
    assert response.status == 404, (f"Expected 404 on second delete, got {response.status}")

  @allure.title("DELETE malformed UUID — expect 400 (BUG-API-007)")
  @pytest.mark.negative
  @pytest.mark.xfail(reason="BUG-API-007: malformed UUID returns 405 not 400",strict=True)
  def test_delete_malformed_uuid(self, api: ApiClient) -> None:
    response = api.delete_employee("not-a-valid-uuid")
    assert response.status in (400, 404), (
      f"Expected 400 or 404, got {response.status}"
    )