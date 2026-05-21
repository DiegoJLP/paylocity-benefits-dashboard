"""
Validates API response body shapes against expected schemas

Why this instead of Pact contract testing:
  Pact is designed for multi-team microservice environments where a
  consumer team and provider team deploy independently and need to
  agree on a contract without direct communication

  In this challenge both UI and API are owned by Paylocity,
  Schema validation gives us the same coverage easier
"""

import re
import logging

logger = logging.getLogger(__name__)

# UUID pattern — xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


class SchemaValidator:
  """
  The swagger documentation doesnt define response schema, only
  '200: Success' with no body definition
  These validators are for 2 reasons:
    1. Verify the actual response contains expected fields and types
    2. Document the actual API response contract
  """

  # Expected fields and their Python types
  EMPLOYEE_SCHEMA = {
    "id":            str,
    "firstName":     str,
    "lastName":      str,
    "username":      str,
    "dependants":    int,
    "gross":         float,
    "benefitsCost":  float,
    "net":           float,
    "partitionKey":  str,
    "sortKey":       str,
  }

  @classmethod
  def validate_employee(cls, body: dict) -> None:
    """
    Validate a single employee response body.
    Checks:
      - All expected fields are present
      - All fields have the correct type
      - id and sortKey are valid UUID format
      - gross, benefitsCost, net are positive numbers
    
    Args:
      body: JSON response body as a dict.
    Raises:
      AssertionError: With a descriptive message if validation fails.
    """
    cls._validate_fields_present(body)
    cls._validate_field_types(body)
    cls._validate_uuid_fields(body)
    cls._validate_numeric_fields(body)
    logger.debug("Schema validation passed for employee id: %s", body.get("id"))

  @classmethod
  def validate_employee_list(cls, body: list) -> None:
      """
      Checks:
        - Response is a list (not null, not dict, not error)
        - Each element passes validate_employee

      Args:
        body: JSON response body as a list

      Raises:
        AssertionError: With a descriptive message if validation fails
      """
      assert isinstance(body, list), (
        f"Expected response to be a list, got {type(body).__name__}\n"
      )
      logger.debug("GET all response is a list with %d employees", len(body))

      for i, employee in enumerate(body):
        assert isinstance(employee, dict), (
          f"Expected element {i} to be a dict, got {type(employee).__name__}"
        )
        cls.validate_employee(employee)

  @classmethod
  def validate_empty_list(cls, body: list) -> None:
    """
    Validate that GET all returns an empty list array when no employees exist

    Args:
      body: JSON response body

    Raises:
      AssertionError: If body is not an empty list
    """
    assert isinstance(body, list), (
      f"Expected empty list [], got {type(body).__name__}.\n"
      f"API should return [] not null or 404"
    )
    assert len(body) == 0, (
      f"Expected empty list, got {len(body)} employees."
    )


  @classmethod
  def _validate_fields_present(cls, body: dict) -> None:
    #Assert all expected fields are present in the response
    missing = [
      field for field in cls.EMPLOYEE_SCHEMA
      if field not in body
    ]
    assert not missing, (
      f"Response missing expected fields: {missing}\n"
      f"Full response: {body}\n"
      f"DOCUMENTATION NOTE: Swagger defines no response schema "
      f"These fields were expected based on observed API behavior"
    )

  @classmethod
  def _validate_field_types(cls, body: dict) -> None:
    #Assert all fields have the correct Python type
    for field, expected_type in cls.EMPLOYEE_SCHEMA.items():
      if field not in body:
        continue
      value = body[field]
      # Allow int where float is expected since int is valid float in JSON
      if expected_type is float and isinstance(value, int):
        continue
      assert isinstance(value, expected_type), (
        f"Field '{field}' expected type {expected_type.__name__}, "
        f"got {type(value).__name__} (value: {value!r})"
      )

  @classmethod
  def _validate_uuid_fields(cls, body: dict) -> None:
    #Assert id and sortKey match UUID format
    for field in ("id", "sortKey"):
      value = body.get(field, "")
      assert UUID_PATTERN.match(str(value)), (
        f"Field '{field}' is not a valid UUID: {value!r}\n"
        f"Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      )

  @classmethod
  def _validate_numeric_fields(cls, body: dict) -> None:
    #Assert gross, benefitsCost, and net are positive numbers
    for field in ("gross", "benefitsCost", "net"):
      value = body.get(field, 0)
      assert value > 0, (
        f"Field '{field}' should be a positive number, got {value}\n"
        f"gross should always be 2000.00\n"
        f"benefitsCost and net depend on dependants count"
      )