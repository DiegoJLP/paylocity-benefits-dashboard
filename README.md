# paylocity-benefits-dashboard
This repository contains all my efforts to complete the Bug Finding and Automation challenge.

## Setup Python Virtual Environment (.venv)

1. Open a terminal in the project root directory.
2. Run the following command to create a virtual environment:
	```powershell
	python -m venv .venv
	```
3. Activate the virtual environment:
	```powershell
	.venv\Scripts\Activate
	```
4. Install dependencies:
	```powershell
	pip install -r requirements.txt
	```

## Running Only UI Tests

To run only the UI tests (located in the `tests` folder, e.g., `test_ui_bugs.py`):

```powershell
pytest tests/test_ui_bugs.py
```

You can replace `test_ui_bugs.py` with any other test file to run only those tests.
