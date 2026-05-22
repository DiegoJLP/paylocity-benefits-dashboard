"""
Page Object for the Benefits Dashboard page.

Selector strategy:
  - id stable attributes for all modal buttons
  - table id stable for the employee table
  - has_text filter for row selection — avoid flakiness to row reordering
  - fa-edit / fa-times class for action icons — only option available

Selectors confirmed from manual inspection:
  Add button:      <button id="add">
  Log Out:         <a href="/Prod/Account/LogOut">Log Out</a>
  Table:           <table id="employeesTable">
  Modal:           <div id="employeeModal">
  firstName:       <input id="firstName">
  lastName:        <input id="lastName">
  dependants:      <input id="dependants">
  Add confirm:     <button id="addEmployee">
  Update confirm:  <button id="updateEmployee">
  Cancel:          <button class="btn btn-secondary" data-dismiss="modal">
  Edit icon:       <i class="fas fa-edit">
  Delete icon:     <i class="fas fa-times">
  Delete modal:    <div id="deleteModal">
  Delete confirm:  <button id="deleteEmployee">

Table column indexes (data insertion order from employeeClient.js):
  0: id
  1: firstName value  -> displayed under "Last Name" header (BUG-UI-002)
  2: lastName value   -> displayed under "First Name" header (BUG-UI-002)
  3: dependants
  4: salary
  5: gross
  6: benefitsCost
  7: net
  8: actions

Note on BUG-UI-002:
  Row selection uses has_text which matches anywhere in the row.
  Rows are located by an identifier (firstName value or UUID) — not by
  column header. This means selectors work correctly despite the column swap bug.

Synchronization:
  After Add/Edit/Delete the app fires:
    1. POST/PUT/DELETE -> 200
    2. GET /api/employees -> 200 (table reload)
"""

import logging

import allure
from playwright.sync_api import Locator, Page, expect

from tests.ui.pages.base_page import BasePage

logger = logging.getLogger(__name__)


class DashboardPage(BasePage):
  """ All interactions on the Benefits Dashboard page."""

  PATH = "Benefits"

  def __init__(self, page: Page) -> None:
    super().__init__(page)

    self.add_employee_button = page.locator("#add")
    self.logout_link = page.locator("a[href*='LogOut']")

    self.employee_table = page.locator("#employeesTable")
    self.table_body = self.employee_table.locator("tbody")
    self.table_rows = self.table_body.locator("tr")
    self.empty_state = self.table_body.locator("td[colspan='9']")

    # One modal handles both Add and Edit - #employeeModal
    self.modal = page.locator("#employeeModal")
    self.modal_first_name = self.modal.locator("#firstName")
    self.modal_last_name = self.modal.locator("#lastName")
    self.modal_dependants = self.modal.locator("#dependants")
    # Add and Update buttons are toggled by JS — both always in DOM
    self.modal_add_button = self.modal.locator("#addEmployee")
    self.modal_update_button = self.modal.locator("#updateEmployee")
    self.modal_cancel_button = self.modal.locator("button.btn-secondary[data-dismiss='modal']").first

    # Delete confirmation modal
    self.delete_modal = page.locator("#deleteModal")
    self.delete_confirm_button = self.delete_modal.locator("#deleteEmployee")
    self.delete_cancel_button = self.delete_modal.locator("button.btn-secondary[data-dismiss='modal']")

  def navigate(self) -> None:
    """Go to the Benefits Dashboard and wait for the Add Employee button to be visible."""
    super().navigate(self.PATH)
    self.wait_for_visible(self.add_employee_button, "Add Employee button")

  def get_employee_row(self, identifier: str) -> Locator:
    """
    Return the <tr> that contains the given identifier.
    Accepts either a firstName value or a UUID (column 0) — has_text
    matches anywhere in the row so both work identically.

    Args:
      identifier: firstName value or employee UUID.

    Returns:
      Playwright Locator scoped to the matching row.
    """
    return self.table_rows.filter(has_text=identifier)

  def get_employee_id(self, identifier: str) -> str:
    """
    Read the UUID from column 0 of an employee row.

    Args:
      identifier: firstName value or employee UUID to locate the row.

    Returns:
      Employee UUID as a string.
    """
    return self.get_text(self.get_employee_cell(identifier, 0))

  def get_employee_cell(self, identifier: str, col_index: int) -> Locator:
    """
    Return a specific <td> from an employee row by column index.

    Column indexes match data insertion order (not header order):
      0=id, 1=firstName, 2=lastName, 3=dependants,
      4=salary, 5=gross, 6=benefitsCost, 7=net, 8=actions

    Args:
      identifier: firstName value or employee UUID to locate the row.
      col_index: Zero-based column index.

    Returns:
      Playwright Locator for the specific cell.
    """
    return self.get_employee_row(identifier).locator("td").nth(col_index)

  @allure.step("Open Add Employee modal")
  def open_add_modal(self) -> None:
    """Click Add Employee and wait for the modal to appear."""
    self.click(self.add_employee_button, "Add Employee button")
    self.wait_for_visible(self.modal_first_name, "firstName in modal")

  @allure.step("Fill Add Employee form")
  def fill_add_form(self, first_name: str, last_name: str, dependants: int = 0) -> None:
    """
    Fill all fields in the Add Employee modal.

    Args:
      first_name: Employee first name
      last_name: Employee last name
      dependants: Number of dependants. Defaults to 0.
    """
    self.fill(self.modal_first_name, first_name, "First Name")
    self.fill(self.modal_last_name, last_name, "Last Name")
    self.fill(self.modal_dependants, str(dependants), "Dependants")

  @allure.step("Save new employee")
  def save_add_form(self) -> None:
    """
    Click Add button and wait for table to reload.

    Synchronization: waits for GET /api/employees after POST completes.
    """
    with self.wait_for_api_response("/api/employees"):
      self.click(self.modal_add_button, "Add button")
    self.wait_for_hidden(self.modal, "Add Employee modal")

  def add_employee(self, first_name: str, last_name: str, dependants: int = 0) -> None:
    """
    Full Add Employee flow: open modal -> fill -> save

    Args:
      first_name: Employee first name
      last_name: Employee last name
      dependants: Number of dependants. Defaults to 0
    """
    self.open_add_modal()
    self.fill_add_form(first_name, last_name, dependants)
    self.save_add_form()

  @allure.step("Open Edit modal for employee")
  def open_edit_modal(self, identifier: str) -> None:
    """
    Click the Edit icon on a specific employee row and wait
    for the modal to open with pre-populated values.

    Args:
      identifier: firstName value or employee UUID to locate the row.
    """
    row = self.get_employee_row(identifier)

    # Scope Edit icon to the row — prevents acting on wrong row
    edit_icon = row.locator("i.fa-edit")
    self.click(edit_icon, f"Edit icon for {identifier}")
    self.wait_for_visible(self.modal_first_name, "firstName in Edit modal")

  @allure.step("Save edited employee")
  def save_edit_form(self) -> None:
    """
    Click Update button and wait for table to reload.

    Synchronization: waits for GET /api/employees after PUT completes.
    """
    with self.wait_for_api_response("/api/employees"):
      self.click(self.modal_update_button, "Update button")
    self.wait_for_hidden(self.modal, "Edit Employee modal")

  def edit_employee(self, identifier: str, new_first_name: str = "", new_last_name: str = "", new_dependants: int = None) -> None:
    """
    Full Edit Employee flow: open modal -> update fields -> save
    Only updates fields that are explicitly provided.

    Args:
      identifier: firstName value or employee UUID to locate the row to edit.
      new_first_name: New first name. Skipped if empty string
      new_last_name: New last name. Skipped if empty string
      new_dependants: New dependants count. Skipped if None
    """
    self.open_edit_modal(identifier)
    if new_first_name:
      self.fill(self.modal_first_name, new_first_name, "First Name")
    if new_last_name:
      self.fill(self.modal_last_name, new_last_name, "Last Name")
    if new_dependants is not None:
      self.fill(self.modal_dependants, str(new_dependants), "Dependants")
    self.save_edit_form()

  @allure.step("Delete employee")
  def delete_employee(self, identifier: str) -> None:
    """
    Click the Delete icon, confirm the dialog, and wait for
    the row to disappear from the table.
    Captures the UUID before deletion and asserts by ID after — more robust
    than asserting by name since names can repeat.
    Synchronization: waits for GET /api/employees after DELETE completes.

    Args:
      identifier: firstName value or employee UUID to locate the row to delete.
    """
    employee_id = self.get_employee_id(identifier)
    row = self.get_employee_row(identifier)
    # Scope Delete icon to the row — prevents acting on wrong row
    delete_icon = row.locator("i.fa-times")
    self.click(delete_icon, f"Delete icon for {identifier}")
    # Wait for confirmation modal
    self.wait_for_visible(self.delete_confirm_button, "Delete confirm button")
    with self.wait_for_api_response("/api/employees"):
      self.click(self.delete_confirm_button, "Confirm delete")
    # Assert by UUID — name collisions cannot cause a false pass
    expect(self.get_employee_row(employee_id)).to_have_count(0)

  def cancel_delete(self) -> None:
    """
    Cancel the delete confirmation dialog.
    Used to verify Cancel keeps the employee in the table.
    """
    self.wait_for_visible(
      self.delete_cancel_button, "Delete cancel button"
    )
    self.click(self.delete_cancel_button, "Cancel delete")
    self.wait_for_hidden(self.delete_modal, "Delete modal")

  @allure.step("Assert employee visible in table")
  def assert_employee_in_table(self, identifier: str) -> None:
    """
    Assert an employee row is visible in the table.

    Args:
      identifier: firstName value or employee UUID to search for
    """
    expect(self.get_employee_row(identifier)).to_be_visible()

  @allure.step("Assert employee NOT in table")
  def assert_employee_not_in_table(self, identifier: str) -> None:
    """
    Assert an employee row does not exist in the table.

    Args:
      identifier: firstName value or employee UUID to search for.
    """
    expect(self.get_employee_row(identifier)).to_have_count(0)

  @allure.step("Get benefit calculations for employee")
  def get_employee_calculations(self, identifier: str) -> dict:
    """
    Read benefit calculation values from an employee table row.

    Returns values from the actual data columns regardless of
    column header labels (accounts for BUG-UI-002).

    Args:
      identifier: firstName value or employee UUID to identify the row.

    Returns:
      dict with keys: gross, benefits_cost, net (all floats).
    """
    def parse(text: str) -> float:
      return float(text.replace("$", "").replace(",", "").strip())

    gross = self.get_text(self.get_employee_cell(identifier, 5))
    benefits_cost = self.get_text(self.get_employee_cell(identifier, 6))
    net = self.get_text(self.get_employee_cell(identifier, 7))

    return {
      "gross": parse(gross),
      "benefits_cost": parse(benefits_cost),
      "net": parse(net),
    }

  def assert_empty_state(self) -> None:
    """Assert the table shows the empty-state row (single td spanning all 9 columns)."""
    self.assert_visible(self.empty_state, "Empty state row")
