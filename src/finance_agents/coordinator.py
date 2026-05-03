from __future__ import annotations

from typing import Iterable, List

from finance_agents.agents.base import BaseAgent
from finance_agents.agents.budget_agent import BudgetAgent
from finance_agents.agents.data_agent import DataIngestionAgent
from finance_agents.agents.debt_agent import DebtAgent
from finance_agents.agents.forecast_agent import ForecastAgent
from finance_agents.agents.investment_agent import InvestmentAgent
from finance_agents.agents.report_agent import ReportAgent
from finance_agents.agents.risk_agent import RiskAgent
from finance_agents.models import AgentResult, Blackboard, FinancialProfile


class PersonalFinanceCoordinator:
    """
    Multi-agent coordinator.

    The coordinator implements a blackboard-style cooperation mechanism:
    1. Each agent reads shared state from Blackboard.
    2. Each agent writes structured AgentResult back to Blackboard.
    3. Later agents can reuse earlier agents' outputs.
    """

    def __init__(self, profile: FinancialProfile, transactions_df, report_path: str | None = None, chart_path: str | None = None):
        self.blackboard = Blackboard(profile=profile, transactions_df=transactions_df)
        self.agents: List[BaseAgent] = [
            DataIngestionAgent(),
            BudgetAgent(),
            ForecastAgent(months_ahead=12, chart_path=chart_path),
            DebtAgent(),
            RiskAgent(),
            InvestmentAgent(),
            ReportAgent(out_path=report_path),
        ]

    def run(self, selected_agents: Iterable[str] | None = None) -> Blackboard:
        selected = set(selected_agents) if selected_agents else None
        for agent in self.agents:
            if selected is not None and agent.name not in selected:
                continue
            agent.run(self.blackboard)
        return self.blackboard

    def summaries(self) -> list[AgentResult]:
        return list(self.blackboard.results.values())
