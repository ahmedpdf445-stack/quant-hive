"""Moving-average signal generation agent."""

import logging
import math
from typing import Any, Dict

logger = logging.getLogger(__name__)


class SignalAgent:
    """Generate a trend signal using 20-period and 50-period simple averages."""

    def generate(self, data: Any) -> Dict[str, Any]:
        """Return direction, price, averages, and a conservative stop estimate."""
        try:
            if data is None or getattr(data, "empty", False):
                return {"direction": "HOLD", "entry": None, "stop": None, "reason": "No market data"}
            if "Close" not in data:
                raise ValueError("Market data must contain a Close column")
            close = data["Close"]
            if getattr(close, "ndim", 1) > 1:
                close = close.iloc[:, 0]
            close = close.dropna()
            if close.empty:
                return {"direction": "HOLD", "entry": None, "stop": None, "reason": "No closing prices"}
            fast = close.rolling(window=20, min_periods=20).mean()
            slow = close.rolling(window=50, min_periods=50).mean()
            price = float(close.iloc[-1])
            fast_value = float(fast.iloc[-1]) if not fast.empty else float("nan")
            slow_value = float(slow.iloc[-1]) if not slow.empty else float("nan")
            if not math.isfinite(price) or price <= 0:
                raise ValueError("Latest closing price must be finite and positive")
            if not math.isfinite(fast_value) or not math.isfinite(slow_value):
                direction = "HOLD"
                reason = "At least 50 valid observations are required"
            elif fast_value > slow_value:
                direction = "BUY"
                reason = "SMA 20 is above SMA 50"
            elif fast_value < slow_value:
                direction = "SELL"
                reason = "SMA 20 is below SMA 50"
            else:
                direction = "HOLD"
                reason = "SMA 20 equals SMA 50"
            stop = price * (0.98 if direction != "SELL" else 1.02)
            result = {
                "direction": direction,
                "entry": price,
                "stop": stop,
                "sma_20": fast_value if math.isfinite(fast_value) else None,
                "sma_50": slow_value if math.isfinite(slow_value) else None,
                "reason": reason,
            }
            logger.info("Generated %s signal at %.4f", direction, price)
            return result
        except Exception:
            logger.exception("Unable to generate signal")
            return {"direction": "HOLD", "entry": None, "stop": None, "reason": "Signal analysis error"}
