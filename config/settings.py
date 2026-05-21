"""
Configuration values.
Loads at import from environment variables. (.env - python-dotenv)
"""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

@dataclass(frozen=True) #Make values FINAL (overwriting any of this raises FrozenInstanceError) 
class Settings:
  base_url: str
  api_base_url: str

  auth_token: str

  ui_username: str
  ui_password: str

  headless: bool
  slow_mo: int
  browser: str

  default_timeout: int
  navigation_timeout: int
  
  salary_per_paycheck: float=2000.00
  paychecks_per_year: int = 26
  employee_benefits_cost_per_year: float = 1000.0
  dependent_cost_per_year: float = 500.0

def _load_settings() -> Settings:
  def _require(key:str) -> str:
    value = os.getenv(key)
    if not value:
      raise EnvironmentError(
        f"Environment {key} is missing, get value from .env"
      )
    return value

  def _bool(key: str, default: bool = True) -> bool:
    return os.getenv(key, str(default)).lower() in ("true", "1", "yes")
  
  def _int(key: str, default: int) -> int:
    return int(os.getenv(key, str(default)))
  
  return Settings(
      base_url=_require("BASE_URL").rstrip("/"),
      api_base_url=_require("API_BASE_URL").rstrip("/"),
      auth_token=_require("AUTH_TOKEN"),
      ui_username=_require("UI_USERNAME"),
      ui_password=_require("UI_PASSWORD"),
      headless=_bool("HEADLESS", default=False),
      browser=os.getenv("BROWSER", "chromium"),
      default_timeout=_int("DEFAULT_TIMEOUT", default=30000),
      navigation_timeout=_int("NAVIGATION_TIMEOUT", default=60000),
  )

settings = _load_settings()
