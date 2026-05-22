"""
Unit tests for helpers/calculations.py

Fastest tests in the suite since they dont require browser, network, or API
Pure Python math verified against the business rules from the spec

Business rules under test:
  - Gross per paycheck: $2,000.00 (always fixed)
  - Paychecks per year: 26
  - Employee benefit cost: $1,000/year
  - Dependent benefit cost: $500/year each
  - Valid dependants range: 0-32

Why unit tests here:
  calculate_benefits() is pure logic with no external dependencies.
  A bug in this formula affects every API and UI test that asserts
  on benefit calculations. Catching it here is faster and cheaper
  than discovering it through a failing UI test.
"""

import pytest

from helpers.calculations import BenefitResult, calculate_benefits


class TestCalculateBenefitsHappyPath:

  def test_zero_dependants(self) -> None:
    """
    0 dependants — employee cost only.
    total_annual = 1000
    benefits_cost = round(1000 / 26, 2) = 38.46
    net = round(2000 - 38.46, 2) = 1961.54
    """
    result = calculate_benefits(dependants=0)

    assert result.gross == 2000.00
    assert result.benefits_cost == 38.46
    assert result.net == 1961.54

  def test_one_dependant(self) -> None:
    """
    1 dependant — employee + one dependent cost.
    total_annual = 1000 + 500 = 1500
    benefits_cost = round(1500 / 26, 2) = 57.69
    net = round(2000 - 57.69, 2) = 1942.31
    """
    result = calculate_benefits(dependants=1)

    assert result.gross == 2000.00
    assert result.benefits_cost == 57.69
    assert result.net == 1942.31

  def test_two_dependants(self) -> None:
    """
    2 dependants — most common scenario in acceptance criteria.
    total_annual = 1000 + (2 x 500) = 2000
    benefits_cost = round(2000 / 26, 2) = 76.92
    net = round(2000 - 76.92, 2) = 1923.08
    """
    result = calculate_benefits(dependants=2)

    assert result.gross == 2000.00
    assert result.benefits_cost == 76.92
    assert result.net == 1923.08

  def test_five_dependants(self) -> None:
    """
    5 dependants — used in edit employee recalculation tests.
    total_annual = 1000 + (5 x 500) = 3500
    benefits_cost = round(3500 / 26, 2) = 134.62
    net = round(2000 - 134.62, 2) = 1865.38
    """
    result = calculate_benefits(dependants=5)

    assert result.gross == 2000.00
    assert result.benefits_cost == 134.62
    assert result.net == 1865.38

  def test_gross_always_fixed(self) -> None:
    """
    Gross is always $2,000 regardless of dependants.
    Spec invariant: all employees paid $2,000 per paycheck.
    """
    for dependants in [0, 1, 5, 10, 32]:
      result = calculate_benefits(dependants=dependants)
      assert result.gross == 2000.00, (
        f"Expected gross=2000.00 for dependants={dependants}, "
        f"got {result.gross}"
      )

  def test_net_equals_gross_minus_benefits_cost(self) -> None:
    """
    Net is always gross minus benefits_cost.
    Verified for several values to ensure rounding consistency.
    """
    for dependants in [0, 1, 2, 5, 10, 32]:
      result = calculate_benefits(dependants=dependants)
      expected_net = round(result.gross - result.benefits_cost, 2)
      assert result.net == expected_net, (
        f"net != gross - benefits_cost for dependants={dependants}: "
        f"{result.net} != {expected_net}"
      )


class TestCalculateBenefitsBoundaries:

  def test_minimum_dependants_zero(self) -> None:
    """0 is the documented minimum — must succeed."""
    result = calculate_benefits(dependants=0)
    assert isinstance(result, BenefitResult)
    assert result.benefits_cost > 0

  def test_maximum_dependants_32(self) -> None:
    """
    32 is the documented maximum — must succeed.
    total_annual = 1000 + (32 x 500) = 17000
    benefits_cost = round(17000 / 26, 2) = 653.85
    net = round(2000 - 653.85, 2) = 1346.15
    """
    result = calculate_benefits(dependants=32)

    assert result.gross == 2000.00
    assert result.benefits_cost == 653.85
    assert result.net == 1346.15

  def test_over_maximum_raises_value_error(self) -> None:
    """33 exceeds the documented maximum — must raise ValueError."""
    with pytest.raises(ValueError, match="dependants must be between 0 and 32"):
      calculate_benefits(dependants=33)

  def test_negative_dependants_raises_value_error(self) -> None:
    """Negative dependants are invalid — must raise ValueError."""
    with pytest.raises(ValueError, match="dependants must be between 0 and 32"):
      calculate_benefits(dependants=-1)


class TestCalculateBenefitsReturnType:

  def test_returns_benefit_result_dataclass(self) -> None:
    """Result is always a BenefitResult dataclass."""
    result = calculate_benefits(dependants=0)
    assert isinstance(result, BenefitResult)

  def test_all_fields_are_floats(self) -> None:
    """gross, benefits_cost, and net are all floats."""
    result = calculate_benefits(dependants=2)
    assert isinstance(result.gross, float)
    assert isinstance(result.benefits_cost, float)
    assert isinstance(result.net, float)

  def test_result_is_immutable(self) -> None:
    """BenefitResult is frozen -> fields cannot be reassigned."""
    result = calculate_benefits(dependants=0)
    with pytest.raises((AttributeError, TypeError)):
      result.gross = 9999.0