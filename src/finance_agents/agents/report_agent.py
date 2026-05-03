from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from finance_agents.agents.base import BaseAgent
from finance_agents.models import AgentResult, Blackboard
from finance_agents.utils import money, pct


class ReportAgent(BaseAgent):
    name = "ReportAgent"

    def __init__(self, out_path: str | None = None):
        self.out_path = out_path

    def run(self, blackboard: Blackboard) -> AgentResult:
        profile = blackboard.profile
        lines: list[str] = []
        lines.append("# 多 Agent 个人财务顾问报告")
        lines.append("")
        lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("> 免责声明：本报告仅用于教育和信息参考，不构成投资、税务、保险或法律建议。")
        lines.append("")
        if profile:
            lines.append("## 1. 用户画像")
            lines.append("")
            lines.append(f"- 姓名：{profile.name}")
            lines.append(f"- 年龄：{profile.age}")
            lines.append(f"- 风险偏好：{profile.risk_preference}")
            lines.append(f"- 现金资产：{money(profile.cash_assets)}")
            lines.append(f"- 应急金：{money(profile.emergency_fund)}")
            lines.append(f"- 投资资产：{money(profile.investment_assets)}")
            lines.append("")

        data_result = blackboard.get_result("DataIngestionAgent")
        if data_result:
            lines.append("## 2. 总览")
            lines.append("")
            lines.append(data_result.summary)
            lines.append("")
            lines.append("### 月度汇总")
            lines.append("")
            monthly = pd.DataFrame(data_result.data["months"])
            if not monthly.empty:
                lines.append("| 月份 | 收入 | 支出 | 净现金流 | 储蓄率 |")
                lines.append("|---|---:|---:|---:|---:|")
                for _, r in monthly.iterrows():
                    lines.append(
                        f"| {r['month']} | {money(float(r['income']))} | {money(float(r['expense']))} | "
                        f"{money(float(r['net_cashflow']))} | {pct(float(r['savings_rate']))} |"
                    )
                lines.append("")

            categories = pd.DataFrame(data_result.data["categories"])
            if not categories.empty:
                lines.append("### 支出类别 Top")
                lines.append("")
                lines.append("| 类别 | 支出 | 笔数 |")
                lines.append("|---|---:|---:|")
                for _, r in categories.head(8).iterrows():
                    lines.append(f"| {r['category']} | {money(float(r['expense']))} | {int(r['count'])} |")
                lines.append("")

        lines.append("## 3. Agent 分析结果")
        lines.append("")
        for name, result in blackboard.results.items():
            if name == self.name:
                continue
            lines.append(f"### {name}")
            lines.append("")
            lines.append(result.summary)
            lines.append("")
            if result.warnings:
                lines.append("**风险提醒：**")
                for w in result.warnings:
                    lines.append(f"- {w}")
                lines.append("")
            if result.recommendations:
                lines.append("**建议：**")
                for rec in result.recommendations:
                    lines.append(f"- {rec}")
                lines.append("")

        forecast = blackboard.get_result("ForecastAgent")
        if forecast and forecast.data.get("chart_path"):
            lines.append("## 4. 现金流预测图")
            lines.append("")
            lines.append(f"![现金流预测图]({forecast.data['chart_path']})")
            lines.append("")

        lines.append("## 5. 建议执行顺序")
        lines.append("")
        lines.append("1. 先确保月度现金流为正，并建立最低 3 个月支出的应急金。")
        lines.append("2. 对高息债务采用雪崩法优先偿还。")
        lines.append("3. 对最大支出类别设置预算上限，连续跟踪 3 个月。")
        lines.append("4. 应急金达标后，再按风险档位做长期资产配置。")
        lines.append("5. 每月更新流水，每季度复盘预算、债务和资产配置。")
        lines.append("")

        report = "\n".join(lines)
        if self.out_path:
            path = Path(self.out_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(report, encoding="utf-8")

        result = AgentResult(
            agent_name=self.name,
            summary="已生成完整财务顾问报告。",
            data={"report": report, "out_path": self.out_path},
            recommendations=[],
            warnings=[],
        )
        blackboard.add_result(result)
        return result
