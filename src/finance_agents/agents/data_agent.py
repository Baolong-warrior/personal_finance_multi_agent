from __future__ import annotations

import pandas as pd

from finance_agents.agents.base import BaseAgent
from finance_agents.models import AgentResult, Blackboard
from finance_agents.utils import infer_category, money, pct


class DataIngestionAgent(BaseAgent):
    name = "DataIngestionAgent"

    def run(self, blackboard: Blackboard) -> AgentResult:
        if blackboard.transactions_df is None:
            raise ValueError("transactions_df is required")

        df = blackboard.transactions_df.copy()
        if "category" not in df.columns or df["category"].isna().all():
            df["category"] = df.apply(
                lambda r: infer_category(r["description"], r["amount"], r["type"]), axis=1
            )

        df["signed_expense"] = df["amount"].apply(lambda x: -x if x < 0 else 0)
        df["income_amount"] = df["amount"].apply(lambda x: x if x > 0 else 0)
        df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)

        monthly = df.groupby("month").agg(
            income=("income_amount", "sum"),
            expense=("signed_expense", "sum"),
            net_cashflow=("amount", "sum"),
            transaction_count=("amount", "count"),
        ).reset_index()
        monthly["savings_rate"] = monthly.apply(
            lambda r: r["net_cashflow"] / r["income"] if r["income"] > 0 else 0,
            axis=1,
        )

        category = (
            df[df["amount"] < 0]
            .groupby("category")
            .agg(expense=("signed_expense", "sum"), count=("amount", "count"))
            .sort_values("expense", ascending=False)
            .reset_index()
        )

        blackboard.transactions_df = df
        blackboard.monthly_summary = monthly
        blackboard.category_summary = category

        avg_income = float(monthly["income"].mean()) if not monthly.empty else 0
        avg_expense = float(monthly["expense"].mean()) if not monthly.empty else 0
        avg_net = float(monthly["net_cashflow"].mean()) if not monthly.empty else 0
        avg_savings_rate = avg_net / avg_income if avg_income > 0 else 0

        recs = []
        warnings = []
        if avg_savings_rate < 0.1:
            warnings.append("平均储蓄率低于 10%，建议优先控制非必要支出或提高收入。")
        if avg_net < 0:
            warnings.append("近几个月平均现金流为负，需要立即检查固定支出和高频消费。")
        if not category.empty:
            top_cat = category.iloc[0]
            recs.append(f"当前最大支出类别是 {top_cat['category']}，累计支出 {money(float(top_cat['expense']))}。")

        result = AgentResult(
            agent_name=self.name,
            summary=(
                f"已处理 {len(df)} 条交易。月均收入 {money(avg_income)}，"
                f"月均支出 {money(avg_expense)}，月均净现金流 {money(avg_net)}，"
                f"平均储蓄率 {pct(avg_savings_rate)}。"
            ),
            data={
                "avg_income": avg_income,
                "avg_expense": avg_expense,
                "avg_net_cashflow": avg_net,
                "avg_savings_rate": avg_savings_rate,
                "months": monthly.to_dict(orient="records"),
                "categories": category.to_dict(orient="records"),
            },
            recommendations=recs,
            warnings=warnings,
        )
        blackboard.add_result(result)
        return result
