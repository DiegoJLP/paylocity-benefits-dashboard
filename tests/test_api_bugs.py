import requests
from utils.environment import environment

base_url = environment["prod"]["base_url"]
employees_endpoint = environment["prod"]["endpoints"]["employees"]
auth_code = environment["prod"]["auth_code"]
headers = {
	"Authorization": auth_code,
	"Content-Type": "application/json"
}

employee_id = None

def test_get_employees():
	url = base_url + employees_endpoint
	response = requests.get(url, headers=headers)
	assert response.status_code == 200, f"GET failed: {response.text}"

#Overwritten username bug
def test_post_employee():
	url = base_url + employees_endpoint
	payload = {
		"firstName": "Test",
		"lastName": "User",
		"dependents": 1,
		"username": "Somerandomusername"
	}
	response = requests.post(url, json=payload, headers=headers)
	assert response.status_code in [200, 201], f"POST failed: {response.text}"
	employee = response.json()
	print(f"Created employee: {employee}")
	global employee_id
	employee_id = employee.get("id")
	assert employee_id, "No employee ID returned in POST response"
	assert employee.get("username") == "Somerandomusername", f"Username overwritten: expected 'Somerandomusername', got '{employee.get('username')}'"

#ReadOnly properties bug
def test_put_employee():
	global employee_id
	url = base_url + employees_endpoint
	payload = {
		"id": employee_id,
		"firstName": "Updated",
		"lastName": "User",
		"partitionKey": "ShouldNotChange",
		"sortKey": "ShouldNotChangeToo",
		"gross": 2000,
		"benefitsCost": 2000,
		"net": 48000,
		"dependents": 2
	}
	response = requests.put(url, json=payload, headers=headers)
	print(f"Updated employee response: {response.json()}")
	assert response.status_code in [400, 405], f"Expected 400 or 405 for sending read-only properties: {response.text}"

def test_delete_employee():
	global employee_id
	url = base_url + employees_endpoint + f"/{employee_id}"
	response = requests.delete(url, headers=headers)
	assert response.status_code in [200, 204], f"DELETE failed: {response.text}"
	print(f"Deleted employee ID: {employee_id}")

#Deleting non-existent employee bug
def test_delete_non_existent_employee():
	global employee_id
	url = base_url + employees_endpoint + f"/{employee_id}"
	response = requests.delete(url, headers=headers)
	print(f"Deleted user: {employee_id}")
	assert response.status_code in [404], f"Expected 404 when deleting non-existent employee, got {response.status_code}"

#Get non-existent employee bug
def test_get_deleted_employee():
	global employee_id
	print(f"Getting deleted user: {employee_id}")
	url = base_url + employees_endpoint + f"/{employee_id}"
	response = requests.get(url, headers=headers)
	assert response.status_code == 404, f"Expected 404 for deleted employee, got {response.status_code}"

#Username not required bug
def test_post_without_username():
    url = base_url + employees_endpoint
    payload = {
        "firstName": "JOHN",
        "lastName": "123",
        "dependents": 0
    }
    response = requests.post(url, json=payload, headers=headers)
    employee = response.json()
    print(f"Created employee: {employee}")
    global employee_id
    employee_id = employee.get("id")
    print(f"New employee created without username: {employee_id}")
    print(f"POST without username response: {response.json()}")
    assert response.status_code == 400, f"Expected 400 for invalid data, got {response.status_code}"

#Salary should not be updated to invalid values bug
def test_put_employee_invalid_salary():
    global employee_id
    print(f"Updating employee with invalid salary: {employee_id}")
    url = base_url + employees_endpoint
    payload = {
        "id": employee_id,
        "firstName": "Updated",
        "lastName": "User",
		"salary": -5000,
        "dependents": 32
    }
    response = requests.put(url, json=payload, headers=headers)
    print(f"PUT with invalid salary response: {response.json()}")
    assert response.status_code in [400], f"Expected 400 for invalid salary values, got {response.status_code}"