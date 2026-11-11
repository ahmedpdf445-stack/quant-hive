
QUANT-HIVE 
Super Multi-Agent Quant System — Built From Scratch

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Tests](https://img.shields.io/badge/Tests-15%2F15_Passed-green)
![Architecture](https://img.shields.io/badge/Architecture-Clean-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Production_Ready-success)

> ⚠️ **NOT a trading bot.** It does **NOT** connect to a broker, submit orders, or manage a portfolio.
> It is a **Risk & Analysis-only** research and decision-support system.

**Built From Scratch — No LangChain, No CrewAI, No Backtrader, No Frameworks.**
**6 Agents. 1 Orchestrator. 0 Magic. 100% Transparent Code.**

---

🚀 What Is QUANT-HIVE?

QUANT-HIVE is a clean-architecture, multi-agent system that analyzes a market symbol end-to-end:

**Data → Signal → Backtest → Risk → News → Report**

You give it `BTC-USD`, it gives you a full institutional-grade report in seconds:
Signal, Backtest PnL, Win Rate, Risk Verdict, and News Sentiment — all with auditable logic.

---

📊 Example Output — Real Run

```text
=== QUANT-HIVE REPORT: BTC-USD ===
Signal: BUY | Last: 97,500.00 | SMA20: 96,820.12 | SMA50: 94,310.45
Backtest: +1,250.00 PnL | Win Rate: 62.5% | Trades: 8
Risk: PROCEED | Level: LOW | Max Loss: -185.40
News: BULLISH - Institutional demand remains strong for BTC.
Decision: PROCEED - BUY
No black box. Every number is traceable to a line of code.

---

🏛️ Architecture — Clean, Sequential, Auditable
                    ┌──────────────────┐
                    │   CLI / main.py  │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │   Orchestrator   │
                    │ Sequential Flow  │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  1. Data     │    │  2. Signal   │    │  5. News     │
│  yfinance    │───▶│  SMA 20/50   │───▶│  Groq LLM    │
│  OHLCV       │    │  BUY/SELL    │    │  Sentiment   │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └─────────┬─────────┴─────────┬─────────┘
                 ▼                   ▼
        ┌──────────────┐    ┌──────────────┐
        │ 3. Backtest  │───▶│  4. Risk     │
        │ 252 Days     │    │  Engine +    │
        │ Simulation   │    │  Agent       │
        └──────┬───────┘    └──────┬───────┘
               │                   │
               └─────────┬─────────┘
                         ▼
                ┌──────────────┐
                │  6. Report   │
                │  Final Report│
                └──────┬───────┘
                       ▼
                ┌──────────────┐
                │   Memory     │
                │  Run History │
                └──────────────┘
*Agents execute sequentially via Orchestrator.* No parallel magic, no hidden state.
Each stage is isolated, testable, and replaceable.
Agent	Responsibility	Input → Output
**Data Agent**	Fetch OHLCV	`BTC-USD` → 252 bars
**Signal Agent**	SMA 20 / 50 Crossover	Prices → `BUY / SELL / HOLD`
**Backtest Agent**	Historical Simulation	Prices + Signal → Trades, PnL, Win Rate
**Risk Agent + Engine**	Sizing & Verdict	Signal + Backtest → `PROCEED / CAUTION / AVOID`
**News Agent**	LLM Sentiment (Optional)	Symbol → `BULLISH / BEARISH / NEUTRAL`
**Report Agent**	Final Report	All Stages → Human-readable Report
---

📁 Project Structure
quant-hive/
├── main.py                  # CLI Entry Point
├── README.md
├── LICENSE                  # MIT
├── requirements.txt
├── config/
│   └── quant.json           # Capital, Risk, Symbols, Lookback
├── kernel/
│   ├── __init__.py
│   ├── orchestrator.py      # Coordinates 6 Agents
│   ├── risk_engine.py       # Position Sizing Math
│   └── memory.py            # In-Memory Audit Log
├── agents/
│   ├── __init__.py
│   ├── data_agent.py        # yfinance
│   ├── signal_agent.py      # SMA Crossover
│   ├── backtest_agent.py    # Simulation
│   ├── risk_agent.py        # Verdict Logic
│   ├── news_agent.py        # Groq Llama 3.3
│   └── report_agent.py      # Report Compiler
└── tests/
    └── test_hive.py         # 15 Tests, 0 Network Calls
---

⚡ Quick Start

1. Install
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
2. Run
With symbol
python main.py BTC-USD

Without symbol - will prompt you
python main.py

Multiple symbols
python main.py BTC-USD ETH-USD GC=F
3. Run Tests
python -m pytest tests/ -v
15 passed in 0.42s
Tests use mocks. *No network calls. No API keys required for tests.*

4. Optional - News Sentiment
export GROQ_API_KEY=your_key_here
python main.py BTC-USD
Without a key, News Agent returns `NEUTRAL` and the system continues. No crash.

---

🧮 Configuration & Risk Model

`config/quant.json`:
{
  "capital": 10000.0,
  "risk_per_trade": 0.02,
  "symbols": ["BTC-USD", "ETH-USD", "GC=F"],
  "lookback_days": 252,
  "risk_free_rate": 0.05
}
*Position Sizing Math:*
Position Size = (Capital × Risk Per Trade) / |Entry - Stop|
Example: (10,000 × 0.02) / |100 - 98| = 100 shares
Max Loss Per Trade = $200 (2% of capital)
*Signal Logic:*
- `SMA20 > SMA50` → *BUY*
- `SMA20 < SMA50` → *SELL*
- `< 50 closes` → *HOLD* (insufficient data)

*Risk Verdict:*
- *PROCEED:* Win Rate ≥ 50% + Positive PnL + Low Risk
- *CAUTION:* Positive PnL but High Risk / Low Win Rate
- *AVOID:* No Trades / Negative PnL / High Risk

---

✅ Engineering Principles

- *Clean Architecture:* Kernel ≠ Agents ≠ CLI. No circular imports.
- *Single Responsibility:* Each Agent does one thing, and does it well.
- *No Frameworks:* No LangChain, No CrewAI. Pure Python. You can read every line.
- *Fail-Safe:* Any Agent fails → System returns `AVOID`, never crashes.
- *Testable:* 15 unit tests, 100% offline, 100% deterministic.
- *Auditable:* `Memory` logs every stage for every run.

---

🛠️ Tech Stack
Layer	Tech
**Language**	Python 3.11
**Market Data**	yfinance
**LLM**	Groq — Llama 3.3 70B Versatile
**Testing**	pytest
**Architecture**	Clean Architecture, Multi-Agent
---

⚠️ Disclaimer — Not a Trading Bot

QUANT-HIVE is *NOT* a trading bot. It is a *Risk & Analysis-only* research tool.

It does *NOT* place, route, or execute trades. It does *NOT* provide investment, legal, or tax advice. It must *NOT* be relied upon as a recommendation to buy, sell, or hold any asset.

Signals and backtest results can be wrong, incomplete, stale, or misleading. Model-generated text may be inaccurate or fabricated and is *NOT* verified news. Backtests are simplified historical simulations — they omit fees, slippage, liquidity, taxes, corporate actions, gaps, and short-sale constraints.

Financial markets involve substantial risk, including loss of principal. You are solely responsible for independently verifying information and for any decisions you make. *Use at your own risk. No performance or accuracy is guaranteed.*

---

📄 License

MIT License — See [LICENSE](LICENSE) for details.
Free to use, modify, and distribute with attribution.

---

👨‍💻 Author

Focused on Clean Architecture, Quantitative Finance, and Multi-Agent Systems.

*Topics:* `quantitative-finance` `multi-agent-systems` `python` `clean-architecture` `algorithmic-trading` `risk-management` `yfinance`
