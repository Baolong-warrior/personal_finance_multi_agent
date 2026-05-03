# 多 Agent 协同的个人财务顾问系统

这是一个可运行的 Python 项目，用于演示“多 Agent 协同”的个人财务顾问系统。系统不依赖大模型也能运行，采用规则推理 + 协同黑板机制完成财务分析；后续也可以在 `Coordinator` 中接入 LLM。

> 说明：本项目输出的是教育性、信息性建议，不构成投资、税务、保险或法律建议。真实决策前请咨询持牌专业人士。

## 功能

- 交易流水 CSV 导入与自动分类
- 收入、支出、储蓄率、现金流分析
- 预算 Agent：50/30/20 预算框架、超支类别识别
- 预测 Agent：未来 12 个月现金流与应急金覆盖月数预测
- 债务 Agent：雪球法、雪崩法还款策略
- 风险 Agent：应急金、收入集中度、支出波动风险
- 投资 Agent：风险承受能力估计与资产配置建议
- 报告 Agent：自动生成 Markdown 财务建议报告
- CLI 与 Streamlit Web 界面

## 项目结构

```text
personal_finance_multi_agent/
├── app_streamlit.py                 # Streamlit Web 应用
├── cli_demo.py                      # 命令行入口
├── requirements.txt
├── README.md
├── data/
│   ├── sample_transactions.csv
│   └── sample_profile.json
├── reports/
├── src/
│   └── finance_agents/
│       ├── models.py
│       ├── coordinator.py
│       ├── utils.py
│       └── agents/
│           ├── base.py
│           ├── data_agent.py
│           ├── budget_agent.py
│           ├── forecast_agent.py
│           ├── debt_agent.py
│           ├── risk_agent.py
│           ├── investment_agent.py
│           └── report_agent.py
└── tests/
    └── test_smoke.py
```

## 安装与运行

```bash
cd personal_finance_multi_agent
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 1. CLI 运行

```bash
python cli_demo.py --transactions data/sample_transactions.csv --profile data/sample_profile.json --out reports/report.md
```

运行后会生成：

```text
reports/report.md
reports/cashflow_forecast.png
```

### 2. Streamlit Web 界面

```bash
streamlit run app_streamlit.py
```

## CSV 数据格式

交易流水 CSV 至少包含以下字段：

```csv
date,description,amount,account,type
2026-01-01,Salary,25000,Checking,income
2026-01-03,Rent,-6000,Checking,expense
```

字段含义：

- `date`: 日期，格式如 `YYYY-MM-DD`
- `description`: 交易描述
- `amount`: 金额，收入为正，支出为负
- `account`: 账户名称
- `type`: `income` 或 `expense`，可缺省，系统会按金额推断

## Profile JSON 格式

```json
{
  "name": "Demo User",
  "age": 26,
  "monthly_income_target": 25000,
  "emergency_fund": 30000,
  "investment_assets": 50000,
  "cash_assets": 30000,
  "risk_preference": "medium",
  "goals": [
    {"name": "Build emergency fund", "target_amount": 90000, "target_months": 12}
  ],
  "debts": [
    {"name": "Credit Card", "balance": 12000, "apr": 0.18, "min_payment": 600}
  ]
}
```

## 后续可扩展方向

- 接入 OpenAI / 本地大模型，让 ReportAgent 生成更自然的解释
- 接入银行 API、支付宝/微信账单解析
- 加入税务 Agent、保险 Agent、家庭资产负债表 Agent
- 加入 RAG：读取合同、贷款文件、保险条款后进行问答
- 加入强化学习或优化算法做目标约束下的现金流规划
