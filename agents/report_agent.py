"""Human-readable analysis report compiler."""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ReportAgent:
    """Compile structured agent output into a readable risk report."""

    def compile(self, results: Dict[str, Any]) -> str:
        """Format signal, backtest, risk, and news details for CLI display."""
        try:
            symbol = str(results.get("symbol", "UNKNOWN"))
            signal = results.get("signal") or {}
            backtest = results.get("backtest") or {}
            risk = results.get("risk", "CAUTION")
            news = results.get("news", "No news context available.")
            direction = signal.get("direction", "HOLD") if isinstance(signal, dict) else "HOLD"
            entry = signal.get("entry") if isinstance(signal, dict) else None
            stop = signal.get("stop") if isinstance(signal, dict) else None
            entry_text = f"{float(entry):.4f}" if entry is not None else "N/A"
            stop_text = f"{float(stop):.4f}" if stop is not None else "N/A"
            lines = [
                f"QUANT HIVE ANALYSIS — {symbol}",
                "=" * 48,
                f"Signal: {direction}",
                f"Reference entry: {entry_text}",
                f"Reference stop: {stop_text}",
                f"Risk verdict: {risk}",
                "",
                "Historical simulation (not a forecast):",
                f"  Status: {backtest.get('status', 'unavailable')}",
                f"  Regime changes/trades: {backtest.get('trade_count', 0)}",
                f"  Return: {float(backtest.get('return_pct', 0.0)):.2f}%",
                f"  Maximum drawdown: {float(backtest.get('max_drawdown_pct', 0.0)):.2f}%",
                "",
                "News context:",
                str(news),
                "",
                "Analysis only — not an instruction to trade.",
            ]
            report = "\n".join(lines)
            logger.info("Compiled analysis report for %s", symbol)
            return report
        except Exception:
            logger.exception("Unable to compile analysis report")
            return "QUANT HIVE ANALYSIS\nReport generation failed; see application logs."
