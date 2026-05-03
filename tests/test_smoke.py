from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from finance_agents import PersonalFinanceCoordinator, load_profile, load_transactions


def test_system_runs():
    profile = load_profile(ROOT / "data" / "sample_profile.json")
    df = load_transactions(ROOT / "data" / "sample_transactions.csv")
    coordinator = PersonalFinanceCoordinator(profile, df)
    blackboard = coordinator.run()
    assert "DataIngestionAgent" in blackboard.results
    assert "ReportAgent" in blackboard.results
    assert blackboard.get_result("DataIngestionAgent").data["avg_income"] > 0
