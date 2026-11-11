"""Sequentially coordinate Quant Hive's analysis agents."""

import logging
from typing import Any, Dict

from agents.backtest_agent import BacktestAgent
from agents.data_agent import DataAgent
from agents.news_agent import NewsAgent
from agents.report_agent import ReportAgent
from agents.risk_agent import RiskAgent
from agents.signal_agent import SignalAgent
from kernel.memory import Memory
from kernel.risk_engine import RiskEngine

logger = logging.getLogger(__name__)


class Orchestrator:
    """Run the six analysis agents and retain their output in shared memory."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Create agents using a validated configuration dictionary."""
        try:
            self.config = dict(config)
            self.memory = Memory()
            self.risk_engine = RiskEngine(
                capital=self.config.get("capital", 10000.0),
                risk_per_trade=self.config.get("risk_per_trade", 0.02),
            )
            self.data_agent = DataAgent()
            self.signal_agent = SignalAgent()
            self.backtest_agent = BacktestAgent(self.risk_engine)
            self.risk_agent = RiskAgent(self.risk_engine)
            self.news_agent = NewsAgent()
            self.report_agent = ReportAgent()
        except Exception:
            logger.exception("Unable to initialize orchestrator")
            raise

    def run(self, symbol: str) -> Dict[str, Any]:
        """Fetch market data and run each analysis agent sequentially."""
        try:
            if not isinstance(symbol, str) or not symbol.strip():
                raise ValueError("symbol must be a non-empty string")
            symbol = symbol.strip().upper()
            lookback = int(self.config.get("lookback_days", 252))
            if lookback <= 0:
                raise ValueError("lookback_days must be positive")

            data = self.data_agent.fetch(symbol, lookback)
            self.memory.set("data", data)
            signal = self.signal_agent.generate(data)
            self.memory.set("signal", signal)
            backtest = self.backtest_agent.run(data, signal)
            self.memory.set("backtest", backtest)
            risk = self.risk_agent.assess(signal, backtest)
            self.memory.set("risk", risk)
            news = self.news_agent.analyse(symbol)
            self.memory.set("news", news)

            results: Dict[str, Any] = {
                "symbol": symbol,
                "data": data,
                "signal": signal,
                "backtest": backtest,
                "risk": risk,
                "news": news,
            }
            report = self.report_agent.compile(results)
            self.memory.set("report", report)
            results["report"] = report
            logger.info("Completed analysis for %s", symbol)
            return results
        except Exception:
            logger.exception("Analysis failed for symbol %r", symbol)
            raise
