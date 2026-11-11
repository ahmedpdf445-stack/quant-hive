"""Command-line entry point for Quant Hive analysis."""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from kernel.orchestrator import Orchestrator

logger = logging.getLogger(__name__)


def load_config(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load and validate the JSON application configuration."""
    try:
        config_path = path or Path(__file__).resolve().parent / "config" / "quant.json"
        with config_path.open("r", encoding="utf-8") as config_file:
            config = json.load(config_file)
        if not isinstance(config, dict):
            raise ValueError("Configuration root must be a JSON object")
        return config
    except Exception:
        logger.exception("Unable to load configuration")
        raise


def main(argv: Optional[List[str]] = None) -> int:
    """Run one symbol analysis from an argument or an interactive prompt."""
    try:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
        arguments = list(sys.argv[1:] if argv is None else argv)
        symbol = arguments[0].strip() if arguments else input("Enter a symbol (for example AAPL): ").strip()
        if not symbol:
            raise ValueError("A non-empty symbol is required")
        config = load_config()
        results = Orchestrator(config).run(symbol)
        print(results["report"])
        return 0
    except (EOFError, KeyboardInterrupt):
        logger.warning("Analysis cancelled by user")
        return 130
    except Exception as exc:
        logger.exception("Quant Hive analysis could not be completed")
        print(f"Quant Hive error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
