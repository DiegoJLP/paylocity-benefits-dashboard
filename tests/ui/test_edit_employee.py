"""
UI Edit Employee tests.

Uses created_employee fixture for API-driven setup.
"""

import allure
import pytest

from helpers.calculations import calculate_benefits
from helpers.data_factory import EmployeeFactory
from tests.ui.pages.dashboard_page import DashboardPage


@allure.epic("UI")
@allure.feature("Edit Employee")
@pytest.mark.ui
class TestEditEmployee:

  @allure.title("Edit employee — new values visible in table")
  @pytest.mark.smoke
  def test_edit_employee_updates_table(self, authenticated_page, created_employee) -> None:
    dashboard = DashboardPage(authenticated_page)
    dashboard.navigate()

    original_name = created_employee["firstName"]
    new_payload = EmployeeFactory.valid()

    dashboard.edit_employee(identifier=original_name, new_first_name=new_payload["firstName"])
    dashboard.assert_employee_in_table(new_payload["firstName"])
    dashboard.assert_employee_not_in_table(original_name)

  @allure.title("Edit dependants — benefit cost recalculates")
  @pytest.mark.smoke
  def test_edit_recalculates_benefits(self, authenticated_page, created_employee) -> None:
    dashboard = DashboardPage(authenticated_page)
    dashboard.navigate()

    first_name = created_employee["firstName"]
    dashboard.edit_employee(identifier=first_name, new_dependants=2)
    calcs = dashboard.get_employee_calculations(first_name)
    expected = calculate_benefits(dependants=2)

    assert abs(calcs["benefits_cost"] - expected.benefits_cost) < 0.02
    assert abs(calcs["net"] - expected.net) < 0.02

  @allure.title("Edit cancel — original data unchanged")
  @pytest.mark.regression
  def test_edit_cancel_preserves_data(self, authenticated_page, created_employee) -> None:
    dashboard = DashboardPage(authenticated_page)
    dashboard.navigate()

    original_name = created_employee["firstName"]
    dashboard.open_edit_modal(original_name)
    dashboard.fill(dashboard.modal_first_name, "CancelledEdit", "First Name")
    dashboard.click(dashboard.modal_cancel_button, "Cancel button")
    dashboard.assert_employee_in_table(original_name)
    dashboard.assert_employee_not_in_table("CancelledEdit")

  @allure.title("No console errors after editing employee")
  @pytest.mark.regression
  def test_no_console_errors_after_edit(self, authenticated_page, created_employee, console_errors) -> None:
    dashboard = DashboardPage(authenticated_page)
    dashboard.navigate()

    dashboard.edit_employee(identifier=created_employee["firstName"], new_dependants=1)
    assert console_errors == [], (f"Console errors after edit: {console_errors}")