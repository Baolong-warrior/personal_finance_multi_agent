from __future__ import annotations

from finance_agents.agents.base import BaseAgent
from finance_agents.models import AgentResult, Blackboard
from finance_agents.utils import money, pct


NEEDS = {"Housing", "Food", "Transport", "Utilities", "Health", "Insurance", "Debt Payment"}
WANTS = {"Shopping", "Entertainment", "Other"}


class BudgetAgent(BaseAgent):
    name = "BudgetAgent"

    def run(self, blackboard: Blackboard) -> AgentResult:
        data_result = blackboard.get_result("DataIngestionAgent")
        if data_result is None:
            raise ValueError("DataIngestionAgent must run before BudgetAgent")
        df = blackboard.transactions_df
        avg_income = data_result.data["avg_income"]

        expense_df = df[df["amount"] < 0].copy()
        expense_df["expense"] = -expense_df["amount"]
        needs = float(expense_df[expense_df["category"].isin(NEEDS)]["expense"].sum())
        wants = float(expense_df[expense_df["category"].isin(WANTS)]["expense"].sum())
        debt = float(expense_df[expense_df["category"].eq("Debt Payment")]["expense"].sum())
        months = max(1, df["month"].nunique())
        monthly_needs = needs / months
        monthly_wants = wants / months
        monthly_debt = debt / months

        target_needs = avg_income * 0.50
        target_wants = avg_income * 0.30
        target_saving = avg_income * 0.20
        actual_saving = data_result.data["avg_net_cashflow"]

        warnings = []
        recommendations = []
        if monthly_needs > target_needs:
            warnings.append(f"必要支出占比 {pct(monthly_needs / avg_income if avg_income else 0)}，超过 50% 参考线。")
            recommendations.append("优先检查房租、通勤、通信、水电等固定成本，固定支出一旦下降会长期改善现金流。")
        if monthly_wants > target_wants:
            warnings.append(f"弹性消费占比 {pct(monthly_wants / avg_income if avg_income else 0)}，超过 30% 参考线。")
            recommendations.append("对娱乐、购物、外食设置月度封顶额度，建议先压缩 10%～20%。")
        if actual_saving < target_saving:
            gap = target_saving - actual_saving
            recommendations.append(f"距离 20% 储蓄目标每月还差 {money(gap)}，可将其拆分到 2～3 个高支出类别中削减。")

        result = AgentResult(
            agent_name=self.name,
            summary=(
                f"按 50/30/20 框架：建议必要支出≤{money(target_needs)}，"
                f"弹性消费≤{money(target_wants)}，储蓄/投资≥{money(target_saving)}。"
            ),
            data={
                "monthly_needs": monthly_needs,
                "monthly_wants": monthly_wants,
                "monthly_debt": monthly_debt,
                "target_needs": target_needs,
                "target_wants": target_wants,
                "target_saving": target_saving,
                "actual_saving": actual_saving,
            },
            recommendations=recommendations,
            warnings=warnings,
        )
        blackboard.add_result(result)
        return result
