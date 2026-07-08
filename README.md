# Indian Equity Momentum Pilot

Pilot backtesting project for Indian equities using public NSE data, yfinance, Python, and LLM-assisted research workflows.

This project evaluates simple trend-following, equal-weight portfolio, and momentum-based strategies on Indian large-cap stocks against the Nifty 50 benchmark (`^NSEI`).

> Status: research pilot only. This is not investment advice, not a live trading system, and it does not place orders.

## Purpose

The goal is to build a disciplined workflow for Indian equity research:

1. Validate NSE data availability from public sources.
2. Compare each strategy against a clear benchmark.
3. Reject weak strategies early.
4. Keep calculations deterministic and reproducible in Python.
5. Use LLM tools only for research assistance, interpretation, and reporting.

## Tools

- Python
- pandas
- numpy
- yfinance
- Vibe-Trading / LLM-assisted research workflow for exploration and reporting

## Project Structure

```text
indian-equity-momentum-pilot/
├── README.md
├── requirements.txt
├── .gitignore
├── docs/
│   └── methodology.md
├── results/
│   └── pilot_results_summary.md
└── scripts/
    ├── reliance_backtest.py
    ├── portfolio_backtest.py
    ├── momentum_compare.py
    └── momentum_lookback_compare.py
```

## Strategies Tested

### 1. RELIANCE SMA Crossover

Two simple moving-average timing rules on `RELIANCE.NS`:

- 20-day / 50-day SMA
- 50-day / 200-day SMA

Result: both failed versus buy-and-hold.

### 2. Equal-Weight 3-Stock Portfolio

Monthly rebalanced equal-weight portfolio of:

- `RELIANCE.NS`
- `HDFCBANK.NS`
- `INFY.NS`

Result: underperformed Nifty 50.

### 3. Large-Cap Momentum Pilot

Monthly momentum strategy on a 15-stock Indian large-cap universe. Stocks are ranked by historical momentum and the top N are selected.

The strongest pilot result came from diversified Top-10 momentum, especially in the 12-month lookback test.

## Current Best Pilot Result

The best observed result in this pilot was the Top-10, 12-month momentum strategy:

| Metric | Top-10 12M Momentum | Nifty 50 |
|---|---:|---:|
| CAGR | 14.11% | 11.99% |
| Sharpe | 1.23 | 0.98 |
| Max Drawdown | -12.23% | Benchmark period differs by alignment |

These results are preliminary and should not be treated as live-trading evidence.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/momentum_lookback_compare.py
```

## Important Limitations

- Small universe of 15 manually selected large-cap stocks.
- Short sample period: 2021–2025.
- No full survivorship-bias control.
- Simplified transaction cost assumptions.
- No slippage model.
- No liquidity constraint model.
- No tax impact.
- No walk-forward validation yet.
- No out-of-sample paper trading yet.

## Suggested Next Steps

1. Expand the universe to Nifty 50 or Nifty 100.
2. Add sector constraints.
3. Add volatility-adjusted weights.
4. Add risk-free-rate adjusted Sharpe.
5. Add rolling walk-forward testing.
6. Add turnover and slippage analysis.
7. Add monthly holdings export.
8. Add automated result tables and charts.
9. Compare momentum with quality, valuation, and low-volatility factors.
10. Keep live trading disabled until research, risk controls, and paper trading pass.

## Disclaimer

This repository is for educational and research purposes only. It is not financial advice, investment advice, or a recommendation to buy or sell securities.
