# Paylocity Benefits Dashboard Test Automation Framework

End-to-end test automation suite for the Paylocity Benefits Dashboard, built with Playwright + pytest. Covers UI, API, and accessibility layers with parallel execution and Allure reporting.

---

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
│   └── settings.py          # Centralized config loaded from .env (frozen dataclass)
├── helpers/
│   └── calculations.py      # Benefits cost calculation logic (mirrors business rules)
├── tests/                   # Test files (auto-discovered by pytest)
├── reports/
│   ├── allure-results/      # Allure output (gitignored)
│   └── test.log             # Full DEBUG log per run (gitignored)
├── .env                     # Local secrets — never commit (gitignored)
├── pytest.ini               # Pytest config, markers, logging
└── requirements.txt         # Required dependencies
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

**Generate a static report:**

```bash
allure generate reports/allure-results -o allure-report --clean
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

## Environment & Secrets

- `.env` is **gitignored** — never commit it.
- All config is accessed through the `settings` singleton in `config/settings.py`.
- Missing required env vars raise an `EnvironmentError` at import time with a clear message.
