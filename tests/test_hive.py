"""Offline tests for Quant Hive components and orchestration."""

import logging
import os
from unittest.mock import patch

import numpy as np
import pandas as pd

from agents.backtest_agent import BacktestAgent
from agents.news_agent import NewsAgent
from agents.report_agent import ReportAgent
from agents.risk_agent import RiskAgent
from agents.signal_agent import SignalAgent
from kernel.memory import Memory
from kernel.orchestrator import Orchestrator
from kernel.risk_engine import RiskEngine

logger = logging.getLogger(__name__)


def test_memory_set_get_and_default() -> None:
    """Memory stores values and returns a default for absent keys."""
    memory = Memory()
    memory.set("answer", 42)
    assert memory.get("answer") == 42
    assert memory.get("missing", "fallback") == "fallback"


def test_memory_history_records_updates() -> None:
    """Memory history preserves successful writes in their original order."""
    memory = Memory()
    memory.set("state", "first")
    memory.set("state", "second")
    assert memory.history() == [
        {"key": "state", "value": "first"},
        {"key": "state", "value": "second"},
    ]


def test_memory_clear_removes_values_and_history() -> None:
    """Clear empties both the current store and its history."""
    memory = Memory()
    memory.set("state", True)
    memory.clear()
    assert memory.get("state") is None
    assert memory.history() == []


def test_risk_engine_calculates_position_size() -> None:
    """Position size allocates the configured loss budget at the stop."""
    engine = RiskEngine(10000.0, 0.02)
    assert engine.position_size(100.0, 98.0) == 100.0


def test_risk_engine_validates_risk_limit_and_bad_input() -> None:
    """Validation accepts in-budget exposure and rejects excessive exposure."""
    engine = RiskEngine(10000.0, 0.02)
    assert engine.validate(100.0, 100.0, 98.0)
    assert not engine.validate(101.0, 100.0, 98.0)
    assert not engine.validate(float("nan"), 100.0, 98.0)
    assert engine.position_size(100.0, 100.0) == 0.0


def test_signal_agent_detects_bullish_sma_regime() -> None:
    """An ascending price series has a 20-period average above its 50-period average."""
    frame = pd.DataFrame({"Close": np.arange(1.0, 81.0)})
    signal = SignalAgent().generate(frame)
    assert signal["direction"] == "BUY"
    assert signal["sma_20"] > signal["sma_50"]
    assert signal["entry"] == 80.0


def test_signal_agent_holds_with_insufficient_history() -> None:
    """Signal generation declines to infer a trend without 50 observations."""
    frame = pd.DataFrame({"Close": np.arange(1.0, 25.0)})
    signal = SignalAgent().generate(frame)
    assert signal["direction"] == "HOLD"
    assert signal["entry"] == 24.0


def test_backtest_agent_returns_metrics_for_sufficient_data() -> None:
    """Backtest produces finite metrics and sizes its reference position."""
    prices = np.concatenate([np.linspace(100.0, 120.0, 80), np.linspace(120.0, 105.0, 40), np.linspace(105.0, 135.0, 80)])
    frame = pd.DataFrame({"Close": prices})
    engine = RiskEngine(10000.0, 0.02)
    result = BacktestAgent(engine).run(frame, {"entry": 135.0, "stop": 132.3, "direction": "BUY"})
    assert result["status"] == "complete"
    assert result["trade_count"] >= 0
    assert np.isfinite(result["return_pct"])
    assert result["position_size"] > 0


def test_backtest_agent_handles_empty_data() -> None:
    """Backtest returns a stable no-data result instead of raising."""
    result = BacktestAgent(RiskEngine(10000.0, 0.02)).run(pd.DataFrame(), {})
    assert result["status"] == "insufficient_data"
    assert result["trade_count"] == 0


def test_risk_agent_proceeds_on_positive_valid_backtest() -> None:
    """A valid signal with positive results and controlled drawdown proceeds."""
    engine = RiskEngine(10000.0, 0.02)
    signal = {"direction": "BUY", "entry": 100.0, "stop": 98.0}
    backtest = {
        "position_size": 100.0,
        "status": "complete",
        "trade_count": 3,
        "return_pct": 8.0,
        "max_drawdown_pct": 5.0,
    }
    assert RiskAgent(engine).assess(signal, backtest) == "PROCEED"


def test_risk_agent_uses_caution_for_hold_or_unproven_strategy() -> None:
    """Neutral signals and incomplete simulations are treated cautiously."""
    engine = RiskEngine(10000.0, 0.02)
    assessor = RiskAgent(engine)
    assert assessor.assess({"direction": "HOLD"}, {}) == "CAUTION"
    signal = {"direction": "BUY", "entry": 100.0, "stop": 98.0}
    assert assessor.assess(signal, {"position_size": 100.0, "status": "insufficient_data"}) == "CAUTION"


def test_risk_agent_avoids_excessive_risk() -> None:
    """A stop distance with an oversized position is rejected."""
    engine = RiskEngine(10000.0, 0.02)
    signal = {"direction": "BUY", "entry": 100.0, "stop": 98.0}
    backtest = {
        "position_size": 1000.0,
        "status": "complete",
        "trade_count": 4,
        "return_pct": 20.0,
        "max_drawdown_pct": 2.0,
    }
    assert RiskAgent(engine).assess(signal, backtest) == "AVOID"


def test_report_agent_compiles_readable_report() -> None:
    """Report contains the key symbol, verdict, and safety framing."""
    report = ReportAgent().compile(
        {
            "symbol": "AAPL",
            "signal": {"direction": "BUY", "entry": 200.0, "stop": 196.0},
            "backtest": {"status": "complete", "trade_count": 2, "return_pct": 4.5, "max_drawdown_pct": 3.0},
            "risk": "PROCEED",
            "news": "Neutral context.",
        }
    )
    assert "AAPL" in report
    assert "PROCEED" in report
    assert "not an instruction to trade" in report


def test_news_agent_skips_groq_when_api_key_is_missing() -> None:
    """News analysis remains graceful and offline without a Groq API key."""
    with patch.dict(os.environ, {}, clear=True), patch("groq.Groq") as groq_client:
        result = NewsAgent().analyse("AAPL")
    assert "GROQ_API_KEY" in result
    groq_client.assert_not_called()


def test_orchestrator_runs_agents_and_returns_all_required_sections() -> None:
    """Orchestration coordinates data, Groq, analysis, memory, and report offline."""
    prices = np.concatenate([np.linspace(100.0, 120.0, 80), np.linspace(120.0, 105.0, 40), np.linspace(105.0, 135.0, 180)])
    frame = pd.DataFrame(
        {
            "Open": prices,
            "High": prices + 1.0,
            "Low": prices - 1.0,
            "Close": prices,
            "Volume": np.full(len(prices), 1000),
        },
        index=pd.date_range("2022-01-01", periods=len(prices), freq="D"),
    )
    groq_response = type(
        "Response",
        (),
        {"choices": [type("Choice", (), {"message": type("Message", (), {"content": "Balanced context."})()})()]},
    )()
    with patch("yfinance.download", return_value=frame) as download, patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}), patch("groq.Groq") as groq_class:
        groq_class.return_value.chat.completions.create.return_value = groq_response
        orchestrator = Orchestrator(
            {"capital": 10000.0, "risk_per_trade": 0.02, "lookback_days": 252}
        )
        results = orchestrator.run("aapl")
    assert set(results) == {"symbol", "data", "signal", "backtest", "risk", "news", "report"}
    assert results["symbol"] == "AAPL"
    assert "QUANT HIVE ANALYSIS" in results["report"]
    assert results["news"] == "Balanced context."
    assert len(orchestrator.memory.history()) == 6
    download.assert_called_once()
    groq_class.return_value.chat.completions.create.assert_called_once()
