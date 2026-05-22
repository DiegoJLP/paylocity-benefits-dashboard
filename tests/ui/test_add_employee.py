"""
UI Add Employee tests.

Uses authenticated_page fixture — already logged in.
Uses created_employee for setup via API where needed.
"""

import allure
import pytest

from helpers.calculations import calculate_benefits
from helpers.data_factory import EmployeeFactory
from tests.ui.pages.dashboard_page import DashboardPage


@allure.epic("UI")
@allure.feature("Add Employee")
@pytest.mark.ui
class TestAddEmployee:

  @allure.title("Add employee — appears in table")
  @pytest.mark.smoke
  def test_add_employee_appears_in_table(self, authenticated_page) -> None:
    dashboard = DashboardPage(authenticated_page)
    dashboard.navigate()
    payload = EmployeeFactory.valid(dependants=0)

    dashboard.add_employee(payload["firstName"], payload["lastName"], dependants=0)
    dashboard.assert_employee_in_table(payload["firstName"])

    # Cleanup
    dashboard.delete_employee(payload["firstName"])

  @allure.title("Add employee — calculations correct (0 dependants)")
  @pytest.mark.smoke
  def test_add_employee_calculations(self, authenticated_page) -> None:
    dashboard = DashboardPage(authenticated_page)
    dashboard.navigate()
    payload = EmployeeFactory.valid(dependants=0)

    dashboard.add_employee(payload["firstName"],payload["lastName"],dependants=0)
    calcs = dashboard.get_employee_calculations(payload["firstName"])
    expected = calculate_benefits(dependants=0)

    assert abs(calcs["gross"] - expected.gross) < 0.02
    assert abs(calcs["benefits_cost"] - expected.benefits_cost) < 0.02
    assert abs(calcs["net"] - expected.net) < 0.02

    dashboard.delete_employee(payload["firstName"])

  @allure.title("Add employee — cancel does not save")
  @pytest.mark.regression
  def test_add_employee_cancel(self, authenticated_page) -> None:
    dashboard = DashboardPage(authenticated_page)
    dashboard.navigate()
    payload = EmployeeFactory.valid()

    dashboard.open_add_modal()
    dashboard.fill_add_form(payload["firstName"], payload["lastName"])
    dashboard.click(dashboard.modal_cancel_button, "Cancel button")
    # TODO: assert_employee_not_in_table uses has_text which matches anywhere in
    # the row. If another user in the shared environment has the same string in
    # any column (e.g. firstName="William" matches a row where lastName="Williams"),
    # the assertion fails as a false positive. Fix: use employee UUID as identifier.
    dashboard.assert_employee_not_in_table(payload["firstName"])

  @allure.title("No console errors after adding employee")
  @pytest.mark.regression
  def test_no_console_errors_after_add(self, authenticated_page, console_errors) -> None:
    dashboard = DashboardPage(authenticated_page)
    dashboard.navigate()
    payload = EmployeeFactory.valid(dependants=0)

    dashboard.add_employee(payload["firstName"], payload["lastName"], dependants=0)
    assert console_errors == [], (f"Console errors after add: {console_errors}")
    dashboard.delete_employee(payload["firstName"])