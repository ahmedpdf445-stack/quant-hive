"""Market-data retrieval agent backed by yfinance."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)


class DataAgent:
    """Retrieve historical OHLCV observations for a market symbol."""

    def fetch(self, symbol: str, lookback: int) -> Any:
        """Download historical market data for the requested number of days."""
        try:
            if not isinstance(symbol, str) or not symbol.strip():
                raise ValueError("symbol must be a non-empty string")
            days = int(lookback)
            if days <= 0:
                raise ValueError("lookback must be a positive number of days")
            import yfinance as yf
            import pandas as pd

            end = datetime.now(timezone.utc).date() + timedelta(days=1)
            start = end - timedelta(days=days)
            frame = yf.download(
                symbol.strip().upper(),
                start=start.isoformat(),
                end=end.isoformat(),
                auto_adjust=True,
                progress=False,
                threads=False,
            )
            if frame is None or frame.empty:
                logger.warning("No market data returned for %s", symbol)
                return pd.DataFrame()
            if isinstance(frame.columns, pd.MultiIndex):
                price_level = next(
                    (level for level in range(frame.columns.nlevels) if "Close" in frame.columns.get_level_values(level)),
                    0,
                )
                frame.columns = frame.columns.get_level_values(price_level)
            frame = frame.copy()
            frame.columns = [str(column).title() for column in frame.columns]
            if "Close" not in frame.columns:
                raise ValueError("Downloaded data does not contain a Close column")
            logger.info("Fetched %d rows for %s", len(frame), symbol)
            return frame
        except Exception:
            logger.exception("Unable to fetch market data for %r", symbol)
            try:
                import pandas as pd
                return pd.DataFrame()
            except Exception:
                logger.exception("Pandas is unavailable while handling data fetch error")
                return []
