from __future__ import annotations

from finance_agents.agents.base import BaseAgent
from finance_agents.models import AgentResult, Blackboard
from finance_agents.utils import money


class DebtAgent(BaseAgent):
    name = "DebtAgent"

    def run(self, blackboard: Blackboard) -> AgentResult:
        profile = blackboard.profile
        if profile is None or not profile.debts:
            result = AgentResult(
                agent_name=self.name,
                summary="未提供债务信息，跳过债务规划。",
                data={"debts": []},
                recommendations=["如果存在信用卡、消费贷、车贷或房贷，可在 profile.json 中补充 debts 字段。"],
            )
            blackboard.add_result(result)
            return result

        debts = [d.model_dump() for d in profile.debts]
        total_balance = sum(d["balance"] for d in debts)
        total_min_payment = sum(d["min_payment"] for d in debts)

        avalanche = sorted(debts, key=lambda x: x["apr"], reverse=True)
        snowball = sorted(debts, key=lambda x: x["balance"])

        high_interest = [d for d in debts if d["apr"] >= 0.12]
        warnings = []
        recommendations = []
        if high_interest:
            names = ", ".join(d["name"] for d in high_interest)
            warnings.append(f"存在高息债务：{names}。")
            recommendations.append("优先采用雪崩法：在满足所有最低还款后，把额外现金流集中偿还最高 APR 债务。")
        else:
            recommendations.append("债务利率不算极高；如果心理激励更重要，可采用雪球法先还小额债务。")

        recommendations.append(
            f"债务总额 {money(total_balance)}，每月最低还款合计 {money(total_min_payment)}。"
        )
        recommendations.append(
            "雪崩法顺序：" + " → ".join(f"{d['name']}({d['apr']*100:.1f}%)" for d in avalanche)
        )
        recommendations.append(
            "雪球法顺序：" + " → ".join(f"{d['name']}({money(d['balance'])})" for d in snowball)
        )

        result = AgentResult(
            agent_name=self.name,
            summary=f"识别到 {len(debts)} 笔债务，总余额 {money(total_balance)}。",
            data={
                "total_balance": total_balance,
                "total_min_payment": total_min_payment,
                "avalanche_order": avalanche,
                "snowball_order": snowball,
            },
            recommendations=recommendations,
            warnings=warnings,
        )
        blackboard.add_result(result)
        return result
