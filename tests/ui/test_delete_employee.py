"""
UI Delete Employee tests.

Uses created_employee fixture for API-driven setup.
"""

import allure
import pytest

from helpers.data_factory import EmployeeFactory
from tests.ui.pages.dashboard_page import DashboardPage


@allure.epic("UI")
@allure.feature("Delete Employee")
@pytest.mark.ui
class TestDeleteEmployee:

  @allure.title("Delete employee — row disappears from table")
  @pytest.mark.smoke
  def test_delete_employee_removed_from_table(self, authenticated_page, created_employee) -> None:
    dashboard = DashboardPage(authenticated_page)
    dashboard.navigate()

    employee_id = created_employee["id"]
    first_name = created_employee["firstName"]

    dashboard.delete_employee(first_name)
    dashboard.assert_employee_not_in_table(employee_id)

  @allure.title("Delete employee — still gone after page reload")
  @pytest.mark.smoke
  def test_delete_persists_after_reload(self, authenticated_page, created_employee) -> None:
    dashboard = DashboardPage(authenticated_page)
    dashboard.navigate()

    employee_id = created_employee["id"]
    first_name = created_employee["firstName"]

    dashboard.delete_employee(first_name)
    authenticated_page.reload()
    dashboard.wait_for_visible(dashboard.add_employee_button, "Add Employee button")
    dashboard.assert_employee_not_in_table(employee_id)

  @allure.title("Delete scoped to correct row — other rows unaffected")
  @pytest.mark.regression
  def test_delete_scoped_to_correct_row(self, authenticated_page, api) -> None:
    from helpers.api_client import ApiClient

    keep_payload = EmployeeFactory.valid()
    delete_payload = EmployeeFactory.valid()

    keep_id = api.create_employee_and_get_id(keep_payload)
    delete_id = api.create_employee_and_get_id(delete_payload)

    dashboard = DashboardPage(authenticated_page)
    dashboard.navigate()

    dashboard.delete_employee(delete_payload["firstName"])
    dashboard.assert_employee_not_in_table(delete_id)
    dashboard.assert_employee_in_table(keep_payload["firstName"])

    api.cleanup_employee(keep_id)

  @allure.title("Cancel delete — employee stays in table")
  @pytest.mark.regression
  def test_cancel_delete_keeps_employee(self, authenticated_page, created_employee) -> None:
    dashboard = DashboardPage(authenticated_page)
    dashboard.navigate()

    first_name = created_employee["firstName"]
    row = dashboard.get_employee_row(first_name)
    delete_icon = row.locator("i.fa-times")
    dashboard.click(delete_icon, f"Delete icon for {first_name}")
    dashboard.cancel_delete()
    dashboard.assert_employee_in_table(first_name)

  @allure.title("No console errors after delete")
  @pytest.mark.regression
  def test_no_console_errors_after_delete(self, authenticated_page, created_employee, console_errors) -> None:
    dashboard = DashboardPage(authenticated_page)
    dashboard.navigate()

    dashboard.delete_employee(created_employee["firstName"])
    assert console_errors == [], (f"Console errors after delete: {console_errors}")