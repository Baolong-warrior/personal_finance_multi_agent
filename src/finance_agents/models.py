from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


RiskPreference = Literal["low", "medium", "high"]


class Goal(BaseModel):
    name: str
    target_amount: float = Field(ge=0)
    target_months: int = Field(gt=0)


class Debt(BaseModel):
    name: str
    balance: float = Field(ge=0)
    apr: float = Field(ge=0, description="Annual percentage rate, e.g. 0.18 for 18%")
    min_payment: float = Field(ge=0)


class FinancialProfile(BaseModel):
    name: str = "User"
    age: int = Field(default=30, ge=18, le=100)
    monthly_income_target: float = Field(default=0, ge=0)
    emergency_fund: float = Field(default=0, ge=0)
    investment_assets: float = Field(default=0, ge=0)
    cash_assets: float = Field(default=0, ge=0)
    risk_preference: RiskPreference = "medium"
    goals: List[Goal] = Field(default_factory=list)
    debts: List[Debt] = Field(default_factory=list)


class Transaction(BaseModel):
    date: date
    description: str
    amount: float
    account: str = "Unknown"
    type: Literal["income", "expense"]
    category: str = "Uncategorized"

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, v: Any) -> str:
        if v is None or v == "":
            return "expense"
        v = str(v).lower().strip()
        if v in {"income", "in", "收入"}:
            return "income"
        if v in {"expense", "out", "支出"}:
            return "expense"
        raise ValueError("type must be income or expense")


@dataclass
class AgentResult:
    agent_name: str
    summary: str
    data: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class Blackboard:
    """Shared memory for all agents."""

    profile: Optional[FinancialProfile] = None
    transactions_df: Any = None
    monthly_summary: Any = None
    category_summary: Any = None
    results: Dict[str, AgentResult] = field(default_factory=dict)

    def add_result(self, result: AgentResult) -> None:
        self.results[result.agent_name] = result

    def get_result(self, agent_name: str) -> Optional[AgentResult]:
        return self.results.get(agent_name)
