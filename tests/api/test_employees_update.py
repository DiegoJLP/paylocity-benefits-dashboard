"""
PUT /api/Employees

Known bugs:
  BUG-API-003: salary mutable via PUT — marked xfail
  BUG-API-008: PUT without ID returns 405 — marked xfail
  BUG-API-009: PUT non-existent ID returns 405 — marked xfail
"""

import allure
import pytest

from helpers.api_client import ApiClient
from helpers.calculations import calculate_benefits
from helpers.data_factory import EmployeeFactory
from config.settings import settings


@allure.epic("API")
@allure.feature("Employees — Update")
@pytest.mark.api
class TestUpdateEmployee:

  @allure.title("PUT valid update — expect 200 and updated values")
  @pytest.mark.smoke
  def test_update_valid(self, api: ApiClient) -> None:
    employee_id = api.create_employee_and_get_id(
      EmployeeFactory.valid(dependants=0)
    )
    payload = EmployeeFactory.with_overrides(
      id=employee_id, dependants=2
    )
    response = api.update_employee(payload)
    assert response.status == 200, (
      f"Expected 200, got {response.status}"
    )
    body = response.json()
    assert body["dependants"] == 2
    expected = calculate_benefits(dependants=2)
    assert abs(body["benefitsCost"] - expected.benefits_cost) < 0.02
    assert abs(body["net"] - expected.net) < 0.02
    api.cleanup_employee(employee_id)

  @allure.title("PUT recalculates benefit cost on dependant change")
  @pytest.mark.smoke
  def test_update_recalculates(self, api: ApiClient) -> None:
    employee_id = api.create_employee_and_get_id(
      EmployeeFactory.valid(dependants=0)
    )
    payload = EmployeeFactory.with_overrides(
      id=employee_id, dependants=5
    )
    response = api.update_employee(payload)
    assert response.status == 200
    body = response.json()
    expected = calculate_benefits(dependants=5)
    assert abs(body["benefitsCost"] - expected.benefits_cost) < 0.02
    assert abs(body["net"] - expected.net) < 0.02
    api.cleanup_employee(employee_id)

  @allure.title("PUT missing firstName — expect 400")
  @pytest.mark.negative
  def test_update_missing_first_name(self, api: ApiClient) -> None:
    employee_id = api.create_employee_and_get_id(
      EmployeeFactory.valid()
    )
    payload = {"id": employee_id, "lastName": "Test", "dependants": 0}
    response = api.update_employee(payload)
    assert response.status == 400, (
      f"Expected 400, got {response.status}"
    )
    api.cleanup_employee(employee_id)

  @allure.title("PUT empty firstName — expect 400")
  @pytest.mark.negative
  def test_update_empty_first_name(self, api: ApiClient) -> None:
    employee_id = api.create_employee_and_get_id(
      EmployeeFactory.valid()
    )
    payload = EmployeeFactory.with_overrides(
      id=employee_id, firstName=""
    )
    response = api.update_employee(payload)
    assert response.status == 400, (
      f"Expected 400, got {response.status}"
    )
    api.cleanup_employee(employee_id)

  @allure.title("PUT dependants=33 — expect 400")
  @pytest.mark.negative
  def test_update_over_max_dependants(self, api: ApiClient) -> None:
    employee_id = api.create_employee_and_get_id(
      EmployeeFactory.valid()
    )
    payload = EmployeeFactory.with_overrides(
      id=employee_id, dependants=33
    )
    response = api.update_employee(payload)
    assert response.status == 400, (
      f"Expected 400, got {response.status}"
    )
    api.cleanup_employee(employee_id)

  @allure.title("PUT salary mutable — expect ignored (BUG-API-003)")
  @pytest.mark.negative
  @pytest.mark.xfail(
    reason="BUG-API-003: salary is mutable via PUT — violates business rules",
    strict=True,
  )
  def test_update_salary_readonly(self, api: ApiClient) -> None:
    employee_id = api.create_employee_and_get_id(
      EmployeeFactory.valid()
    )
    payload = EmployeeFactory.with_overrides(
      id=employee_id, salary=99999.0
    )
    response = api.update_employee(payload)
    assert response.status == 200
    body = response.json()
    assert abs(body["salary"] - 52000.0) < 0.01, (
      f"Salary was mutated to {body['salary']} — should be 52000"
    )
    api.cleanup_employee(employee_id)

  @allure.title("PUT without ID — expect 400 (BUG-API-008)")
  @pytest.mark.negative
  @pytest.mark.xfail(
    reason="BUG-API-008: PUT without ID returns 405 not 400",
    strict=True,
  )
  def test_update_no_id(self, api: ApiClient) -> None:
    payload = EmployeeFactory.valid()
    response = api.update_employee(payload)
    assert response.status == 400, (
      f"Expected 400, got {response.status}"
    )

  @allure.title("PUT non-existent ID — expect 404 (BUG-API-009)")
  @pytest.mark.negative
  @pytest.mark.xfail(
    reason="BUG-API-009: PUT non-existent ID returns 405 not 404",
    strict=True,
  )
  def test_update_nonexistent_id(self, api: ApiClient) -> None:
    payload = EmployeeFactory.with_overrides(
      id=EmployeeFactory.nonexistent_id()
    )
    response = api.update_employee(payload)
    assert response.status == 404, (
      f"Expected 404, got {response.status}"
    )