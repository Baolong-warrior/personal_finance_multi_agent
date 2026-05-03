from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from finance_agents import PersonalFinanceCoordinator, load_profile, load_transactions  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="多 Agent 协同个人财务顾问系统 CLI")
    parser.add_argument("--transactions", default="data/sample_transactions.csv", help="交易流水 CSV 路径")
    parser.add_argument("--profile", default="data/sample_profile.json", help="用户画像 JSON 路径")
    parser.add_argument("--out", default="reports/report.md", help="输出 Markdown 报告路径")
    parser.add_argument("--chart", default="reports/cashflow_forecast.png", help="现金流预测图路径")
    args = parser.parse_args()

    profile = load_profile(args.profile)
    df = load_transactions(args.transactions)

    coordinator = PersonalFinanceCoordinator(
        profile=profile,
        transactions_df=df,
        report_path=args.out,
        chart_path=args.chart,
    )
    blackboard = coordinator.run()

    print("\n=== 多 Agent 分析完成 ===\n")
    for result in blackboard.results.values():
        print(f"[{result.agent_name}] {result.summary}")
        for w in result.warnings:
            print(f"  ! {w}")
        for r in result.recommendations[:3]:
            print(f"  - {r}")
        print()
    print(f"报告已保存：{args.out}")
    print(f"图表已保存：{args.chart}")


if __name__ == "__main__":
    main()
