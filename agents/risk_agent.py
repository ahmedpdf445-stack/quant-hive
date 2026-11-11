"""Translate signal and backtest metrics into an analysis risk verdict."""

import logging
import math
from typing import Any, Dict

logger = logging.getLogger(__name__)


class RiskAgent:
    """Assess a candidate analysis as PROCEED, CAUTION, or AVOID."""

    def __init__(self, risk_engine: Any) -> None:
        """Initialize the assessor with the shared risk engine."""
        try:
            if risk_engine is None:
                raise ValueError("risk_engine is required")
            self.risk_engine = risk_engine
        except Exception:
            logger.exception("Unable to initialize risk agent")
            raise

    def assess(self, signal: Dict[str, Any], backtest: Dict[str, Any]) -> str:
        """Return a conservative verdict based on signal quality and simulation."""
        try:
            if not isinstance(signal, dict) or not isinstance(backtest, dict):
                return "AVOID"
            direction = str(signal.get("direction", "HOLD")).upper()
            if direction not in {"BUY", "SELL"}:
                return "CAUTION"
            entry = signal.get("entry")
            stop = signal.get("stop")
            size = backtest.get("position_size", 0.0)
            if not entry or not stop or not self.risk_engine.validate(size, entry, stop):
                return "AVOID"
            if backtest.get("status") != "complete" or int(backtest.get("trade_count", 0)) <= 0:
                return "CAUTION"
            result = float(backtest.get("return_pct", 0.0))
            drawdown = float(backtest.get("max_drawdown_pct", 0.0))
            if not math.isfinite(result) or not math.isfinite(drawdown):
                return "AVOID"
            if drawdown >= 30.0 or result <= -10.0:
                verdict = "AVOID"
            elif result > 0 and drawdown < 20.0:
                verdict = "PROCEED"
            else:
                verdict = "CAUTION"
            logger.info("Risk assessment verdict: %s", verdict)
            return verdict
        except Exception:
            logger.exception("Risk assessment failed")
            return "AVOID"
