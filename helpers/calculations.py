"""
Business Rules (from spec):
  - All employees get $2,000/paycheck
  - 26 paychecks/year
  - Benefits - $1,000/year
  - Dependant - $500/year additional cost
"""

from dataclasses import dataclass
from config.settings import settings

@dataclass(frozen=True)
class BenefitResult:
  #paycheck breakdown for any employee
  gross: float
  benefits_cost: float
  net: float


def calculate_benefits(dependants: int = 0) -> BenefitResult:
  # Raise ValueError if dependants is outside the valid range 0-32.
  if dependants < 0 or dependants > 32:
    raise ValueError(
      "dependants must be between 0 and 32"
    )

  _total_annual = (
      settings.employee_benefits_cost_per_year
      + (dependants * settings.dependent_cost_per_year)
  )

  benefits_cost = round(_total_annual / settings.paychecks_per_year, 2)
  gross = settings.salary_per_paycheck
  net = round(gross - benefits_cost, 2)

  return BenefitResult(
      gross=gross,
      benefits_cost=benefits_cost,
      net=net,
  )