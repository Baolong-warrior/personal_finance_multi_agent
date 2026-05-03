from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from finance_agents.agents.base import BaseAgent
from finance_agents.models import AgentResult, Blackboard
from finance_agents.utils import money


class ForecastAgent(BaseAgent):
    name = "ForecastAgent"

    def __init__(self, months_ahead: int = 12, chart_path: str | None = None):
        self.months_ahead = months_ahead
        self.chart_path = chart_path

    def run(self, blackboard: Blackboard) -> AgentResult:
        data_result = blackboard.get_result("DataIngestionAgent")
        if data_result is None:
            raise ValueError("DataIngestionAgent must run before ForecastAgent")
        profile = blackboard.profile
        avg_income = data_result.data["avg_income"]
        avg_expense = data_result.data["avg_expense"]
        avg_net = data_result.data["avg_net_cashflow"]

        start_cash = (profile.cash_assets + profile.emergency_fund) if profile else 0
        last_month = pd.Period(blackboard.monthly_summary["month"].max(), freq="M")
        rows = []
        balance = start_cash
        for i in range(1, self.months_ahead + 1):
            month = str(last_month + i)
            balance += avg_net
            rows.append({
                "month": month,
                "projected_income": avg_income,
                "projected_expense": avg_expense,
                "projected_net": avg_net,
                "projected_cash_balance": balance,
            })
        forecast = pd.DataFrame(rows)

        emergency_months = start_cash / avg_expense if avg_expense > 0 else 999
        warnings = []
        recommendations = []
        if emergency_months < 3:
            warnings.append(f"当前现金与应急金约可覆盖 {emergency_months:.1f} 个月支出，低于 3 个月安全线。")
            recommendations.append("在增加高风险投资前，先把应急金补到 3～6 个月生活支出。")
        elif emergency_months < 6:
            recommendations.append("应急金已超过 3 个月支出，可继续逐步补足到 6 个月。")
        else:
            recommendations.append("应急金覆盖较充分，新增结余可更多流向长期目标或投资。")

        if avg_net < 0:
            warnings.append("未来现金余额将按当前趋势持续下降。")
        elif avg_net > 0:
            recommendations.append(f"若维持当前结余，每年可新增储蓄约 {money(avg_net * 12)}。")

        chart_file = None
        if self.chart_path:
            path = Path(self.chart_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            plt.figure(figsize=(9, 4.8))
            plt.plot(forecast["month"], forecast["projected_cash_balance"], marker="o")
            plt.xticks(rotation=45)
            plt.title("Projected Cash Balance")
            plt.xlabel("Month")
            plt.ylabel("Cash Balance")
            plt.tight_layout()
            plt.savefig(path, dpi=160)
            plt.close()
            chart_file = str(path)

        result = AgentResult(
            agent_name=self.name,
            summary=f"基于历史均值预测，未来 {self.months_ahead} 个月月均净现金流约为 {money(avg_net)}。",
            data={
                "forecast": forecast.to_dict(orient="records"),
                "emergency_months": emergency_months,
                "chart_path": chart_file,
            },
            recommendations=recommendations,
            warnings=warnings,
        )
        blackboard.add_result(result)
        return result
