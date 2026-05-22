"""
Base class for all Page Object Model pages.
Individual page objects handle WHAT the page represents.

Responsibilities:
  - Navigation
  - Safe click and fill wrappers with auto-wait
  - Explicit wait strategies
  - Logging every action
  - Allure step wrapping
  - Screenshot helper
  - Console error collection (via conftest autouse fixture)
"""

import logging

import allure
from playwright.sync_api import Locator, Page, expect

from config.settings import settings

logger = logging.getLogger(__name__)


class BasePage:
  """
  Base class for all Page Object Model pages.

  Args:
    page: Playwright Page object injected from pytest fixture.
  """

  def __init__(self, page: Page) -> None:
    self.page = page
    self.page.set_default_timeout(settings.default_timeout)
    self.page.set_default_navigation_timeout(settings.navigation_timeout)

  def navigate(self, path: str = "") -> None:
    """
    Navigate to a path relative to BASE_URL.
    Args:
      path: URL path to navigate to. Leading slash optional.
    """
    url = f"{settings.base_url}/{path.lstrip('/')}"
    logger.info("Navigating to: %s", url)
    with allure.step(f"Navigate to {url}"):
      self.page.goto(url)

  def wait_for_url(self, pattern: str) -> None:
    """
    Args:
      pattern: Glob pattern e.g. '**/Benefits'
    """
    logger.debug("Waiting for URL pattern: %s", pattern)
    self.page.wait_for_url(pattern, timeout=settings.navigation_timeout)

  def click(self, locator: Locator, description: str = "") -> None:
    """
    Click a locator after Playwright auto-waits for it to be
    visible, enabled, and stable.
    Args:
      locator: Playwright Locator to click.
      description: Human-readable label for logging and Allure.
    """
    label = description or str(locator)
    logger.info("Clicking: %s", label)
    with allure.step(f"Click '{label}'"):
      locator.click()

  def fill(self, locator: Locator, value: str, description: str = "") -> None:
    """
    Clear an input field and fill it with a value.
    Uses clear() first to avoid appending to existing values.
    Args:
      locator: Playwright Locator for the input field.
      value: Text to enter.
      description: Human-readable label for logging and Allure.
    """
    label = description or str(locator)
    logger.info("Filling '%s' with: %s", label, value)
    with allure.step(f"Fill '{label}'"):
      locator.clear()
      locator.fill(value)

  def get_text(self, locator: Locator) -> str:
    """
    Return the inner text of a visible element.
    Args:
      locator: Playwright Locator to read text from.
    Returns:
      Stripped inner text string.
    """
    expect(locator).to_be_visible()
    return locator.inner_text().strip()

  def wait_for_visible(self, locator: Locator, description: str = "") -> None:
    """
    Explicitly wait for an element to become visible.
    Use for synchronization issues.
    Args:
      locator: Playwright Locator to wait for.
      description: Human-readable label for logging.
    """
    label = description or "element"
    logger.debug("Waiting for visible: %s", label)
    expect(locator).to_be_visible(timeout=settings.default_timeout)

  def wait_for_hidden(self, locator: Locator, description: str = "") -> None:
    """
    Wait for an element to disappear.
    Used after modal close, delete confirmation, etc.
    Args:
      locator: Playwright Locator to wait for hidden state.
      description: Human-readable label for logging.
    """
    label = description or "element"
    logger.debug("Waiting for hidden: %s", label)
    expect(locator).not_to_be_visible(timeout=settings.default_timeout)

  def wait_for_count(self, locator: Locator, count: int) -> None:
    """
    Wait until a locator matches exactly N elements.
    Useful for asserting a table row appeared or disappeared.
    Args:
      locator: Playwright Locator to count.
      count: Expected number of matching elements.
    """
    logger.debug("Waiting for count %d", count)
    expect(locator).to_have_count(count, timeout=settings.default_timeout)

  def wait_for_api_response(self, url_pattern: str):
    """
    Context manager that waits for a network response matching
    a URL pattern. Use to synchronize UI actions with API calls.
    Args:
      url_pattern: String pattern to match in the response URL.
    Returns:
      Playwright expect_response context manager.
    """
    return self.page.expect_response(lambda r: url_pattern in r.url, timeout=settings.default_timeout)

  def assert_visible(self, locator: Locator, description: str = "") -> None:
    """
    Assert an element is visible. Adds an Allure step.
    Args:
      locator: Playwright Locator to assert.
      description: Human-readable label for the Allure step.
    """
    label = description or str(locator)
    with allure.step(f"Assert visible: {label}"):
      expect(locator).to_be_visible()

  def assert_url_contains(self, fragment: str) -> None:
    """
    Assert the current URL contains a substring.
    Args:
      fragment: URL fragment to look for.
    """
    with allure.step(f"Assert URL contains '{fragment}'"):
      expect(self.page).to_have_url(f"**{fragment}**")

  def take_screenshot(self, name: str) -> None:
    """
    Manually capture a screenshot and attach to Allure report.
    Use at key steps in complex flows.

    Args:
      name: Label for the screenshot in the Allure report.
    """
    logger.info("Taking screenshot: %s", name)
    screenshot = self.page.screenshot(full_page=True)
    allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)