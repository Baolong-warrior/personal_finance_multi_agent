from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from finance_agents import FinancialProfile, PersonalFinanceCoordinator, load_transactions  # noqa: E402


st.set_page_config(page_title="多 Agent 个人财务顾问", layout="wide")
st.title("多 Agent 协同的个人财务顾问系统")
st.caption("教育性财务分析演示，不构成投资、税务、保险或法律建议。")

with st.sidebar:
    st.header("输入数据")
    tx_file = st.file_uploader("上传交易流水 CSV", type=["csv"])
    profile_file = st.file_uploader("上传用户画像 JSON", type=["json"])
    use_sample = st.checkbox("使用内置样例数据", value=True)
    run_btn = st.button("开始分析", type="primary")


def load_inputs():
    if use_sample or tx_file is None:
        tx_path = ROOT / "data" / "sample_transactions.csv"
    else:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        tmp.write(tx_file.getbuffer())
        tmp.close()
        tx_path = Path(tmp.name)

    if use_sample or profile_file is None:
        profile_data = json.loads((ROOT / "data" / "sample_profile.json").read_text(encoding="utf-8"))
    else:
        profile_data = json.loads(profile_file.getvalue().decode("utf-8"))

    profile = FinancialProfile.model_validate(profile_data)
    df = load_transactions(tx_path)
    return profile, df


if run_btn:
    profile, df = load_inputs()
    report_path = ROOT / "reports" / "streamlit_report.md"
    chart_path = ROOT / "reports" / "streamlit_cashflow_forecast.png"
    coordinator = PersonalFinanceCoordinator(profile, df, str(report_path), str(chart_path))
    blackboard = coordinator.run()

    data_result = blackboard.get_result("DataIngestionAgent")
    risk_result = blackboard.get_result("RiskAgent")
    forecast_result = blackboard.get_result("ForecastAgent")
    invest_result = blackboard.get_result("InvestmentAgent")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("月均收入", f"¥{data_result.data['avg_income']:,.0f}")
    c2.metric("月均支出", f"¥{data_result.data['avg_expense']:,.0f}")
    c3.metric("月均净现金流", f"¥{data_result.data['avg_net_cashflow']:,.0f}")
    c4.metric("风险评分", f"{risk_result.data['risk_score']}/100")

    tab1, tab2, tab3, tab4 = st.tabs(["总览", "预算/风险", "投资/债务", "完整报告"])

    with tab1:
        st.subheader("月度现金流")
        monthly = pd.DataFrame(data_result.data["months"])
        st.dataframe(monthly, use_container_width=True)
        st.subheader("支出类别")
        categories = pd.DataFrame(data_result.data["categories"])
        st.dataframe(categories, use_container_width=True)
        if forecast_result.data.get("chart_path"):
            st.image(forecast_result.data["chart_path"], caption="未来现金余额预测")

    with tab2:
        for name in ["BudgetAgent", "RiskAgent", "ForecastAgent"]:
            result = blackboard.get_result(name)
            st.markdown(f"### {name}")
            st.write(result.summary)
            if result.warnings:
                st.warning("\n".join(result.warnings))
            if result.recommendations:
                st.success("\n".join(result.recommendations))

    with tab3:
        for name in ["DebtAgent", "InvestmentAgent"]:
            result = blackboard.get_result(name)
            st.markdown(f"### {name}")
            st.write(result.summary)
            if result.warnings:
                st.warning("\n".join(result.warnings))
            if result.recommendations:
                st.success("\n".join(result.recommendations))
        st.json(invest_result.data)

    with tab4:
        report_text = blackboard.get_result("ReportAgent").data["report"]
        st.markdown(report_text)
        st.download_button("下载 Markdown 报告", data=report_text, file_name="finance_report.md")
else:
    st.info("点击左侧“开始分析”运行内置样例，或上传自己的 CSV/JSON 数据。")
