"""Historical strategy simulation agent."""

import logging
import math
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class BacktestAgent:
    """Simulate a simple SMA-regime strategy without placing real orders."""

    def __init__(self, risk_engine: Any) -> None:
        """Initialize the simulator with the shared risk sizing engine."""
        try:
            if risk_engine is None:
                raise ValueError("risk_engine is required")
            self.risk_engine = risk_engine
        except Exception:
            logger.exception("Unable to initialize backtest agent")
            raise

    def run(self, data: Any, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate historical SMA exposure and return performance statistics."""
        try:
            empty_result: Dict[str, Any] = {
                "trade_count": 0,
                "return_pct": 0.0,
                "max_drawdown_pct": 0.0,
                "position_size": 0.0,
                "status": "insufficient_data",
                "trades": [],
            }
            if data is None or getattr(data, "empty", False) or "Close" not in data:
                return empty_result
            close = data["Close"]
            if getattr(close, "ndim", 1) > 1:
                close = close.iloc[:, 0]
            close = close.astype(float).dropna()
            if len(close) < 51:
                return empty_result
            fast = close.rolling(20, min_periods=20).mean()
            slow = close.rolling(50, min_periods=50).mean()
            regime = (fast > slow).astype(float)
            daily_returns = close.pct_change().replace([float("inf"), float("-inf")], 0).fillna(0)
            strategy_returns = (regime.shift(1).fillna(0) * daily_returns).iloc[50:]
            equity = (1.0 + strategy_returns).cumprod()
            if equity.empty:
                return empty_result
            return_pct = (float(equity.iloc[-1]) - 1.0) * 100.0
            running_peak = equity.cummax()
            drawdowns = (equity / running_peak - 1.0) * 100.0
            max_drawdown = abs(float(drawdowns.min())) if not drawdowns.empty else 0.0
            changes = regime.diff().fillna(regime.iloc[0]).abs()
            trade_count = int((changes.iloc[50:] > 0).sum())
            entry = signal.get("entry") if isinstance(signal, dict) else None
            stop = signal.get("stop") if isinstance(signal, dict) else None
            size = self.risk_engine.position_size(entry, stop) if entry and stop else 0.0
            trades: List[Dict[str, Any]] = []
            if trade_count:
                trades.append({"type": "SMA regime changes", "count": trade_count})
            result = {
                "trade_count": trade_count,
                "return_pct": return_pct if math.isfinite(return_pct) else 0.0,
                "max_drawdown_pct": max_drawdown if math.isfinite(max_drawdown) else 0.0,
                "position_size": float(size),
                "status": "complete",
                "trades": trades,
            }
            logger.info("Backtest completed: %.2f%% return over %d regime changes", result["return_pct"], trade_count)
            return result
        except Exception:
            logger.exception("Backtest failed")
            return {
                "trade_count": 0,
                "return_pct": 0.0,
                "max_drawdown_pct": 0.0,
                "position_size": 0.0,
                "status": "error",
                "trades": [],
            }
