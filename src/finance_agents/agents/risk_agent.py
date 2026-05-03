from __future__ import annotations

import numpy as np

from finance_agents.agents.base import BaseAgent
from finance_agents.models import AgentResult, Blackboard
from finance_agents.utils import money


class RiskAgent(BaseAgent):
    name = "RiskAgent"

    def run(self, blackboard: Blackboard) -> AgentResult:
        profile = blackboard.profile
        monthly = blackboard.monthly_summary
        data_result = blackboard.get_result("DataIngestionAgent")
        if data_result is None:
            raise ValueError("DataIngestionAgent must run before RiskAgent")

        avg_expense = data_result.data["avg_expense"]
        emergency = profile.emergency_fund if profile else 0
        emergency_months = emergency / avg_expense if avg_expense > 0 else 999

        net_std = float(np.std(monthly["net_cashflow"].to_numpy())) if len(monthly) > 1 else 0
        avg_income = data_result.data["avg_income"]
        volatility_ratio = net_std / avg_income if avg_income > 0 else 0

        score = 100
        warnings = []
        recommendations = []
        if emergency_months < 3:
            score -= 30
            warnings.append("应急金不足 3 个月支出。")
            recommendations.append(f"建议至少补足到 3 个月支出：目标约 {money(avg_expense * 3)}。")
        elif emergency_months < 6:
            score -= 10
            recommendations.append(f"可把应急金进一步提升到 6 个月支出：目标约 {money(avg_expense * 6)}。")

        if volatility_ratio > 0.4:
            score -= 20
            warnings.append("月度现金流波动较大。")
            recommendations.append("建议建立年度大额支出清单，将保险、学费、旅行等支出按月预提。")

        if avg_income <= 0:
            score -= 25
            warnings.append("未识别到稳定收入。")

        score = max(0, min(100, score))
        if score >= 80:
            level = "稳健"
        elif score >= 60:
            level = "中等"
        else:
            level = "偏高"

        result = AgentResult(
            agent_name=self.name,
            summary=f"综合财务风险评分 {score}/100，风险水平：{level}。",
            data={
                "risk_score": score,
                "risk_level": level,
                "emergency_months": emergency_months,
                "cashflow_volatility_ratio": volatility_ratio,
            },
            recommendations=recommendations,
            warnings=warnings,
        )
        blackboard.add_result(result)
        return result
