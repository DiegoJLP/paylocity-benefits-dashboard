# paylocity-benefits-dashboard
Hello, thank you for taking the time to review this project. 
This repository contains all my efforts to complete the Bug Finding and Automation challenge.
If you have any issues whatsoever while conducting the review process feel free to reach out via email:
	diego.jlp262@gmail.com
or whatsapp:
	+52 3339571431
Please note that the UI tests might not run in MacOS or Linux due to errors with the ChromeDriver Manager version I used (at least I encountered issues). Ideally these tests should be conducted in a windows environment.

## Process
I first created the test executions for the UI tests and the API tests

Test Executions
https://docs.google.com/spreadsheets/d/18qd4DwZDnH2sXnWMUttag625pqUYF9pfDG75EG9_8Rc/edit?usp=sharing
https://docs.google.com/spreadsheets/d/16MkKa1V_on5IRxtV_uIwq0CqNYTQXOv2wA07yH9BdFU/edit?usp=sharing

## Reports
Then I created the reports that you'll be able to read here:
UI Bug Report
https://docs.google.com/document/d/1xQLCRCU3WGqGPsSs2fu-brgJWKPMaRxW7ij6phHsB44/edit?usp=sharing
API Bug Report
https://docs.google.com/document/d/13AL3b-VRdch44D87DyvjRGMPVYrGtgqhY0L8v9oY_ak/edit?usp=sharing

## Setup Python Virtual Environment (.venv)
Please note that these set of instructions are directed for Windows OS.
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

