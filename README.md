# Paylocity Benefits Dashboard Test Automation Framework

End-to-end test automation suite for the Paylocity Benefits Dashboard, built with Playwright + pytest. Covers UI, API, and accessibility layers with parallel execution and Allure reporting.

---
## Last run results:
<img width="1431" height="848" alt="Captura de Pantalla 2026-05-22 a la(s) 13 19 26" src="https://github.com/user-attachments/assets/fd7e3500-80bc-4ebe-8877-acc229c22457" />


## Test Documentation

All manual test execution artifacts are in `docs/`:

| File                                     | Description                                               |
| ---------------------------------------- | --------------------------------------------------------- |
| `docs/test-execution/UI_TestCases.xlsx`  | 66 UI test cases across Login, Add, Edit, Delete Employee |
| `docs/test-execution/API_TestCases.xlsx` | 61 API test cases across all endpoints                    |
| `docs/bug-reports/BUG_REPORT_UI.docx`    | 11 UI bugs found during manual execution                  |
| `docs/bug-reports/BUG_REPORT_API.docx`   | 14 API bugs found during manual execution                 |
| `docs/bug-reports/OBSERVATIONS.docx`     | 10 UI behavioral observations                             |
| `docs/bug-reports/API_OBSERVATIONS.docx` | 7 API behavioral observations                             |

## Selector Strategy

Priority order used throughout the Page Object layer:

| Priority | Strategy            | Example                                             |
| -------- | ------------------- | --------------------------------------------------- |
| 1        | Stable id attribute | `page.locator("#add")`                              |
| 2        | Type + class CSS    | `page.locator("button[type='submit'].btn-primary")` |
| 3        | has_text filter     | `table_rows.filter(has_text=identifier)`            |
| 4        | Scoped icon class   | `row.locator("i.fa-edit")`                          |

## Synchronization Strategy

No `time.sleep()` anywhere in the suite.

| Scenario                | Strategy                                   |
| ----------------------- | ------------------------------------------ |
| Wait for modal to open  | `expect(locator).to_be_visible()`          |
| Wait for modal to close | `expect(locator).not_to_be_visible()`      |
| Wait for table reload   | `page.expect_response("**/api/employees")` |
| Wait after navigation   | `page.wait_for_url("**/Benefits")`         |

## Manual Inspection Artifacts

During manual execution, DevTools inspection was performed on all key
pages. The findings are documented in `docs/`:

| File                 | Description                                                                                                                                                                      |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs/selectors.txt` | Confirmed HTML selectors for all interactive elements — Login, Dashboard, Add/Edit/Delete modals, employee table                                                                 |
| `docs/Benefits.txt`  | Full page source and `employeeClient.js` source captured during execution — used to identify root causes for BUG-UI-002 (column swap) and BUG-UI-004 (missing `.fail()` handler) |

These artifacts were used to write accurate Page Object selectors
and to provide root cause evidence in the bug reports.

## Tech Stack

| Tool                  | Version | Purpose                         |
| --------------------- | ------- | ------------------------------- |
| Python                | 3.11+   | Runtime                         |
| pytest                | 8.3.4   | Test runner                     |
| Playwright            | 1.49.0  | Browser automation              |
| pytest-playwright     | 0.6.2   | Playwright-pytest integration   |
| pytest-xdist          | 3.6.1   | Parallel test execution         |
| allure-pytest         | 2.13.5  | Test reporting                  |
| axe-playwright-python | 0.1.3   | WCAG 2.1 accessibility checks   |
| Faker                 | 33.1.0  | Test data generation            |
| python-dotenv         | 1.0.1   | Environment variable management |

---

## Project Structure

```
paylocity-benefits-dashboard/
├── config/
│   └── settings.py                  # Centralized config loaded from .env (frozen dataclass)
│
├── docs/                            # Manual testing artifacts (not part of automation)
│   ├── BUG_REPORT_API.pdf
│   ├── BUG_REPORT_UI.pdf
│   ├── API_OBSERVATIONS.pdf
│   ├── UI_OBSERVATIONS.pdf
│   ├── Benefits.txt                 # Business rules reference + employeeClient.js source
│   ├── selectors.txt                # Confirmed HTML selectors from DevTools inspection
│   └── test-executions/
│       ├── API_TestCases.xlsx       # 61 API test cases
│       └── UI_TestCases.xlsx        # 66 UI test cases
│
├── helpers/
│   ├── api_client.py                # Playwright APIRequestContext wrapper (all endpoints)
│   ├── calculations.py              # Benefits cost logic (mirrors business rules)
│   ├── data_factory.py              # Faker-based test data builders (EmployeeFactory)
│   └── schema_validator.py          # JSON schema assertions for API responses
│
├── tests/
│   ├── conftest.py                  # Root fixtures: api client, created_employee, session cleanup
│   │
│   ├── api/                         # API layer tests (no browser)
│   │   ├── test_auth.py             # Auth boundary — missing/invalid token
│   │   ├── test_employees_create.py # POST /api/Employees — happy path + negative
│   │   ├── test_employees_read.py   # GET /api/Employees and GET /{id}
│   │   ├── test_employees_update.py # PUT /api/Employees
│   │   └── test_employees_delete.py # DELETE /api/Employees/{id}
│   │
│   ├── ui/
│   │   ├── conftest.py              # UI fixtures: timeouts, screenshots, traces, console errors
│   │   ├── pages/                   # Page Object Model
│   │   │   ├── base_page.py         # Shared navigation, click, fill, wait, assert helpers
│   │   │   ├── login_page.py        # /Account/Login page
│   │   │   └── dashboard_page.py    # /Benefits — table, modals, CRUD actions
│   │   ├── test_login.py            # Login flows and validations
│   │   ├── test_add_employee.py     # Add employee modal — happy path + cancel
│   │   ├── test_edit_employee.py    # Edit employee modal — field updates + recalculation
│   │   ├── test_delete_employee.py  # Delete flow — confirmation, persistence, cancel
│   │   └── test_accesibility.py     # WCAG 2.1 AA checks via axe-core
│   │
│   └── unit/
│       └── test_calculations.py     # Pure unit tests for helpers/calculations.py
│
├── reports/                         # Generated on every run (gitignored)
│   ├── allure-results/              # Raw Allure JSON written by pytest
│   ├── allure-report/               # Generated HTML report (allure generate)
│   ├── traces/                      # Playwright trace .zip files (UI failures only)
│   └── test.log                     # Full DEBUG log
│
├── .env                             # Local secrets — never commit (gitignored)
├── .gitignore
├── pytest.ini                       # Pytest config: markers, addopts, logging
└── requirements.txt                 # Python dependencies
```

---

## Setup

**1. Create and activate a virtual environment:**

**macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (Command Prompt):**

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

> **Windows PowerShell note:** if you get an error about script execution being disabled, run this first:
>
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

Once activated, your terminal prompt will show `(.venv)` confirming the environment is active.

**2. Install dependencies:**

```bash
pip install -r requirements.txt
```

**3. Install browser binaries** (only needed on first setup or after Playwright version updates):

```bash
playwright install chromium      # or playwright install  (any browser)
```

**4. Configure environment variables** — create a `.env` file at the project root:

```dotenv
BASE_URL=https://...
API_BASE_URL=https://...
AUTH_TOKEN=your_token

UI_USERNAME=your_username
UI_PASSWORD=your_password

HEADLESS=false
BROWSER=chromium
DEFAULT_TIMEOUT=30000
NAVIGATION_TIMEOUT=60000
```

---

## Running Tests

**Full suite:**

```bash
pytest
```

**By marker:**

```bash
pytest -m smoke           # core happy-path only
pytest -m regression      # full regression suite
pytest -m api             # API tests, no browser
pytest -m ui              # UI tests
pytest -m a11y            # accessibility tests
pytest -m negative        # edge cases and negative paths
```

**In parallel:**

```bash
pytest -n auto            # uses all available CPU cores
pytest -n 4               # fixed worker count
```

**Single file or test:**

```bash
pytest tests/test_benefits.py
pytest tests/test_benefits.py::TestBenefits::test_employee_no_dependants
```

---

## Reporting

Allure results are written to `reports/allure-results/` automatically on every run (`--alluredir` and `--clean-alluredir` are set in `pytest.ini`).

**Serve the report locally:**

```bash
allure serve reports/allure-results
```

I had to use npx due to an error installing allure in my environment

```bash
npx allure serve reports/allure-results
```

**Generate a static report:**

```bash
allure generate reports/allure-results -o allure-report --clean
```

or

```bash
npx allure generate reports/allure-results -o allure-report --clean
```

A full DEBUG log is also written to `reports/test.log` on every run.

---

## Business Rules

Defined in `config/settings.py` and used by `helpers/calculations.py`:

| Rule                         | Value     |
| ---------------------------- | --------- |
| Salary per paycheck          | $2,000.00 |
| Paychecks per year           | 26        |
| Employee benefits cost/year  | $1,000.00 |
| Dependent benefits cost/year | $500.00   |

**Net paycheck formula:**

```
annual_cost = employee_cost + (dependants × dependent_cost)
benefits_per_paycheck = annual_cost / 26
net = gross - benefits_per_paycheck
```

Valid dependant range: 0–32. Values outside this range raise a `ValueError`.

---

## Test Markers

Defined in `pytest.ini`. Always tag your tests with at least one marker:

| Marker       | When to use                                 |
| ------------ | ------------------------------------------- |
| `smoke`      | Core happy-path, must pass on every commit  |
| `regression` | Full suite, typically run on PRs or nightly |
| `api`        | API-only tests (no browser needed)          |
| `ui`         | Tests that need browser                     |
| `auth`       | Authentication flows                        |
| `negative`   | Edge cases, invalid inputs, error handling  |
| `a11y`       | WCAG 2.1 accessibility checks via axe       |

---

## Known Limitations & TODOs

| #   | Area         | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| --- | ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | UI tests     | `has_text` row matching is fragile in a shared environment. If `identifier="William"` is used, it also matches rows where another user has "Williams" in any column. Fix: always pass the employee UUID as identifier rather than firstName. Tracked in `test_add_employee_cancel`.                                                                                                                                                                                                                                                                        |
| 2   | All UI tests | **BUG-UI-008 causes intermittent failures.** Session expiry after idle or page reload drops the `Authorization` header from the app's JavaScript API calls, causing the employee table to load empty. Tests that create an employee via API and then look for it in the dashboard are affected. Although this was initially triaged as P3-Low during manual inspection, running the full suite reveals it causes intermittent failures across multiple UI tests. **Recommend prioritising this fix before relying on UI test results as a stable signal.** |
| 3   | Data cleanup | BUG-API-008 means `DELETE` does not actually remove records server-side. The session-end `cleanup_all_employees` fixture attempts deletion of all employees after every run, but ghost records may persist. Schema and list-validation tests are insulated from this via targeted GET-by-ID assertions.                                                                                                                                                                                                                                                    |

---

## Bugs Discovered by This Suite

The following bugs were found by running this test suite against the live environment. None were known before testing.

| ID          | Layer | Severity | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ----------- | ----- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| BUG-API-004 | API   | High     | Invalid `Authorization` token crashes the server with `500 Internal Server Error` instead of returning `401 Unauthorized`. The token validation middleware does not guard against malformed input before it hits processing logic.                                                                                                                                                                                                             |
| BUG-API-008 | API   | Critical | **DELETE does not remove records.** `DELETE /api/Employees/{id}` returns `200 OK` but the record is never removed from the data store. A subsequent `GET` on the same ID still returns `200` with the full employee body. A `PUT` on a deleted employee also succeeds and causes the employee to **reappear in the UI**. Ghost records with `salary=0` / `gross=0` accumulate in the database and corrupt the results of `GET /api/Employees`. |
| BUG-UI-008  | UI    | High     | Session expires after short idle or repeated page refresh. Authenticated pages return `401` on the JavaScript API calls that populate the employee table, causing the table to load empty. Tests that create an employee via API and then look for it in the UI are affected.                                                                                                                                                                  |
| BUG-UI-010  | UI    | Low      | `favicon.ico` is not deployed — every page load triggers a `403` browser console error for the missing asset.                                                                                                                                                                                                                                                                                                                                  |

---

## Environment & Secrets

- `.env` is **gitignored** — never commit it.
- All config is accessed through the `settings` singleton in `config/settings.py`.
- Missing required env vars raise an `EnvironmentError` at import time with a clear message.
