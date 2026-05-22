"""
GET /api/Employees
GET /api/Employees/{id}

Known bugs affecting assertions:
  BUG-API-006: non-existent ID returns 500 + HTML — marked xfail
  BUG-API-007: malformed UUID returns 405 — marked xfail
"""

import allure
import pytest

from helpers.api_client import ApiClient
from helpers.data_factory import EmployeeFactory
from helpers.schema_validator import SchemaValidator


@allure.epic("API")
@allure.feature("Employees — Read")
@pytest.mark.api
class TestReadEmployees:

  @allure.title("GET all employees — expect 200 and array")
  @pytest.mark.smoke
  def test_get_all_returns_list(self, api: ApiClient) -> None:
    response = api.get_all_employees()

    assert response.status == 200, (
      f"Expected 200, got {response.status}: {response.text()}"
    )
    body = response.json()
    assert isinstance(body, list), (
      f"Expected list, got {type(body).__name__}: {body}"
    )

  @allure.title("GET all — created employee appears in list")
  @pytest.mark.smoke
  def test_created_employee_in_list(self, api: ApiClient) -> None:
    payload = EmployeeFactory.valid()
    employee_id = api.create_employee_and_get_id(payload)

    response = api.get_all_employees()
    assert response.status == 200
    ids = [e["id"] for e in response.json()]
    assert employee_id in ids, (
      f"Created employee {employee_id} not found in GET all"
    )

    api.cleanup_employee(employee_id)

  @allure.title("GET created employee — schema valid")
  @pytest.mark.regression
  def test_get_all_schema_valid(self, api: ApiClient) -> None:
    # Validates schema on the employee we own, not the full list.
    # The full list contains ghost records (gross=0, salary=0) left by BUG-API-008
    # (DELETE returns 200 but does not remove the record). Validating all records
    # would cause a false failure unrelated to our test. See test_list_no_ghost_records.
    payload = EmployeeFactory.valid()
    employee_id = api.create_employee_and_get_id(payload)

    response = api.get_employee(employee_id)
    assert response.status == 200
    SchemaValidator.validate_employee(response.json())

    api.cleanup_employee(employee_id)

  @allure.title("GET all — no ghost records with corrupt data (BUG-API-008)")
  @pytest.mark.regression
  @pytest.mark.xfail(
    reason="BUG-API-008: DELETE does not remove records — ghost employees with salary=0/gross=0 accumulate in the list",
    strict=True,
  )
  def test_list_no_ghost_records(self, api: ApiClient) -> None:
    response = api.get_all_employees()
    assert response.status == 200
    SchemaValidator.validate_employee_list(response.json())

  @allure.title("GET existing employee by ID — expect 200")
  @pytest.mark.smoke
  def test_get_existing_employee(self, api: ApiClient) -> None:
    payload = EmployeeFactory.valid()
    employee_id = api.create_employee_and_get_id(payload)

    response = api.get_employee(employee_id)
    assert response.status == 200, (
      f"Expected 200, got {response.status}: {response.text()}"
    )
    body = response.json()
    assert body["id"] == employee_id

    api.cleanup_employee(employee_id)

  @allure.title("GET existing employee — schema valid")
  @pytest.mark.regression
  def test_get_by_id_schema_valid(self, api: ApiClient) -> None:
    payload = EmployeeFactory.valid()
    employee_id = api.create_employee_and_get_id(payload)

    response = api.get_employee(employee_id)
    assert response.status == 200
    SchemaValidator.validate_employee(response.json())

    api.cleanup_employee(employee_id)

  @allure.title("GET non-existent ID — expect 404 (BUG-API-006)")
  @pytest.mark.negative
  @pytest.mark.xfail(reason="BUG-API-006: non-existent ID returns 500 with HTML body", strict=True)
  def test_get_nonexistent_employee(self, api: ApiClient) -> None:
    fake_id = EmployeeFactory.nonexistent_id()
    response = api.get_employee(fake_id)
    assert response.status == 404, (
      f"Expected 404, got {response.status}: {response.text()}"
    )

  @allure.title("GET malformed UUID — expect 400 (BUG-API-007)")
  @pytest.mark.negative
  @pytest.mark.xfail(reason="BUG-API-007: malformed UUID returns 405 not 400", strict=True,)
  def test_get_malformed_uuid(self, api: ApiClient) -> None:
    response = api.get_employee("not-a-valid-uuid")
    assert response.status in (400, 404), (
      f"Expected 400 or 404, got {response.status}: {response.text()}"
    )