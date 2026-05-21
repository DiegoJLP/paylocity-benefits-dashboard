"""
Generates Employee request payloads for test cases

Using Faker to enforce the use of unique data, 
no two tests will ever create an employee with the same name or username
This to avoid data collisions in parallel runs.
"""

import uuid

from faker import Faker

fake = Faker()


class EmployeeFactory:

  @staticmethod
  def valid(dependants: int = 0) -> dict:
    """
    Minimal valid payload, only required fields plus dependants.
    Args:
      dependants: Number of dependants (0-32). Defaults to 0.

    Returns:
      dict with firstName, lastName, username, dependants.
    """
    return {
      "firstName": fake.first_name(),
      "lastName": fake.last_name(),
      "username": fake.user_name()[:50],
      "dependants": dependants,
    }

  @staticmethod
  def with_overrides(**overrides) -> dict:
    # Override specific field from a valid payload
    payload = EmployeeFactory.valid()
    payload.update(overrides)
    return payload

  @staticmethod
  def missing_field(field: str) -> dict:
    """
    Valid payload with one required field removed.

    Args:
      field: Field name to remove. One of: firstName, lastName, username.
    """
    payload = EmployeeFactory.valid()
    payload.pop(field, None)
    return payload

  @staticmethod
  def empty_body() -> dict:
    # Empty payload
    return {}


  @staticmethod
  def empty_field(field: str) -> dict:
    """
    Valid payload with one field set to empty string.
    Different from missing_field — the key is present but blank.

    Args:
      field: Field name to empty. One of: firstName, lastName, username.
    """
    return EmployeeFactory.with_overrides(**{field: ""})

  @staticmethod
  def whitespace_field(field: str) -> dict:
    """
    Valid payload with one field set to whitespace only.
    Tests whether the API trims and validates whitespace-only strings.

    Args:
      field: Field name to set to whitespace.
    """
    return EmployeeFactory.with_overrides(**{field: "     "})

  @staticmethod
  def null_field(field: str) -> dict:
    """
    Valid payload with one field explicitly set to null (None).

    Args:
      field: Field name to null.
    """
    return EmployeeFactory.with_overrides(**{field: None})


  @staticmethod
  def field_at_max_length(field: str, max_length: int = 50) -> dict:
    """
    Valid payload with one field set to exactly max_length characters.

    Args:
      field: Field name to set to max length.
      max_length: The maximum allowed length from swagger specs
    """
    return EmployeeFactory.with_overrides(**{field: "A" * max_length})

  @staticmethod
  def field_over_max_length(field: str, max_length: int = 50) -> dict:
    """
    Invalid payload with one field set to max_length + 1 characters.

    Args:
      field: Field name to exceed.
      max_length: The maximum allowed length from swagger specs
    """
    return EmployeeFactory.with_overrides(**{field: "A" * (max_length + 1)})

  @staticmethod
  def max_dependants() -> dict:
    # Valid payload at maximum dependants 32
    return EmployeeFactory.valid(dependants=32)

  @staticmethod
  def over_max_dependants() -> dict:
    # Invalid payload — dependants exceeds maximum 
    return EmployeeFactory.with_overrides(dependants=33)

  @staticmethod
  def negative_dependants() -> dict:
    # Invalid payload — dependants below minimum -1 < 0
    return EmployeeFactory.with_overrides(dependants=-1)

  @staticmethod
  def string_dependants() -> dict:
    # Invalid payload — dependants as string instead of integer
    return EmployeeFactory.with_overrides(dependants="two")

  @staticmethod
  def float_dependants() -> dict:
    # Invalid payload — dependants as float instead of integer
    return EmployeeFactory.with_overrides(dependants=2.5)

  @staticmethod
  def with_readonly_fields() -> dict:
    """
    To test if the API ignores or rejects supplied values

    The server must NOT save these values:
      gross=9999 instead of 2000
      benefitsCost=0.01 instead of computed value
      net=9999 instead of computed value
    """
    return {
      "firstName": fake.first_name(),
      "lastName": fake.last_name(),
      "username": fake.user_name()[:50],
      "dependants": 0,
      "gross": 9999.00,
      "benefitsCost": 0.01,
      "net": 9999.00,
      "partitionKey": "hacked",
      "sortKey": str(uuid.uuid4()),
    }


  @staticmethod
  def sql_injection(field: str) -> dict:
    """
    Valid payload with SQL injection string in one field
    To test input sanitization not trying to actually inject,
    verifying the app handles the string safely

    Acceptable results:
      400: input rejected
      200: saved as literal string, no side effects

    Unacceptable outcome:
        500: injection reached database layer
    """
    injections = {
      "firstName": "' OR '1'='1", #Might return wrong data or 500
      "lastName": "O'Reilly",
      "username": "admin'--", #Might return 500 or bypass authentication in login
    }
    return EmployeeFactory.with_overrides(
      **{field: injections.get(field, "' OR '1'='1")}
    )

  @staticmethod
  def nonexistent_id() -> str:
    """
    A UUID guaranteed not to exist in the system
    Used for testing 404 responses on GET, PUT, DELETE.
    """
    return str(uuid.uuid4())