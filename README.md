# Quant Hive

**Quant Hive** is a Python 3.11 Super Multi-Agent Quant System for market-data analysis, historical simulation, and risk review. It is a research and decision-support project only: it does not connect to a broker, submit orders, or manage a portfolio.

## Architecture

```text
                       +----------------------+
                       |      CLI / main.py   |
                       +----------+-----------+
                                  |
                       +----------v-----------+
                       |    Orchestrator      |
                       | sequential workflow  |
                       +----------+-----------+
                                  |
        +-------------------------+-------------------------+
        |                         |                         |
+-------v--------+       +--------v-------+       +---------v-------+
| Data Agent     |       | Signal Agent   |       | News Agent      |
| yfinance OHLCV |       | SMA 20 / SMA 50|       | optional Groq   |
+-------+--------+       +--------+-------+       +---------+-------+
        |                         |                         |
        +-------------------------+-------------------------+
                                  |
                       +----------v-----------+
                       | Backtest Agent       |
                       | historical simulation|
                       +----------+-----------+
                                  |
                      +-----------v-----------+
                      | Risk Agent + Engine   |
                      | sizing / assessment   |
                      +-----------+-----------+
                                  |
                       +----------v-----------+
                       | Report Agent         |
                       | analysis-only output |
                       +----------------------+
                                  |
                       +----------v-----------+
                       | Memory (run history) |
                       +----------------------+
```

The agents execute sequentially. Market history comes from `yfinance`; an optional Groq API call may add model-generated context. The backtest is a simplified historical SMA-regime simulation—not a forecast or a representation of live execution. In-memory `Memory` records each stage of the current process.

## Requirements

- Python 3.11
- Packages listed in `requirements.txt`
- Optional: a `GROQ_API_KEY` environment variable for model-generated news context

Install dependencies:

```bash
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## How to Run

Run with a symbol argument:

```bash
python main.py AAPL
```

Or run without an argument to be prompted for a symbol:

```bash
python main.py
```

The default configuration is `config/quant.json`. It defines the reference capital, maximum risk per modeled position, supported example symbols, and lookback period. The command prints a formatted report to the terminal. A Groq key is optional; without it, the system clearly marks news analysis unavailable and continues.

Run the offline test suite:

```bash
python -m pytest -q
```

The tests patch external data/API clients and do not make network calls.

## Configuration and Risk Model

- `capital` is the reference capital used for position sizing.
- `risk_per_trade` is the maximum fraction of reference capital modeled as loss between entry and stop.
- Position size is calculated as `capital × risk_per_trade / abs(entry − stop)`.
- The signal uses the latest 20- and 50-observation simple moving averages. Fewer than 50 valid closes result in `HOLD`.
- Risk assessments are `PROCEED`, `CAUTION`, or `AVOID`, based on basic rule-based checks of the signal and backtest metrics.

These calculations are educational analysis aids, not individualized financial advice. Historical performance, position sizing, and risk labels are simplified and may omit fees, liquidity, slippage, taxes, corporate actions, gaps, short-sale constraints, and other real-world factors.

## Disclaimer — Not a Trading Bot

**Quant Hive is NOT a trading bot. It is a Risk & Analysis-only research tool.** It does not place, route, or execute trades; it does not provide investment, legal, or tax advice; and it must not be relied upon as a recommendation to buy, sell, or hold any asset. Signals and backtest results can be wrong, incomplete, stale, or misleading. Model-generated text may be inaccurate or fabricated and is not verified news. Financial markets involve substantial risk, including the loss of principal. You are solely responsible for independently verifying information and for any decisions you make. Use at your own risk; no performance or accuracy is guaranteed.
