"""
POST /api/Employees

Known bugs affecting assertions (see BUG_REPORT_API.md):
  BUG-API-002: username always overwritten with authenticated user
  BUG-API-011: benefitsCost and net have 5dp — use tolerance 0.02
  BUG-API-001: missing username returns 200 — marked xfail
"""

import allure
import pytest

from helpers.api_client import ApiClient
from helpers.calculations import calculate_benefits
from helpers.data_factory import EmployeeFactory
from config.settings import settings


@allure.epic("API")
@allure.feature("Employees — Create")
@pytest.mark.api
class TestCreateEmployee:

  @allure.title("POST valid employee — expect 200 and correct schema")
  @pytest.mark.smoke
  def test_create_valid_employee(self, api: ApiClient) -> None:
    payload = EmployeeFactory.valid(dependants=0)
    response = api.create_employee(payload)

    assert response.status == 200, (
      f"Expected 200, got {response.status}: {response.text()}"
    )
    body = response.json()

    # Schema — all fields present
    for field in ("id", "firstName", "lastName", "dependants", "gross", "benefitsCost", "net", "partitionKey", "sortKey", "salary"):
      assert field in body, f"Missing field: {field}"

    # id assigned by server
    assert body["id"], "id field is empty"

    # firstName and lastName match request
    assert body["firstName"] == payload["firstName"]
    assert body["lastName"] == payload["lastName"]

    # BUG-API-002: username always overwritten with login credentials
    assert body["username"] == settings.ui_username, (
      f"BUG-API-002: username overwritten with {body['username']}"
    )

    api.cleanup_employee(body["id"])

  @allure.title("POST 0 dependants — calculations correct")
  @pytest.mark.smoke
  def test_create_calculations_zero_dependants(self, api: ApiClient) -> None:
    payload = EmployeeFactory.valid(dependants=0)
    response = api.create_employee(payload)
    assert response.status == 200
    body = response.json()

    expected = calculate_benefits(dependants=0)
    # BUG-API-011: values have 5dp — use tolerance
    assert abs(body["gross"] - expected.gross) < 0.02
    assert abs(body["benefitsCost"] - expected.benefits_cost) < 0.02
    assert abs(body["net"] - expected.net) < 0.02

    api.cleanup_employee(body["id"])

  @allure.title("POST 2 dependants — calculations correct")
  @pytest.mark.smoke
  def test_create_calculations_two_dependants(self, api: ApiClient) -> None:
    payload = EmployeeFactory.valid(dependants=2)
    response = api.create_employee(payload)
    assert response.status == 200
    body = response.json()

    expected = calculate_benefits(dependants=2)
    assert abs(body["benefitsCost"] - expected.benefits_cost) < 0.02
    assert abs(body["net"] - expected.net) < 0.02

    api.cleanup_employee(body["id"])

  @allure.title("POST 32 dependants (max boundary) — expect 200")
  @pytest.mark.regression
  def test_create_max_dependants(self, api: ApiClient) -> None:
    payload = EmployeeFactory.max_dependants()
    response = api.create_employee(payload)
    assert response.status == 200, (
      f"Expected 200 at max boundary, got {response.status}"
    )
    body = response.json()
    expected = calculate_benefits(dependants=32)
    assert abs(body["benefitsCost"] - expected.benefits_cost) < 0.02

    api.cleanup_employee(body["id"])

  @allure.title("POST missing firstName — expect 400")
  @pytest.mark.negative
  def test_create_missing_first_name(self, api: ApiClient) -> None:
    payload = EmployeeFactory.missing_field("firstName")
    response = api.create_employee(payload)
    assert response.status == 400, (
      f"Expected 400, got {response.status}: {response.text()}"
    )

  @allure.title("POST missing lastName — expect 400")
  @pytest.mark.negative
  def test_create_missing_last_name(self, api: ApiClient) -> None:
    payload = EmployeeFactory.missing_field("lastName")
    response = api.create_employee(payload)
    assert response.status == 400, (
      f"Expected 400, got {response.status}: {response.text()}"
    )

  @allure.title("POST missing username — expect 400 (BUG-API-001)")
  @pytest.mark.negative
  @pytest.mark.xfail(reason="BUG-API-001: API accepts request without required username", strict=True)
  def test_create_missing_username(self, api: ApiClient) -> None:
    payload = EmployeeFactory.missing_field("username")
    response = api.create_employee(payload)
    assert response.status == 400, (
      f"Expected 400, got {response.status}: {response.text()}"
    )

  @allure.title("POST empty body — expect 400")
  @pytest.mark.negative
  def test_create_empty_body(self, api: ApiClient) -> None:
    response = api.create_employee(EmployeeFactory.empty_body())
    assert response.status == 400, (
      f"Expected 400, got {response.status}"
    )

  @allure.title("POST firstName empty string — expect 400")
  @pytest.mark.negative
  def test_create_empty_first_name(self, api: ApiClient) -> None:
    payload = EmployeeFactory.empty_field("firstName")
    response = api.create_employee(payload)
    assert response.status == 400, (
      f"Expected 400, got {response.status}: {response.text()}"
    )

  @allure.title("POST firstName whitespace only — expect 400")
  @pytest.mark.negative
  def test_create_whitespace_first_name(self, api: ApiClient) -> None:
    payload = EmployeeFactory.whitespace_field("firstName")
    response = api.create_employee(payload)
    assert response.status == 400, (
      f"Expected 400, got {response.status}: {response.text()}"
    )

  @allure.title("POST firstName exactly 50 chars — expect 200")
  @pytest.mark.regression
  def test_create_first_name_at_max_length(
    self, api: ApiClient
  ) -> None:
    payload = EmployeeFactory.field_at_max_length("firstName")
    response = api.create_employee(payload)
    assert response.status == 200, (
      f"Expected 200 at max boundary, got {response.status}"
    )
    api.cleanup_employee(response.json()["id"])

  @allure.title("POST firstName 51 chars — expect 400")
  @pytest.mark.negative
  def test_create_first_name_over_max_length(
    self, api: ApiClient
  ) -> None:
    payload = EmployeeFactory.field_over_max_length("firstName")
    response = api.create_employee(payload)
    assert response.status == 400, (
      f"Expected 400, got {response.status}: {response.text()}"
    )

  @allure.title("POST dependants=33 (over max) — expect 400")
  @pytest.mark.negative
  def test_create_over_max_dependants(self, api: ApiClient) -> None:
    payload = EmployeeFactory.over_max_dependants()
    response = api.create_employee(payload)
    assert response.status == 400, (
      f"Expected 400, got {response.status}: {response.text()}"
    )

  @allure.title("POST dependants=-1 (below min) — expect 400")
  @pytest.mark.negative
  def test_create_negative_dependants(self, api: ApiClient) -> None:
    payload = EmployeeFactory.negative_dependants()
    response = api.create_employee(payload)
    assert response.status == 400, (
      f"Expected 400, got {response.status}: {response.text()}"
    )

  @allure.title("POST dependants as string — expect 400")
  @pytest.mark.negative
  @pytest.mark.xfail(reason="BUG-API-005: string in dependants returns 405 not 400", strict=True)
  def test_create_string_dependants(self, api: ApiClient) -> None:
    payload = EmployeeFactory.string_dependants()
    response = api.create_employee(payload)
    assert response.status == 400, (
      f"Expected 400, got {response.status}: {response.text()}"
    )

  @allure.title("POST readOnly fields — server must ignore them")
  @pytest.mark.regression
  def test_create_readonly_fields_ignored(self, api: ApiClient) -> None:
    payload = EmployeeFactory.with_readonly_fields()
    response = api.create_employee(payload)

    assert response.status == 200, (
      f"Expected 200, got {response.status}: {response.text()}"
    )
    body = response.json()

    # Server must NOT use caller-supplied readOnly values
    assert abs(body["gross"] - 2000.0) < 0.02, (
      f"gross was not computed by server: {body['gross']}"
    )
    assert body["gross"] != 9999.0, (
      "Server accepted caller-supplied gross — readOnly not enforced"
    )

    api.cleanup_employee(body["id"])

  @allure.title("POST SQL injection in firstName — handled safely")
  @pytest.mark.negative
  def test_create_sql_injection_first_name(self, api: ApiClient) -> None:
    payload = EmployeeFactory.sql_injection("firstName")
    response = api.create_employee(payload)

    # Acceptable: 200 saved as literal OR 400 rejected
    # Unacceptable: 500 server crash
    assert response.status in (200, 400), (
      f"SQL injection caused server crash: {response.status}\n"
      f"Body: {response.text()}"
    )
    if response.status == 200:
      api.cleanup_employee(response.json()["id"])