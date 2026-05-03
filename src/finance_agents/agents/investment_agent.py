from __future__ import annotations

from finance_agents.agents.base import BaseAgent
from finance_agents.models import AgentResult, Blackboard
from finance_agents.utils import money


ALLOCATIONS = {
    "low": {"cash": 0.25, "bonds": 0.45, "equity_index": 0.25, "alternatives": 0.05},
    "medium": {"cash": 0.15, "bonds": 0.30, "equity_index": 0.50, "alternatives": 0.05},
    "high": {"cash": 0.10, "bonds": 0.15, "equity_index": 0.70, "alternatives": 0.05},
}


class InvestmentAgent(BaseAgent):
    name = "InvestmentAgent"

    def run(self, blackboard: Blackboard) -> AgentResult:
        profile = blackboard.profile
        data_result = blackboard.get_result("DataIngestionAgent")
        risk_result = blackboard.get_result("RiskAgent")
        if profile is None:
            raise ValueError("profile is required for InvestmentAgent")

        risk_pref = profile.risk_preference
        if profile.age < 30 and risk_pref == "medium":
            inferred = "medium"
        elif profile.age > 55 and risk_pref == "high":
            inferred = "medium"
        else:
            inferred = risk_pref

        avg_expense = data_result.data["avg_expense"] if data_result else 0
        emergency_months = (profile.emergency_fund / avg_expense) if avg_expense > 0 else 999
        allocation = ALLOCATIONS[inferred]
        investable = max(0.0, profile.cash_assets + profile.investment_assets - avg_expense * 6)

        warnings = []
        recommendations = []
        if emergency_months < 3:
            warnings.append("应急金不足时，不建议贸然增加高波动资产。")
            recommendations.append("优先补充应急金，再考虑长期投资。")
        else:
            recommendations.append(f"估算可用于长期配置的资产约 {money(investable)}。")
            recommendations.append(
                "参考配置："
                + ", ".join(f"{k} {v*100:.0f}%" for k, v in allocation.items())
                + "。"
            )
            recommendations.append("建议采用定投和年度再平衡，而不是基于短期市场波动频繁择时。")

        if risk_result and risk_result.data.get("risk_score", 100) < 60:
            warnings.append("整体财务风险偏高，投资计划应保守推进。")

        result = AgentResult(
            agent_name=self.name,
            summary=f"根据年龄、风险偏好和现金储备，估计适合的投资风险档位为：{inferred}。",
            data={
                "risk_profile": inferred,
                "allocation": allocation,
                "investable_assets_estimate": investable,
            },
            recommendations=recommendations,
            warnings=warnings,
        )
        blackboard.add_result(result)
        return result
