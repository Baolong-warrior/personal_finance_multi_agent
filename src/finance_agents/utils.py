from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import pandas as pd

from .models import FinancialProfile


CATEGORY_KEYWORDS: Dict[str, list[str]] = {
    "Housing": ["rent", "mortgage", "apartment", "物业", "房租", "租金"],
    "Food": ["restaurant", "grocery", "food", "supermarket", "coffee", "餐", "超市", "咖啡"],
    "Transport": ["uber", "taxi", "metro", "train", "bus", "gas", "交通", "地铁", "火车"],
    "Shopping": ["amazon", "taobao", "jd", "mall", "clothes", "购物", "淘宝", "京东"],
    "Health": ["hospital", "doctor", "pharmacy", "gym", "医院", "药", "健身"],
    "Education": ["course", "book", "tuition", "school", "课程", "学费", "书"],
    "Entertainment": ["movie", "game", "netflix", "spotify", "cinema", "娱乐", "电影", "游戏"],
    "Utilities": ["electric", "water", "internet", "phone", "utility", "电费", "水费", "话费", "宽带"],
    "Insurance": ["insurance", "premium", "保险"],
    "Debt Payment": ["loan", "credit card", "repayment", "debt", "贷款", "信用卡", "还款"],
    "Income": ["salary", "bonus", "interest", "dividend", "工资", "奖金", "利息"],
}


def load_profile(path: str | Path) -> FinancialProfile:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return FinancialProfile.model_validate(data)


def load_transactions(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"date", "description", "amount"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")
    if "account" not in df.columns:
        df["account"] = "Unknown"
    if "type" not in df.columns:
        df["type"] = df["amount"].apply(lambda x: "income" if x >= 0 else "expense")
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    df["type"] = df.apply(
        lambda r: str(r["type"]).lower().strip() if pd.notna(r["type"]) else ("income" if r["amount"] >= 0 else "expense"),
        axis=1,
    )
    df["type"] = df.apply(lambda r: "income" if r["amount"] >= 0 else "expense" if r["type"] not in {"income", "expense"} else r["type"], axis=1)
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df


def infer_category(description: str, amount: float, tx_type: str) -> str:
    desc = str(description).lower()
    if tx_type == "income" or amount > 0:
        for kw in CATEGORY_KEYWORDS["Income"]:
            if kw.lower() in desc:
                return "Income"
        return "Income"
    for category, keywords in CATEGORY_KEYWORDS.items():
        if category == "Income":
            continue
        for kw in keywords:
            if kw.lower() in desc:
                return category
    return "Other"


def money(x: float) -> str:
    return f"¥{x:,.2f}"


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"
