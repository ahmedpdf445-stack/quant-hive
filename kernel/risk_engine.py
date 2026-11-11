"""Position sizing and risk-limit validation utilities."""

import logging
import math
from typing import Any

logger = logging.getLogger(__name__)


class RiskEngine:
    """Calculate position sizes constrained by per-trade capital risk."""

    def __init__(self, capital: float, risk_per_trade: float) -> None:
        """Initialize the engine after validating its capital parameters."""
        try:
            self.capital = float(capital)
            self.risk_per_trade = float(risk_per_trade)
            if not math.isfinite(self.capital) or self.capital <= 0:
                raise ValueError("capital must be a finite positive number")
            if not math.isfinite(self.risk_per_trade) or not 0 < self.risk_per_trade <= 1:
                raise ValueError("risk_per_trade must be greater than 0 and at most 1")
        except (TypeError, ValueError, OverflowError):
            logger.exception("Invalid risk engine configuration")
            raise

    def position_size(self, entry: float, stop: float) -> float:
        """Return units sized so stop-loss exposure stays within the risk budget."""
        try:
            entry_value = float(entry)
            stop_value = float(stop)
            distance = abs(entry_value - stop_value)
            if not all(math.isfinite(value) for value in (entry_value, stop_value)):
                raise ValueError("entry and stop must be finite")
            if entry_value <= 0 or stop_value <= 0 or distance <= 0:
                raise ValueError("entry and stop must be positive and different")
            size = (self.capital * self.risk_per_trade) / distance
            logger.info("Calculated position size %.8f", size)
            return size
        except (TypeError, ValueError, ZeroDivisionError, OverflowError):
            logger.exception("Unable to calculate position size")
            return 0.0

    def validate(self, size: float, entry: float, stop: float) -> bool:
        """Check that a proposed size is finite, valid, and within the risk budget."""
        try:
            size_value = float(size)
            entry_value = float(entry)
            stop_value = float(stop)
            if not all(math.isfinite(value) for value in (size_value, entry_value, stop_value)):
                return False
            if size_value <= 0 or entry_value <= 0 or stop_value <= 0:
                return False
            distance = abs(entry_value - stop_value)
            if distance <= 0:
                return False
            permitted_loss = self.capital * self.risk_per_trade
            valid = size_value * distance <= permitted_loss + 1e-9
            logger.info("Position risk validation result: %s", valid)
            return valid
        except (TypeError, ValueError, OverflowError):
            logger.exception("Unable to validate proposed position")
            return False
