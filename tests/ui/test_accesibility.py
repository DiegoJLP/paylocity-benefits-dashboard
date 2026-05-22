"""
Accessibility tests using axe-core via axe-playwright-python.

WCAG 2.1 AA compliance checks on key pages.
Tests run on the page as-is — any violations are reported
with impact level, description, and affected elements.
"""

import allure
import pytest
from axe_playwright_python.sync_playwright import Axe

from config.settings import settings
from tests.ui.pages.login_page import LoginPage
from tests.ui.pages.dashboard_page import DashboardPage


@allure.epic("UI")
@allure.feature("Accessibility")
@pytest.mark.ui
@pytest.mark.a11y
class TestAccessibility:

  @allure.title("Login page — no critical a11y violations")
  def test_login_page_accessibility(self, page) -> None:
    login = LoginPage(page)
    login.navigate()

    axe = Axe()
    results = axe.run(page)
    violations = results.response["violations"]

    critical = [
      v for v in violations
      if v.get("impact") in ("critical", "serious")
    ]
    violation_summary = "\n".join([
      f"[{v['impact']}] {v['id']}: {v['description']}"
      for v in critical
    ])
    allure.attach(violation_summary or "No critical violations", name="A11y Violations — Login",attachment_type=allure.attachment_type.TEXT)
    assert not critical, (f"Critical a11y violations on Login:\n{violation_summary}")

  @allure.title("Favicon loads without 403 on dashboard page (BUG-UI-010)")
  @pytest.mark.xfail(reason="BUG-UI-010: favicon.ico not deployed, always returns 403", strict=False)
  def test_favicon_no_error(self, authenticated_page) -> None:
    favicon_errors = []
    authenticated_page.on("response", lambda r: favicon_errors.append(r.url) if "favicon" in r.url.lower() and r.status == 403 else None)
    dashboard = DashboardPage(authenticated_page)
    dashboard.navigate()
    assert not favicon_errors, f"Favicon returned 403: {favicon_errors}"

  @allure.title("Dashboard page — no critical a11y violations")
  def test_dashboard_accessibility(self, authenticated_page) -> None:
    dashboard = DashboardPage(authenticated_page)
    dashboard.navigate()

    axe = Axe()
    results = axe.run(authenticated_page)
    violations = results.response["violations"]

    critical = [
      v for v in violations
      if v.get("impact") in ("critical", "serious")
    ]
    violation_summary = "\n".join([
      f"[{v['impact']}] {v['id']}: {v['description']}"
      for v in critical
    ])
    allure.attach(violation_summary or "No critical violations", name="A11y Violations — Dashboard", attachment_type=allure.attachment_type.TEXT)
    assert not critical, (f"Critical a11y violations on Dashboard:\n{violation_summary}")